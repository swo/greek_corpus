#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the database.
#
# - Each wiktionary entry is for one headword
# - Each headword can have multiple etymologies
# - Each etymology can have multiple definitions
# - Each definition can have multiple "texts"
#
# So if x is the entry for "με":
# x[0]['definitions'][0]['text'][0] is
# first etymology, list of definitions, first definition, list of definition texts, first definition text

import re, sqlite3, json, yaml

class Word:
    def __init__(self, word, raw_wiki, supplemental_definitions):
        self.word = word
        self.wiki = json.loads(raw_wiki)

        if self.word in supplemental_definitions:
            # don't parse, just look in the manually-entered data
            self.anki = supplemental_definitions[self.word]['anki']
            # change the word to the new display
            self.word = supplemental_definitions[self.word]['new_word']
            self.keep = True
        else:
            if self.wiki is None:
                # drop if no wiki data
                self.keep = False
            else:
                self.definitions = [Definition(self.word, x) for etymology in self.wiki for x in etymology['definitions']]

                if len([x for x in self.definitions if x.keep]) > 0:
                    self.keep = True
                    self.anki = self.ankiize()
                else:
                    self.keep = False

    def ankiize(self):
        return "<br><br>".join([x.anki for x in self.definitions if x.keep])


class Definition:
    def __init__(self, word, definition):
        self.word = word
        self.part_of_speech = definition['partOfSpeech']

        if self.part_of_speech in ['numeral', 'letter']:
            self.keep = False
        else:
            self.texts = self.clean_texts(definition['text'])

        if self.keep:
            self.anki = self.ankiize()

    @staticmethod
    def useless_text(x):
        return ('dated' in x) or (x.startswith('form of'))

    def clean_texts(self, texts):
        texts = [x for x in texts if not self.useless_text(x)]
        # print('*texts*', texts)

        if len(texts) == 0:
            self.keep = False
            return None

        first_text = texts[0]

        if '•' not in first_text:
            self.keep = False
            return None

        m = re.match("(?P<word>.+)\s+•\s+\((?P<pronunciation>.+)\)\s*(?P<rest>.*)", first_text)
        if m is None:
            raise RuntimeError('unparsed definition:', self.word, first_text, other_texts)

        self.first_text_rest = m.groupdict()['rest']
        self.other_texts = [re.sub('\s+', ' ', x) for x in texts[1:]]
        self.keep = True

    def ankiize(self):
        # print([self.word, self.part_of_speech, self.first_text_rest, self.texts])
        first_line = "{} {}".format(self.word, self.part_of_speech)

        if self.first_text_rest != '':
            first_line += self.first_text_rest

        lines = [first_line] + self.other_texts
        return "<br>".join(lines)


def load_supplemental_definitions(fn):
    with open(fn) as f:
        defs = yaml.load(f)

    for word, data in defs.items():
        if 'new_word' not in data:
            data['new_word'] = word

        data['anki'] = data['new_word'] + " " + re.sub(";", "<br>", data['def'])

    return defs


if __name__ == '__main__':
    # load up DB
    connection = sqlite3.connect('greek_db')
    cursor = connection.cursor()

    # load up words to skip
    with open('words_to_skip.txt') as f:
        words_to_skip = [line.rstrip() for line in f]

    # load up supplemental definitions
    supplemental_definitions = load_supplemental_definitions('supplemental_definitions.yaml')

    rows = list(cursor.execute('''select word, wiki from lemmas where wiki is not null order by frequency desc'''))

    with open('words.txt', 'w') as f:
        for row in rows:
            print(row[0], file=f)

    words = [Word(x[0], x[1], supplemental_definitions) for x in rows if x[0] not in words_to_skip]

    # look for dropped words
    dropped_words = [x for x in words if not x.keep]
    with open('dropped_words.txt', 'w') as f:
        for x in dropped_words:
            print(x.word, file=f)

    with open('anki.tsv', 'w') as f:
        for word in words:
            if word.keep:
                print(word.word, word.anki, sep='\t', file=f)
