import os
import sqlite3
import urllib.error
from concurrent.futures import Future
from typing import cast

from anki.collection import CsvMetadata
from anki.decks import DeckId
from aqt import mw
from aqt.deckchooser import DeckChooser
from aqt.qt import QDialog, QDialogButtonBox, QPushButton, qtmajor
from aqt.utils import getFile, showInfo, showText

from . import config_manager, csv_importer, kindleimporter, last_run
from .kindleimporter import KindleImporter

if qtmajor == 5:
    from . import kind2anki_ui
else:
    from . import kind2anki_ui_qt6 as kind2anki_ui


DupeResolutionValue = CsvMetadata.DupeResolution.ValueType

DUPE_RESOLUTION_BY_INDEX = (
    CsvMetadata.DupeResolution.UPDATE,
    CsvMetadata.DupeResolution.PRESERVE,
    CsvMetadata.DupeResolution.DUPLICATE,
)


class Kind2AnkiDialog(QDialog):
    def __init__(self) -> None:
        QDialog.__init__(self)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        b = QPushButton("Import")
        cast(QDialogButtonBox, self.frm.button_box).addButton(b, QDialogButtonBox.ButtonRole.AcceptRole)
        self.deck = DeckChooser(self.mw, self.frm.deck_area, label=False)

        assert self.mw.col is not None
        tr = self.mw.col.tr
        self.frm.import_mode.setItemText(0, tr.importing_update_existing_notes_when_first_field())
        self.frm.import_mode.setItemText(1, tr.importing_ignore_lines_where_first_field_matches())
        self.frm.import_mode.setItemText(2, tr.importing_import_even_if_existing_note_has())
        self.frm.import_mode.setCurrentIndex(config_manager.get_import_mode())

        self.days_since_last_run = last_run.get_days_since_last_run()
        self.frm.import_days.setValue(self.days_since_last_run)

    def accept(self) -> None:
        db_path = get_db_path()
        if db_path is None:
            self.reject()
            return

        target_language = self.frm.language_select.currentText()
        include_usage = self.frm.include_usage.isChecked()
        do_translate = self.frm.do_translate.isChecked()
        import_days = self.frm.import_days.value()
        import_mode = self.frm.import_mode.currentIndex()
        config_manager.set_import_mode(import_mode)
        dupe_resolution = DUPE_RESOLUTION_BY_INDEX[import_mode]
        deck_id = self.deck.selectedId()

        super().accept()

        self.mw.progress.start(immediate=True, label="Processing...")
        self.mw.taskman.run_in_background(
            lambda: translate_words(db_path, target_language, include_usage, do_translate, import_days),
            lambda fut: on_translated(fut, deck_id, dupe_resolution),
        )


def translate_words(
    db_path: str, target_language: str, include_usage: bool, do_translate: bool, import_days: int
) -> str | None:
    kindle_importer = KindleImporter(db_path, target_language, include_usage, do_translate, import_days)
    kindle_importer.translate_words_from_db()
    return kindle_importer.create_temporary_file()


def on_translated(fut: Future[str | None], deck_id: DeckId, dupe_resolution: DupeResolutionValue) -> None:
    mw.progress.finish()
    try:
        temp_file_path = fut.result()
        if temp_file_path is None:
            showText("Nothing to import!")
        else:
            import_to_anki(temp_file_path, deck_id, dupe_resolution)
    except urllib.error.URLError:
        showInfo("Cannot connect")
    except sqlite3.DatabaseError:
        showInfo("Selected file is not a DB")
    except csv_importer.CsvImportError as error:
        showInfo(str(error))
    else:
        last_run.save_days_since_last_run()
    finally:
        mw.reset()


def import_to_anki(temp_file_path: str, deck_id: DeckId, dupe_resolution: DupeResolutionValue) -> None:
    assert mw.col is not None
    mw.progress.start(immediate=True, label="Importing...")
    try:
        response = csv_importer.import_csv(mw.col, temp_file_path, deck_id, dupe_resolution)
    finally:
        mw.progress.finish()
        os.remove(temp_file_path)

    showText(csv_importer.format_import_log(response))


def get_db_path() -> str | None:
    vocab_path = kindleimporter.get_kindle_vocab_path()
    if vocab_path == "":
        key = "Import"
        dir = None
    else:
        key = None
        dir = vocab_path
    db_path = getFile(mw, "Select db file", None, dir=dir, key=key, filter="*.db")
    return str(db_path) if db_path else None
