import csv
import datetime
import getpass
import os
import sqlite3
import string
import tempfile
import time
from functools import partial
from sys import platform

from .translate import translate


def translate_word(word, target_language):
    return str(translate(word, to_lang=target_language))


def get_kindle_vocab_path():
    try:
        if platform == "win32":
            for drive in string.ascii_uppercase:
                path = rf"{drive}:\system\vocabulary\vocab.db"
                if os.path.exists(path):
                    return rf"{drive}:\system\vocabulary"
        elif platform == "darwin":
            path = "/Volumes/Kindle/system/vocabulary/vocab.db"
            if os.path.exists(path):
                return "/Volumes/Kindle/system/vocabulary"
        else:
            user = getpass.getuser()
            for mount_root in (f"/media/{user}", f"/run/media/{user}"):
                path = f"{mount_root}/Kindle/system/vocabulary"
                if os.path.exists(f"{path}/vocab.db"):
                    return path
        return ""
    except Exception:
        return ""


class KindleImporter:
    def __init__(self, db_path, target_language, include_usage=False, do_translate=True, import_days=5):
        self.db_path = db_path
        self.target_language = target_language
        self.include_usage = include_usage
        self.do_translate = do_translate
        self.timestamp = self._create_timestamp(import_days) * 1000

    def _create_timestamp(self, days):
        d = datetime.date.today() - datetime.timedelta(days=days)
        return int(time.mktime(d.timetuple()))

    def translate_words_from_db(self):
        self._get_words_from_db()
        self.translated = self._translate_words()

    def fetch_words_from_db_without_translation(self):
        self._get_words_from_db()
        self.translated = len(self.words) * [""]

    def _get_words_from_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT word, id FROM words WHERE timestamp > ?", (str(self.timestamp),))
        words_and_ids = c.fetchall()
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]
        conn.close()

    def _translate_words(self):
        translated = []
        translate = partial(translate_word, target_language=self.target_language)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys, strict=False):
            translated_word = ""
            if self.include_usage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?", [word_key])
                usages = c.fetchall()
                for usage in usages:
                    usage = usage[0].replace(word, f"<b>{word}</b>")
                    translated_word += usage + "<hr>"

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
        path = os.path.join(tempfile.gettempdir(), "kind2anki_temp.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            for w, t in zip(self.words, self.translated, strict=False):
                writer.writerow([w, t])
        return path
