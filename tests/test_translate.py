import pytest

from kind2anki.translate import translate


@pytest.mark.live
def test_translation_works():
    assert translate("nothing", to_lang="pl").lower() == "nic"
