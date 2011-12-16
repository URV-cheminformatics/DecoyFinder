#!/bin/sh

. ./debdist
. ./win32.sh

rm -r packages
mkdir packages

mv *.deb *_installer.exe *.bz2 packages/
