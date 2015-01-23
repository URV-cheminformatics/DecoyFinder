#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       find_decoys.py is part of Decoy Finder
#
#       Copyright 2011-2014 Adrià Cereto Massagué <adrian.cereto@urv.cat>
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

import os, urllib2, tempfile, random,  sys,  gzip,  datetime, time, itertools
import numpy as np
from cStringIO import StringIO
from cinfony import rdk
try:
    from cinfony import pybel
except ImportError:
    print "Pybel is not available"
    pybel = False
if "can" not in rdk.outformats:
    if not pybel:
        e = "Unable to generate canonical smiles. Please upgrade cinfony, the RDKit or install OpenBabel python bindings"
        print e
        raise e
    else:
        obcan = True
else:
    obcan = False

from decimal import Decimal
import metadata
#Decimal() can represent floating point data with higher precission than built-in float

informats = ''
informats_set = set()
for format in rdk.informats.iterkeys():
    informats_set.add(format)
    informats += "*.%s " %format
if pybel:
    for format in pybel.informats.iterkeys():
        informats_set.add(format)
        for compression in ('gz', 'tar',  'bz',  'bz2',  'tar.gz',  'tar.bz',  'tar.bz2'):
            informats_set.add(format)


#Some default values:

HBA_t = 0 #1
HBD_t = 0#1
ClogP_t = Decimal(1)#1.5
tanimoto_t = Decimal('0.9')
tanimoto_d = Decimal('0.9')
MW_t = 40
RB_t = 0#1

#Dict of ZINC subsets
ZINC_subsets = {
    "lead-like":"1"
    ,"fragment-like":"2"
    ,"drug-like":"3"
    ,"all-purchasable":"6"
    ,"everything":"10"
    ,"clean-leads":"11"
    ,"clean-fragments":"12"
    ,"clean-drug-like":"13"
    ,"all-clean":"16"
    ,"leads-now":"21"
    ,"frags-now":"22"
    ,"drugs-now":"23"
    ,"all-now":"26"
    ,"sarah":"37"
    ,"Stan":"94"
    }

class ComparableMol():
    """
    """
    def __init__(self, mol):
        self.mol = mol
        self._fp = None
        self.title = mol.title
        self.mw = mol.molwt
        self._hba = None
        self._hbd = None
        self._clogp = None
        self._rot = None
        if obcan:
            self.obmol = pybel.Molecule(mol)
            self.mol.write = self.obmol.write

    @property
    def fp(self):
        if self._fp is  None:
            self._fp = self.mol.calcfp("MACCS")
        return self._fp

    @property
    def hba(self):
        if self._hba is  None:
            self._hba = Decimal(str(self.mol.calcdesc(['NumHAcceptors'])['NumHAcceptors']))
        return self._hba

    @property
    def hbd(self):
        if self._hbd is  None:
            self._hbd = Decimal(str(self.mol.calcdesc(['NumHDonors'])['NumHDonors']))
        return self._hbd

    @property
    def clogp(self):
        if self._clogp is  None:
            self._clogp = Decimal(str(self.mol.calcdesc(['MolLogP'])['MolLogP']))
        return self._clogp

    @property
    def rot(self):
        if self._rot is  None:
            self._rot = self.mol.calcdesc(["NumRotatableBonds"])["NumRotatableBonds"]
        return self._rot

    def __str__(self):
        """
        For debug purposes
        """
        return "Title: %s; HBA: %s; HBD: %s; CLogP: %s; MW:%s \n" % (self.title, self.hba, self.hbd, self.clogp, self.mw)

def get_zinc_slice(slicename = 'all', subset = '10', cachedir = tempfile.gettempdir(),  keepcache = False):
    """
    returns an iterable list of files from  online ZINC slices
    """
    if slicename in ('all', 'single', 'usual', 'metals'):
        script = "http://zinc12.docking.org/db/bysubset/%s/%s.sdf.csh" % (subset,slicename)
        print 'Downloading files in %s' % script
        handler = urllib2.urlopen(script)
        print("Reading ZINC data...")
        scriptcontent = handler.read().split('\n')
        handler.close()
        filelist = []
        parenturl = None
        for line in scriptcontent:
            if not line.startswith('#'):
                if not parenturl and 'http://' in line:
                    parenturl = 'http://' + line.split('http://')[1].split()[0]
                    if not parenturl.endswith('/'):
                        parenturl += '/'
                elif line.endswith('.sdf.gz'):
                    filelist.append(line)
        yield len(filelist)
        random.shuffle(filelist)
        for file in filelist:
            dbhandler = urllib2.urlopen(parenturl + file)
            outfilename = os.path.join(cachedir, file)
            download_needed = True
            if keepcache:
