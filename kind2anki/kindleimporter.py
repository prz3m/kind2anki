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

def translate_word(word, target_language):
    return str(translate(word, to_lang=target_language))


def get_kindle_vocab_path():
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
    except Exception:
        return ""


class KindleImporter():
    def __init__(self, db_path, target_language, include_usage=False,
                 do_translate=True, import_days=5):
        self.db_path = db_path
        self.target_language = target_language
        self.include_usage = include_usage
        self.do_translate = do_translate
        self.timestamp = self._create_timestamp(import_days) * 1000

    def _create_timestamp(self, days):
        d = (datetime.date.today() - datetime.timedelta(days=days))
        return int(time.mktime(d.timetuple()))

    def translate_words_from_db(self):
        self._get_words_from_db()
        self.translated = self._translate_words()

    def fetch_words_from_db_without_translation(self):
        self._get_words_from_db()
        self.translated = len(self.words) * ['']

    def _get_words_from_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT word, id FROM words WHERE timestamp > ?",
                  (str(self.timestamp),))
        words_and_ids = c.fetchall()
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]
        conn.close()

    def _translate_words(self):
        translated = []
        translate = partial(
            translate_word, target_language=self.target_language)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys):
            translated_word = ""
            if self.include_usage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?",
                          [word_key])
                usages = c.fetchall()
                for usage in usages:
                    usage = usage[0].replace(word, "<b>%s</b>" % word)
                    translated_word += usage.replace(";", ",") + "<hr>"

            if self.do_translate:
                try:
                    translated_word += translate(word)
                except Exception:
                    translated_word += "cannot translate"

            translated.append(translated_word)

        conn.close()
        return translated

    def create_temporary_file(self):
        if len(self.words) == 0:
            return None
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.txt")
        with open(path, "w", encoding="utf-8") as f:
            for w, t in zip(self.words, self.translated):
                f.write(u"{0};{1}\n".format(w, t))
        return path
