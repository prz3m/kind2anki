# coding=utf-8
import sqlite3
import sys
import os
import tempfile
import codecs
from aqt import mw

from translate import Translator


class KindleImporter():
    def __init__(self, db_path, target_language, includeUsage=False,
                 doTranslate=True):
        self.db_path = db_path
        self.target_language = target_language
        self.includeUsage = includeUsage
        self.doTranslate = doTranslate

    def translateWordsFromDB(self):
        self.getWordsFromDB()
        self.translated = self.translateWords()

    def getWordsFromDB(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT word, id FROM WORDS")
        words_and_ids = c.fetchall()
        # hard limit...
        if self.doTranslate and len(words_and_ids) > 800:
            words_and_ids = words_and_ids[-800:]
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]
        conn.close()

    def translateWords(self):
        translated = []
        translator = Translator(to_lang=self.target_language)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys):
            translated_word = ""
            if self.includeUsage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?", [word_key])
                usages = c.fetchall()
                for usage in usages:
                    translated_word += usage[0].replace(";", ",") + "<hr>"

            if self.doTranslate:
                try:
                    translated_word += translator.translate(word)
                except:
                    translated_word += "cannot translate"

            translated.append(translated_word)

        conn.close()
        return translated

    def createTemporaryFile(self):
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.txt")
        with codecs.open(path, "w", encoding="utf-8") as f:
            for w, t in zip(self.words, self.translated):
                f.write(u"{0};{1}\n".format(w, t))
        return path
