# coding=utf-8
from typing import cast

from aqt.deckchooser import DeckChooser
from aqt import mw
from aqt.utils import showInfo, getFile, showText
from anki.importing import TextImporter
from aqt.qt import QThread, pyqtSignal, qtmajor, QDialogButtonBox, QPushButton, \
    QDialog

import os
import sqlite3
import urllib

# addon's ui (generated)
if qtmajor == 5:
    from . import kind2anki_ui
else:
    from . import kind2anki_ui_qt6 as kind2anki_ui

from . import kindleimporter
from .kindleimporter import KindleImporter


class ThreadTranslate(QThread):
    startProgress = pyqtSignal(object, object)
    done = pyqtSignal(object, object)

    def __init__(self, args=None):
        QThread.__init__(self)
        self.args = args
        self.dialog = None

    def __del__(self):
        self.wait()

    def run(self):
        self.startProgress.emit(self.dialog, "start")
        kindleImporter = KindleImporter(*self.args)
        kindleImporter.translateWordsFromDB()
        temp_file_path = kindleImporter.createTemporaryFile()
        self.done.emit(self.dialog, temp_file_path)


# moved from class beacause it cannot work as a slot :(
def importToAnki(dialog, temp_file_path):
    mw.progress.finish()
    if temp_file_path is not None:
        mw.progress.start(immediate=True, label="Importing...")
        dialog.setupImporter(temp_file_path)
        dialog.selectDeck()

        dialog.importer.run()
        mw.progress.finish()

        txt = "Importing complete.\n"
        if dialog.importer.log:
            txt += "\n".join(dialog.importer.log)

        os.remove(temp_file_path)
    else:
        txt = "Nothing to import!"
    showText(txt)


def startProgressBar(dialog, nth):
    mw.progress.start(immediate=True, label="Processing...")


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        self.t = ThreadTranslate()
        self.t.done.connect(importToAnki)
        self.t.startProgress.connect(startProgressBar)

        b = QPushButton("Import")
        cast(QDialogButtonBox, self.frm.buttonBox).addButton(b, QDialogButtonBox.ButtonRole.AcceptRole)
        self.deck = DeckChooser(
            self.mw, self.frm.deckArea, label=False)
        self.frm.importMode.setCurrentIndex(
                    self.mw.pm.profile.get('importMode', 1))

        self.daysSinceLastRun = kindleimporter.getDaysSinceLastRun()
        self.frm.importDays.setValue(self.daysSinceLastRun)

        self.exec()

    def accept(self):
        try:
            db_path = getDBPath()
            kindleimporter.writeCurrentTimestampToFile()  # update lastRun timestamp

            target_language = self.frm.languageSelect.currentText()
            includeUsage = self.frm.includeUsage.isChecked()
            doTranslate = self.frm.doTranslate.isChecked()
            importDays = self.frm.importDays.value()

            self.t.dialog = self
            self.t.args = (
                db_path, target_language, includeUsage, doTranslate, importDays
                )

            self.t.start()

        except urllib.error.URLError:
            showInfo("Cannot connect")
        except IOError:
            showInfo("DB file not selected, exiting")
        except sqlite3.DatabaseError:
            showInfo("Selected file is not a DB")
        finally:
            self.close()
            self.mw.reset()

    def setupImporter(self, temp_file_path):
        self.importer = TextImporter(self.mw.col, str(temp_file_path))
        self.importer.initMapping()
        self.importer.allowHTML = True
        self.importer.importMode = self.frm.importMode.currentIndex()
        self.mw.pm.profile['importMode'] = self.importer.importMode
        self.importer.delimiter = ';'

    def selectDeck(self):
        did = self.deck.selectedId()
        if did != self.importer.model['did']:
            self.importer.model['did'] = did
            self.mw.col.models.save(self.importer.model)
        self.mw.col.decks.select(did)


def getDBPath():
    vocab_path = kindleimporter.getKindleVocabPath()
    if vocab_path == "":
        key = "Import"
        dir = None
    else:
        key = None
        dir = vocab_path
    db_path = getFile(
        mw, "Select db file", None, dir=dir, key=key, filter="*.db"
    )
    if not db_path:
        raise IOError
    db_path = str(db_path)
    return db_path
