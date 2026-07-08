from aqt import mw
from aqt.qt import QAction
from aqt.utils import qconnect

from .kind2anki.kind2anki_dialog import Kind2AnkiDialog

action = QAction("kind2anki", mw)
qconnect(action.triggered, Kind2AnkiDialog)
mw.form.menuTools.addAction(action)
