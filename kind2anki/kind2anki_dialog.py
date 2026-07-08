import os
import sqlite3
import urllib
from typing import cast

from anki.importing import TextImporter
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


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        b = QPushButton("Import")
        cast(QDialogButtonBox, self.frm.button_box).addButton(b, QDialogButtonBox.ButtonRole.AcceptRole)
        self.deck = DeckChooser(self.mw, self.frm.deck_area, label=False)
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

        last_run.save_days_since_last_run()  # update lastRun timestamp

        target_language = self.frm.language_select.currentText()
        include_usage = self.frm.include_usage.isChecked()
        do_translate = self.frm.do_translate.isChecked()
        import_days = self.frm.import_days.value()
        import_mode = self.frm.import_mode.currentIndex()
        config_manager.set_import_mode(import_mode)
        deck_id = self.deck.selectedId()

        self.close()

        self.mw.progress.start(immediate=True, label="Processing...")
        self.mw.taskman.run_in_background(
            lambda: translate_words(db_path, target_language, include_usage, do_translate, import_days),
            lambda fut: on_translated(fut, deck_id, import_mode),
        )


def translate_words(db_path, target_language, include_usage, do_translate, import_days):
    kindle_importer = KindleImporter(db_path, target_language, include_usage, do_translate, import_days)
    kindle_importer.translate_words_from_db()
    return kindle_importer.create_temporary_file()


def on_translated(fut, deck_id, import_mode):
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
            import_to_anki(temp_file_path, deck_id, import_mode)
    mw.reset()


def import_to_anki(temp_file_path, deck_id, import_mode):
    mw.progress.start(immediate=True, label="Importing...")
    importer = build_importer(temp_file_path, deck_id, import_mode)
    importer.run()
    mw.progress.finish()

    txt = "Importing complete.\n"
    if importer.log:
        txt += "\n".join(importer.log)

    os.remove(temp_file_path)
    showText(txt)


def build_importer(temp_file_path, deck_id, import_mode):
    importer = TextImporter(mw.col, str(temp_file_path))
    importer.initMapping()
    importer.allowHTML = True
    importer.importMode = import_mode
    importer.delimiter = ";"

    if deck_id != importer.model["did"]:
        importer.model["did"] = deck_id
        mw.col.models.save(importer.model)
    mw.col.decks.select(deck_id)
    return importer


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
