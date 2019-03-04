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

def good_headword(r, supplemental_definitions):
    if r['word'] in supplemental_definitions:
        return True

    # missing homonyms?
    if r['homonyms'] is None or r['homonyms'] == []:
        return False

    # just empty definitions?
    empty_def = any([len(h['definitions']) == 0 for h in r['homonyms']])
    nonempty_def = any([len(h['definitions']) > 0 for h in r['homonyms']])

    if empty_def and not nonempty_def:
        return False

    return True

def ankiize_headword(x, supplemental_definitions):
    word = x['word']

    if word in supplemental_definitions:
        return supplemental_definitions[word]

    return "<br><br>".join([ankiize_homonym(h, word) for h in x['homonyms']])

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
    # load up DB
    db = TinyDB('db.json')
    query = Query()

    # load up supplemental definitions
    supplemental_definitions = {}
    with open('supplemental_definitions.tsv') as f:
        for line in f:
            word, definition = line.rstrip().split('\t')
            supplemental_definitions[word] = definition

    headwords = sorted([x for x in db.all() if 'wiktionary_entry' in x], key=lambda x: x['frequency'], reverse=True)
    clean_headwords = [clean_headword(x) for x in headwords]
    good_headwords = [x for x in clean_headwords if good_headword(x, supplemental_definitions)]

    missing_definitions = [x for x in clean_headwords if not good_headword(x, supplemental_definitions)]
    if len(missing_definitions) > 0:
        print("{} missing definitions must be manually defined".format(len(missing_definitions)))
        with open('missing_words.txt', 'w') as f:
            for x in missing_definitions:
                print(x['word'], file=f)

        print("Words written to missing_words.txt")

    with open('anki.tsv', 'w') as f:
        for headword in good_headwords:
            print(headword['word'], ankiize_headword(headword, supplemental_definitions), sep='\t', file=f)
