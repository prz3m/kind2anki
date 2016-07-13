# coding=utf-8
import sqlite3
import sys
import os
import tempfile
import codecs
from aqt import mw

# idea taken from Syntax Highlighting for Code addon, thanks!
try:
    # Try to find the modules in the global namespace:
    import textblob
    from textblob import TextBlob
except:
    # If not present, import modules from ./libs folder
    sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki", "libs"))
    import textblob
    from textblob import TextBlob


class KindleImporter():
    def __init__(self, db_path, target_language):
        self.db_path = db_path
        self.target_language = target_language

    def translateWordsFromDB(self):
        self.words = self.getWordsFromDB()
        self.translated = self.translateWords()

    def fetchWordsFromDBWithoutTranslation(self):
        self.words = self.getWordsFromDB()
        self.translated = len(self.words) * ['']
        
    def getWordsFromDB(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT word FROM WORDS")
        words = c.fetchall()
        words = [w[0] for w in words]
        conn.close()
        return words

    def translateWords(self):
        translated = []
        for word in self.words:
            try:
                translated.append(
                    TextBlob(word).translate(to=self.target_language))
            except textblob.exceptions.NotTranslated:
                translated.append('cannot translate')
        return translated

    def createTemporaryFile(self):
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.txt")
        with codecs.open(path, "w", encoding="utf-8") as f:
            for w, t in zip(self.words, self.translated):
                f.write(u"{0};{1}\n".format(w, t))
        return path
