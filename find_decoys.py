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

import pybel, os, urllib2, tempfile, random

##### Aquesta part és necessària per a poder fer servir MACCS fingerprinting des de pybel en versions antiquades d'openbabel
if "MACCS" not in pybel.fps:
    pybel.fps.append("MACCS")
    pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)
#####

#Alguns valors per defecte:

HBA_t = 0 #1
HBD_t = 0#1
ClogP_t = 1#1.5
tanimoto_t = 0.9
tanimoto_d = 0.9
MW_t = 40
RB_t = 0

#Creem dos filtres per aconseguir els HBD i HBA:
HBD = pybel.Smarts("[#7,#8;!H0]")
HBA = pybel.Smarts("[#7,#8]")


class ComparableMol():
    """
    """
    def __init__(self, mol):
        self.mol = mol
        self.fp = mol.calcfp("MACCS")
        self.hba = len(HBA.findall(mol))
        self.hbd = len(HBD.findall(mol))
        self.clogp = mol.calcdesc(['logP'])['logP']
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
    while ext == 'gz':
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
    decoy_dict = {}
    for decoyfile in decoyfilelist:
        decoyfile = str(decoyfile)
        mols = pybel.readfile(get_fileformat(decoyfile), decoyfile)
        for mol in mols:
            cmol = ComparableMol(mol)
            decoy_dict[cmol.fp.__str__()] = cmol
    return decoy_dict

def isdecoy(
                db_mol
                ,ligand
                ,HBA_t = 0 #1
                ,HBD_t = 0#1
                ,ClogP_t = 1#1.5
                ,tanimoto_t = 0.9
                ,MW_t = 40
                ,RB_t = 0
                ):
    """
    """
    tanimoto = db_mol.fp | ligand.fp
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

def save_decoys(decoys_dict, outputfile):
    """
    """
    print 'saving %s decoys' % len(decoys_dict)
    if len(decoys_dict):
        fileexists = 0
        if os.path.splitext(outputfile)[1].lower()[1:] not in pybel.outformats.keys():
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
        for decoyfp in decoys_dict.iterkeys():
            decoy = decoys_dict[decoyfp]
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
    print "Looking for decoys!"

    yield 0,  'known decoy files...' #TODO: print only when needed
    decoys_dict = parse_decoy_files(decoy_files)

    db_entry_gen = parse_db_files(db_files)

    ligands_dict = parse_query_files(query_files)

    ligands_ndecoys_dict = {}

    rejected = 0
    limitreached = False
    ndecoys = 0
    total_limit = len(ligands_dict)*limit

    yield ('total_limit',  total_limit)

    for ligand in ligands_dict.iterkeys():
        for decoyfp in decoys_dict.iterkeys():
            if isdecoy(decoys_dict[decoyfp],ligand,HBA_t,HBD_t,ClogP_t,tanimoto_t,MW_t,RB_t ):
                ligands_dict[ligand] +=1
                ndecoys +=1
                yield ('ndecoys',  ndecoys)

    for db_mol, filecount, db_file in db_entry_gen:
        #print db_mol.title
        yield ('file',  filecount, db_file)
        if ligands_dict:
            #print len(ligands_dict), 'actives pending'
            for ligand in ligands_dict.keys():
                if not limit  or (limit and ligands_dict[ligand] <  limit):
                    if isdecoy(db_mol,ligand,HBA_t,HBD_t,ClogP_t,tanimoto_t,MW_t,RB_t ):
                        not_repeated = True
                        if tanimoto_d < 1:
                            for fp in decoys_dict.iterkeys():
                                decoy_T = decoys_dict[fp].fp | db_mol.fp
                                if  decoy_T >= tanimoto_d:
    #                                print decoy_T
    #                                print 'discarding too similar molecule'
                                    rejected +=1
                                    not_repeated = False
                        if not_repeated:
                            ligands_dict[ligand] += 1
                            ndecoys +=1
                            decoys_dict[db_mol.fp.__str__()] = db_mol
                            #yield ndecoys, db_file
                            print ndecoys
                            yield ('ndecoys',  ndecoys, len(ligands_ndecoys_dict))
                            if ligands_dict[ligand] ==  limit:
                                print 'limit successfully reached for ', ligand.title
                                ligands_ndecoys_dict[ligand] = ligands_dict.pop(ligand)
        else:
            break
        if os.path.exists(stopfile):
            os.remove(stopfile)
            break

    if total_limit == ndecoys:
        print 'limit successfully reached for all ligands'
        limitreached = True
        #Fix a last molecule = decoy error:
        if not ligands_ndecoys_dict:
            ligands_ndecoys_dict.update(ligands_dict)
    else:
        ligands_ndecoys_dict.update(ligands_dict)
    print '%s rejected decoys due to similarity' % rejected
    #Last, special yield:
    yield ('result',  ligands_ndecoys_dict,  (save_decoys(decoys_dict, outputfile), limitreached))

if __name__ == '__main__':
    pass
    #TODO: OptParse
    #find_decoys('','')

