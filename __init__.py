from aqt import mw
from aqt.qt import QAction

from .kind2anki.kind2anki_dialog import Kind2AnkiDialog

action = QAction("kind2anki", mw)
action.triggered.connect(Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
