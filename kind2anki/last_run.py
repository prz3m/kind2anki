import datetime
import time

ADDON_PACKAGE = __name__.split(".")[0]
CONFIG_KEY = "lastRun"
DEFAULT_DAYS = 10


def _addon_manager():
    from aqt import mw

    return mw.addonManager


def _read_config():
    return _addon_manager().getConfig(ADDON_PACKAGE) or {}


def _write_config(config):
    _addon_manager().writeConfig(ADDON_PACKAGE, config)


def save_days_since_last_run():
    config = _read_config()
    now = datetime.datetime.now()
    config[CONFIG_KEY] = int(time.mktime(now.timetuple()))
    _write_config(config)


def _get_days_since_timestamp(timestamp):
    now = datetime.datetime.now()
    previous = datetime.datetime.fromtimestamp(timestamp)
    return (now - previous).days


def get_days_since_last_run():
    timestamp = _read_config().get(CONFIG_KEY)
    if timestamp:
        days = _get_days_since_timestamp(timestamp) + 1  # round up
    else:
        days = DEFAULT_DAYS

    return days
