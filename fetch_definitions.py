#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the
# database.

import wiktionaryparser
from tinydb import TinyDB, Query

# for fetching wiktionary pages
parser = wiktionaryparser.WiktionaryParser()

def fetch_definition(word):
    result = parser.fetch(word, 'greek')

    if not (len(result) == 1 and 'definitions' in result[0]):
        return 'bad length result'

    definitions = result[0]['definitions']
    texts = [x['text'] for x in definitions]

    return '\n\n'.join(['\n'.join(x) for x in texts])


if __name__ == '__main__':
    db = TinyDB('db.json')
    query = Query()

    for record in db:
        if 'definition' not in record:
            word = record['word']

            try:
                definition = fetch_definition(word)
            except:
                definition = 'bad definition'

            print(definition)

            db.update({'definition': definition}, query.word == word)
            print('\n---\n')
