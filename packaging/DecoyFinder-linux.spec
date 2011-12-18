#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os, shutil, platform
# Process the includes and excludes first

cwd = os.path.abspath(os.getcwd())

obdir = '/opt/openbabel-2.3.1/lib/openbabel/2.3.1'
datadir = '/opt/openbabel-2.3.1/share/openbabel/2.3.1'

data_files = [(file,os.path.join(datadir, file),'DATA') for file in os.listdir(datadir)]

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = []
dll_includes = []

for file in os.listdir(obdir):
    if os.path.splitext(file)[1].lower() == '.so':
        dll_includes.append((file, os.path.join(obdir, file),
                'BINARY'))
# Set up the more obscure PyInstaller runtime options

options = [('O', '', 'OPTION')]
options.append(('v', '', 'OPTION'))

# This is a place where the user custom code may go. You can do almost
# whatever you want, even modify the data_files, includes and friends
# here as long as they have the same variable name that the setup call
# below is expecting.

# No custom code added

# The setup for PyInstaller is different from py2exe. Here I am going to
# use some common spec file declarations

bindir = os.path.join(os.environ['HOME'] ,'winbin')

analysis = Analysis([os.path.abspath(os.path.join(bindir, 'pyinstaller-1.5.1-linux/support/_mountzlib.py')),
           os.path.abspath(os.path.join(bindir, 'pyinstaller-1.5.1-linux/support/useUnicode.py')),
           os.path.abspath(os.path.join(cwd,'../decoy_finder.py'))],
                    pathex=[],
                    hookspath=[],
                    excludes=excludes)

pyz = PYZ(analysis.pure, level=9)


executable = EXE( pyz,
                 analysis.scripts + includes + packages + options,
                 analysis.binaries - dll_excludes + dll_includes + data_files,
                 name=r"DecoyFinder_" + platform.architecture()[0],
                 debug=False,
                 console=False,
                 strip=False,
                 upx=True,
                 icon=os.path.abspath(os.path.join(cwd, '../icon.ico')),
                 version=None)

# This is a place where any post-compile code may go.
# You can add as much code as you want, which can be used, for example,
# to clean up your folders or to do some particular post-compilation
# actions.



# And we are done. That's a setup script :-D

