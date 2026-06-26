# The SQL schema below mirrors Kindle's real vocab.db DDL verbatim; the
# CREATE TABLE statements can't be wrapped without distorting the fixture.
# ruff: noqa: E501
import datetime
import os
import sqlite3
import sys

LANG = "en-US"

REFERENCE_DATETIME = datetime.datetime(2024, 2, 1, 12, 0, 0)
WORDS_ADDED_DAYS_AGO = 17

BOOKS = [
    ("BOOK1", "Book One", "Author One"),
    ("BOOK2", "Book Two", "Author Two"),
    ("BOOK3", "Book Three", "Author Three"),
]

DICT = ("EN-DICT", "en", "en")

WORDS = [
    "apple",
    "house",
    "river",
    "music",
    "garden",
    "window",
    "coffee",
    "mountain",
    "pencil",
    "bridge",
    "summer",
    "yellow",
    "table",
    "forest",
    "candle",
    "orange",
    "silver",
    "pocket",
    "ocean",
    "ladder",
    "button",
    "cloud",
    "kitten",
    "honey",
]
WORD_COUNT = len(WORDS)

SCHEMA = """
CREATE TABLE WORDS (id TEXT PRIMARY KEY NOT NULL, word TEXT, stem TEXT, lang TEXT, category INTEGER DEFAULT 0, timestamp INTEGER DEFAULT 0, profileid TEXT);
CREATE TABLE LOOKUPS (id TEXT PRIMARY KEY NOT NULL, word_key TEXT, book_key TEXT, dict_key TEXT, pos TEXT, usage TEXT, timestamp INTEGER DEFAULT 0);
CREATE TABLE BOOK_INFO (id TEXT PRIMARY KEY NOT NULL, asin TEXT, guid TEXT, lang TEXT, title TEXT, authors TEXT);
CREATE TABLE DICT_INFO (id TEXT PRIMARY KEY NOT NULL, asin TEXT, langin TEXT, langout TEXT);
CREATE TABLE METADATA (id TEXT PRIMARY KEY NOT NULL, dsname TEXT, sscnt INTEGER, profileid TEXT);
CREATE TABLE VERSION (id TEXT PRIMARY KEY NOT NULL, dsname TEXT, value INTEGER);
CREATE INDEX lookupbookkey ON LOOKUPS (book_key);
CREATE INDEX lookupwordkey ON LOOKUPS (word_key);
CREATE INDEX wordprofileid ON WORDS (profileid);
"""


def _ms(dt):
    """Kindle stores timestamps as epoch milliseconds."""
    return int(dt.timestamp() * 1000)


def build(db_path):
    """(Re)create the fixture database at ``db_path``.

    All words are timestamped WORDS_ADDED_DAYS_AGO before REFERENCE_DATETIME (a
    minute apart, so their ids stay distinct).
    """
    if os.path.exists(db_path):
        os.remove(db_path)

    base = REFERENCE_DATETIME - datetime.timedelta(days=WORDS_ADDED_DAYS_AGO)
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.executescript(SCHEMA)

        for book_id, title, authors in BOOKS:
            c.execute(
                "INSERT INTO BOOK_INFO (id, asin, guid, lang, title, authors) VALUES (?, ?, ?, ?, ?, ?)",
                (book_id, book_id, book_id, LANG, title, authors),
            )

        dict_id, langin, langout = DICT
        c.execute(
            "INSERT INTO DICT_INFO (id, asin, langin, langout) VALUES (?, ?, ?, ?)",
            (dict_id, dict_id, langin, langout),
        )

        for i, word in enumerate(WORDS):
            word_id = f"{LANG}:{word}"
            ts = _ms(base + datetime.timedelta(minutes=i))
            c.execute(
                "INSERT INTO WORDS (id, word, stem, lang, category, timestamp, profileid) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (word_id, word, word, LANG, 0, ts, ""),
            )

            book_id = BOOKS[i % len(BOOKS)][0]
            # Usage contains the word so the "include usage" path has something
            # to bold; the semicolon exercises the ';' -> ',' sanitising.
            usage = f'The author chose the word "{word}" with care; a {word} sentence reads more clearly.'
            c.execute(
                "INSERT INTO LOOKUPS (id, word_key, book_key, dict_key, pos, "
                "usage, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    f"{book_id}:{word_id}:{i}",
                    word_id,
                    book_id,
                    dict_id,
                    "0",
                    usage,
                    ts + 50,
                ),
            )

        for ds in ("WORDS", "LOOKUPS"):
            c.execute("INSERT INTO VERSION (id, dsname, value) VALUES (?, ?, ?)", (ds, ds, 1))

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    out = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(os.path.dirname(os.path.realpath(__file__)), "sample_vocab.db")
    )
    build(out)
    print(f"wrote {out} with {WORD_COUNT} words")
