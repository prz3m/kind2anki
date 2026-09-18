import pytest
import sample_vocab

from kind2anki import config_manager, kindleimporter


@pytest.fixture(scope="session")
def db_path(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("kindle") / "vocab.db")
    sample_vocab.build(path)
    return path


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def fake_translate(word, **kwargs):
        return "fake"

    monkeypatch.setattr(kindleimporter, "translate", fake_translate)
    return fake_translate


@pytest.fixture
def fake_config(monkeypatch):
    class FakeAddonManager:
        def __init__(self):
            self._config = {}

        def getConfig(self, _module):
            return dict(self._config)

        def writeConfig(self, _module, config):
            self._config = dict(config)

    manager = FakeAddonManager()
    monkeypatch.setattr(config_manager, "_addon_manager", lambda: manager)
    return manager
