#-*- coding:utf-8 -*-
#
#       This file is part of Decoy Finder
#
#       Copyright 2012 Adrià Cereto Massagué <adrian.cereto@urv.cat>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os, sys, shutil, subprocess, tarfile
from glob import glob
sys.path.append('..')
import metadata
exit
if metadata.PYQT:
    metadata.NAME += '-pyqt'

PI = os.path.join(os.path.expanduser('~'), 'winbin', 'pyinstaller-1.5.1', 'pyinstaller.py')

author = "Adrià Cereto Massagué"
author_email = "adrian.cereto@urv.cat"
description = "A tool to find decoy molecule sets for given active ligand sets"
#long_description=read('README.txt')
long_description="""DecoyFinder is a graphical tool which helps finding sets of decoy molecules for a given group of active ligands. It does so by finding molecules which have a similar number of rotational bonds, hydrogen bond acceptors, hydrogen bond donors, logP value and molecular weight, but are chemically different, which is defined by a maximum Tanimoto value threshold between active ligand and decoy molecule MACCS fingerprints. Optionally, a maximum Tanimoto value threshold can be set between decoys in order assure chemical diversity in the decoy set."""

def get_clean_src(parent = '..'):
    srcdir = metadata.NAME + '-' + metadata.VERSION
    datafiles = [
                 'README.txt'
                , 'LICENCE.txt'
                , 'RELEASE_NOTES.txt'
                , 'LICENCE.html'
                , 'icon.png'
                 ]
    filelist = ['MainWindow.py'
                , 'Ui_MainWindow.py'
                , 'AboutDiag.py'
                , 'Ui_AboutDiag.py'
                , 'decoy_finder.py'
                , 'find_decoys.py'
                , 'metadata.py'
                , 'resources_rc.py'
                , 'icons_rc.py'
                ]
    if os.path.exists(srcdir):
        shutil.rmtree(srcdir)
    os.makedirs(srcdir)
    for file in filelist + datafiles:
        shutil.copy(os.path.join(parent, file), srcdir)
    for file in datafiles:
        if os.path.exists(file):
            os.remove(file)
        shutil.copy(os.path.join(parent, file), '.')
    return srcdir

def make_archive(dir):
    fname = metadata.NAME+'-'+ metadata.VERSION + '.tar.bz2'
    print 'Generating %s ... ' % fname
    if os.path.exists(fname):
        os.remove(fname)
    archive = tarfile.open(fname, 'w:bz2')
    for file in os.listdir(dir):
        archive.add(os.path.join(dir, file))
    archive.close()
    print 'Done'


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
#def read(fname):
#    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def generate_deb_control():
    control = 'Package: %s\n' % metadata.NAME.lower()
    control += 'Version: %s\n' % metadata.VERSION
    control += 'Section: science\n'
    control += 'Maintainer: %s\n' % (author + ' <%s>' % author_email)
    control += 'Architecture: all\n'
    control += 'Homepage: http://%s\n' % metadata.URL
    control += 'Depends: python-qt4 , python-openbabel (>= 2.3.0)\n'
    control += 'Description:%s\n' % description
    control += ' %s\n' % long_description
    control += '\n'
    return control

