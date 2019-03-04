#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the
# database.

import wiktionaryparser, multiprocessing
from tinydb import TinyDB, Query

# for fetching wiktionary pages
parser = wiktionaryparser.WiktionaryParser()

def fetch_entry(word):
    try:
        result = parser.fetch(word, 'greek')
    except Exception:
        result = None

    return result

def add_entry(word, db, query):
    print(word)
    wiki = fetch_entry(word)
    print(wiki)
    db.update({'wiktionary_entry': wiki}, query.word == word)
    print('updated')
    print()

    return (word, wiki)


if __name__ == '__main__':
    db = TinyDB('db.json')
    query = Query()

    words_to_fetch = [x['word'] for x in db.all() if 'wiktionary_entry' not in x]

    def f(x):
        add_entry(x, db, query)

    with multiprocessing.Pool(5) as pool:
        pool.map(f, words_to_fetch)
