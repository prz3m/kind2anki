# coding=utf-8
import sqlite3
import sys
import os
import tempfile
import codecs
import json
import urllib
import datetime
import time
from urllib.parse import quote

from aqt import mw
from functools import partial

from .translate import translate


def translateWord(word, target_language):
    return str(translate(word, to_lang=target_language))


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
        with codecs.open(path, "w", encoding="utf-8") as f:
            for w, t in zip(self.words, self.translated):
                f.write(u"{0};{1}\n".format(w, t))
        return path
