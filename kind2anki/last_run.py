import datetime
import os
import time
from pathlib import Path

ROOT_FOLDER = Path(__file__).resolve().parent.parent


def _get_last_run_file_path():
    return str(ROOT_FOLDER / "lastRun.txt")


def save_days_since_last_run():
    path = _get_last_run_file_path()
    now = datetime.datetime.now()
    with open(path, "w") as f:
        f.write(str(int(time.mktime(now.timetuple()))))


def _get_days_since_timestamp(timestamp):
    now = datetime.datetime.now()
    previous = datetime.datetime.fromtimestamp(timestamp)
    return (now - previous).days


def get_days_since_last_run():
    path = _get_last_run_file_path()
    if os.path.isfile(path):
        with open(path) as f:
            timestamp = int(f.read())
        days = _get_days_since_timestamp(timestamp) + 1  # round up
    else:
        days = 10

    return days
