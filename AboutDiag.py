# -*- coding: utf-8 -*-

"""
Module implementing AboutDialog.
"""
import webbrowser,  os

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignature as Slot
from Ui_AboutDiag import Ui_Dialog

class AboutDialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        if "_MEIPASS2" in os.environ:
            self.fdir = os.environ["_MEIPASS2"]
        else:
            self.fdir = os.path.dirname(__file__)

    @Slot("")
    def on_licenseButton_clicked(self):
        webbrowser.open_new_tab(os.path.join(self.fdir,'LICENCE.html'))

    @Slot("")
    def on_ReleaseNotesButton_clicked(self):
        webbrowser.open_new_tab(os.path.join(self.fdir,'RELEASE_NOTES.txt'))

    @Slot("")
    def on_okButton_clicked(self):
        self.accept()
