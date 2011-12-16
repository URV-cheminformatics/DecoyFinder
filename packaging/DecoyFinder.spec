#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os, shutil
# Process the includes and excludes first

data_files = [('formats_xml.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_xml.obf',
              'DATA'), ('plugin_fingerprints.obf', os.environ['BABEL_DATADIR'] + '\\..\\plugin_fingerprints.obf',
              'DATA'), ('formats_cairo.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_cairo.obf',
              'DATA'), ('formats_misc.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_misc.obf',
              'DATA'), ('formats_utility.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_utility.obf',
              'DATA'), ('plugin_charges.obf', os.environ['BABEL_DATADIR'] + '\\..\\plugin_charges.obf',
              'DATA'), ('plugin_descriptors.obf', os.environ['BABEL_DATADIR'] + '\\..\\plugin_descriptors.obf',
              'DATA'), ('plugin_ops.obf', os.environ['BABEL_DATADIR'] + '\\..\\plugin_ops.obf',
              'DATA'), ('formats_compchem.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_compchem.obf',
              'DATA'), ('plugin_forcefields.obf', os.environ['BABEL_DATADIR'] + '\\..\\plugin_forcefields.obf',
              'DATA'), ('formats_common.obf', os.environ['BABEL_DATADIR'] + '\\..\\formats_common.obf',
              'DATA')]

includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter']
packages = []
dll_excludes = []
dll_includes = [('QtCore4.dll', 'C:\\Python27\\Lib\\site-packages\\PySide\\QtCore4.dll',
                'BINARY'), ('QtGui4.dll', 'C:\\Python27\\Lib\\site-packages\\PySide\\QtGui4.dll',
                'BINARY')]

# Set up the more obscure PyInstaller runtime options

options = [('v', '', 'OPTION'), ('O', '', 'OPTION')]

# This is a place where the user custom code may go. You can do almost
# whatever you want, even modify the data_files, includes and friends
# here as long as they have the same variable name that the setup call
# below is expecting.

# No custom code added

# The setup for PyInstaller is different from py2exe. Here I am going to
# use some common spec file declarations

analysis = Analysis(['Z:\\home\\adria\\winbin\\pyinstaller-1.5.1\\support\\_mountzlib.py',
           'Z:\\home\\adria\\winbin\\pyinstaller-1.5.1\\support\\useUnicode.py',
           'Z:\\home\\adria\\Documents\\decoys\\decoy_finder.py'],
                    pathex=[],
                    hookspath=[],
                    excludes=excludes)

pyz = PYZ(analysis.pure, level=9)


executable = EXE( pyz,
                 analysis.scripts + includes + packages + options,
                 analysis.binaries - dll_excludes + dll_includes + data_files,
                 name=r"DecoyFinder.exe",
                 debug=False,
                 console=False,
                 strip=False,
                 upx=True,
                 icon=r'Z:\home\adria\Documents\decoys\icon.ico',
                 version=None)

# This is a place where any post-compile code may go.
# You can add as much code as you want, which can be used, for example,
# to clean up your folders or to do some particular post-compilation
# actions.

if os.path.isdir('obdata'):
    shutil.rmtree('obdata')
shutil.copytree(os.environ['BABEL_DATADIR'],'obdata')



# And we are done. That's a setup script :-D

