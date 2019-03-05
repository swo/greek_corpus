#!/usr/bin/env python3
#
# This script parses the csv frequency lists downloaded from TenTen and
# uses them to populate the database.

import glob, re, functools, csv, sqlite3, os.path

class Lemma:
    def __init__(self, word, frequency):
        self.word = word
        self.frequency = frequency

    def __eq__(self, other):
        return self.word == other.word and self.frequency == other.frequency

    def __repr__(self):
        return self.word

def load_word_list(fn):
    with open(fn, newline='') as f:
        reader = csv.reader(f)
        rows = [tuple(x) for x in reader]

    assert rows[2] == ('lemma_lc', 'Freq')
    rows = rows[3:]

    return rows

def load_word_lists(fns):
    rows = [row for fn in fns for row in load_word_list(fn)]

    # remove duplicates
    rows = set(rows)

    # lemmatize

    words, frequencies = zip(*rows)
    frequencies = [int(re.sub(',', '', x)) for x in frequencies]

    lemmas = [Lemma(w, f) for w, f in zip(words, frequencies)]

    return lemmas


if __name__ == '__main__':
    fns = glob.glob('raw/*.csv')

    lemmas = load_word_lists(fns)

    # check that there are no duplicates
    words = [lemma.word for lemma in lemmas]
    duplicated_words = set([x for x in words if words.count(x) > 1])
    if len(duplicated_words) > 0:
        raise RuntimeError("Duplicated words in lemma list: {}".format(duplicated_words))

    db_fn = 'greek_db'
    if os.path.isfile(db_fn):
        raise RuntimeError("Database '{}' already exists".format(db_fn))

    connection = sqlite3.connect(db_fn)
    cursor = connection.cursor()
    cursor.execute('''create table lemmas (word text, frequency int, wiki text)''')
    connection.commit()

    for lemma in lemmas:
        cursor.execute('''insert into lemmas (word, frequency) values (?, ?)''', (lemma.word, lemma.frequency))

    connection.commit()
    connection.close()
