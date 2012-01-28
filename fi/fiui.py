# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fi.ui'
#
# Created: Mon May 23 10:20:10 2011
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_fidialog(object):
    def setupUi(self, fidialog):
        fidialog.setObjectName("fidialog")
        fidialog.resize(491, 300)
        self.verticalLayoutWidget = QtGui.QWidget(fidialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 7, 491, 291))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.plainTextEdit = QtGui.QPlainTextEdit(self.verticalLayoutWidget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        self.buttonBox = QtGui.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Help|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(fidialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), fidialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), fidialog.reject)
        QtCore.QMetaObject.connectSlotsByName(fidialog)

    def retranslateUi(self, fidialog):
        fidialog.setWindowTitle(QtGui.QApplication.translate("fidialog", "Forgetting index", None, QtGui.QApplication.UnicodeUTF8))

