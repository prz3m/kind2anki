# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kind2anki_ui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_kind2ankiDialog(object):
    def setupUi(self, kind2ankiDialog):
        kind2ankiDialog.setObjectName(_fromUtf8("kind2ankiDialog"))
        kind2ankiDialog.resize(376, 193)
        self.vboxlayout = QtGui.QVBoxLayout(kind2ankiDialog)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.groupBox = QtGui.QGroupBox(kind2ankiDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.toplayout = QtGui.QVBoxLayout(self.groupBox)
        self.toplayout.setObjectName(_fromUtf8("toplayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.deckArea = QtGui.QWidget(self.groupBox)
        self.deckArea.setObjectName(_fromUtf8("deckArea"))
        self.gridLayout_2.addWidget(self.deckArea, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.toplayout.addLayout(self.gridLayout_2)
        self.importMode = QtGui.QComboBox(self.groupBox)
        self.importMode.setObjectName(_fromUtf8("importMode"))
        self.importMode.addItem(_fromUtf8(""))
        self.importMode.addItem(_fromUtf8(""))
        self.importMode.addItem(_fromUtf8(""))
        self.toplayout.addWidget(self.importMode)
        self.doTranslate = QtGui.QCheckBox(self.groupBox)
        self.doTranslate.setChecked(True)
        self.doTranslate.setObjectName(_fromUtf8("doTranslate"))
        self.toplayout.addWidget(self.doTranslate)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.languageSelect = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.languageSelect.sizePolicy().hasHeightForWidth())
        self.languageSelect.setSizePolicy(sizePolicy)
#        self.languageSelect.setToolTipDuration(-6)
        self.languageSelect.setEditable(True)
        self.languageSelect.setObjectName(_fromUtf8("languageSelect"))
        self.languageSelect.addItem(_fromUtf8(""))
        self.languageSelect.addItem(_fromUtf8(""))
        self.languageSelect.addItem(_fromUtf8(""))
        self.languageSelect.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.languageSelect, 1, 1, 1, 1)
        self.toplayout.addLayout(self.gridLayout)
        self.vboxlayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(kind2ankiDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Help)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(kind2ankiDialog)
        self.languageSelect.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), kind2ankiDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), kind2ankiDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(kind2ankiDialog)

    def retranslateUi(self, kind2ankiDialog):
        kind2ankiDialog.setWindowTitle(_("kind2anki"))
        self.groupBox.setTitle(_("Import options"))
        self.label_2.setText(_("Deck"))
        self.importMode.setItemText(0, _("Update existing notes when first field matches"))
        self.importMode.setItemText(1, _("Ignore lines where first field matches existing note"))
        self.importMode.setItemText(2, _("Import even if existing note has same first field"))
        self.doTranslate.setText(_("Translate words"))        
        self.label.setText(_("Target language:"))
        self.languageSelect.setItemText(0, _("pl"))
        self.languageSelect.setItemText(1, _("de"))
        self.languageSelect.setItemText(2, _("fr"))
        self.languageSelect.setItemText(3, _("es"))
