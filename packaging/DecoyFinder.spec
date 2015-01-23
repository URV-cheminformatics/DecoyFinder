#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os, shutil, platform
# Process the includes and excludes first

NAME=r"DecoyFinder"
NAME2 = NAME + "_" + "_".join([platform.system().lower(), platform.architecture()[0]])
if os.name == 'nt':
    NAME += '.exe'
else:
    NAME = NAME2

cwd = os.path.abspath(os.getcwd())

try:
    datadir = os.environ['BABEL_DATADIR']
except KeyError:
    datadir = "/usr/share/openbabel/2.3.2/"

try:
    libdir = os.environ['BABEL_LIBDIR']
except KeyError:
    if os.name == "nt":
        for p in os.environ["PATH"].split(os.pathsep):
            if os.path.isfile(os.path.join(p, "obabel.exe")):
                libdir = p
    else:
        libdir = "/usr/lib/openbabel/2.3.2/"

data_files = []

if os.name == 'nt':
    data_files = [(file,os.path.join(libdir, file),'DATA') for file in os.listdir(libdir) if os.path.splitext(file)[1].lower() == '.obf']

for file in os.listdir(datadir):
    data_files.append((file, os.path.join(datadir, file),
             'DATA'))

data_files.append(('qt.conf', os.path.join(cwd, 'qt.conf'),
             'DATA'))
data_files.append(('LICENCE.html', os.path.join(cwd, '..',  'LICENCE.html'),
             'DATA'))
data_files.append(('RELEASE_NOTES.txt', os.path.join(cwd, '..',  'RELEASE_NOTES.txt'),
             'DATA'))

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter', "PySide"]
dll_excludes = []
dll_includes = []

for file in os.listdir(libdir):
    if os.path.splitext(file)[1].lower() in ('.dll', '.so'):
        if 'csharp' in file.lower() or 'dotnet'in file.lower() or 'java' in file.lower():
            dll_excludes.append((file, os.path.join(libdir, file),
                'BINARY'))
        else:
            dll_includes.append((file, os.path.join(libdir, file),
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

analysis = Analysis([os.path.abspath(os.path.join(cwd,'..','decoy_finder.py'))],
                    pathex=[],
                    hookspath=[],
                    excludes=excludes,
                    runtime_hooks=["rthooks.py"])

pyz = PYZ(analysis.pure, level=9)

executable = EXE( pyz,
                 analysis.scripts + includes  + options,
                 analysis.binaries - dll_excludes + dll_includes + data_files,
                 name=NAME,
                 debug=False,
                 console=False,
                 strip= os.name != 'nt',
                 upx=True,
                 icon=os.path.abspath(os.path.join(cwd, '../icon.ico')),
                 #manifest="manifest",
                 version=None)
executable_dir = EXE( pyz,
                 analysis.scripts + includes  + options,
                 name=NAME,
                 exclude_binaries=True,
                 debug=False,
                 console=False,
                 strip= os.name != 'nt',
                 upx=True,
                 icon=os.path.abspath(os.path.join(cwd, '../icon.ico')),
                 #manifest="manifest",
                 version=None)

coll = COLLECT(executable_dir,
               analysis.binaries - dll_excludes + dll_includes + data_files,
               analysis.zipfiles,
               analysis.datas,
               strip=None,
               upx=True,
               name=NAME2 + "_dir")
# This is a place where any post-compile code may go.
# You can add as much code as you want, which can be used, for example,
# to clean up your folders or to do some particular post-compilation
# actions.

# And we are done. That's a setup script :-D

