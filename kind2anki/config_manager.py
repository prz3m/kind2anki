from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aqt.addons import AddonManager

LAST_RUN_KEY = "lastRun"
IMPORT_MODE_KEY = "importMode"

DEFAULT_IMPORT_MODE = 1  # = CsvMetadata.DupeResolution.PRESERVE

ADDON_PACKAGE = __name__.split(".")[0]


def _addon_manager() -> AddonManager:
    from aqt import mw

    return mw.addonManager


def _get(key: str, default: Any = None) -> Any:
    config = _addon_manager().getConfig(ADDON_PACKAGE) or {}
    value = config.get(key)
    return default if value is None else value


def _set(key: str, value: Any) -> None:
    manager = _addon_manager()
    config = manager.getConfig(ADDON_PACKAGE) or {}
    config[key] = value
    manager.writeConfig(ADDON_PACKAGE, config)


def get_last_run() -> int | None:
    return _get(LAST_RUN_KEY)


def set_last_run(timestamp: int) -> None:
    _set(LAST_RUN_KEY, timestamp)


def get_import_mode() -> int:
    return _get(IMPORT_MODE_KEY, DEFAULT_IMPORT_MODE)


def set_import_mode(mode: int) -> None:
    _set(IMPORT_MODE_KEY, mode)
