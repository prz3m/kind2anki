from aqt import mw
from aqt.qt import QAction, qconnect

from .kind2anki.kind2anki_dialog import Kind2AnkiDialog

action = QAction("kind2anki", mw)
qconnect(action.triggered, lambda: Kind2AnkiDialog().exec())
mw.form.menuTools.addAction(action)
