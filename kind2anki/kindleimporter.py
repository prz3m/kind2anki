# coding=utf-8
import sqlite3
import os
import tempfile
import datetime
import time
import string
import getpass
from sys import platform
from functools import partial

from .translate import translate

ADDON_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def translateWord(word, target_language):
    return str(translate(word, to_lang=target_language))


def getKindleVocabPath():
    try:
        if platform == "win32":
            for l in string.ascii_uppercase:
                path = r"{}:\system\vocabulary\vocab.db".format(l)
                if os.path.exists(path):
                    return r"{}:\system\vocabulary".format(l)
        elif platform == "darwin":
            path = "/Volumes/Kindle/system/vocabulary/vocab.db"
            if os.path.exists(path):
                return "/Volumes/Kindle/system/vocabulary"
        else:
            user = getpass.getuser()
            path = r"/media/{}/Kindle/system/vocabulary/vocab.db".format(user)
            if os.path.exists(path):
                return r"/media/{}/Kindle/system/vocabulary/".format(user)
        return ""
    except:
        return ""


def getLastRunFilePath():
    return os.path.join(ADDON_ROOT, "lastRun.txt")


def getDaysSinceTimestamp(timestamp):
    now = datetime.datetime.now()
    previous = datetime.datetime.fromtimestamp(timestamp)
    return (now - previous).days


def getDaysSinceLastRun():
    path = getLastRunFilePath()
    if os.path.isfile(path):
        with open(path, "r") as f:
            timestamp = int(f.read())
        days = getDaysSinceTimestamp(timestamp) + 1  # round up
    else:
        days = 10

    return days


def writeCurrentTimestampToFile():
    path = getLastRunFilePath()
    now = datetime.datetime.now()
    with open(path, "w") as f:
        f.write(str(int(time.mktime(now.timetuple()))))


class KindleImporter():
    def __init__(self, db_path, target_language, includeUsage=False,
                 doTranslate=True, importDays=5):
        self.db_path = db_path
        self.target_language = target_language
        self.includeUsage = includeUsage
        self.doTranslate = doTranslate
        self.timestamp = self.createTimestamp(importDays) * 1000

    def createTimestamp(self, days):
        d = (datetime.date.today() - datetime.timedelta(days=days))
        return int(time.mktime(d.timetuple()))

    def translateWordsFromDB(self):
        self.getWordsFromDB()
        self.translated = self.translateWords()

    def fetchWordsFromDBWithoutTranslation(self):
        self.getWordsFromDB()
        self.translated = len(self.words) * ['']

    def getWordsFromDB(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT word, id FROM words WHERE timestamp > ?",
                  (str(self.timestamp),))
        words_and_ids = c.fetchall()
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]
        conn.close()

    def translateWords(self):
        translated = []
        translate = partial(
            translateWord, target_language=self.target_language)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys):
            translated_word = ""
            if self.includeUsage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?",
                          [word_key])
                usages = c.fetchall()
                for usage in usages:
                    usage = usage[0].replace(word, "<b>%s</b>" % word)
                    translated_word += usage.replace(";", ",") + "<hr>"

            if self.doTranslate:
                try:
                    translated_word += translate(word)
                except:
                    translated_word += "cannot translate"

            translated.append(translated_word)

        conn.close()
        return translated

    def createTemporaryFile(self):
        if len(self.words) == 0:
            return None
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.txt")
        with open(path, "w", encoding="utf-8") as f:
            for w, t in zip(self.words, self.translated):
                f.write(u"{0};{1}\n".format(w, t))
        return path
