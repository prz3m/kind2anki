import pytest
from anki.collection import ImportCsvRequest
from anki.decks import DeckId

from kind2anki import csv_importer

NOTE_TYPE_ID = 37
DECK_ID = DeckId(21)


class FakeModels:
    def __init__(self, notetype):
        self.notetype = notetype

    def by_name(self, _name):
        return self.notetype


class FakeCollection:
    def __init__(self, notetype):
        self.models = FakeModels(notetype)
        self.request: ImportCsvRequest | None = None

    def import_csv(self, request):
        self.request = request
        return "response"


def make_note_type(field_count):
    return {"id": NOTE_TYPE_ID, "flds": [{} for _ in range(field_count)]}


def test_maps_csv_columns_by_field_position():
    collection = FakeCollection(make_note_type(3))

    csv_importer.import_csv(collection, "/tmp/words.csv", DECK_ID, csv_importer.CsvMetadata.DupeResolution.PRESERVE)

    assert collection.request is not None
    assert collection.request.path == "/tmp/words.csv"
    metadata = collection.request.metadata
    assert metadata.deck_id == DECK_ID
    assert metadata.global_notetype.id == NOTE_TYPE_ID
    assert metadata.global_notetype.field_columns == [1, 2, 0]


def test_rejects_missing_basic_note_type():
    with pytest.raises(csv_importer.CsvImportError, match="was not found"):
        csv_importer.import_csv(
            FakeCollection(None),
            "/tmp/words.csv",
            DECK_ID,
            csv_importer.CsvMetadata.DupeResolution.PRESERVE,
        )


def test_rejects_basic_note_type_with_fewer_than_two_fields():
    with pytest.raises(csv_importer.CsvImportError, match="at least two fields"):
        csv_importer.import_csv(
            FakeCollection(make_note_type(1)),
            "/tmp/words.csv",
            DECK_ID,
            csv_importer.CsvMetadata.DupeResolution.PRESERVE,
        )
