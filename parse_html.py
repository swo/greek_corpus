#!/usr/bin/env python3
#
# This script parses pages downloaded from TenTen and uses them to populate
# the database.

import glob, re, functools
from bs4 import BeautifulSoup
from tinydb import TinyDB, Query

class Word:
    def __init__(self, word, frequency):
        self.word = word
        self.frequency = frequency

    def __eq__(self, other):
        return (self.word, self.frequency) == (other.word, other.frequency)

    def __lt__(self, other):
        return self.frequency < other.frequency or (self.frequency == other.frequency and self.word < other.word)

    def __repr__(self):
        return self.word


class Page:
    def __init__(self, content):
        self.content = content
        self.words = self.page_words(self.content)

        self.min_word_frequency = min([word.frequency for word in self.words])
        template = 'https://old.sketchengine.co.uk/corpus/wordlist?corpname=preloaded/eltenten14_tt2;usesubcorp=;wlattr=lemma;wlminfreq=1000;wlmaxfreq={};wlpat=.%2A;wlmaxitems=100;wlsort=f;ref_corpname=;ref_usesubcorp=;wlcache=;simple_n=1.0;wltype=simple;wlnums=frq;include_nonwords=0;blcache=;wlpage=1;usengrams=0;ngrams_n=2;ngrams_max_n=2;nest_ngrams=0;complement_subc=0'
        self.next_page_query = template.format(self.min_word_frequency)

    def __eq__(self, other):
        return all([w1 == w2 for w1, w2 in zip(self.words, other.words)])

    def __gt__(self, other):
        return self.min_word_frequency > other.min_word_frequency

    @classmethod
    def page_words(cls, content):
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', class_ = 'result numtab')

        return cls.table_words(table)

    @classmethod
    def table_words(cls, table):
        rows = table.find_all('tr')

        # check that first row in the table is the header
        assert [cell.text.strip() for cell in rows[0].find_all('th')] == ['lemma', 'frequency']

        # get words from everything except the first row
        return [cls.row_words(row) for row in rows[1:]]

    @classmethod
    def row_words(cls, row):
        cells = row.find_all('td')
        text_word = cells[0].text.strip()
        freq = int(re.sub(',', '', cells[1].text))
        return Word(text_word, freq)


def run_on_file(fn, func):
    with open(fn) as f:
        content = f.read()

    return(func(content))

if __name__ == '__main__':
    fns = glob.glob('raw/*.html')
    pages = sorted([run_on_file(fn, Page) for fn in fns], reverse=True)
    words = sorted([word for page in pages for word in page.words], reverse=True)

    db = TinyDB('db.json')
    Entry = Query()

    for word in words:
        existing_entries = db.search(Entry.word == word.word)
        if len(existing_entries) == 0:
            # insert this word
            db.insert({'word': word.word, 'frequency': word.frequency})

    with open('words.txt', 'w') as f:
        for x in words:
            print(x, file=f)

    print('List of words saved to file')
    print('Query for more words:', pages[-1].next_page_query)
