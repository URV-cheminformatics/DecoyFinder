#!/bin/sh
. ./common.sh
rm -r ${GENERIC}
mkdir ${GENERIC}
cp  ../*.py ../*.txt ../*.html ../icon.png ${GENERIC}/
