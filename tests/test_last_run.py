from freezegun import freeze_time

import kind2anki.last_run as last_run


class FakeAddonManager:
    def __init__(self):
        self._config = {}

    def getConfig(self, _module):
        return dict(self._config)

    def writeConfig(self, _module, config):
        self._config = dict(config)


def test_write_then_read_last_run(monkeypatch):
    manager = FakeAddonManager()
    monkeypatch.setattr(last_run, "_addon_manager", lambda: manager)
    with freeze_time("2026-06-25"):
        last_run.save_days_since_last_run()
    with freeze_time("2026-06-28"):
        assert last_run.get_days_since_last_run() == 4
