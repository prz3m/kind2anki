import sys
import os

import pytest

# not elegant, but avoids importing PyQT etc.
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(dir_path, "..", "kind2anki"))
from translate import translate


@pytest.mark.live
def test_translation_works():
    assert translate('nothing', to_lang='pl').lower() == 'nic'