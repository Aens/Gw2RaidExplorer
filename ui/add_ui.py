# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add.ui',
# licensing of 'add.ui' applies.
#
# Created: Thu Feb  7 15:57:55 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(581, 90)
        self.lineKey = QtWidgets.QLineEdit(Dialog)
        self.lineKey.setGeometry(QtCore.QRect(70, 20, 501, 20))
        self.lineKey.setStyleSheet("background-color: rgb(255,250,209);")
        self.lineKey.setAlignment(QtCore.Qt.AlignCenter)
        self.lineKey.setObjectName("lineKey")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 20, 51, 16))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.lineName = QtWidgets.QLineEdit(Dialog)
        self.lineName.setGeometry(QtCore.QRect(70, 50, 111, 20))
        self.lineName.setStyleSheet("background-color: rgb(255,250,209);")
        self.lineName.setAlignment(QtCore.Qt.AlignCenter)
        self.lineName.setObjectName("lineName")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 51, 16))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.buttonSave = QtWidgets.QPushButton(Dialog)
        self.buttonSave.setGeometry(QtCore.QRect(490, 50, 81, 31))
        self.buttonSave.setStyleSheet("background-color: rgb(170, 208, 169);")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/Save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonSave.setIcon(icon)
        self.buttonSave.setIconSize(QtCore.QSize(20, 20))
        self.buttonSave.setObjectName("buttonSave")
        self.labelInfo = QtWidgets.QLabel(Dialog)
        self.labelInfo.setGeometry(QtCore.QRect(190, 50, 291, 21))
        self.labelInfo.setStyleSheet("color: rgb(255, 0, 0);")
        self.labelInfo.setText("")
        self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.labelInfo.setObjectName("labelInfo")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Add new API Key", None, -1))
        self.lineKey.setPlaceholderText(QtWidgets.QApplication.translate("Dialog", "12345-12345-12345-12345-12345-12345-12345", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Key:", None, -1))
        self.lineName.setPlaceholderText(QtWidgets.QApplication.translate("Dialog", "My main account", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Save as:", None, -1))
        self.buttonSave.setText(QtWidgets.QApplication.translate("Dialog", "Save", None, -1))

