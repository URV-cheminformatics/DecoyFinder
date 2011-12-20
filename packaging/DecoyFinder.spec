#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os, shutil, platform
# Process the includes and excludes first

NAME=r"DecoyFinder"
if os.name == 'nt':
    NAME += '.exe'
else:
    NAME +="_" + "_".join([platform.system().lower(), platform.architecture()[0]])

cwd = os.path.abspath(os.getcwd())

datadir = os.environ['BABEL_DATADIR']

data_files = []

if os.name == 'nt':
    obdir = os.path.abspath(os.path.join(datadir , '..'))
    data_files = [(file,os.path.join(obdir, file),'DATA') for file in os.listdir(obdir) if os.path.splitext(file)[1].lower() == '.obf']
else:
    obdir = os.environ['BABEL_LIBDIR'] #'/opt/openbabel-2.3.1/lib/openbabel/2.3.1'

for file in os.listdir(datadir):
    data_files.append((file, os.path.join(os.environ['BABEL_DATADIR'], file),
             'DATA'))

data_files.append(('qt.conf', os.path.join(cwd, 'qt.conf'),
             'DATA'))

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = []
dll_includes = []
if os.name == 'nt':
    dll_includes = [('QtCore4.dll', 'C:\\Python27\\Lib\\site-packages\\PySide\\QtCore4.dll',
                    'BINARY'), ('QtGui4.dll', 'C:\\Python27\\Lib\\site-packages\\PySide\\QtGui4.dll',
                    'BINARY')]


for file in os.listdir(obdir):
    if os.path.splitext(file)[1].lower() in ('.dll', '.so'):
        if 'csharp' in file.lower() or 'dotnet'in file.lower() or 'java' in file.lower():
            dll_excludes.append((file, os.path.join(obdir, file),
                'BINARY'))
        else:
            dll_includes.append((file, os.path.join(obdir, file),
                'BINARY'))
# Set up the more obscure PyInstaller runtime options

options = [('O', '', 'OPTION')]
#options.append(('v', '', 'OPTION'))

# This is a place where the user custom code may go. You can do almost
# whatever you want, even modify the data_files, includes and friends
# here as long as they have the same variable name that the setup call
# below is expecting.

# No custom code added

# The setup for PyInstaller is different from py2exe. Here I am going to
# use some common spec file declarations
if os.name == 'nt':
    homepath = os.path.join('Z:/home', os.environ['USER'])
else:
    homepath = os.environ['HOME']

pidir = os.path.join(homepath ,'winbin', 'pyinstaller-1.5.1')

print os.path.abspath(os.path.join(pidir, 'support','_mountzlib.py'))

analysis = Analysis([os.path.abspath(os.path.join(pidir, 'support','_mountzlib.py')),
           os.path.abspath(os.path.join(pidir, 'support','useUnicode.py')),
           os.path.abspath(os.path.join(cwd,'..','decoy_finder.py'))],
                    pathex=[],
                    hookspath=[],
                    excludes=excludes)

pyz = PYZ(analysis.pure, level=9)

executable = EXE( pyz,
                 analysis.scripts + includes + packages + options,
                 analysis.binaries - dll_excludes + dll_includes + data_files,
                 name=NAME,
                 debug=False,
                 console=False,
                 strip= os.name != 'nt',
                 upx=True,
                 icon=os.path.abspath(os.path.join(cwd, '../icon.ico')),
                 version=None)

# This is a place where any post-compile code may go.
# You can add as much code as you want, which can be used, for example,
# to clean up your folders or to do some particular post-compilation
# actions.

vcredist = os.path.join(obdir, 'vcredist_x86.exe')
if os.path.isfile(vcredist):
    shutil.copy(vcredist,  cwd)

# And we are done. That's a setup script :-D

