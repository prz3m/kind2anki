# coding=utf-8
"""Puts the words gathered by kind2anki into the collection.

Anki removed ``anki.importing.TextImporter`` in 26.09 (upstream commit
d4fdbef); the supported replacement is ``Collection.import_csv()``, which is
handed the whole import configuration as a protobuf message instead of being
configured attribute by attribute. Builds predating that method keep using the
old importer.
"""

# the temporary file holds the word in the first column and its translation
# (optionally preceded by usage examples) in the second one
COLUMN_COUNT = 2

DELIMITER = ";"


def importIntoCollection(col, path, deckId, importMode):
    """Import the temporary file into deckId, returning a list of log lines.

    importMode is an index into the dialog's duplicate handling combo box.
    """
    if hasattr(col, "import_csv"):
        return _importWithBackend(col, path, deckId, importMode)
    return _importWithLegacyImporter(col, path, deckId, importMode)


def _importWithBackend(col, path, deckId, importMode):
    from anki.collection import CsvMetadata, DupeResolution, ImportCsvRequest

    # the combo box lists the modes in this order
    dupeResolutions = (
        DupeResolution.UPDATE,
        DupeResolution.PRESERVE,
        DupeResolution.DUPLICATE,
    )

    col.decks.select(deckId)
    notetype = col.models.current()

    # let the backend work out the shape of the file, then pin down everything
    # kind2anki has an opinion about
    metadata = col.get_csv_metadata(path, CsvMetadata.Delimiter.SEMICOLON)
    metadata.force_delimiter = True
    metadata.is_html = True
    metadata.force_is_html = True
    metadata.deck_id = deckId
    metadata.dupe_resolution = dupeResolutions[importMode]
    metadata.global_notetype.id = notetype["id"]
    del metadata.global_notetype.field_columns[:]
    metadata.global_notetype.field_columns.extend(
        # our two columns fill the first two fields; 0 leaves a field unmapped
        i + 1 if i < COLUMN_COUNT else 0
        for i in range(len(col.models.field_names(notetype)))
    )

    response = col.import_csv(ImportCsvRequest(path=path, metadata=metadata))
    return summarizeLog(response.log)


def _importWithLegacyImporter(col, path, deckId, importMode):
    from anki.importing import TextImporter

    importer = TextImporter(col, path)
    importer.initMapping()
    importer.allowHTML = True
    importer.importMode = importMode
    importer.delimiter = DELIMITER

    if deckId != importer.model["did"]:
        importer.model["did"] = deckId
        col.models.save(importer.model)
    col.decks.select(deckId)

    importer.run()
    return list(importer.log)


def summarizeLog(log):
    from anki.collection import DupeResolution

    added = len(log.new)
    updated = len(log.updated)
    skipped = 0

    # notes whose first field matched an existing note are reported apart from
    # the rest; what actually happened to them depends on the chosen mode
    matched = len(log.first_field_match)
    if log.dupe_resolution == DupeResolution.UPDATE:
        updated += matched
    elif log.dupe_resolution == DupeResolution.DUPLICATE:
        added += matched
    else:
        skipped = matched

    counts = (
        (added, "note(s) added"),
        (updated, "note(s) updated"),
        (skipped, "note(s) skipped (first field matched an existing note)"),
        (len(log.duplicate), "note(s) left alone (identical to an existing note)"),
        (len(log.conflicting), "note(s) skipped (conflicting notetype)"),
        (len(log.empty_first_field), "note(s) skipped (empty first field)"),
    )
    return ["{0} {1}".format(count, label) for count, label in counts if count]
