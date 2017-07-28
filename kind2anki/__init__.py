# coding=utf-8
# anki stuff import
from aqt.deckchooser import DeckChooser
from aqt import mw
from aqt.utils import showInfo, getFile, showText
from aqt.qt import *
from anki.importing import TextImporter
from PyQt4.QtCore import QThread, pyqtSignal

# some python libs
import os
import sys
import sqlite3
import urllib2
import datetime
import time
import string
from sys import platform
import getpass

# addon's ui
import kind2anki_ui

from kindleimporter import KindleImporter

sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki", "libs"))


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
    mw.progress.start(immediate=True, label="Importing...")
    dialog.setupImporter(temp_file_path)
    dialog.selectDeck()

    dialog.importer.run()
    mw.progress.finish()

    txt = _("Importing complete.") + "\n"
    if dialog.importer.log:
        txt += "\n".join(dialog.importer.log)
    showText(txt)
    os.remove(temp_file_path)


def startProgressBar(dialog, nth):
    mw.progress.start(immediate=True, label="Processing...")


class Kind2AnkiDialog(QDialog):
    def __init__(self):
        global mw
        QDialog.__init__(self, mw, Qt.Window)
        self.mw = mw
        self.frm = kind2anki_ui.Ui_kind2ankiDialog()
        self.frm.setupUi(self)

        self.t = ThreadTranslate()
        self.t.done.connect(importToAnki)
        self.t.startProgress.connect(startProgressBar)

        b = QPushButton(_("Import"))
        self.frm.buttonBox.addButton(b, QDialogButtonBox.AcceptRole)
        self.deck = DeckChooser(
            self.mw, self.frm.deckArea, label=False)
        self.frm.importMode.setCurrentIndex(
                    self.mw.pm.profile.get('importMode', 1))

        self.daysSinceLastRun = self.getDaysSinceLastRun()
        self.frm.importDays.setValue(self.daysSinceLastRun)

        self.exec_()

    def accept(self):
        try:
            db_path = getDBPath()
            self.writeCurrentTimestampToFile()  # update lastRun timestamp

            target_language = self.frm.languageSelect.currentText()
            includeUsage = self.frm.includeUsage.isChecked()
            doTranslate = self.frm.doTranslate.isChecked()
            importDays = self.frm.importDays.value()

            # if doTranslate:
            #     showInfo("Translating words from database, it can take a while...")
            # else:
            #     showInfo("Fetching words from database, it can take a while...")

            self.t.dialog = self
            self.t.args = (
                db_path, target_language, includeUsage, doTranslate, importDays
                )

            self.t.start()

        except urllib2.URLError:
            showInfo("Cannot connect")
        except IOError:
            showInfo("DB file not selected, exiting")
        except sqlite3.DatabaseError:
            showInfo("Selected file is not a DB")
        finally:
            self.close()
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

    def getDaysSinceLastRun(self):
        path = self.getLastRunFilePath()
        if os.path.isfile(path):
            with open(path, "r") as f:
                timestamp = int(f.read())
            days = self.getDaysSinceTimestamp(timestamp) + 1 # round up
        else:
            days = 10

        return days

    def getDaysSinceTimestamp(self, timestamp):
        now = datetime.datetime.now()
        previous = datetime.datetime.fromtimestamp(timestamp)
        return (now - previous).days

    def writeCurrentTimestampToFile(self):
        path = self.getLastRunFilePath()
        now = datetime.datetime.now()
        with open(path, "w") as f:
            f.write(str(int(time.mktime(now.timetuple()))))

    def getLastRunFilePath(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(dir_path, "lastRun.txt")


def getDBPath():
    global mw
    # vocab_path = getKindleVocabPath()
    db_path = getFile(
        mw, _("Select db file"), None, key="Import", filter="*.db"
    )
    if not db_path:
        raise IOError
    db_path = unicode(db_path)
    return db_path


def getKindleVocabPath():
    try:
        if platform == "win32":
            for l in string.ascii_uppercase:
                path = r"{}:\\system\vocabulary\vocab.db".format(l)
                if os.path.exists(path):
                    return r"{}:\\system\vocabulary".format(l)
        else:
            user = getpass.getuser()
            path = r"/media/{}/Kindle/system/vocabulary/vocab.db".format(user)
            if os.path.exists(path):
                return r"/media/{}/Kindle/system/vocabulary/".format(user)
        return ""
    except:
        return ""



action = QAction("kind2anki", mw)
mw.connect(action, SIGNAL("triggered()"), Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
