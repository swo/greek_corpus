#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the
# database.

import wiktionaryparser
from tinydb import TinyDB, Query

# for fetching wiktionary pages
parser = wiktionaryparser.WiktionaryParser()

def fetch_entry(word):
    try:
        result = parser.fetch(word, 'greek')
    except Exception:
        result = None

    return result

# def fetch_definition(word):
#     result = parser.fetch(word, 'greek')

#     if not (len(result) == 1 and 'definitions' in result[0]):
#         return 'bad length result'

#     definitions = result[0]['definitions']
#     texts = [x['text'] for x in definitions]

#     return '\n\n'.join(['\n'.join(x) for x in texts])


if __name__ == '__main__':
    db = TinyDB('db.json')
    query = Query()

    for record in db:
        if 'wiktionary_entry' not in record:
            word = record['word']
            print(word)

            entry = fetch_entry(word)
            print(entry)

            db.update({'wiktionary_entry': entry}, query.word == word)
            print()
