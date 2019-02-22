#!/usr/bin/env python3
#
# This script parses the csv frequency lists downloaded from TenTen and
# uses them to populate the database.

import glob, re, functools, csv
from tinydb import TinyDB, Query

class Lemma:
    def __init__(self, word, frequency):
        self.word = word
        self.frequency = frequency

    def __eq__(self, other):
        return (self.word, self.frequency) == (other.word, other.frequency)

    def __lt__(self, other):
        return self.frequency < other.frequency or (self.frequency == other.frequency and self.word < other.word)

    def __repr__(self):
        return self.word


def load_word_list(fn):
    with open(fn, newline='') as f:
        reader = csv.reader(f)
        rows = [x for x in reader]

    assert rows[2] == ['lemma_lc', 'Freq']

    words, frequencies = zip(*rows[3:])
    frequencies = [int(re.sub(',', '', x)) for x in frequencies]

    lemmas = [Lemma(w, f) for w, f in zip(words, frequencies)]

    return lemmas

def run_on_file(fn, func):
    with open(fn) as f:
        content = f.read()

    return(func(content))

if __name__ == '__main__':
    fns = glob.glob('raw/*.csv')
    lemmas = sorted([x for fn in fns for x in load_word_list(fn)], reverse=True)

    db = TinyDB('db.json')
    Entry = Query()

    # find which words we need to add to the database
    csv_words = set([x.word for x in lemmas])
    db_words = set([x['word'] for x in iter(db)])
    words_to_add = csv_words - db_words
    lemmas_to_add = [lemma for lemma in lemmas if lemma.word in words_to_add]

    for lemma in lemmas_to_add:
        db.insert({'word': lemma.word, 'frequency': lemma.frequency})

    with open('words.txt', 'w') as f:
        for lemma in lemmas:
            print(lemma, file=f)
