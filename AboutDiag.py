#-*- coding:utf-8 -*-
#
#     This file is part of Decoy Finder
#
#     Copyright 2011-2012 Adrià Cereto Massagué <adrian.cereto@urv.cat>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

"""
Module implementing AboutDialog.
"""
import webbrowser,  os

from PySide.QtGui import QDialog
from PySide.QtCore import Slot
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
