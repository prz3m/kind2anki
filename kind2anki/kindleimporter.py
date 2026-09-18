import csv
import datetime
import getpass
import html
import os
import re
import sqlite3
import string
import tempfile
import time
from sys import platform
from urllib.error import URLError

from .translate import TranslationUnchanged, translate


def get_kindle_vocab_path() -> str:
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
    def __init__(
        self,
        db_path: str,
        target_language: str,
        include_usage: bool = False,
        do_translate: bool = True,
        import_days: int = 5,
    ) -> None:
        self.db_path = db_path
        self.target_language = target_language
        self.include_usage = include_usage
        self.do_translate = do_translate
        self.timestamp = self._create_timestamp(import_days) * 1000
        self.words: list[str] = []
        self.word_keys: list[int] = []
        self.translated: list[str] = []

    def _create_timestamp(self, days: int) -> int:
        d = datetime.date.today() - datetime.timedelta(days=days)
        return int(time.mktime(d.timetuple()))

    def translate_words_from_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            self._get_words_from_db(conn)
            self.translated = self._translate_words(conn)
        finally:
            conn.close()

    def _get_words_from_db(self, conn: sqlite3.Connection) -> None:
        c = conn.cursor()
        c.execute("SELECT word, id FROM words WHERE timestamp > ?", (self.timestamp,))
        words_and_ids = c.fetchall()
        self.words = [w[0] for w in words_and_ids]
        self.word_keys = [w[1] for w in words_and_ids]

    def _translate_words(self, conn: sqlite3.Connection) -> list[str]:
        translated: list[str] = []
        c = conn.cursor()
        for word, word_key in zip(self.words, self.word_keys, strict=True):
            translated_word = ""
            if self.include_usage:
                c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?", [word_key])
                usages = c.fetchall()
                escaped_word = html.escape(word, quote=False)
                word_pattern = re.compile(rf"\b{re.escape(escaped_word)}\b", re.IGNORECASE)
                for usage in usages:
                    usage = word_pattern.sub(r"<b>\g<0></b>", html.escape(usage[0], quote=False))
                    translated_word += usage + "<hr>"

            if self.do_translate:
                try:
                    translated_word += html.escape(translate(word, to_lang=self.target_language), quote=False)
                except TranslationUnchanged:
                    translated_word += html.escape(word, quote=False)
                except URLError:
                    raise
                except Exception:
                    translated_word += "cannot translate"

            translated.append(translated_word)

        return translated

    def create_temporary_file(self) -> str | None:
        if len(self.words) == 0:
            return None
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False) as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            for w, t in zip(self.words, self.translated, strict=True):
                writer.writerow([html.escape(w, quote=False), t])
        return f.name
