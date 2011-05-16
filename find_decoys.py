#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       find_decoys.py is part of Decoy Finder
#
#       Copyright 2011 Adrià Cereto Massagué <adrian.cereto@gmail.com>
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

#Condicions per al decoy respecte el lligand actiu:
# - Tanimoto MACCS < 0,9
# - HBA 0 (+-1)
# - ClogP  +-1 (+- 1.5)
# - HBD 0 (+-1)
# - Molecular weight +/-40 Da
# - exact same number of rotational bonds

import pybel, os, urllib2, tempfile, random,  sys
from decimal import Decimal
#Decimal() serveix per fer operacions exactes amb decimals, ja que el built-in float és imprecís

##### Aquesta part és necessària per a poder fer servir MACCS fingerprinting des de pybel en versions antiquades d'openbabel
if "MACCS" not in pybel.fps:
    pybel.fps.append("MACCS")
    pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)
#####
informats = ''
for format in pybel.informats.iterkeys():
    informats += "*.%s " %format
    if os.name != 'nt':
        for compression in ('gz', 'tar',  'bz',  'bz2',  'tar.gz',  'tar.bz',  'tar.bz2'):
            informats += "*.%s.%s " % (format,  compression)


#Alguns valors per defecte:

HBA_t = 0 #1
HBD_t = 0#1
ClogP_t = Decimal(1)#1.5
tanimoto_t = Decimal('0.9')
tanimoto_d = Decimal('0.9')
MW_t = 40
RB_t = 0#1

#Creem dos filtres per aconseguir els HBD i HBA:
HBA = pybel.Smarts("[#7,#8]")
HBD = pybel.Smarts("[#7,#8;!H0]")

class ComparableMol():
    """
    """
    def __init__(self, mol):
        self.mol = mol
        self.fp = mol.calcfp("MACCS")
        self.hba = len(HBA.findall(mol))
        self.hbd = len(HBD.findall(mol))
        self.clogp = Decimal(str(mol.calcdesc(['logP'])['logP']))
        self.mw = mol.molwt
        self.rot = mol.OBMol.NumRotors()
        self.title = mol.title
    def __str__(self):
        return "Title: %s; HBA: %s; HBD: %s; CLogP: %s; MW:%s \n" % (self.title, self.hba, self.hbd, self.clogp, self.mw)

def get_zinc_slice(slicename,  cachedir = tempfile.gettempdir(),  keepcache = False):
    """
    returns an iterable list of files from  online ZINC slices
    """
    if slicename in ('all', 'single', 'usual', 'metals'):
        subset = '10' #subset 'everything'
        script = "http://zinc.docking.org/subset1/%s/%s.sdf.csh" % (subset,slicename)
        handler = urllib2.urlopen(script)
        print "Reading ZINC data..."
        scriptcontent = handler.read().split('\n')
        handler.close()
        filelist = scriptcontent[1:-2]
        #print slicename
        yield len(filelist)
        random.shuffle(filelist)
        #print filelist
        #print "Provant si va o no"
        parenturl = scriptcontent[0].split()[1].split('=')[1]
        for file in filelist:
            #print "treballant amb %s" % file

            outfilename = os.path.join(cachedir, file)
            if not (keepcache and os.path.isfile(outfilename)):
                print 'File not cached or cache disabled; downloading %s' % parenturl + file
                dbhandler = urllib2.urlopen(parenturl + file)
                outfile = open(outfilename, "wb")
                outfile.write(dbhandler.read())
                dbhandler.close()
                outfile.close()
            else:
                print "Loading cached file: %s" % outfilename
            yield str(outfilename)
            #print outfilename
            if not keepcache:
                try:
                    os.remove(outfilename)
                except Exception,  e:
                    print "Unable to remove %s" % (outfilename)
                    print unicode(e)
    else:
        raise Exception,  u"Unknown slice"