#                filesize = dbhandler.info().get('Content-Length')
#                if filesize:
#                    filesize = int(filesize)

                if not os.path.isfile(outfilename[:-3]):
                    download_needed = True
                    print("Local file outdated or incomplete")
                else:
                    download_needed = False

            if download_needed:
                print('Downloading %s' % parenturl + file)
                buf = StringIO(dbhandler.read())
                dbhandler.close()
                outfile = open(outfilename[:-3], "wb")
                f = gzip.GzipFile(fileobj=buf)
                outfile.write(f.read())
                f.close()
                outfile.close()
            else:
                print("Loading cached file: %s" % outfilename[:-3])
            yield str(outfilename[:-3])

            if not keepcache:
                try:
                    os.remove(outfilename[:-3])
                except Exception,  e:
                    print("Unable to remove %s" % (outfilename[:-3]))
                    print(unicode(e))
    else:
        raise Exception,  u"Unknown slice"

def get_fileformat(file,  rdkout = 0):
    """
    Guess the file format from its extension
    """
    index = -1
    ext = file.split(".")[index].lower()
    print file
    print ext
    if ext in rdk.informats.keys() and ext != "mol2":
        return ext, 0
    elif rdkout:
       print("%s: unknown format"  % file)
       raise ValueError
    while ext in ('gz', 'tar',  'bz',  'bz2'):
        index -= 1
        ext = file.split(".")[index].lower()
    if pybel and ext in pybel.informats.keys():
        return ext, 1
    else:
       print("%s: unknown format"  % file)
       raise ValueError

def readfile(filename):
    fileformat,  usepybel = get_fileformat(filename)
    if not usepybel:
        return rdk.readfile(fileformat, filename)
    else:
        return Ob2RDK(fileformat, filename)

def Ob2RDK(fileformat, filename):
    for mol in pybel.readfile(fileformat, filename):
        try:
            rdkmol = rdk.Molecule(mol)
            yield rdkmol
        except IOError:
            pass

def parse_db_files(filelist):
    """
    Parses files where to llok for decoys
    """
    filecount = 0
    if type(filelist) == list:
        random.shuffle(filelist)
    for dbfile in filelist:
        mols = readfile(dbfile)
        for mol in mols:
            try:
                yield ComparableMol(mol), filecount, dbfile
            except:
                continue
        filecount += 1

def parse_query_files(filelist):
    """
    Parses files containing active ligands
    """
    query_dict = {}
    for file in filelist:
        file = str(file)
        mols = readfile(file)
        for mol in mols:
            try:
                cmol = ComparableMol(mol)
            except:
                continue
            query_dict[cmol] = 0
    return query_dict

def parse_decoy_files(decoyfilelist):
    """
    Parses files containing known decoys
    """
    decoy_set = set()
    for decoyfile in decoyfilelist:
        decoyfile = str(decoyfile)
        mols = readfile(decoyfile)
        for mol in mols:
            try:
                cmol = ComparableMol(mol)
            except:
                continue
            decoy_set.add(cmol)
    return decoy_set

def isdecoy(
                db_mol
                ,ligand
                ,HBA_t = 0 #1
                ,HBD_t = 0#1
                ,ClogP_t = Decimal(1)#1.5
                ,MW_t = 40
                ,RB_t = 0
                ):
    """
    Check if db_mol can be considered a decoy of ligand
    """
    if  ligand.hba - HBA_t <= db_mol.hba <= ligand.hba + HBA_t\
    and ligand.hbd - HBD_t <= db_mol.hbd <= ligand.hbd + HBD_t\
    and ligand.clogp - ClogP_t <= db_mol.clogp <= ligand.clogp + ClogP_t \
    and ligand.mw - MW_t <= db_mol.mw <= ligand.mw + MW_t \
    and ligand.rot - RB_t <= db_mol.rot <= ligand.rot + RB_t \
    :
        return True
    return False

def is_mw_decoy(db_mol, ligand, ligand_std, maxStds):
    return ligand.mw - maxStds * ligand_std <= db_mol.mw <= ligand.mw + maxStds * ligand_std

def checkoutputfile(outputfile):
    """
    Return a safe output filename
    """
    fileexists = 0
    if os.path.splitext(outputfile)[1].lower()[1:] not in rdk.outformats:
        outputfile += "_decoys.sdf"
    while os.path.isfile(outputfile):
        fileexists += 1
        filename,  extension = os.path.splitext(outputfile)
        if filename.endswith("_%s" % (fileexists -1)):
            filename = '_'.join(filename.split('_')[:-1]) +"_%s" % fileexists
        else:
            filename += "_%s" % fileexists
        outputfile = filename + extension
    return outputfile

