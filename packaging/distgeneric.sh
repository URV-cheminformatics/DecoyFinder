#!/bin/sh
. ./common.sh
rm -r ${GENERIC} ${GENERIC}.tar.bz2
mkdir ${GENERIC}
cp  ../*.py ../*.txt ../*.html ../icon.png ${GENERIC}/
apack ${GENERIC}.tar.bz2 ${GENERIC}
