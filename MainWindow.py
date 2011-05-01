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
from PySide.QtGui import QMainWindow, QFileDialog, QTableWidgetItem
from PySide.QtCore import QSettings, QThread, Signal
from PySide.QtCore import Slot as pyqtSignature

from find_decoys import get_fileformat, find_decoys, get_zinc_slice
from Ui_MainWindow import Ui_MainWindow


class DecoyFinderThread(QThread):
    """
    """
    def __init__(self, query_files, db_files, parent = None):
        """
        """
        print "thread created"
        self.query_files = query_files
        self.db_files = db_files
        self.settings = QSettings()
        super(DecoyFinderThread, self).__init__(parent)

    info = Signal(unicode) #needs to be defined OUTSIDE __init__
    progress = Signal(int)
    finished = Signal()

    def run(self):
        """
        """
        self.info.emit(u"thread running")
        try:
            filecount = -1
            for filecount, current_file in find_decoys(
                        query_files = self.query_files
                        ,db_files = self.db_files
                        ,outputdir =  self.settings.value('outdir', os.getcwd())
                        ,HBA_t = int(self.settings.value('HBA_t', 0))
                        ,HBD_t = int(self.settings.value('HBD_t', 0))
                        ,ClogP_t = float(self.settings.value('ClogP_t', 1))
                        ,tanimoto_t = float(self.settings.value('tanimoto_t', 0.9))
                        ,MW_t = int(self.settings.value('MW_t',40))
                        ,RB_t = int(self.settings.value('RB_t',0))
                        ):
                self.info.emit("Reading %s" % current_file)
                self.progress.emit(filecount)
            self.progress.emit(filecount +1)
        except:
            self.info.emit("An error ocurred")
        self.finished.emit()

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
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.settings = QSettings()
        self.hbaBox.setValue(int(self.settings.value('HBA_t', 0)))
        self.hbdBox.setValue(int(self.settings.value('HBD_t', 0)))
        self.clogpBox.setValue(float(self.settings.value('ClogP_t', 1)))
        self.tanimotoBox.setValue(float(self.settings.value('tanimoto_t', 0.9)))
        self.molwtBox.setValue(int(self.settings.value('MW_t',40)))
        self.rotbBox.setValue(int(self.settings.value('RB_t',0)))
        self.supported_files = self.tr('Molecule files') + ' ('
        for format in pybel.informats.iterkeys():
            self.supported_files += "*.%s " %format
            self.supported_files += "*.%s.gz " %format
        self.supported_files += ')'
        self.outputDirectoryLineEdit.setText(self.settings.value('outdir',os.getcwd()))

    def _getListWidgetItemTextList(self, listWidget):
        """
        """
        itemlist = [listWidget.item(index).text() for index in xrange(listWidget.count())]
        return itemlist

    def on_finder_finished(self):
        """
        """
        self.tabWidget.setEnabled(True)


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
            #print "select files"
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
                self.statusbar.showMessage(self.tr("Unable to read selected directory"))

    @pyqtSignature("")
    def on_findDecoysButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.findDecoysButton.setEnabled(False)
        #print self.settings.value('outdir')
        query_files = self._getListWidgetItemTextList(self.queryList)

        db_items = self._getListWidgetItemTextList(self.dbListWidget)
        db_files = []
        self.progressBar.maximum = 0
        for item in db_items:
            if item.split()[0] == 'ZINC':
                pass #TODO download from ZINC
            elif os.path.isfile(item):
                db_files.append(str(item))
        self.progressBar.setMaximum(len(db_files))
        self.finder = DecoyFinderThread(query_files, db_files)
        #self.statusbar.showMessage("hola")
        self.finder.info.connect(self.statusbar.showMessage)
        self.finder.progress.connect(self.progressBar.setValue)
        self.finder.finished.connect(self.on_finder_finished)
        self.tabWidget.setEnabled(False)
        print "starting thread"
        self.finder.start()
        print "started"

    @pyqtSignature("")
    def on_clearButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.progressBar.setMaximum(1)


    ############ Options tab  #############
    @pyqtSignature("")
    def on_tanimotoBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('tanimoto_t', self.tanimotoBox.value())
        print "value changed"


    @pyqtSignature("")
    def on_clogpBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('ClogP_t', self.clogpBox.value())

    @pyqtSignature("")
    def on_molwtBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('MW_t', self.molwtBox.value())

    @pyqtSignature("")
    def on_rotbBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('RB_t', self.rotbBox.value())

    @pyqtSignature("")
    def on_hbaBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('HBA_t', self.hbaBox.value())

    @pyqtSignature("")
    def on_hbdBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('HBD_t', self.hbdBox.value())

    @pyqtSignature("")
    def on_defaultsButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.hbaBox.setValue(0)
        self.hbdBox.setValue(0)
        self.clogpBox.setValue(1)
        self.tanimotoBox.setValue(0.9)
        self.molwtBox.setValue(40)
        self.rotbBox.setValue(0)
        for field in (self.hbaBox, self.hbdBox, self.clogpBox, self.tanimotoBox, self.molwtBox, self.rotbBox):
            field.editingFinished.emit()

    #################################


    @pyqtSignature("")
    def on_actionAbout_activated(self):
        """
        Slot documentation goes here.
        """
        # TODO: on_actionAbout_activated
        #raise NotImplementedError
