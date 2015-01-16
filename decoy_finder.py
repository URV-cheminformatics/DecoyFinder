#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       decoy_finder.py is part of Decoy Finder
#
#       Copyright 2011-2014 Adrià Cereto Massagué <adrian.cereto@urv.cat>
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
import os
if os.environ.has_key("_MEIPASS2"):
    #On Windows it's going to run,most probably, from a frozen pyinstaller package. When this is the case,
    #if there is an OpenBabel version installed on the machine which differs from the packaged one, bad things could happen.
    #So we just ignore any possible openBabel installation and point the environmental variables to the temporal
    #directory where everything is unpacked when DecoyFinder is run
    #However the following applies presumably on any platform when running from a pyinstaller package:
    os.environ['BABEL_DATADIR'] = os.environ["_MEIPASS2"]
    os.environ['BABEL_LIBDIR'] = os.environ["_MEIPASS2"]
    #%_MEIPASS2% is the directory where the package is decompressed and where all libraries and data are.
    os.environ['PATH'] =  os.environ['_MEIPASS2'] + ';' + os.environ['PATH']
    print 'BABEL_DATADIR set to ', os.environ['BABEL_DATADIR']

import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QTranslator, QLocale

from metadata import *

def main():
    """
    """
    from MainWindow import MainWindow

    translator = QTranslator() #Build the translator
    translator.load(":/locales/df_%s" % QLocale.system().name())
    qttranslator = QTranslator()#A translator for Qt standard strings
    qttranslator.load("qt_%s" % (QLocale.system().name()))
    App = QApplication(sys.argv) #Creating the app
    App.setOrganizationName(ORGNAME) #Setting organization and application's
    App.setApplicationName(NAME)#name. It's only useful for QSettings
    App.setApplicationVersion(VERSION)
    App.setOrganizationDomain(URL)
    App.installTranslator(translator)#Install translators into the application.
    App.installTranslator(qttranslator)
    mw = MainWindow(App) #Now it's time to instantiate the main window
    mw.show() #And show it
    sys.exit(App.exec_()) #When the app finishes, exit.

if __name__ == '__main__':
    main()
