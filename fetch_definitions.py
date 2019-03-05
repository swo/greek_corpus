#!/usr/bin/env python3
#
# This script searches for definitions for those words already in the
# database.

import wiktionaryparser, multiprocessing, sqlite3, json

# for fetching wiktionary pages
parser = wiktionaryparser.WiktionaryParser()

def fetch_entry(word):
    try:
        result = parser.fetch(word, 'greek')
    except Exception:
        result = None

    return result

def add_entry(word, connection):
    wiki = fetch_entry(word)
    wiki_str = json.dumps(wiki)

    print(word, wiki)

    cursor = connection.cursor()
    cursor.execute('''update lemmas set wiki = ? where word = ?''', (wiki_str, word))

    connection.commit()

    return (word, wiki)


if __name__ == '__main__':
    connection = sqlite3.connect('greek_db')
    cursor = connection.cursor()

    known_words = [x[0] for x in cursor.execute('''select word from lemmas where wiki is not null''')]
    words_to_fetch = [x[0] for x in cursor.execute('''select word from lemmas where wiki is null''')]

    print("There are {} words with wiki entries and {} left to fetch".format(len(known_words), len(words_to_fetch)))

    def f(x):
        add_entry(x, connection)

    with multiprocessing.Pool(5) as pool:
        pool.map(f, words_to_fetch)

    connection.commit()
    connection.close()
