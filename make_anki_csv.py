#!/usr/bin/env python3
#
# This script turns the database into an Anki csv.

import re
from tinydb import TinyDB, Query

def ankiize(item):
    assert 'word' in item.keys() and 'definition' in item.keys()
    new_definition = re.sub('\n', '<br/>', item['definition'])

    return item['word'] + '\t' + new_definition


if __name__ == '__main__':
    db = TinyDB('db.json')
    query = Query()

    lines = [ankiize(record) for record in db.search(query.definition.exists())]

    with open('anki.tsv', 'w') as f:
        for line in lines:
            print(line, file=f)
