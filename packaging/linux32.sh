#!/bin/sh
. ./common.sh
export BABEL_DATADIR=/opt/openbabel-2.3.1/share/openbabel/2.3.1
export BABEL_LIBDIR=/opt/openbabel-2.3.1/lib/openbabel/2.3.1
python $PI -C $PIDIR/config-linux32.dat -F  DecoyFinder.spec
