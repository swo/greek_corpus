# Most common Greek words

I pulled lists of the most common Greek words appearing in a corpus of web
pages from [SketchEngine](https://www.sketchengine.eu/). Then I used
[WiktionaryParser](https://github.com/Suyash458/WiktionaryParser) to pull
definitions from [Wiktionary](https://www.wiktionary.org/). I packaged the
results as a tsv that can be uploaded to [Anki](https://apps.ankiweb.net/), a
flashcard app.

## Files

### Data files

- `anki.tsv` is the Anki flashcard list
- `db.json` is a database with the words, their frequencies, and their definitions
- `words.txt` is just a list of the words included in the lists
- `raw/` contains un-tracked files downloaded from SketchEngine that are parsed

### Script files

- `parse_html.py` turns the html files in `raw/` into database entries
- `fetch_definitions.py` populates the database with Wiktionary definitions
- `make_anki_tsv.py` translates the database into the Anki-ready file

## Alternative data sources

I considered but did not ultimately pursue scraping a Greek-English dictionary
website (e.g., [dict.com](www.dict.com) or [Word Reference](wordreference.com))
in part because of the difficulty in reliably parsing the pages and also
because of licensing concerns.