def find_decoys(
                query_files
                ,db_files
                ,outputfile = 'found_decoys'
                ,HBA_t = 0
                ,HBD_t = 0
                ,ClogP_t = Decimal(1)
                ,tanimoto_t = Decimal('0.9')
                ,tanimoto_d = Decimal('0.9')
                ,MW_t = 40
                ,RB_t = 0
                ,min = 36
                ,max = 36
                ,decoy_files = []
                ,stopfile = ''
                ,maxStds = 1.0
                ,method = 1
                ):
    """
    This is the star of the show
    """
    start_time = time.time()
    outputfile = checkoutputfile(outputfile)
    tanimoto_t = Decimal(str(tanimoto_t))
    tanimoto_d = Decimal(str(tanimoto_d))
    ClogP_t = Decimal(str(ClogP_t))
    print("Looking for decoys!")

    db_files = itertools.chain(decoy_files, db_files)

    db_entry_gen = parse_db_files(db_files)

    used_db_files = set()

    ligands_dict = parse_query_files(query_files)
    ligand_std = 0
    if method == 0:
        active_fp_set = set(active.fp for active in ligands_dict)
    if method == 1:
        ligand_std = np.std([active.mw for active in ligands_dict])

    nactive_ligands = len(ligands_dict)

    complete_ligand_sets = 0

    minreached = False
    if min:
        total_min = nactive_ligands*min
        yield ('total_min',  total_min,  nactive_ligands)
    else:
        min = None

    decoys_can_set = set()
    ndecoys = 0
    ligands_max = 0

    outputfile = checkoutputfile(outputfile)
    format, usepybel = get_fileformat(outputfile, rdkout=True)
    decoyfile = rdk.Outputfile(format, str(outputfile))
    if method == 0:
        decoys_fp_set = set()

    yield ('ndecoys', ndecoys,  complete_ligand_sets)

    for db_mol, filecount, db_file in db_entry_gen:
        used_db_files.add(db_file)
        yield ('file',  filecount, db_file)
        if max and ligands_max >= nactive_ligands:
            break
        if (not min or ndecoys < total_min) or complete_ligand_sets < nactive_ligands:
            if method == 0:
                too_similar = False
                if tanimoto_d < Decimal(1):
                    for decoyfp in decoys_fp_set:
                        decoy_T = Decimal(str(decoyfp | db_mol.fp))
                        if  decoy_T > tanimoto_d:
                            too_similar = True
                            break
                if not too_similar:
                    for active_fp in active_fp_set:
                        active_T = Decimal(str(active_fp | db_mol.fp))
                        if  active_T > tanimoto_t:
                            too_similar = True
                            break
                    if too_similar:
                        continue
            ligands_max = 0
            for ligand in ligands_dict.iterkeys():
                if max and ligands_dict[ligand] >= max:
                    ligands_max +=1
                    continue
                if method == 0:
                    is_a_decoy = isdecoy(db_mol,ligand,HBA_t,HBD_t,ClogP_t,MW_t,RB_t )
                if method == 1:
                    is_a_decoy = is_mw_decoy(db_mol, ligand, ligand_std, maxStds)
                if is_a_decoy:
                    can = db_mol.mol.write('can')
                    if can not in decoys_can_set:
                        if method == 0:
                            decoys_fp_set.add(db_mol.fp)
                        decoyfile.write(db_mol.mol)
                        decoys_can_set.add(can)
                        ndecoys = len(decoys_can_set )
                        ligands_dict[ligand] += 1
                        print('%s decoys found' % ndecoys)
                        yield ('ndecoys',  ndecoys, complete_ligand_sets)
                    if ligands_dict[ligand] ==  min:
                        print('Decoy set completed for ', ligand.title)
                        complete_ligand_sets += 1
                        yield ('ndecoys',  ndecoys, complete_ligand_sets)
                    if max:
                        break
        else:
            print("finishing")
            break
        if os.path.exists(stopfile):
            os.remove(stopfile)
            print('stopping by user request')
            break

    if min:
        print('Completed %s of %s decoy sets' % (complete_ligand_sets, nactive_ligands ))
        minreached = complete_ligand_sets >= nactive_ligands
    if minreached and total_min <= len(decoys_can_set):
        print("Found all wanted decoys")
    else:
        print("Not all wanted decoys found")
    #Generate logfile
    log = '"%s %s log file generated on %s\n"' % (metadata.NAME,  metadata.VERSION,  datetime.datetime.now())
    log += "\n"
    log += '"Output file:","%s"\n' % outputfile
    log += "\n"
    log += '"Active ligand files:"\n'
    for file in query_files:
        log += '"%s"\n' % str(file)
    log += "\n"
    log += '"Decoy sources:"\n'
    for file in used_db_files:
        log += '"%s"\n' % str(file)
    log += "\n"
    log += '"Search settings:"\n'
    if method == 0:
        log += '"Active ligand vs decoy tanimoto threshold","%s"\n' % str(tanimoto_t)
        log += '"Decoy vs decoy tanimoto threshold","%s"\n' % str(tanimoto_d)
        log += '"Hydrogen bond acceptors range","%s"\n' % str(HBA_t)
        log += '"Hydrogen bond donors range","%s"\n' % str(HBD_t)
        log += '"LogP range","%s"\n' % str(ClogP_t)
        log += '"Molecular weight range","%s"\n' % str(MW_t)
        log += '"Rotational bonds range","%s"\n' % str(RB_t)
    if method == 1:
        log += '"Maximum molecular weight standard deviations","%s"\n' % str(maxStds)
        log += '"Active molecular weight standard deviation ","%s"\n' % str(ligand_std)
    log += '"Minimum nº of decoys per active ligand","%s"\n' % str(min)
    log += '"Maximum nº of decoys per active ligand","%s"\n' % str(max)
    log += "\n"
    log += '"Active ligand","HBA","HBD","logP","MW","RB","nº of Decoys found"\n'
    for active in ligands_dict:
        log += '"%s","%s","%s","%s","%s","%s","%s"\n' % (active.title,  active.hba,  active.hbd,  active.clogp,  active.mw,  active.rot,  ligands_dict[active])
    log += "\n"

    with open('%s_log.csv' % outputfile,  'wb') as logfile:
        logfile.write(log)

    decoyfile.close()
    if method == 0:
        if not decoys_fp_set:
            os.remove(outputfile)
    end_time = time.time()
    print end_time - start_time
    #Last, special yield:
    yield ('result',  ligands_dict,  outputfile, minreached)

