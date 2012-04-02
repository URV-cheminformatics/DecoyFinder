#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#     This file is part of Decoy Finder
#
#     Copyright 2011-2012 Adrià Cereto Massagué <adrian.cereto@urv.cat>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#

import pybel, os, urllib2, tempfile, random,  sys,  gzip,  datetime
import metadata
from decimal import Decimal
#Decimal() can represent floating point data with higher precission than built-in float

informats = ''
for format in pybel.informats.iterkeys():
    informats += "*.%s " %format
    for compression in ('gz', 'tar',  'bz',  'bz2',  'tar.gz',  'tar.bz',  'tar.bz2'):
        informats += "*.%s.%s " % (format,  compression)


#Some default values:

HBA_t = 2
HBD_t = 1
ClogP_t = Decimal(1)#1.5
tanimoto_t = Decimal('0.75')
tanimoto_d = Decimal('0.9')
MW_t = 25
RB_t = 1
mind = 36
maxd = mind

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
        self.fp = mol.calcfp("MACCS")

    def calcdesc(self):
        """
        Calculate all interesting descriptors. Should be  called only when needed
        """
        self.hba = Decimal(str(self.mol.calcdesc(['HBA2'])['HBA2']))
        self.hbd = Decimal(str(self.mol.calcdesc(['HBD'])['HBD']))
        self.clogp = Decimal(str(self.mol.calcdesc(['logP'])['logP']))
        self.mw = self.mol.molwt
        self.rot = self.mol.OBMol.NumRotors()
        self.title = self.mol.title

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
                filesize = dbhandler.info().get('Content-Length')
                if filesize:
                    filesize = int(filesize)

                if os.path.isfile(outfilename):
                    localsize = os.path.getsize(outfilename)
                    download_needed = localsize != filesize
                    if download_needed:
                        print("Local file outdated or incomplete")

            if download_needed:
                print('Downloading %s' % parenturl + file)
                outfile = open(outfilename, "wb")
                outfile.write(dbhandler.read())
                outfile.close()
            else:
                print("Loading cached file: %s" % outfilename)
            dbhandler.close()
            yield str(outfilename)

            if not keepcache:
                try:
                    os.remove(outfilename)
                except Exception,  e:
                    print("Unable to remove %s" % (outfilename))
                    print(unicode(e))
    else:
        raise Exception,  u"Unknown slice"

def get_fileformat(file):
    """
    Guess the file format from its extension
    """
    index = -1
    ext = file.split(".")[index].lower()
    while ext in ('gz', 'tar',  'bz',  'bz2'):
        index -= 1
        ext = file.split(".")[index].lower()
    if ext in pybel.informats.keys():
        return ext
    else:
       print("%s: unknown format"  % file)
       raise ValueError

def parse_db_files(filelist):
    """
    Parses files where to look for decoys
    """
    filecount = 0
    if type(filelist) == list:
        random.shuffle(filelist)
    for dbfile in filelist:
        mols = pybel.readfile(get_fileformat(dbfile), dbfile)
        for mol in mols:
            try:
                cmol= ComparableMol(mol)
                yield cmol, filecount, dbfile
            except Exception, e:
                print e
        filecount += 1

def parse_query_files(filelist):
    """
    Parses files containing active ligands
    """
    query_dict = {}
    for file in filelist:
        file = str(file)
        mols = pybel.readfile(get_fileformat(file), file)
        for mol in mols:
            try:
                cmol = ComparableMol(mol)
                cmol.calcdesc()
                query_dict[cmol] = 0
            except e,  Exception:
                print e
    return query_dict

def parse_decoy_files(decoyfilelist):
    """
    Parses files containing known decoys
    """
    decoy_set = set()
    for decoyfile in decoyfilelist:
        decoyfile = str(decoyfile)
        mols = pybel.readfile(get_fileformat(decoyfile), decoyfile)
        for mol in mols:
            try:
                cmol = ComparableMol(mol)
                cmol.calcdesc()
                decoy_set.add(cmol)
            except e,  Exception:
                print e
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

def get_ndecoys(ligands_dict, maxd):
    return sum((x for x in ligands_dict.itervalues() if not maxd or maxd >= x))

