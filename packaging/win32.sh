#!/bin/sh
. ./common.sh
export WINEPREFIX=$HOME/.wine
export PI=$HOME/winbin/pyinstaller-1.5.1/pyinstaller.py
rm -r DecoyFinder*.exe warnDecoyFinder.txt build
wine c:/Python27/python $PI -w -i ../icon.ico -X -n DecoyFinder -F  DecoyFinder.spec
makensis installer.nsi
