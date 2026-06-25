import pytest

from kind2anki import kindleimporter
import sample_vocab


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
