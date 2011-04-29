# -*- coding: utf-8 -*-

#       Copyright 2011 Adrià Cereto Massagué <adrian.cereto@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

"""
Module implementing MainWindow.
"""

import os, pybel
import openbabel as ob
from PySide.QtGui import QMainWindow, QFileDialog, QTableWidgetItem
from PySide.QtCore import QSettings
from PySide.QtCore import Slot as pyqtSignature

from find_decoys import get_fileformat, find_decoys, get_zinc_slice
from Ui_MainWindow import Ui_MainWindow
def readfile(format, filename):
    """Iterate over the molecules in a file.

    Required parameters:
       format - see the informats variable for a list of available
                input formats
       filename

    You can access the first molecule in a file using the next() method
    of the iterator:
        mol = readfile("smi", "myfile.smi").next()

    You can make a list of the molecules in a file using:
        mols = list(readfile("smi", "myfile.smi"))

    You can iterate over the molecules in a file as shown in the
    following code snippet:
    >>> atomtotal = 0
    >>> for mol in readfile("sdf", "head.sdf"):
    ...     atomtotal += len(mol.atoms)
    ...
    >>> print atomtotal
    43
    """
    obconversion = ob.OBConversion()
    formatok = obconversion.SetInFormat(format)
    if not formatok:
        raise ValueError("%s is not a recognised OpenBabel format" % format)
    if not os.path.isfile(filename):
        raise IOError("No such file: '%s'" % filename)
    obmol = ob.OBMol()
    print "sense string:", filename
    print "amb string:", str(filename)
    notatend = obconversion.ReadFile(obmol,str(filename))
    print notatend
    if not notatend:
        raise caca
    while notatend:
        yield Molecule(obmol)
        obmol = ob.OBMol()
        notatend = obconversion.Read(obmol)

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.settings = QSettings()
        self.supported_files = self.tr('Molecule files') + ' ('
        for format in pybel.informats.iterkeys():
            self.supported_files += "*.%s " %format
            self.supported_files += "*.%s.gz " %format
        self.supported_files += ')'
        self.outputDirectoryLineEdit.setText(self.settings.value('outdir'))

    def _getListWidgetItemTextList(self, listWidget):
        """
        """
        itemlist = [listWidget.item(index).text() for index in xrange(listWidget.count())]
        return itemlist



    @pyqtSignature("")
    def on_addQueryButton_clicked(self):
        """
        Slot documentation goes here.
        """
        itemlist = self._getListWidgetItemTextList(self.queryList)
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter(self.supported_files)
        dialog.setDirectory(os.path.expanduser('~'))
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            filelist = dialog.selectedFiles()
            for file in filelist:
                if file not in itemlist:
                    self.queryList.addItem(file)


    @pyqtSignature("")
    def on_addDButton_clicked(self):
        """
        Slot documentation goes here.
        """
        itemlist = self._getListWidgetItemTextList(self.dbListWidget)
        if self.dbComboBox.currentIndex() == 0:
            print "select files"
            dialog =  QFileDialog(self)
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setNameFilter(self.supported_files)
            dialog.setDirectory(os.path.expanduser('~'))
            dialog.setOption(QFileDialog.DontUseNativeDialog)
            if dialog.exec_():
                dblist = dialog.selectedFiles()
                for file in dblist:
                    if file not in itemlist:
                        self.dbListWidget.addItem(file)
        else:
            text = self.dbComboBox.currentText()
            if text.split()[0] == 'ZINC':
                if text not in itemlist and 'ZINC all' not in itemlist:
                    self.dbListWidget.addItem(self.dbComboBox.currentText())

    @pyqtSignature("")
    def on_outputDirectoryLineEdit_editingFinished(self):
        """
        Slot documentation goes here.
        """
        dir = self.outputDirectoryLineEdit.text()
        if os.path.isdir(dir):
            self.settings.setValue('outdir', dir)

    @pyqtSignature("")
    def on_outDirButton_clicked(self):
        """
        Slot documentation goes here.
        """
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setDirectory(os.path.expanduser('~'))
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            dir = dialog.selectedFiles()[0]
            if os.path.isdir(dir):
                self.outputDirectoryLineEdit.setText(dir)
                self.settings.setValue('outdir', dir)
            else:
                pass # TODO: inform statusbar about it

    @pyqtSignature("")
    def on_findDecoysButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_findDecoysButton_clicked
        #print self.settings.value('outdir')
#        query_files = self._getListWidgetItemTextList(self.queryList)
#
#        db_items = self._getListWidgetItemTextList(self.dbListWidget)
#        db_files = []
#        for item in db_items:
#            if item.split()[0] == 'ZINC':
#                pass #TODO download from ZINC
#            elif os.path.isfile(item):
#                db_files.append(str(item))
#        print db_files
        query_files = ['/home/ssorgatem/uni/PEI/trypsin_ligands.sdf.gz']
        db_files = ["/home/ssorgatem/uni/PEI/ZINC/10_p0.101.sdf.gz"]
        mols = readfile('sdf', '/home/ssorgatem/uni/PEI/trypsin_ligands.sdf.gz')
        print mols.next().mol.title
#        find_decoys(
#                    query_files = query_files
#                    ,db_files = db_files)
                    #,outputdir =  self.settings.value('outdir'))

    ############ Options tab  #############
    @pyqtSignature("")
    def on_tanimotoBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_tanimotoBox_editingFinished
        raise NotImplementedError

    @pyqtSignature("")
    def on_clogpBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_clogpBox_editingFinished
        raise NotImplementedError

    @pyqtSignature("")
    def on_molwtBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_molwtBox_editingFinished
        raise NotImplementedError

    @pyqtSignature("")
    def on_rotbBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_rotbBox_editingFinished
        raise NotImplementedError

    @pyqtSignature("")
    def on_hbaBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_hbaBox_editingFinished
        raise NotImplementedError

    @pyqtSignature("")
    def on_hbdBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_hbdBox_editingFinished
        print self.hbdBox.value()

    @pyqtSignature("")
    def on_defaultsButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_defaultsButton_clicked
        raise NotImplementedError

    #################################


    @pyqtSignature("")
    def on_actionAbout_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_actionAbout_activated
        raise NotImplementedError
