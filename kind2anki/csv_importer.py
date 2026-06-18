from collections import Counter
from heapq import nlargest

from anki.collection import Collection, CsvMetadata, ImportCsvRequest, ImportLogWithChanges
from anki.decks import DeckId
from anki.models import NotetypeDict, NotetypeId

DupeResolutionValue = CsvMetadata.DupeResolution.ValueType


class CsvImportError(Exception):
    pass


def import_csv(
    collection: Collection, path: str, deck_id: DeckId, dupe_resolution: DupeResolutionValue
) -> ImportLogWithChanges:
    notetype = _select_notetype(collection, deck_id)
    request = ImportCsvRequest(path=path, metadata=_create_metadata(notetype, deck_id, dupe_resolution))
    return collection.import_csv(request)


def _create_metadata(notetype: NotetypeDict, deck_id: DeckId, dupe_resolution: DupeResolutionValue) -> CsvMetadata:
    field_count = len(notetype["flds"])
    if field_count < 2:
        raise CsvImportError(f'The note type "{notetype["name"]}" must have at least two fields.')

    return CsvMetadata(
        delimiter=CsvMetadata.Delimiter.SEMICOLON,
        force_delimiter=True,
        is_html=True,
        force_is_html=True,
        deck_id=deck_id,
        global_notetype=CsvMetadata.MappedNotetype(id=notetype["id"], field_columns=[1, 2] + [0] * (field_count - 2)),
        dupe_resolution=dupe_resolution,
    )


def _select_notetype(collection: Collection, deck_id: DeckId) -> NotetypeDict:
    recent_card_ids = nlargest(10, collection.decks.cids(deck_id, children=False))
    if recent_card_ids:
        recent_notetypes = [collection.get_card(card_id).note_type() for card_id in recent_card_ids]
        notetype_counts = Counter(notetype["id"] for notetype in recent_notetypes)
        notetype_id = NotetypeId(notetype_counts.most_common(1)[0][0])
        return next(notetype for notetype in recent_notetypes if notetype["id"] == notetype_id)

    defaults = collection.defaults_for_adding(current_review_card=None)
    return next(notetype for notetype in collection.models.all() if notetype["id"] == defaults.notetype_id)


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
