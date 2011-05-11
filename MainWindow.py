#-*- coding:utf-8 -*-
#
#       MainWindow.py is part of Decoy Finder
#
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

import os, pybel,  itertools,  random, tempfile
try:
    from PySide.QtGui import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox
    from PySide.QtCore import QSettings, QThread, Signal, Qt, Slot
except:
    print "PySide not found! trying PyQt4"
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
    from PyQt4.QtGui import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox
    from PyQt4.QtCore import QSettings, QThread, Qt
    from PyQt4.QtCore import pyqtSignal as Signal
    from PyQt4.QtCore import pyqtSignature as Slot

from find_decoys import get_fileformat, find_decoys, get_zinc_slice
from Ui_MainWindow import Ui_MainWindow


class DecoyFinderThread(QThread):
    """
    """
    info = Signal(unicode) #needs to be defined OUTSIDE __init__
    progress = Signal(int)
    finished = Signal(tuple)
    error = Signal(unicode)

    def __init__(self, query_files, db_files, decoy_files,  parent = None):
        """
        """
        print "thread created"
        self.decoy_files = decoy_files
        self.query_files = query_files
        self.db_files = db_files
        self.settings = QSettings()
        super(DecoyFinderThread, self).__init__(parent)

    def run(self):
        """
        """
        self.info.emit(self.tr("Reading files..."))
        #result = ()
        limitreached = True
        try:
            self.filecount = 0
            for filecount, current_file in find_decoys(
                        query_files = self.query_files
                        ,db_files = self.db_files
                        ,outputfile =  self.settings.value('outputfile', os.getcwd())
                        ,HBA_t = int(self.settings.value('HBA_t', 0))
                        ,HBD_t = int(self.settings.value('HBD_t', 0))
                        ,ClogP_t = float(self.settings.value('ClogP_t', 1))
                        ,tanimoto_t = float(self.settings.value('tanimoto_t', 0.9))
                        ,MW_t = int(self.settings.value('MW_t',40))
                        ,RB_t = int(self.settings.value('RB_t',0))
                        ,limit = int(self.settings.value('decoy_limit',36))
                        ,tanimoto_d = float(self.settings.value('tanimoto_d', 0.9))
                        ,decoy_files = self.decoy_files
                        ):
                if type(filecount) != dict:
                    self.filecount = filecount
                    self.info.emit(self.tr("Reading %s") % current_file)
                    self.progress.emit(self.filecount)
                elif type(filecount) == dict:
                    #print "dict found"
                    outputfile = current_file[0]
                    limitreached = current_file[1]
                    result = (filecount,  outputfile,  limitreached)
                else:
                    self.error.emit(self.trUtf8('Unexpected error: %s; %s') % (filecount, current_file))
            self.progress.emit(self.filecount +1)
        except Exception, e:
            err = unicode(e)
            self.error.emit(self.trUtf8("Error: %s" % err))
        self.finished.emit(result)

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
        self.kdecoysFrame.setVisible(False)
        self.cacheCheckBox.setVisible(False)
        self.cacheCheckBox.setChecked(bool(int(self.settings.value('usecache',  False))))
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        ######Display current settings########
        self.hbaBox.setValue(int(self.settings.value('HBA_t', 0)))
        self.hbdBox.setValue(int(self.settings.value('HBD_t', 0)))
        self.clogpBox.setValue(float(self.settings.value('ClogP_t', 1)))
        self.tanimotoBox.setValue(float(self.settings.value('tanimoto_t', 0.9)))
        self.molwtBox.setValue(int(self.settings.value('MW_t',40)))
        self.rotbBox.setValue(int(self.settings.value('RB_t',0)))
        self.decoyLimitSpinBox.setValue(int(self.settings.value('decoy_limit',36)))
        self.dTanimotoBox.setValue(float(self.settings.value('tanimoto_d', 0.9)))
        self.cachDirectoryLineEdit.setText(self.settings.value('cachedir',tempfile.gettempdir()))
        self.outputDirectoryLineEdit.setText(self.settings.value('outputfile',os.path.join(os.getcwd(), 'found_decoys.sdf') ))
        ########################
        self.supported_files = self.tr('Molecule files') + ' ('
        for format in pybel.informats.iterkeys():
            self.supported_files += "*.%s " %format
            if os.name != 'nt':
                self.supported_files += "*.%s.gz " %format
        self.supported_files += ')'

    def _getListWidgetItemTextList(self, listWidget):
        """
        """
        itemlist = [str(listWidget.item(index).text()) for index in xrange(listWidget.count())]
        return itemlist

    def on_finder_finished(self, resulttuple):
        """
        """
        if not self.progressBar.maximum:
            self.progressBar.setMaximum(1)
        self.progressBar.setValue(self.progressBar.maximum)
        self.resultsTable.setSortingEnabled(False)
        self.tabWidget.setEnabled(True)
        #self.findDecoysButton.setEnabled(True)
        resultdict,  outfile,  limitreached = resulttuple
        if len(resultdict):
            ndecoys = 0
            self.tabWidget.setCurrentIndex(1)
            for ligand in resultdict.iterkeys():
                self.resultsTable.insertRow(0)
                self.resultsTable.setItem(0, 0,  QTableWidgetItem(ligand.title))
                self.resultsTable.setItem(0, 1,  QTableWidgetItem(str(resultdict[ligand])))
                self.resultsTable.setItem(0, 2,  QTableWidgetItem(outfile))
                ndecoys += resultdict[ligand]
            self.resultsTable.sortByColumn(1, Qt.DescendingOrder)
            self.resultsTable.resizeColumnToContents(0)
            self.resultsTable.resizeColumnToContents(2)
            if ndecoys and not limitreached:
                answer = QMessageBox.question(None,
                    self.trUtf8("Not enough decoys found"),
                    self.trUtf8("""Not enough decoys for each ligand were found. Please, try to loosen search constraints in the options tab.\n Found decoys have been added to known decoys list'"""),
                    QMessageBox.StandardButtons(\
                        QMessageBox.Abort | \
                        QMessageBox.Retry))
                if answer == QMessageBox.Retry:
                    self.tabWidget.setCurrentIndex(0)
                    self.decoyList.addItem(outfile)
                    self.kdecoysCheckBox.setChecked(True)
            else:
                self.on_error(self.tr('No decoys found. Try to set lower requirements in the options tab.'))
        else:
            self.on_error(self.tr('No active ligands found. Check your query files.'))
        self.statusbar.showMessage(self.tr("Done."))


    def on_error(self, error):
        """
        """
        #print error
        QMessageBox.critical(None,
            self.trUtf8("Error"),
            self.trUtf8(error),
            QMessageBox.StandardButtons(QMessageBox.Ok)
            )



    @Slot("")
    def on_addQueryButton_clicked(self):
        """
        Slot documentation goes here.
        """
        itemlist = self._getListWidgetItemTextList(self.queryList)
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter(self.supported_files)
        dialog.setDirectory(self.settings.value('lastdir', os.path.expanduser('~')))
        #dialog.setOption(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            filelist = dialog.selectedFiles()
            self.settings.setValue('lastdir', os.path.dirname(unicode(filelist[0])))
            for file in filelist:
                if file not in itemlist:
                    self.queryList.addItem(file)

    @Slot("")
    def on_addDecoysButton_clicked(self):
        """
        Slot documentation goes here.
        """
        itemlist = self._getListWidgetItemTextList(self.decoyList)
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter(self.supported_files)
        dialog.setDirectory(self.settings.value('lastdir', os.path.expanduser('~')))
        if dialog.exec_():
            filelist = dialog.selectedFiles()
            self.settings.setValue('lastdir', os.path.dirname(unicode(filelist[0])))
            for file in filelist:
                if file not in itemlist:
                    self.decoyList.addItem(file)

    @Slot("")
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
            dialog.setDirectory(self.settings.value('lastdir',os.path.expanduser('~')))
            #dialog.setOption(QFileDialog.DontUseNativeDialog)
            if dialog.exec_():
                dblist = dialog.selectedFiles()
                self.settings.setValue('lastdir', os.path.dirname(unicode(dblist[0])))
                for file in dblist:
                    if file not in itemlist:
                        self.dbListWidget.addItem(file)
        else:
            text = self.dbComboBox.currentText()
            if text.split()[0] == 'ZINC':
                if text not in itemlist and 'ZINC all' not in itemlist:
                    self.dbListWidget.addItem(self.dbComboBox.currentText())

    @Slot("")
    def on_outputDirectoryLineEdit_editingFinished(self):
        """
        Slot documentation goes here.
        """
        dir = self.outputDirectoryLineEdit.text()
        self.settings.setValue('outputfile', dir)

    @Slot("")
    def on_outDirButton_clicked(self):
        """
        Slot documentation goes here.
        """
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setDirectory(self.settings.value('lastdir',os.path.expanduser('~')))
        #dialog.setOption(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            file = dialog.selectedFiles()[0]
            self.outputDirectoryLineEdit.setText(file)
            self.settings.setValue('outputfile', file)
            self.settings.setValue('lastdir', os.path.dirname(unicode(file)))

    @Slot("")
    def on_findDecoysButton_clicked(self):
        """
        Slot documentation goes here.
        """
        #self.findDecoysButton.setEnabled(False)
        self.tabWidget.setEnabled(False)
        #print self.settings.value('outdir')
        query_files = self._getListWidgetItemTextList(self.queryList)

        decoy_files = self._getListWidgetItemTextList(self.decoyList)

        db_items = self._getListWidgetItemTextList(self.dbListWidget)
        db_files = []
        zinc_iter = iter('')
        total_files = 0
        self.progressBar.maximum = 0
        for item in db_items:
            if item.split()[0] == 'ZINC':
                #TODO download from ZINC
                #print item.split()[1]
                usecache = self.cacheCheckBox.isChecked()
                zinc_file_gen = get_zinc_slice(item.split()[1], self.settings.value('cachedir',tempfile.gettempdir()),  usecache)
                zfilecount = zinc_file_gen.next()
                if zfilecount:
                    total_files += zfilecount
                    zinc_iter = itertools.chain(zinc_iter, zinc_file_gen)
                else:
                    self.on_error(filecount)

            elif os.path.isfile(item):
                db_files.append(str(item))
        total_files += len(db_files)
        random.shuffle(db_files)
        db_files =itertools.chain(db_files,  zinc_iter)
        if [] == query_files  or not total_files:
            self.on_error(self.tr('You must select at least one file containing query molecules, and at least one molecule library file or source'))
            #self.findDecoysButton.setEnabled(True)
            self.tabWidget.setEnabled(True)
        else:
            if total_files == 1:
                self.progressBar.setMaximum(0)
                self.progressBar.setValue(0)
            else:
                self.progressBar.setMaximum(total_files)
            self.finder = DecoyFinderThread(query_files, db_files, decoy_files)
            self.finder.info.connect(self.statusbar.showMessage)
            self.finder.progress.connect(self.progressBar.setValue)
            self.finder.finished.connect(self.on_finder_finished)
            self.finder.error.connect(self.on_error)
            print "starting thread"
            self.finder.start()
            print "started"

    @Slot("")
    def on_clearButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.progressBar.setMaximum(1)
        while  self.resultsTable.rowCount():
            self.resultsTable.removeRow(0)

    @Slot(int)
    def on_dbComboBox_currentIndexChanged(self,  index):
        """
        Slot documentation goes here.
        """
        self.cacheCheckBox.setVisible(bool(index))

    ############ Options tab  #############
    @Slot("")
    def on_tanimotoBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('tanimoto_t', self.tanimotoBox.value())
        #print "value changed"


    @Slot("")
    def on_clogpBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('ClogP_t', self.clogpBox.value())

    @Slot("")
    def on_molwtBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('MW_t', self.molwtBox.value())

    @Slot("")
    def on_rotbBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('RB_t', self.rotbBox.value())

    @Slot("")
    def on_hbaBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('HBA_t', self.hbaBox.value())

    @Slot("")
    def on_hbdBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('HBD_t', self.hbdBox.value())

    @Slot("")
    def on_decoyLimitSpinBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('decoy_limit', self.decoyLimitSpinBox.value())

    @Slot("")
    def on_dTanimotoBox_editingFinished(self):
        """
        Slot documentation goes here.
        """
        self.settings.setValue('tanimoto_d', self.dTanimotoBox.value())

    @Slot("")
    def on_cachDirectoryLineEdit_editingFinished(self):
        """
        Slot documentation goes here.
        """
        dir = self.cachDirectoryLineEdit.text()
        if os.path.isdir(dir):
            self.settings.setValue('cachedir', dir)

    @Slot("")
    def on_cacheButton_clicked(self):
        """
        Slot documentation goes here.
        """
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setDirectory(self.settings.value('cachedir',os.path.expanduser('~')))
        if dialog.exec_():
            dir = dialog.selectedFiles()[0]
            if os.path.isdir(dir):
                self.cachDirectoryLineEdit.setText(dir)
                self.cachDirectoryLineEdit.editingFinished.emit()
            else:
                self.on_error('Could no acces selected directory.\nPlease, choose a different one')


    @Slot("")
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
        self.decoyLimitSpinBox.setValue(36)
        self.dTanimotoBox.setValue(0.9)
        self.cachDirectoryLineEdit.setText(tempfile.gettempdir())
        for field in (self.hbaBox, self.hbdBox, self.clogpBox, self.tanimotoBox, self.molwtBox, self.rotbBox,  self.decoyLimitSpinBox, self.dTanimotoBox, self.cachDirectoryLineEdit):
            field.editingFinished.emit()

    #################################


    @Slot("")
    def on_actionAbout_activated(self):
        """
        Slot documentation goes here.
        """
        print "Not implemented yet"
        # TODO: on_actionAbout_activated
        #raise NotImplementedError