def get_fileformat(file):
    """
    """
    index = -1
    ext = file.split(".")[index].lower()
    while ext in ('gz', 'tar',  'bz',  'bz2'):
        index -= 1
        ext = file.split(".")[index].lower()
    if ext in pybel.informats.keys():
        #print ext
        return ext
    else:
       print "%s: unknown format"  % file
       raise ValueError

def parse_db_files(filelist):
    """
    """
    filecount = 0
    if type(filelist) == list:
        random.shuffle(filelist)
    for dbfile in filelist:
        mols = pybel.readfile(get_fileformat(dbfile), dbfile)
        for mol in mols:
            yield ComparableMol(mol), filecount, dbfile
        filecount += 1

def parse_query_files(filelist):
    """
    """
    query_dict = {}
    for file in filelist:
        file = str(file)
        mols = pybel.readfile(get_fileformat(file), file)
        for mol in mols:
            query_dict[ComparableMol(mol)] = 0
    return query_dict

def parse_decoy_files(decoyfilelist):
    """
    """
    decoy_set = set()
    for decoyfile in decoyfilelist:
        decoyfile = str(decoyfile)
        mols = pybel.readfile(get_fileformat(decoyfile), decoyfile)
        for mol in mols:
            cmol = ComparableMol(mol)
            decoy_set.add(cmol)
    return decoy_set

def isdecoy(
                db_mol
                ,ligand
                ,HBA_t = 0 #1
                ,HBD_t = 0#1
                ,ClogP_t = Decimal(1)#1.5
                ,tanimoto_t = Decimal('0.9')
                ,MW_t = 40
                ,RB_t = 0
                ):
    """
    """
    tanimoto = Decimal(str(db_mol.fp | ligand.fp))
    if  tanimoto < tanimoto_t \
    and ligand.hba - HBA_t <= db_mol.hba <= ligand.hba + HBA_t\
    and ligand.hbd - HBD_t <= db_mol.hbd <= ligand.hbd + HBD_t\
    and ligand.clogp - ClogP_t <= db_mol.clogp <= ligand.clogp + ClogP_t \
    and ligand.mw - MW_t <= db_mol.mw <= ligand.mw + MW_t \
    and ligand.rot - RB_t <= db_mol.rot <= ligand.rot + RB_t \
    :
        return True
    else:
        return False

def save_decoys(decoy_set, outputfile):
    """
    """
    print 'saving %s decoys' % len(decoy_set)
    if len(decoy_set):
        fileexists = 0
        if os.path.splitext(outputfile)[1].lower()[1:] not in pybel.outformats:
            outputfile += "_decoys.sdf"
        while os.path.isfile(outputfile):
            fileexists += 1
            filename,  extension = os.path.splitext(outputfile)
            if filename.endswith("_%s" % (fileexists -1)):
                filename = '_'.join(filename.split('_')[:-1]) +"_%s" % fileexists
            else:
                filename += "_%s" % fileexists
            outputfile = filename + extension

        format = str(os.path.splitext(outputfile)[1][1:].lower())
        decoyfile = pybel.Outputfile(format, str(outputfile))
        for decoy in decoy_set:
            decoyfile.write(decoy.mol)
        decoyfile.close()
        return outputfile
    else:
        return 'No decoys found'

