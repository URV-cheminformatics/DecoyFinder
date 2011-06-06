#!/bin/sh
rcc -project | grep -v compile.sh | sed s/'<qresource>'/'<qresource prefix=\"icons\">'/| sed s/"\.\/"/"iconset\/"/ > ../icons.qrc
echo 'Written to ../icons.qrc'
