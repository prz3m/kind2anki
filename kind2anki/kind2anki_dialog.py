import os
import sqlite3
import urllib
from typing import cast

from anki.collection import CsvMetadata, ImportCsvRequest
from aqt import mw
from aqt.deckchooser import DeckChooser
from aqt.qt import QDialog, QDialogButtonBox, QPushButton, qtmajor
from aqt.utils import getFile, showInfo, showText

from . import config_manager, last_run

if qtmajor == 5:
    from . import kind2anki_ui
else:
    from . import kind2anki_ui_qt6 as kind2anki_ui

from . import kindleimporter
from .kindleimporter import KindleImporter

DUPE_RESOLUTION_BY_INDEX = (
    CsvMetadata.DupeResolution.UPDATE,
    CsvMetadata.DupeResolution.PRESERVE,
    CsvMetadata.DupeResolution.DUPLICATE,
)


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        b = QPushButton("Import")
        cast(QDialogButtonBox, self.frm.button_box).addButton(b, QDialogButtonBox.ButtonRole.AcceptRole)
        self.deck = DeckChooser(self.mw, self.frm.deck_area, label=False)

        tr = self.mw.col.tr
        self.frm.import_mode.setItemText(0, tr.importing_update_existing_notes_when_first_field())
        self.frm.import_mode.setItemText(1, tr.importing_ignore_lines_where_first_field_matches())
        self.frm.import_mode.setItemText(2, tr.importing_import_even_if_existing_note_has())
        self.frm.import_mode.setCurrentIndex(config_manager.get_import_mode())

        self.days_since_last_run = last_run.get_days_since_last_run()
        self.frm.import_days.setValue(self.days_since_last_run)

        self.exec()

    def accept(self):
        try:
            db_path = get_db_path()
        except OSError:
            showInfo("DB file not selected, exiting")
            self.close()
            return

        target_language = self.frm.language_select.currentText()
        include_usage = self.frm.include_usage.isChecked()
        do_translate = self.frm.do_translate.isChecked()
        import_days = self.frm.import_days.value()
        import_mode = self.frm.import_mode.currentIndex()
        config_manager.set_import_mode(import_mode)
        dupe_resolution = DUPE_RESOLUTION_BY_INDEX[import_mode]
        deck_id = self.deck.selectedId()

        self.close()

        self.mw.progress.start(immediate=True, label="Processing...")
        self.mw.taskman.run_in_background(
            lambda: translate_words(db_path, target_language, include_usage, do_translate, import_days),
            lambda fut: on_translated(fut, deck_id, dupe_resolution),
        )


def translate_words(db_path, target_language, include_usage, do_translate, import_days):
    kindle_importer = KindleImporter(db_path, target_language, include_usage, do_translate, import_days)
    kindle_importer.translate_words_from_db()
    return kindle_importer.create_temporary_file()


def on_translated(fut, deck_id, dupe_resolution):
    mw.progress.finish()
    try:
        temp_file_path = fut.result()
    except urllib.error.URLError:
        showInfo("Cannot connect")
    except sqlite3.DatabaseError:
        showInfo("Selected file is not a DB")
    else:
        if temp_file_path is None:
            showText("Nothing to import!")
        else:
            import_to_anki(temp_file_path, deck_id, dupe_resolution)
        last_run.save_days_since_last_run()
    mw.reset()


def import_to_anki(temp_file_path, deck_id, dupe_resolution):
    mw.progress.start(immediate=True, label="Importing...")
    request = ImportCsvRequest(path=temp_file_path, metadata=build_csv_metadata(deck_id, dupe_resolution))
    response = mw.col.import_csv(request)
    mw.progress.finish()

    os.remove(temp_file_path)
    showText(format_import_log(response))


def build_csv_metadata(deck_id, dupe_resolution):
    notetype = mw.col.models.current()
    field_count = len(notetype["flds"])
    # Which CSV column fills each note-type field (1-based; 0 = leave empty).
    # Field 1 <- word, field 2 <- translation; any further fields stay empty.
    field_columns = [1, 2] + [0] * (field_count - 2)

    return CsvMetadata(
        delimiter=CsvMetadata.Delimiter.SEMICOLON,
        force_delimiter=True,
        is_html=True,
        force_is_html=True,
        deck_id=deck_id,
        global_notetype=CsvMetadata.MappedNotetype(id=notetype["id"], field_columns=field_columns),
        dupe_resolution=dupe_resolution,
    )


def format_import_log(response):
    summary = response.log
    return "\n".join(
        [
            "Importing complete.",
            f"Notes added: {len(summary.new)}",
            f"Notes updated: {len(summary.updated)}",
            f"Duplicates: {len(summary.duplicate)}",
        ]
    )


def get_db_path():
    vocab_path = kindleimporter.get_kindle_vocab_path()
    if vocab_path == "":
        key = "Import"
        dir = None
    else:
        key = None
        dir = vocab_path
    db_path = getFile(mw, "Select db file", None, dir=dir, key=key, filter="*.db")
    if not db_path:
        raise OSError
    db_path = str(db_path)
    return db_path
