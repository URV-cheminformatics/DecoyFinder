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
Module implementing DecoyFinder's main window.
"""

import os, itertools, random, tempfile, time,  webbrowser

from PySide.QtGui import QMainWindow, QFileDialog, QTableWidgetItem, QMessageBox, QIcon, QApplication
from PySide.QtCore import QSettings, QThread, Signal, Qt, Slot

from find_decoys import *
from Ui_MainWindow import Ui_MainWindow
from AboutDiag import AboutDialog

class DecoyFinderThread(QThread):
    """
    """
    info = Signal(unicode) #needs to be defined OUTSIDE __init__
    progress = Signal(int)
    finished = Signal(tuple)
    error = Signal(unicode)
    progLimit = Signal(int)

    def __init__(self, query_files, db_files, decoy_files, stopfile, unique = False):
        self.decoy_files = decoy_files
        self.query_files = query_files
        self.db_files = db_files
        self.unique = unique
        self.stopfile = stopfile
        self.nactive_ligands = 0
        self.ndecoys = 0
        self.settings = QSettings()
        super(DecoyFinderThread, self).__init__(None)

    def run(self):
        self.info.emit(self.tr("Reading files..."))
        result = None
        minreached = True
        try:
            self.filecount = 0
            self.currentfile = ''
            mind = int(self.settings.value('decoy_min', 36))
            outputfile = None
            for info in find_decoys(
                        query_files = self.query_files
                        ,db_files = self.db_files
                        ,outputfile =  str(self.settings.value('outputfile', 'found'))
                        ,HBA_t = int(self.settings.value('HBA_t', HBA_t))
                        ,HBD_t = int(self.settings.value('HBD_t', HBD_t))
                        ,ClogP_t = float(self.settings.value('ClogP_t', ClogP_t))
                        ,tanimoto_t = float(self.settings.value('tanimoto_t', tanimoto_t))
                        ,MW_t = int(self.settings.value('MW_t',MW_t))
                        ,RB_t = int(self.settings.value('RB_t',RB_t))
                        ,mind = int(self.settings.value('decoy_min',mind))
                        ,maxd = int(self.settings.value('decoy_max',maxd))
                        ,tanimoto_d = float(self.settings.value('tanimoto_d', tanimoto_d))
                        ,decoy_files = self.decoy_files
                        ,stopfile = self.stopfile
                        ,unique = self.unique
                        ):
                if info[0] in ('file',  'ndecoys'):
                    if not mind:
                        if info[0] == 'file':
                            self.filecount = info[1]
                            if self.currentfile != info[2]:
                                self.currentfile = info[2]
                                self.info.emit(self.trUtf8("Reading %s, found %s decoys") % (self.currentfile,  self.ndecoys))
                            if self.filecount:
                                self.progress.emit(self.filecount)
                        if info[0] == 'ndecoys':
                            self.ndecoys = info[1]
                            self.info.emit(self.trUtf8("Reading %s, found %s decoys" % (self.currentfile,  self.ndecoys)))
                    else:
                        if info[0] == 'ndecoys':
                            if info[1] > self.total_min:
                                self.progLimit.emit(info[1])
                            self.progress.emit(info[1])
                            self.info.emit(self.trUtf8("%s of %s decoy sets completed") % (info[2],  self.nactive_ligands))
                elif info[0] == 'result':
                    outputfile = info[2][0]
                    minreached =  info[2][1]
                    result = ( info[1],outputfile, minreached)
                elif info[0] == 'total_min':
                    self.total_min = info[1]
                    self.progLimit.emit(self.total_min)
                    self.nactive_ligands = info[2]
                else:
                    print("Something very wrong")

            if self.filecount:
                self.progress.emit(self.filecount +1)
        except Exception, e:
            try:
                err = unicode(e)
            except:
                try:
                    err = str(e)
                except:
                    err =e
            self.error.emit(self.trUtf8("Error: %s" % err))
        if outputfile:
            self.info.emit("Decoys saved to " + outputfile)
        else:
            self.info.emit("No decoys were saved")
        if result:
            self.finished.emit(result)
        else:
            self.error.emit('Search was interrupted by an error or failure')

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app, parent = None):
        """
        Constructor
        """
        self.App = app
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.settings = QSettings()
        self.setWindowFlags (Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("%s %s" % (self.App.applicationName(),  self.App.applicationVersion()))
        self.kdecoysFrame.setVisible(False)
        self.cacheCheckBox.setChecked('false' != self.settings.value('usecache',  True))
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        for subset in ZINC_subsets:
            self.zsubComboBox.addItem(subset)
        self.zsubComboBox.setCurrentIndex(self.zsubComboBox.findText('everything'))
        ###Load icons, if Qt is new enough###
        if 'themeName' in dir(QIcon):
            if not QIcon.themeName():
                print("No icon theme set, using default: Tango")
                import icons_rc
                QIcon.setThemeName('iconset')
            addIcon = QIcon.fromTheme('list-add', QIcon())
            clearIcon = QIcon.fromTheme('edit-clear', QIcon())
            outIcon = QIcon.fromTheme('document-save-as', QIcon())
            finddIcon = QIcon.fromTheme('media-playback-start', QIcon())
            stopIcon = QIcon.fromTheme('process-stop', QIcon())
            cachedirIcon = QIcon.fromTheme('folder-open', QIcon())
            defaultsIcon = QIcon.fromTheme('view-refresh', QIcon())
            helpIcon = QIcon.fromTheme('internet-web-browser', QIcon())
            aboutIcon = QIcon.fromTheme('dialog-information', QIcon())

            self.addQueryButton.setIcon(addIcon)
            self.addDecoysButton.setIcon(addIcon)
            self.addDButton.setIcon(addIcon)

            self.clearActives.setIcon(clearIcon)
            self.clearDecoys.setIcon(clearIcon)
            self.clearDB.setIcon(clearIcon)
            self.clearButton.setIcon(clearIcon)

            self.outDirButton.setIcon(outIcon)
            self.findDecoysButton.setIcon(finddIcon)
            self.stopButton.setIcon(stopIcon)

            self.cacheButton.setIcon(cachedirIcon)
            self.defaultsButton.setIcon(defaultsIcon)

            self.actionAbout.setIcon(aboutIcon)
            self.actionHelp.setIcon(helpIcon)
        else:
            print 'Your version of Qt is way too old. Consider upgrading it to at least 4.6!'
            print 'Icons will not be displayed because of that'
        ############

        self.toolBar.addAction(self.actionAbout)
        self.toolBar.addAction(self.actionHelp)

        ######Display current settings########
        self.hbaBox.setValue(int(self.settings.value('HBA_t', HBA_t)))
        self.hbdBox.setValue(int(self.settings.value('HBD_t', HBD_t)))
        self.clogpBox.setValue(float(self.settings.value('ClogP_t', ClogP_t)))
        self.tanimotoBox.setValue(float(self.settings.value('tanimoto_t', tanimoto_t)))
        self.molwtBox.setValue(int(self.settings.value('MW_t',MW_t)))
        self.rotbBox.setValue(int(self.settings.value('RB_t',RB_t)))
        self.decoyMinSpinBox.setValue(int(self.settings.value('decoy_min',mind)))
        self.decoyMaxSpinBox.setValue(int(self.settings.value('decoy_max',maxd)))
        self.dTanimotoBox.setValue(float(self.settings.value('tanimoto_d', tanimoto_d)))
        self.uniqueCheckBox.setChecked('false' != self.settings.value('unique',  True))
        self.cachDirectoryLineEdit.setText(self.settings.value('cachedir',tempfile.gettempdir()))
        self.outputDirectoryLineEdit.setText(checkoutputfile(self.settings.value('outputfile',os.path.join(os.path.expanduser('~'), 'found_decoys.sdf'))))
        ########################
        self.supported_files = self.tr('OpenBabel accepted formats') + ' (' + informats + ')'
        ########################
        self.stopfile = '' #File to stop iteration

    def _getListWidgetItemTextList(self, listWidget):
        itemlist = [str(listWidget.item(index).text()) for index in xrange(listWidget.count())]
        return itemlist

    def on_finder_finished(self, resulttuple):
        self.resultsTable.setSortingEnabled(False)
        self.tabWidget.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.findDecoysButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        resultdict, outputfile,  minreached = resulttuple
        if len(resultdict):
            self.clearResultsTable()
            ndecoys = 0 #Possible comportament inconsistent -> poc prioritari
            self.tabWidget.setCurrentIndex(1)
            self.informationSavedToLineEdit.setText('%s_log.csv' % outputfile)
            for ligand in resultdict:
                self.resultsTable.insertRow(0)
                self.resultsTable.setItem(0, 0,  QTableWidgetItem(ligand.title))
                self.resultsTable.setItem(0, 1,  QTableWidgetItem(str(resultdict[ligand])))
                self.resultsTable.setItem(0, 2,  QTableWidgetItem(str(ligand.hba)))
                self.resultsTable.setItem(0, 3,  QTableWidgetItem(str(ligand.hbd)))
                self.resultsTable.setItem(0, 4,  QTableWidgetItem(str(ligand.clogp)))
                self.resultsTable.setItem(0, 5,  QTableWidgetItem(str(ligand.mw)))
                self.resultsTable.setItem(0, 6,  QTableWidgetItem(str(ligand.rot)))
                ndecoys += resultdict[ligand]
            self.resultsTable.sortByColumn(1, Qt.DescendingOrder)
            self.resultsTable.resizeColumnToContents(0)
            self.resultsTable.resizeColumnToContents(2)
            if not minreached:
                if ndecoys:
                    answer = QMessageBox.question(None,
                        self.trUtf8("Not enough decoys found"),
                        self.trUtf8(""" Not enough decoys for each active ligand have been found. Please, try either to loosen the search constraints at the options tab or to use new decoy sources.\n Found decoys have been added to known decoys list"""),
                        QMessageBox.StandardButtons(\
                            QMessageBox.Abort | \
                            QMessageBox.Retry))
                    if answer == QMessageBox.Retry:
                        self.tabWidget.setCurrentIndex(0)
                        self.decoyList.addItem(outputfile)
                        self.kdecoysCheckBox.setChecked(True)
                else:
                    self.on_error(self.tr('No decoys found. Try either to set lower requirements in the options tab or a different decoy source.'))
        else:
            self.on_error(self.tr('No active ligands found. Check your query files.'))
        self.statusbar.showMessage(self.tr("Done."))


    def on_error(self, error):
        """
        Display an error dialogue with the error
        """
        self.tabWidget.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.findDecoysButton.setEnabled(True)
        print(error)
        QMessageBox.critical(None,
            self.trUtf8("Error"),
            self.trUtf8(str(error)),
            QMessageBox.StandardButtons(QMessageBox.Ok)
            )

    def clearResultsTable(self):
        while  self.resultsTable.rowCount():
            self.resultsTable.removeRow(0)

    @Slot("")
    def on_addQueryButton_clicked(self):
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
        itemlist = self._getListWidgetItemTextList(self.dbListWidget)
        if self.dbComboBox.currentIndex() == 0:
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
        dir = self.outputDirectoryLineEdit.text()
        self.settings.setValue('outputfile', dir)

    @Slot("")
    def on_outDirButton_clicked(self):
        dialog =  QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setDirectory(self.settings.value('lastdir',os.path.expanduser('~')))
        #dialog.setOption(QFileDialog.DontUseNativeDialog)
        if dialog.exec_():
            file = checkoutputfile(dialog.selectedFiles()[0])
            self.outputDirectoryLineEdit.setText(file)
            self.settings.setValue('outputfile', file)
            self.settings.setValue('lastdir', os.path.dirname(unicode(file)))

    @Slot("")
    def on_findDecoysButton_clicked(self):
        self.tabWidget.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.findDecoysButton.setEnabled(False)
        query_files = self._getListWidgetItemTextList(self.queryList)

        decoy_files = self._getListWidgetItemTextList(self.decoyList)

        db_items = self._getListWidgetItemTextList(self.dbListWidget)
        db_files = []
        zinc_iter = iter('')
        total_files = 0
        self.progressBar.maximum = 0
        for item in db_items:
            if item.split()[0] == 'ZINC':
                usecache = self.cacheCheckBox.isChecked()
                zinc_file_gen = get_zinc_slice(item.split()[1], ZINC_subsets[self.zsubComboBox.currentText()], self.settings.value('cachedir',tempfile.gettempdir()),  usecache)
                try:
                    zfilecount = zinc_file_gen.next()
                    if zfilecount:
                        total_files += zfilecount
                        zinc_iter = itertools.chain(zinc_iter, zinc_file_gen)
                    else:
                        raise
                except Exception, e:
                    self.on_error(e)

            elif os.path.isfile(item):
                db_files.append(str(item))
        total_files += len(db_files)
        random.shuffle(db_files)
        db_files =itertools.chain(db_files,  zinc_iter)
        if [] == query_files  or not total_files:
            self.on_error(self.tr('You must select at least one file containing query molecules, and at least one molecule library file or source'))
            self.tabWidget.setEnabled(True)
            self.clearButton.setEnabled(True)
            self.findDecoysButton.setEnabled(True)
        else:
            self.progressBar.setMaximum(0)
            self.progressBar.setValue(0)
            if not int(self.settings.value('decoy_min',  36)):
                if total_files > 1:
                    self.progressBar.setMaximum(total_files)
            rsg = tempfile._RandomNameSequence()
            self.stopfile = os.path.join(tempfile.gettempdir(),  rsg.next() + rsg.next())
            self.finder = DecoyFinderThread(query_files, db_files, decoy_files,  self.stopfile, unique = self.uniqueCheckBox.isChecked())
            self.finder.info.connect(self.statusbar.showMessage)
            self.finder.progress.connect(self.progressBar.setValue)
            self.finder.finished.connect(self.on_finder_finished)
            self.finder.error.connect(self.on_error)
            self.finder.progLimit.connect(self.progressBar.setMaximum)
            if int(self.settings.value('decoy_min',  36)):
                self.progressBar.setFormat('%v of %m decoys found')
            else:
                self.progressBar.setFormat('%v of %m files read')
            print("starting thread")
            self.finder.start()
            self.stopButton.setEnabled(True)
            print("started")

    @Slot("")
    def on_stopButton_clicked(self):
        if self.stopfile:
            self.stopButton.setEnabled(False)
            stopfile = open(self.stopfile,  'wb')
            stopfile.close()
            while os.path.isfile(self.stopfile):
                time.sleep(0.5) #Wait until the finder thread stops
            self.stopfile = ''

    @Slot("")
    def on_clearButton_clicked(self):
        self.progressBar.setMaximum(1)
        self.clearResultsTable()

    @Slot(int)
    def on_dbComboBox_currentIndexChanged(self,  index):
        for widget in (self.cacheCheckBox, self.zsubComboBox, self.zinclabel):
            widget.setEnabled(bool(index))

    @Slot(int)
    def on_cacheCheckBox_stateChanged(self,  index):
        self.settings.setValue('usecache',  bool(index))

    ############ Options tab  #############

    @Slot(int)
    def on_uniqueCheckBox_stateChanged(self,  index):
        self.settings.setValue('unique',  bool(index))

    @Slot("")
    def on_tanimotoBox_editingFinished(self):
        self.settings.setValue('tanimoto_t', self.tanimotoBox.value())


    @Slot("")
    def on_clogpBox_editingFinished(self):
        self.settings.setValue('ClogP_t', self.clogpBox.value())

    @Slot("")
    def on_molwtBox_editingFinished(self):
        self.settings.setValue('MW_t', self.molwtBox.value())

    @Slot("")
    def on_rotbBox_editingFinished(self):
        self.settings.setValue('RB_t', self.rotbBox.value())

    @Slot("")
    def on_hbaBox_editingFinished(self):
        self.settings.setValue('HBA_t', self.hbaBox.value())

    @Slot("")
    def on_hbdBox_editingFinished(self):
        self.settings.setValue('HBD_t', self.hbdBox.value())

    @Slot("")
    def on_decoyMinSpinBox_editingFinished(self):
        value = self.decoyMinSpinBox.value()
        self.settings.setValue('decoy_min', value)
        if self.decoyMaxSpinBox.value() and value > self.decoyMaxSpinBox.value():
            self.decoyMaxSpinBox.setValue(value)
            self.decoyMaxSpinBox.editingFinished.emit()

    @Slot("")
    def on_decoyMaxSpinBox_editingFinished(self):
        value = self.decoyMaxSpinBox.value()
        self.settings.setValue('decoy_max', value)
        if value  and value < self.decoyMinSpinBox.value():
            self.decoyMinSpinBox.setValue(value)
            self.decoyMinSpinBox.editingFinished.emit()


    @Slot("")
    def on_dTanimotoBox_editingFinished(self):
        self.settings.setValue('tanimoto_d', self.dTanimotoBox.value())

    @Slot("")
    def on_cachDirectoryLineEdit_editingFinished(self):
        dir = self.cachDirectoryLineEdit.text()
        if os.path.isdir(dir):
            self.settings.setValue('cachedir', dir)

    @Slot("")
    def on_cacheButton_clicked(self):
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
        self.uniqueCheckBox.setChecked(True)
        self.hbaBox.setValue(HBA_t)
        self.hbdBox.setValue(HBD_t)
        self.clogpBox.setValue(int(ClogP_t))
        self.tanimotoBox.setValue(float(tanimoto_t))
        self.molwtBox.setValue(MW_t)
        self.rotbBox.setValue(RB_t)
        self.decoyMinSpinBox.setValue(36)
        self.decoyMaxSpinBox.setValue(36)
        self.dTanimotoBox.setValue(float(tanimoto_d))
        self.cachDirectoryLineEdit.setText(tempfile.gettempdir())
        for field in (self.hbaBox, self.hbdBox, self.clogpBox, self.tanimotoBox, self.molwtBox, self.rotbBox,  self.decoyMinSpinBox, self.decoyMaxSpinBox, self.dTanimotoBox, self.cachDirectoryLineEdit):
            field.editingFinished.emit()

    #################################


    @Slot("")
    def on_actionAbout_activated(self):
        aboutdiag = AboutDialog()
        aboutdiag.setWindowTitle('About '+self.App.applicationName())
        fixedinfo = aboutdiag.infolabel.text().replace('URL',  self.App.organizationDomain())
        aboutdiag.infolabel.setText(fixedinfo)
        aboutdiag.nameLabel.setText(self.App.applicationName())
        aboutdiag.versionlabel.setText(self.App.applicationVersion())
        aboutdiag.exec_()

    @Slot("")
    def on_actionHelp_activated(self):
        webbrowser.open_new_tab("http://" + self.App.organizationDomain())
