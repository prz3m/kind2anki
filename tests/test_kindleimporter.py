import csv
from pathlib import Path

import pytest
from freezegun import freeze_time
from sample_vocab import REFERENCE_DATETIME, WORDS, WORDS_ADDED_DAYS_AGO

from kind2anki import kindleimporter
from kind2anki.kindleimporter import KindleImporter

DAYS_COVERING_ALL_WORDS = WORDS_ADDED_DAYS_AGO + 5
DAYS_COVERING_NO_WORDS = WORDS_ADDED_DAYS_AGO - 5


@pytest.fixture(autouse=True)
def freeze():
    with freeze_time(REFERENCE_DATETIME):
        yield


def test_reads_every_recent_word(db_path):
    importer = KindleImporter(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_ALL_WORDS)
    importer.translate_words_from_db()

    assert set(importer.words) == set(WORDS)


def test_skips_words_older_than_the_window(db_path):
    importer = KindleImporter(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_NO_WORDS)
    importer.translate_words_from_db()

    assert importer.words == []


def test_each_word_is_translated_into_the_target_language(db_path, monkeypatch):
    def fake_translate(word, to_lang=None):
        return f"{word}->{to_lang}"

    monkeypatch.setattr(kindleimporter, "translate", fake_translate)

    importer = KindleImporter(db_path, "de", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)
    importer.translate_words_from_db()

    for word, translation in zip(importer.words, importer.translated, strict=False):
        assert translation == f"{word}->de"


def test_failed_translation_is_recorded_as_cannot_translate(db_path, monkeypatch):
    def failing_translate(word, to_lang=None):
        raise RuntimeError("error")

    monkeypatch.setattr(kindleimporter, "translate", failing_translate)

    importer = KindleImporter(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)
    importer.translate_words_from_db()

    assert importer.translated == ["cannot translate"] * len(WORDS)


def test_include_usage_embeds_the_bolded_example_sentence(db_path):
    importer = KindleImporter(
        db_path, "pl", include_usage=True, do_translate=False, import_days=DAYS_COVERING_ALL_WORDS
    )
    importer.translate_words_from_db()

    word = importer.words[0]
    entry = importer.translated[0]
    assert f"<b>{word}</b>" in entry
    assert entry.endswith("<hr>")


def test_fetch_without_translation_keeps_words_but_leaves_them_untranslated(db_path):
    importer = KindleImporter(db_path, "pl", import_days=DAYS_COVERING_ALL_WORDS)
    importer.fetch_words_from_db_without_translation()

    assert set(importer.words) == set(WORDS)
    assert importer.translated == [""] * len(WORDS)


def test_create_temporary_file_writes_word_then_translation_per_line(db_path, monkeypatch):
    monkeypatch.setattr(kindleimporter, "translate", lambda word, to_lang=None: f"translated-{word}")

    importer = KindleImporter(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)
    importer.translate_words_from_db()
    path = importer.create_temporary_file()

    lines = Path(path).read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(WORDS)
    first_word = importer.words[0]
    assert lines[0] == f"{first_word};translated-{first_word}"


def test_create_temporary_file_returns_none_when_there_is_nothing_to_import(db_path):
    importer = KindleImporter(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_NO_WORDS)
    importer.translate_words_from_db()

    assert importer.create_temporary_file() is None


def test_create_temporary_file_quotes_translation_containing_the_delimiter(db_path, monkeypatch):
    monkeypatch.setattr(kindleimporter, "translate", lambda word, to_lang=None: "a;b")

    importer = KindleImporter(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)
    importer.translate_words_from_db()
    path = importer.create_temporary_file()

    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert rows, "expected at least one row"
    assert all(row[1] == "a;b" for row in rows)
