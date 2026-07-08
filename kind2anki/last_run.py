import datetime
import time

from . import config_manager

DEFAULT_DAYS = 10


def save_days_since_last_run():
    now = datetime.datetime.now()
    config_manager.set_last_run(int(time.mktime(now.timetuple())))


def _get_days_since_timestamp(timestamp):
    now = datetime.datetime.now()
    previous = datetime.datetime.fromtimestamp(timestamp)
    return (now - previous).days


def get_days_since_last_run():
    timestamp = config_manager.get_last_run()
    if timestamp:
        days = _get_days_since_timestamp(timestamp) + 1  # round up
    else:
        days = DEFAULT_DAYS

    return days
