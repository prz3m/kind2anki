import os
import sqlite3
import urllib
from typing import cast

from anki.importing import TextImporter
from aqt import mw
from aqt.deckchooser import DeckChooser
from aqt.qt import QDialog, QDialogButtonBox, QPushButton, QThread, pyqtSignal, qtmajor
from aqt.utils import getFile, showInfo, showText

from . import config_manager, last_run

if qtmajor == 5:
    from . import kind2anki_ui
else:
    from . import kind2anki_ui_qt6 as kind2anki_ui

from . import kindleimporter
from .kindleimporter import KindleImporter


class ThreadTranslate(QThread):
    start_progress = pyqtSignal(object, object)
    done = pyqtSignal(object, object)

    def __init__(self, args=None):
        QThread.__init__(self)
        self.args = args
        self.dialog = None

    def __del__(self):
        self.wait()

    def run(self):
        self.start_progress.emit(self.dialog, "start")
        kindle_importer = KindleImporter(*self.args)
        kindle_importer.translate_words_from_db()
        temp_file_path = kindle_importer.create_temporary_file()
        self.done.emit(self.dialog, temp_file_path)


def import_to_anki(dialog, temp_file_path):
    mw.progress.finish()
    if temp_file_path is not None:
        mw.progress.start(immediate=True, label="Importing...")
        dialog.setup_importer(temp_file_path)
        dialog.select_deck()

        dialog.importer.run()
        mw.progress.finish()

        txt = "Importing complete.\n"
        if dialog.importer.log:
            txt += "\n".join(dialog.importer.log)

        os.remove(temp_file_path)
    else:
        txt = "Nothing to import!"
    showText(txt)


def start_progress_bar(dialog, nth):
    mw.progress.start(immediate=True, label="Processing...")


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        self.t = ThreadTranslate()
        self.t.done.connect(import_to_anki)
        self.t.start_progress.connect(start_progress_bar)

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
            last_run.save_days_since_last_run()  # update lastRun timestamp

            target_language = self.frm.language_select.currentText()
            include_usage = self.frm.include_usage.isChecked()
            do_translate = self.frm.do_translate.isChecked()
            import_days = self.frm.import_days.value()

            self.t.dialog = self
            self.t.args = (db_path, target_language, include_usage, do_translate, import_days)

            self.t.start()

        except urllib.error.URLError:
            showInfo("Cannot connect")
        except OSError:
            showInfo("DB file not selected, exiting")
        except sqlite3.DatabaseError:
            showInfo("Selected file is not a DB")
        finally:
            self.close()
            self.mw.reset()

    def setup_importer(self, temp_file_path):
        self.importer = TextImporter(self.mw.col, str(temp_file_path))
        self.importer.initMapping()
        self.importer.allowHTML = True
        self.importer.importMode = self.frm.import_mode.currentIndex()
        config_manager.set_import_mode(self.importer.importMode)
        self.importer.delimiter = ";"

    def select_deck(self):
        did = self.deck.selectedId()
        if did != self.importer.model["did"]:
            self.importer.model["did"] = did
            self.mw.col.models.save(self.importer.model)
        self.mw.col.decks.select(did)


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
