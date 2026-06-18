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
from dataclasses import dataclass
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


@dataclass(frozen=True)
class TranslatedWord:
    word: str
    word_key: int
    translation: str


def _create_timestamp(days: int) -> int:
    d = datetime.date.today() - datetime.timedelta(days=days)
    return int(time.mktime(d.timetuple()))


def translate_words(
    db_path: str,
    target_language: str,
    include_usage: bool = False,
    do_translate: bool = True,
    import_days: int = 5,
) -> list[TranslatedWord]:
    timestamp = _create_timestamp(import_days) * 1000
    conn = sqlite3.connect(db_path)
    try:
        c = conn.cursor()
        c.execute("SELECT word, id FROM words WHERE timestamp > ?", (timestamp,))
        rows = c.fetchall()
        return [
            TranslatedWord(
                word=word,
                word_key=word_key,
                translation=_translate_word(conn, word, word_key, target_language, include_usage, do_translate),
            )
            for word, word_key in rows
        ]
    finally:
        conn.close()


def _translate_word(
    conn: sqlite3.Connection,
    word: str,
    word_key: int,
    target_language: str,
    include_usage: bool,
    do_translate: bool,
) -> str:
    parts: list[str] = []
    if include_usage:
        parts.append(_format_usages(conn, word, word_key))
    if do_translate:
        parts.append(_translate(word, target_language))
    return "".join(parts)


def _format_usages(conn: sqlite3.Connection, word: str, word_key: int) -> str:
    c = conn.cursor()
    c.execute("SELECT usage FROM LOOKUPS WHERE word_key = ?", [word_key])
    usages = c.fetchall()
    escaped_word = html.escape(word, quote=False)
    word_pattern = re.compile(rf"\b{re.escape(escaped_word)}\b", re.IGNORECASE)
    out: list[str] = []
    for (usage,) in usages:
        usage = word_pattern.sub(r"<b>\g<0></b>", html.escape(usage, quote=False))
        out.append(usage + "<hr>")
    return "".join(out)


def _translate(word: str, target_language: str) -> str:
    try:
        return html.escape(translate(word, to_lang=target_language), quote=False)
    except TranslationUnchanged:
        return html.escape(word, quote=False)
    except URLError:
        raise
    except Exception:
        return "cannot translate"


def create_import_file(
    db_path: str,
    target_language: str,
    include_usage: bool = False,
    do_translate: bool = True,
    import_days: int = 5,
) -> str | None:
    entries = translate_words(db_path, target_language, include_usage, do_translate, import_days)
    if not entries:
        return None
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", suffix=".csv", delete=False) as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        for entry in entries:
            writer.writerow([html.escape(entry.word, quote=False), entry.translation])
    return f.name
