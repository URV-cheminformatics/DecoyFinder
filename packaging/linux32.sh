#!/bin/sh
. ./common.sh
OBDIR=/opt/openbabel-2.3.1
export BABEL_DATADIR=$OBDIR/share/openbabel/2.3.1
export BABEL_LIBDIR=$OBDIR/lib/openbabel/2.3.1
export PYTHONPATH=$OBDIR/lib/python2.6/site-packages:$PYTHONPATH
export LD_LIBRARY_PATH=$OBDIR/lib:$LD_LIBRARY_PATH
python $PI -C config-linux32.dat -F  DecoyFinder.spec
