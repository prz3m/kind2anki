"""Single entry point for this add-on's persistent configuration.

Values are stored in Anki's add-on config: defaults come from ``config.json``
and the user's overrides live in ``meta.json``, so they survive add-on updates.
Nothing outside this module should touch ``mw.addonManager`` config or
``mw.pm.profile`` directly.
"""

LAST_RUN_KEY = "lastRun"
IMPORT_MODE_KEY = "importMode"

# Anki NoteImporter mode: 0=update, 1=ignore, 2=add duplicates.
DEFAULT_IMPORT_MODE = 1

ADDON_PACKAGE = __name__.split(".")[0]


def _addon_manager():
    from aqt import mw

    return mw.addonManager


def _get(key, default=None):
    config = _addon_manager().getConfig(ADDON_PACKAGE) or {}
    value = config.get(key)
    return default if value is None else value


def _set(key, value):
    manager = _addon_manager()
    config = manager.getConfig(ADDON_PACKAGE) or {}
    config[key] = value
    manager.writeConfig(ADDON_PACKAGE, config)


def get_last_run():
    return _get(LAST_RUN_KEY)


def set_last_run(timestamp):
    _set(LAST_RUN_KEY, timestamp)


def get_import_mode():
    return _get(IMPORT_MODE_KEY, DEFAULT_IMPORT_MODE)


def set_import_mode(mode):
    _set(IMPORT_MODE_KEY, mode)
