#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the database.
#
# Each wiktionary entry is for a single headword and consists of a list of
# etymologies, which in turn can contain multiple definitions. I put the
# definitions from all etymologies together.

import re
from tinydb import TinyDB, Query

def clean_headword(headword):
    etymologies = headword['wiktionary_entry']

    if etymologies is None:
        homonyms = None
    else:
        homonyms = [clean_definition(definition) for etymology in etymologies for definition in etymology['definitions']]

    return {'word': headword['word'], 'homonyms': homonyms, 'frequency': int(headword['frequency'])}

def clean_definition(definition):
    part_of_speech = definition['partOfSpeech']
    first_text = definition['text'][0]
    other_texts = [x for x in definition['text'][1:] if not useless_text(x)]

    result = {'part_of_speech': part_of_speech, 'definitions': other_texts}

    # add gender for nouns, and also plural form is mentioned
    if part_of_speech == 'noun':
        m = re.match('(.+) • \(([^\(\)]+)\)\xa0([mfn ,]+)', first_text)
        word, pronunciation, gender = m.groups()
        gender = gender.rstrip()
        result.update({'gender': gender})

        if 'plural' in first_text:
            m = re.search('\(plural (.+)\)', first_text)
            assert m is not None
            result.update({'plural': m.groups()[0]})

    return result

def useless_text(x):
    if '\xa0' in x:
        assert ('form of' in x) or ('(dated)' in x)
        return True

    return False

def bad_headword(r):
    # missing homonyms?
    if r['homonyms'] is None or r['homonyms'] == []:
        return True

    # just empty definitions?
    empty_def = any([len(h['definitions']) == 0 for h in r['homonyms']])
    nonempty_def = any([len(h['definitions']) > 0 for h in r['homonyms']])

    if empty_def and not nonempty_def:
        return True

    return False

def ankiize_headword(x):
    return "<br><br>".join([ankiize_homonym(h, x['word']) for h in x['homonyms']])

def ankiize_homonym(homonym, word):
    if homonym['part_of_speech'] == 'noun':
        assert 'gender' in homonym
        if 'plural' in homonym:
            first_line = "{} noun {} (plural {})".format(word, homonym['gender'], homonym['plural'])
        else:
            first_line = "{} noun {}".format(word, homonym['gender'])
    else:
        first_line = "{} {}".format(word, homonym['part_of_speech'])

    lines = [first_line] + homonym['definitions']

    return "<br>".join(lines)


if __name__ == '__main__':
    db = TinyDB('db.json')
    query = Query()

    headwords = [x for x in db.all() if 'wiktionary_entry' in x]
    clean_headwords = [clean_headword(x) for x in headwords]
    bad_headwords = [x for x in clean_headwords if bad_headword(x)]
    good_headwords = sorted([x for x in clean_headwords if not bad_headword(x)], key=lambda x: x['frequency'], reverse=True)

    with open('bad_words.txt', 'w') as f:
        for hw in bad_headwords:
            print(hw['word'], file=f)

    with open('anki.tsv', 'w') as f:
        for headword in good_headwords:
            print(headword['word'], ankiize_headword(headword), sep='\t', file=f)
