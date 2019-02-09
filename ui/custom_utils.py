# -*- coding: utf-8 -*-

"""This is a file that should contain utils that we may
use that doesn't specifically belong to any window."""
from PySide2.QtWidgets import QWidget, QMessageBox, QPushButton

########################################################
################### THEMED LAYOUT ######################
########################################################


class ThemedLayout(QWidget):
    """Special class to iterate over specific QWidgets childrens for colour themes."""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)


###########################################
################ QMESSAGEBOX ##############
###########################################


def msgbox_question(title, message):
    """Generate a popup that requests if you are really sure that you want to delete a record."""
    msgbox = QMessageBox()
    msgbox.setWindowTitle(title)
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.setText(message)
    buttonyes = QPushButton("Yes")
    msgbox.addButton(buttonyes, QMessageBox.YesRole)
    buttonno = QPushButton("No")
    msgbox.addButton(buttonno, QMessageBox.NoRole)
    msgbox.exec_()
    if msgbox.clickedButton() == buttonno:
        return False
    else:
        return True