def main(args = sys.argv[1:]):
    """
    Run this function to run as a command-line application
    """
    try:
        import argparse
    except:
        exit("Unable to import module 'argparse'.\nInstall the argparse python module or upgrade to python 2.7 or higher")

    parser = argparse.ArgumentParser(description='All margins are relative to active ligands\' values')
    parser.add_argument('-a',  '--active-ligands-files', nargs='+', required=True
                        , help='Files containing active ligands'
                        , dest='query_files')
    parser.add_argument('-b', '--database-files', nargs='+', required=True
                        , help='Files containing possible decoys'
                        , dest='db_files')
    parser.add_argument('-d', '--known-decoys-files', nargs='+'
                        , help='Files containing known decoy molecules'
                        , dest='decoy_files')
    parser.add_argument('-o', '--output-file', default='found_decoys.sdf'
                        , help='Output file name'
                        , dest='outputfile')
    decopts = parser.add_argument_group('Decoy finding options')
    decopts.add_argument('-m', '--minimum-decoys-per-set', default=36, type=int
                        , help='Number of decoys to search for each active ligand'
                        , dest='min')
    decopts.add_argument('-M', '--maximum-decoys-per-set', default=36, type=int
                        , help='Stop looking for decoys for ligands with at least so many decoys found'
                        , dest='max')
    decopts.add_argument('-t', '--tanimoto-with-active', default=tanimoto_t, type=Decimal
                        , help='Upper tanimoto threshold between active ligand and decoys'
                        , dest='tanimoto_t')
    decopts.add_argument('-i', '--inter-decoy-tanimoto', default=tanimoto_d, type=Decimal
                        , help='Upper tanimoto threshold between decoys'
                        , dest='tanimoto_d')
    decopts.add_argument('-c','--clogp-margin', default=ClogP_t, type=Decimal
                        , help='Decoy log P value margin'
                        , dest='ClogP_t')
    decopts.add_argument('-y', '--hba-margin', default=HBA_t, type=int
                        , help='Decoy hydrogen bond acceptors margin'
                        , dest='HBA_t')
    decopts.add_argument('-g', '--hbd-margin', default=HBD_t, type=Decimal
                        , help='Decoy hydrogen bond donors margin'
                        , dest='HBD_t')
    decopts.add_argument('-r', '--rotational-bonds-margin', default=RB_t, type=int
                        , help='Decoy rotational bonds margin'
                        , dest='RB_t')
    decopts.add_argument('-w',  '--molecular-weight-margin', default=MW_t, type=int
                        , help='Molecular weight margin'
                        , dest='MW_t')

    ns = parser.parse_args(args)

    for info in find_decoys(
        query_files = ns.query_files
        ,db_files = ns.db_files
        ,outputfile = ns.outputfile
        ,HBA_t = ns.HBA_t
        ,HBD_t = ns.HBD_t
        ,ClogP_t = ns.ClogP_t
        ,tanimoto_t = ns.tanimoto_t
        ,MW_t = ns.MW_t
        ,RB_t = ns.RB_t
        ,min = ns.min
        ,max = ns.max
        ,tanimoto_d = ns.tanimoto_d
        ,decoy_files = ns.decoy_files
    ):
        pass


if __name__ == '__main__':
    main()