def make_deb(srcdir):
    debroot = 'deb'
    print 'Building the .deb package'
    ####Put files in place####
    print 'Copying files...'
    destdir = os.path.join(debroot, 'usr', 'share', 'applications')
    destfile = os.path.join(destdir, metadata.NAME.lower() + '.desktop')
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    elif os.path.exists(destfile):
        os.remove(destfile)
    shutil.copy(metadata.NAME.lower() + '.desktop', destdir)
    destdir = os.path.join(debroot, 'usr', 'local', 'bin')
    destfile = os.path.join(destdir, metadata.NAME.lower())
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    elif os.path.exists(destfile):
        os.remove(destfile)
    shutil.copy(metadata.NAME.lower(), destdir)
    destdir = os.path.join(debroot, 'opt', metadata.NAME)
    if os.path.isdir(destdir):
        shutil.rmtree(destdir)
    shutil.copytree(srcdir, destdir)
    controldir = os.path.join(debroot, 'DEBIAN')
    if not os.path.exists(controldir):
        os.makedirs(controldir)
    controlfile = os.path.join(controldir, 'control')
    if os.path.exists(controlfile):
        os.remove(controlfile)
    cf = open(controlfile, 'wb')
    cf.write(generate_deb_control())
    cf.close()
    subprocess.call(['sudo', 'chown', '-R', 'root:root'] + glob(debroot + '/*'))
    subprocess.call(['sudo', 'chmod', '-R', 'o+rx-w'] + glob(debroot + '/*'))
    subprocess.call(['sudo', 'chmod', 'a-x'] + glob(os.path.join(debroot, 'opt', metadata.NAME, '*')))
    subprocess.call(['sudo', 'chmod', '-R', '0755', controldir ])
    ####Build the package####
    print 'Building the package...'
    pkgfn = metadata.NAME.lower() + '-' + metadata.VERSION + '_all.deb'
    if os.path.isfile(pkgfn):
        os.remove(pkgfn)
    subprocess.call(['sudo', 'dpkg', '--build', debroot, pkgfn])
    subprocess.call(['sudo', 'chmod', '777', pkgfn])
    if os.path.isfile(pkgfn):
        print 'Done (%s)' % pkgfn
        if os.path.exists(os.path.join('packages', pkgfn)):
            os.remove(os.path.join('packages', pkgfn))
        shutil.move(pkgfn, 'packages')
    else:
        print 'Unable to build the .deb package'
    ####Now some cleanup####
    subprocess.call(['sudo', 'chmod', '-R', 'a+rw', debroot])
    for path in (
                 controlfile
                 , os.path.join(debroot, 'opt', metadata.NAME)
                 , os.path.join(debroot, 'usr', 'share', 'applications', metadata.NAME.lower() + '.desktop')
                 , os.path.join(debroot, 'usr', 'local', 'bin', metadata.NAME.lower())
                 ):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            print 'Could not remove %s' %path

def make_win32(srcdir):
    print 'Building Windows binary...'
    args = [PI, '-w', '-X', '-C', 'config-win32.dat', '-F', 'DecoyFinder.spec']
    if os.name == 'nt':
        args = [sys.executable] + args
    else:
        args = ['wine', 'c:/Python27/python'] + args
    subprocess.call(args)
    print 'Done. Building Windows installer...'
    nsi_data = """!define PRODUCT_NAME "%s"
!define PRODUCT_VERSION "%s"
!define PRODUCT_WEB_SITE "http://%s"
    """ % (metadata.NAME, metadata.VERSION, metadata.URL)
    nsi = open('installer.nsi', 'rb').read()
    tmpfn = '_tmp_nsi_file.nsi'
    complete_nsi_file = open(tmpfn, 'wb')
    complete_nsi_file.write(nsi_data)
    complete_nsi_file.write(nsi)
    complete_nsi_file.close()
    subprocess.call(['makensis', tmpfn])
    os.remove(tmpfn)
    installer = metadata.NAME + '-' + metadata.VERSION + '_installer.exe'
    if os.path.isfile(installer):
        print 'Installer successfully built'
        if os.path.exists(os.path.join('packages',  installer)):
            os.remove(os.path.join('packages',  installer))
        shutil.move(installer, 'packages')
    else:
        print 'Could not build windows installer!'
    print 'Done'

