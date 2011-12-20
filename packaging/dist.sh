#!/bin/sh

. ./debdist

current_branch=$(git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3)
if [ "$current_branch" == "master" ]; then
	new_branch=pyqt
else
	new_branch="$current_branch"-pyqt
fi
git checkout $new_branch
git pull
git merge $current_branch
schroot -c lenny ./linux32.sh
git checkout $current_branch

. ./win32.sh



echo $current_branch
echo $new_branch

rm -r packages
mkdir packages


mv *.deb *_installer.exe *.bz2 DecoyFinder_*bit packages/
