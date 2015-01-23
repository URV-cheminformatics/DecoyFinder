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
import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QApplication, QIcon
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
    ###Load icons, if Qt is new enough###
    if 'themeName' in dir(QIcon):
        print("Icon theme support enabled")
        if not QIcon.themeName():
            print("No icon theme set, using default: Tango")
            import icons_rc
            QIcon.setThemeName('iconset')
    else:
        print 'Your version of Qt is way too old. Consider upgrading it to at least 4.6!'
        print 'Icons will not be displayed because of that'
    ############
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
