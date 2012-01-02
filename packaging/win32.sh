#!/bin/sh
. ./common.sh
export WINEPREFIX=$HOME/.wine
rm -r DecoyFinder*.exe warnDecoyFinder.txt build
wine c:/Python27/python $PI -w -X -C config-win32.dat  -F  DecoyFinder.spec
makensis installer.nsi