def find_decoys(
                query_files
                ,db_files
                ,outputfile = 'found_decoys'
                ,HBA_t = 0 #1
                ,HBD_t = 0#1
                ,ClogP_t = 1#1.5
                ,tanimoto_t = 0.9
                ,tanimoto_d = 0.9
                ,MW_t = 40
                ,RB_t = 0
                ,limit = 36
                ,decoy_files = []
                ,stopfile = ''
                ):
    """
    """
    tanimoto_t = Decimal(str(tanimoto_t))
    tanimoto_d = Decimal(str(tanimoto_d))
    ClogP_t = Decimal(str(ClogP_t))
    print "Looking for decoys!"

    db_entry_gen = parse_db_files(db_files)

    ligands_dict = parse_query_files(query_files)

    nactive_ligands = len(ligands_dict)

    complete_ligand_sets = {}

    limitreached = False
    total_limit = nactive_ligands*limit
    yield ('total_limit',  total_limit,  nactive_ligands)

    if decoy_files:
        yield ('file', 0, 'known decoy files...')
        decoys_set = parse_decoy_files(decoy_files)
        for ligand in ligands_dict.keys():
            for decoy in decoys_set:
                if isdecoy(decoy,ligand,HBA_t,HBD_t,ClogP_t,tanimoto_t,MW_t,RB_t ):
                    ligands_dict[ligand] +=1
            if limit and ligands_dict[ligand] >= limit:
                complete_ligand_sets[ligand] = ligands_dict.pop(ligand)
    else:
        decoys_set = set()

    yield ('ndecoys',  len(decoys_set),  len(complete_ligand_sets))

    for db_mol, filecount, db_file in db_entry_gen:
        #print db_mol.title
        yield ('file',  filecount, db_file)
        if not limit or len(decoys_set) < total_limit or len(complete_ligand_sets) < nactive_ligands:
            too_similar = False
            if tanimoto_d < Decimal(1):
                for decoy in decoys_set:
                    decoy_T = Decimal(str(decoy.fp | db_mol.fp))
                    if  decoy_T >= tanimoto_d:
                        too_similar = True
            if not too_similar:
                for ligand in ligands_dict.iterkeys():
                    if isdecoy(db_mol,ligand,HBA_t,HBD_t,ClogP_t,tanimoto_t,MW_t,RB_t ):
                        #print ligands_dict[ligand]
                        ligands_dict[ligand] += 1
                        if db_mol.fp.__str__() not in decoys_set:
                            decoys_set.add(db_mol)
                            print '%s decoys found' % len(decoys_set)
                            yield ('ndecoys',  len(decoys_set), len(complete_ligand_sets))
                        if ligands_dict[ligand] ==  limit:
                            print 'limit successfully reached for ', ligand.title
                            complete_ligand_sets[ligand] = ligands_dict[ligand]
        else:
            break
        if os.path.exists(stopfile):
            os.remove(stopfile)
            print 'stopping by user request'
            break

    if limit:
        print 'Completed %s of %s decoy sets' % (len(complete_ligand_sets), nactive_ligands )
        limitreached = len(complete_ligand_sets) >= nactive_ligands
    if limitreached and total_limit <= len(decoys_set):
        print "Found all wanted decoys"
    else:
        print "Not all wanted decoys found"
    #Last, special yield:
    yield ('result',  ligands_dict,  (save_decoys(decoys_set, outputfile), limitreached))

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
    decopts.add_argument('-l', '--decoys-per-set', default=36, type=int
                        , help='Number of decoys to search for each active ligand'
                        , dest='limit')
    decopts.add_argument('-t', '--tanimoto-with-active', default=tanimoto_t, type=float
                        , help='Upper tanimoto threshold between active ligand and decoys'
                        , dest='tanimoto_t')
    decopts.add_argument('-i', '--inter-decoy-tanimoto', default=tanimoto_d, type=float
                        , help='Upper tanimoto threshold between decoys'
                        , dest='tanimoto_d')
    decopts.add_argument('-c','--clogp-margin', default=ClogP_t, type=float
                        , help='Decoy log P value margin'
                        , dest='ClogP_t')
    decopts.add_argument('-y', '--hba-margin', default=HBA_t, type=float
                        , help='Decoy hydrogen bond acceptors margin'
                        , dest='HBA_t')
    decopts.add_argument('-g', '--hbd-margin', default=HBD_t, type=float
                        , help='Decoy hydrogen bond donors margin'
                        , dest='HBD_t')
    decopts.add_argument('-r', '--rotational-bonds-margin', default=RB_t, type=float
                        , help='Decoy rotational bonds margin'
                        , dest='RB_t')
    decopts.add_argument('-w',  '--molecular-weight-margin', default=MW_t, type=float
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
        ,limit = ns.limit
        ,tanimoto_d = ns.tanimoto_d
        ,decoy_files = ns.decoy_files
    ):
        pass


if __name__ == '__main__':
    main()

