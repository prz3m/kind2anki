import csv
from pathlib import Path

import pytest
from freezegun import freeze_time
from sample_vocab import REFERENCE_DATETIME, WORDS, WORDS_ADDED_DAYS_AGO

from kind2anki import kindle_importer

DAYS_COVERING_ALL_WORDS = WORDS_ADDED_DAYS_AGO + 5
DAYS_COVERING_NO_WORDS = WORDS_ADDED_DAYS_AGO - 5


@pytest.fixture(autouse=True)
def freeze():
    with freeze_time(REFERENCE_DATETIME):
        yield


def test_reads_every_recent_word(db_path):
    entries = kindle_importer.translate_words(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_ALL_WORDS)

    assert {entry.word for entry in entries} == set(WORDS)


def test_skips_words_older_than_the_window(db_path):
    entries = kindle_importer.translate_words(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_NO_WORDS)

    assert len(entries) == 0


def test_each_word_is_translated_into_the_target_language(db_path, monkeypatch):
    def fake_translate(word, to_lang=None):
        return f"{word} in {to_lang}"

    monkeypatch.setattr(kindle_importer, "translate", fake_translate)

    entries = kindle_importer.translate_words(db_path, "de", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)

    for entry in entries:
        assert entry.translation == f"{entry.word} in de"


def test_failed_translation_is_recorded_as_cannot_translate(db_path, monkeypatch):
    def failing_translate(word, to_lang=None):
        raise RuntimeError("error")

    monkeypatch.setattr(kindle_importer, "translate", failing_translate)

    entries = kindle_importer.translate_words(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)

    assert [entry.translation for entry in entries] == ["cannot translate"] * len(WORDS)


def test_include_usage_embeds_the_bolded_example_sentence(db_path):
    entries = kindle_importer.translate_words(
        db_path, "pl", include_usage=True, do_translate=False, import_days=DAYS_COVERING_ALL_WORDS
    )

    first = entries[0]
    assert f"<b>{first.word}</b>" in first.translation
    assert first.translation.endswith("<hr>")


def test_create_import_file_writes_word_then_translation_per_line(db_path, monkeypatch):
    monkeypatch.setattr(kindle_importer, "translate", lambda word, to_lang=None: f"translated-{word}")

    path = kindle_importer.create_import_file(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)

    assert path is not None
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(WORDS)
    first_word, translation = lines[0].split(";")
    assert first_word in WORDS
    assert translation == f"translated-{first_word}"


def test_create_import_file_returns_none_when_there_is_nothing_to_import(db_path):
    assert (
        kindle_importer.create_import_file(db_path, "pl", do_translate=False, import_days=DAYS_COVERING_NO_WORDS)
        is None
    )


def test_create_import_file_quotes_translation_containing_the_delimiter(db_path, monkeypatch):
    monkeypatch.setattr(kindle_importer, "translate", lambda word, to_lang=None: "a;b")

    path = kindle_importer.create_import_file(db_path, "pl", do_translate=True, import_days=DAYS_COVERING_ALL_WORDS)

    assert path is not None
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f, delimiter=";"))

    assert rows, "expected at least one row"
    assert all(row[1] == "a;b" for row in rows)