def checkoutputfile(outputfile):
    """
    Return a safe output filename
    """
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
                ,mind = 36
                ,maxd = 36
                ,decoy_files = []
                ,stopfile = ''
                ,unique = False
                ):
    """
    This is the star of the show
    """
    outputfile = checkoutputfile(outputfile)
    tanimoto_t = Decimal(str(tanimoto_t))
    tanimoto_d = Decimal(str(tanimoto_d))
    ClogP_t = Decimal(str(ClogP_t))
    print("Looking for decoys!")

    db_entry_gen = parse_db_files(db_files)

    used_db_files = set()

    ligands_dict = parse_query_files(query_files)
    active_fp_set = set(active.fp for active in ligands_dict)

    nactive_ligands = len(ligands_dict)

    complete_ligand_sets = 0

    minreached = False
    if mind:
        total_min = nactive_ligands*mind
        yield ('total_min',  total_min,  nactive_ligands)
    else:
        mind = None

    decoys_can_set = set()
    ndecoys = get_ndecoys(ligands_dict, maxd)
    ligands_max = 0

    outputfile = checkoutputfile(outputfile)
    format = get_fileformat(outputfile)
    decoyfile = pybel.Outputfile(format, str(outputfile))
    decoys_fp_set = set()

    if decoy_files:
        yield ('file', 0, 'known decoy files...')
        for decoy in parse_decoy_files(decoy_files):
            decoyfile.write(decoy.mol)
            can = decoy.mol.write('can').split('\t')[0]
            for ligand in ligands_dict:
                if can not in decoys_can_set and isdecoy(decoy,ligand,HBA_t,HBD_t,ClogP_t,MW_t,RB_t ):
                    ligands_dict[ligand] +=1
                    if mind and ligands_dict[ligand] == mind:
                        complete_ligand_sets += 1
                        ndecoys = get_ndecoys(ligands_dict, maxd)
                        yield ('ndecoys',  ndecoys,  complete_ligand_sets)
                    if unique:
                        break
            decoys_can_set.add(can)
            decoys_fp_set.add(decoy.fp)

    yield ('ndecoys', ndecoys,  complete_ligand_sets)

    for db_mol, filecount, db_file in db_entry_gen:
        saved = False
        used_db_files.add(db_file)
        yield ('file',  filecount, db_file)
        if maxd and ligands_max >= nactive_ligands:
            print 'Maximum reached'
            minreached = True
            break
        if complete_ligand_sets >= nactive_ligands:
            print 'All decoy sets complete'
            break
        if not mind or ndecoys < total_min :
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
                can = db_mol.mol.write('can').split('\t')[0]
                ligands_max = 0
                if can not in decoys_can_set:
                    db_mol.calcdesc()
                    for ligand in ligands_dict.iterkeys():
                        if maxd and ligands_dict[ligand] >= maxd:
                            ligands_max +=1
                            continue
                        if isdecoy(db_mol,ligand,HBA_t,HBD_t,ClogP_t,MW_t,RB_t ):
                            ligands_dict[ligand] += 1
                            if not saved:
                                decoyfile.write(db_mol.mol)
                                saved = True
                            ndecoys = get_ndecoys(ligands_dict, maxd)
                            print('%s decoys found' % ndecoys)
                            yield ('ndecoys',  ndecoys, complete_ligand_sets)
                            if ligands_dict[ligand] ==  mind:
                                print('Decoy set completed for ', ligand.title)
                                complete_ligand_sets += 1
                                yield ('ndecoys',  ndecoys, complete_ligand_sets)
                            if unique:
                                break
                    if saved:
                        decoys_can_set.add(can)
                        decoys_fp_set.add(db_mol.fp)
        else:
            print("finishing")
            break
        if os.path.exists(stopfile):
            os.remove(stopfile)
            print('stopping by user request')
            break
    else:
        print 'No more input molecules'

    if mind:
        print('Completed %s of %s decoy sets' % (complete_ligand_sets, nactive_ligands ))
        minreached = complete_ligand_sets >= nactive_ligands
    if minreached:
        print("Found all wanted decoys")
    else:
        print("Not all wanted decoys found")
    #Generate logfile
    log = '"%s %s log file generated on %s"\n' % (metadata.NAME, metadata.VERSION, datetime.datetime.now())
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
    log += '"Active ligand vs decoy tanimoto threshold","%s"\n' % str(tanimoto_t)
    log += '"Decoy vs decoy tanimoto threshold","%s"\n' % str(tanimoto_d)
    log += '"Hydrogen bond acceptors range","%s"\n' % str(HBA_t)
    log += '"Hydrogen bond donors range","%s"\n' % str(HBD_t)
    log += '"LogP range","%s"\n' % str(ClogP_t)
    log += '"Molecular weight range","%s"\n' % str(MW_t)
    log += '"Rotational bonds range","%s"\n' % str(RB_t)
    log += '"Minimum nº of decoys per active ligand","%s"\n' % str(mind)
    log += '"Maximum nº of decoys per active ligand","%s"\n' % str(maxd)
    log += "\n"
    log += '"Active ligand","HBA","HBD","logP","MW","RB","nº of Decoys found"\n'
    for active in ligands_dict:
        log += '"%s","%s","%s","%s","%s","%s","%s"\n' % (active.title,  active.hba,  active.hbd,  active.clogp,  active.mw,  active.rot,  ligands_dict[active])
    log += "\n"

    logfile = open('%s_log.csv' % outputfile,  'wb')
    logfile.write(log)
    logfile.close()

    decoyfile.close()

    if not decoys_fp_set:
        if os.path.exists(outputfile):
            os.remove(outputfile)
    #Last, special yield:
    yield ('result',  ligands_dict,  [outputfile, minreached])