def make_rpm(srcdir):
    rpmdir = 'rpm'
    if not os.path.isdir(rpmdir):
        os.makedirs(rpmdir)
    RPMMACROS = os.path.join(os.path.expanduser('~'), '.rpmmacros')
    macrosfile = open(RPMMACROS, 'wb')
    macrosfile.write("%_topdir " + os.path.abspath(rpmdir) + '\n')
    macrosfile.write("%_buildrootdir "+ os.path.abspath(rpmdir) + "/BUILD\n")
    macrosfile.write("% _rpmdir "+ os.path.abspath(rpmdir) +"/RPMS\n")
    macrosfile.write("%_tmppath "+ os.path.abspath(rpmdir) + "/tmp\n")
    for dir in ('SRPMS', 'BUILD', 'RPMS', 'SPECS', 'tmp'):
        fullpath = os.path.abspath(os.path.join(rpmdir, dir))
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)
    ####Put files in place####
    print 'Copying files...'
    buildroot = os.path.abspath(os.path.join(rpmdir, 'BUILD', "%s-%s-1.noarch" % (metadata.NAME,  metadata.VERSION)))
    if os.path.exists(buildroot):
        shutil.rmtree(buildroot)
    os.makedirs(buildroot)
    destdir = os.path.join(buildroot, 'usr', 'share', 'applications')
    destfile = os.path.join(destdir, metadata.NAME.lower() + '.desktop')
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    elif os.path.exists(destfile):
        os.remove(destfile)
    shutil.copy(metadata.NAME.lower() + '.desktop', destdir)
    destdir = os.path.join(buildroot, 'usr', 'bin')
    destfile = os.path.join(destdir, metadata.NAME.lower())
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    elif os.path.exists(destfile):
        os.remove(destfile)
    shutil.copy(metadata.NAME.lower(), destdir)
    destdir = os.path.join(buildroot, 'opt', metadata.NAME)
    if os.path.isdir(destdir):
        shutil.rmtree(destdir)
    shutil.copytree(srcdir, destdir)
    specfile = metadata.NAME + '-' + metadata.VERSION +'_rpm.spec'
    if os.path.isdir(os.path.join(rpmdir, 'SOURCES')):
        shutil.rmtree(os.path.join(rpmdir, 'SOURCES'))
        os.makedirs(os.path.join(rpmdir, 'SOURCES'))
    shutil.copy(os.path.join('..', 'icon.xpm'), os.path.join(rpmdir, 'SOURCES'))
    if os.path.exists(specfile):
        os.remove(specfile)
    spec_template = ""
    spec_template +="Name: %s\n" % metadata.NAME
    spec_template +="Version: %s\n" % metadata.VERSION
    spec_template +="Url: http://%s\n" % metadata.URL
    spec_template +="Vendor: Grup de Recerca en Nutrigenomica - Universitat Rovira i Virgili\n"
    spec_template +="Packager: %s\n" %(author + ' <%s>' % author_email)
    spec_template +="Release: 1\n"
    spec_template +="Summary: %s\n" % description
    spec_template +="License: GPL v3\n"
    spec_template +="Group: Science\n"
    spec_template +="Icon: %s\n" % 'icon.xpm'
    spec_template +="BuildArch: noarch\n"
    spec_template +="ExclusiveArch: noarch\n"
    spec_template +="Buildroot: %s\n" % buildroot
    spec_template +="Requires: python-openbabel >= 2.3 , PyQt4\n"
    spec_template +="%define _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm\n"
    spec_template +="%define _unpackaged_files_terminate_build 0\n"
    spec_template +="%description\n"
    spec_template +="%s\n" % long_description

    files_spec = """

%files
%defattr(-,root,root,-)
%{_datarootdir}/applications/decoyfinder-pyqt.desktop
%{_bindir}/decoyfinder-pyqt
%dir "/opt/"
%dir "/opt/DecoyFinder-pyqt/"
/opt/DecoyFinder-pyqt/*
"""
    sf = open(specfile, 'wb')
    sf.write(spec_template)
    sf.write(files_spec)
    sf.close()
    subprocess.call(['sudo', 'chown', '-R', 'root:root'] + glob(buildroot + '/*'))
    subprocess.call(['sudo', 'chmod', '-R', 'o+rx-w'] + glob(buildroot + '/*'))
    subprocess.call(['sudo', 'chmod', 'a-x'] + glob(os.path.join(buildroot, 'opt', metadata.NAME, '*')))
    ####Build the RPM####
    macrosfile.close()
    subprocess.call(['rpmbuild', '--target=noarch', '--nodeps', '-bb', specfile])
    rpmname = "%s-%s-1.noarch.rpm" % (metadata.NAME,  metadata.VERSION)
    if os.path.isfile(os.path.join('packages', rpmname)):
        os.remove(os.path.join('packages', rpmname))
    shutil.move(os.path.join(rpmdir, 'RPMS',rpmname), 'packages')
    ####Cleanup####
    print 'Cleaning files...'
    subprocess.call(['sudo', 'chmod', '-R', 'a+rw', buildroot])
    shutil.rmtree(buildroot)
    if os.path.isfile(os.path.join('packages', rpmname)):
        print '%s successfully built!' % rpmname
    else:
        print 'Unable to build rpm package!'

if __name__ == '__main__':
    srcdir = get_clean_src('..')
    make_archive(srcdir)
    if os.name != 'nt':
        make_deb(srcdir)
        make_rpm(srcdir)
    #make_win32(srcdir)
