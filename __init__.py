import os
import sys

from aqt import mw
from aqt.qt import QAction

sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki"))
sys.path.insert(0, os.path.join(mw.pm.addonFolder(), "kind2anki", "kind2anki"))

from .kind2anki.kind2anki_dialog import Kind2AnkiDialog


action = QAction("kind2anki", mw)
action.triggered.connect(Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
