from typing import Any

from anki.collection import CsvMetadata, ImportCsvRequest, ImportLogWithChanges
from anki.decks import DeckId

DupeResolutionValue = CsvMetadata.DupeResolution.ValueType


class CsvImportError(Exception):
    pass


def import_csv(
    collection: Any, path: str, deck_id: DeckId, dupe_resolution: DupeResolutionValue
) -> ImportLogWithChanges:
    request = ImportCsvRequest(path=path, metadata=_create_metadata(collection, deck_id, dupe_resolution))
    return collection.import_csv(request)


def _create_metadata(collection: Any, deck_id: DeckId, dupe_resolution: DupeResolutionValue) -> CsvMetadata:
    notetype = collection.models.by_name("Basic")
    if notetype is None:
        raise CsvImportError("The Basic note type was not found. Restore it in Tools → Manage Note Types.")

    field_count = len(notetype["flds"])
    if field_count < 2:
        raise CsvImportError("The Basic note type must have at least two fields.")

    return CsvMetadata(
        delimiter=CsvMetadata.Delimiter.SEMICOLON,
        force_delimiter=True,
        is_html=True,
        force_is_html=True,
        deck_id=deck_id,
        global_notetype=CsvMetadata.MappedNotetype(id=notetype["id"], field_columns=[1, 2] + [0] * (field_count - 2)),
        dupe_resolution=dupe_resolution,
    )


def format_import_log(response: ImportLogWithChanges) -> str:
    summary = response.log

    added = len(summary.new)
    updated = 0
    skipped = 0
    matched = len(summary.first_field_match)

    if summary.dupe_resolution == CsvMetadata.DupeResolution.UPDATE:
        updated += matched
    elif summary.dupe_resolution == CsvMetadata.DupeResolution.DUPLICATE:
        added += matched
    else:
        skipped += matched

    return "\n".join(
        [
            "Importing complete.",
            f"Notes added: {added}",
            f"Notes updated: {updated}",
            f"Notes skipped: {skipped}",
            f"Identical duplicates: {len(summary.duplicate)}",
        ]
    )
