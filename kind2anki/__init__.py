# coding=utf-8
# anki stuff import
from aqt.deckchooser import DeckChooser
from aqt import mw
from aqt.utils import showInfo, getFile, showText
from aqt.qt import *
from anki.importing import TextImporter

# some python libs
import sys
import tempfile
import os
import sqlite3
import urllib2

# addon's ui
import kind2anki_ui

from kindleimporter import KindleImporter


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        global mw
        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)
        b = QPushButton(_("Import"))
        self.frm.buttonBox.addButton(b, QDialogButtonBox.AcceptRole)
        self.deck = DeckChooser(
            self.mw, self.frm.deckArea, label=False)
        self.frm.importMode.setCurrentIndex(
                    self.mw.pm.profile.get('importMode', 1))

        self.exec_()

    def accept(self):
        try:
            db_path = getDBPath()
            self.close()

            target_language = self.frm.languageSelect.currentText()
            includeUsage = self.frm.includeUsage.isChecked()
            doTranslate = self.frm.doTranslate.isChecked()

            kindleImporter = KindleImporter(db_path, target_language,
                                            includeUsage, doTranslate)

            mw.progress.start(label=_("Processing..."), immediate=True)

            if doTranslate:
                showInfo("Translating words from database, it can take a while...")
            else:
                showInfo("Fetching words from database, it can take a while...")
            kindleImporter.translateWordsFromDB()

            mw.progress.finish()

            temp_file_path = kindleImporter.createTemporaryFile()
            self.setupImporter(temp_file_path)
            self.selectDeck()

            self.mw.progress.start(immediate=True, label="Importing...")
            self.importer.run()
            self.mw.progress.finish()

            txt = _("Importing complete.") + "\n"
            if self.importer.log:
                txt += "\n".join(self.importer.log)
            showText(txt)
            os.remove(temp_file_path)

        except urllib2.URLError:
            showInfo("Cannot connect to Google Translate")
        except IOError:
            showInfo("DB file not selected, exiting")
        except sqlite3.DatabaseError:
            showInfo("Selected file is not a DB")
        finally:
            self.close()
            mw.progress.finish()
            self.mw.reset()

    def setupImporter(self, temp_file_path):
        self.importer = TextImporter(self.mw.col, unicode(temp_file_path))
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
    global mw
    db_path = getFile(
        mw, _("Select db file"), None, key="Import", filter="*.db")
    if not db_path:
        raise IOError
    db_path = unicode(db_path)
    return db_path

action = QAction("kind2anki", mw)
mw.connect(action, SIGNAL("triggered()"), Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
