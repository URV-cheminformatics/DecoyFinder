#!/bin/sh
. ./common.sh
OBDIR=/opt/openbabel-2.3.1
export BABEL_DATADIR=$OBDIR/share/openbabel/2.3.1
export BABEL_LIBDIR=$OBDIR/lib/openbabel/2.3.1
PYTHONPATH=$OBDIR/lib/python2.6/site-packages:$PYTHONPATH
python $PI -C $PIDIR/config-linux32.dat -F  DecoyFinder.spec
