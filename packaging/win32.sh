#!/bin/sh
exit
. ./common.sh
export WINEPREFIX=$HOME/.wine
rm -r DecoyFinder*.exe warnDecoyFinder.txt build
wine c:/Python27/python $PI -w -X -n DecoyFinder -F  DecoyFinder.spec
makensis installer.nsi
