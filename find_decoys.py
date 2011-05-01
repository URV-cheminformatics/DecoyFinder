#!/usr/bin/env python
#-*- coding:utf-8 -*-

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

import pybel, os, urllib2, tempfile
from copy import copy

##### Aquesta part és necessària per a poder fer servir MACCS fingerprinting des de python
pybel.fps.append("MACCS")
pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)
#####

#Alguns valors per defecte:

HBA_t = 0 #1
HBD_t = 0#1
ClogP_t = 1#1.5
tanimoto_t = 0.9
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

def get_zinc_slice(slicename):
    """
    returns an iterable list of files from  online ZINC slices
    """
    if slicename in ('all', 'single', 'usual', 'metals'):
        script = "http://zinc.docking.org/subset1/10/%s.sdf.csh" % slicename
        handler = urllib2.urlopen(script)
        print "Reading ZINC data..."
        scriptcontent = handler.read().split('\n')
        handler.close()
        filelist = scriptcontent[1:-2]
        print slicename
        yield len(filelist)
        #print filelist
        #print "Provant si va o no"
        parenturl = scriptcontent[0].split()[1].split('=')[1]
        for file in filelist:
            #print "treballant amb %s" % file
            dbhandler = urllib2.urlopen(parenturl + file)
            outfilename = os.path.join(tempfile.gettempdir(), file)
            #print "destinació:%s" % outfilename
            outfile = open(outfilename, "wb")
            outfile.write(dbhandler.read())
            dbhandler.close()
            outfile.close()
            yield copy(outfilename)
            #print outfilename
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
        mols = pybel.readfile(get_fileformat(file),
                              file)
        for mol in mols:
            query_dict[ComparableMol(mol)] = []
    return query_dict

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

def save_decoys(ligands_dict, outputdir):
    """
    """
    resultdict = {}
    for ligand in ligands_dict.iterkeys():
        decoy_list = ligands_dict[ligand]
        #print ligand.title, len(decoy_list), "decoys found"
        resultdict[ligand.title] = len(decoy_list)
        if decoy_list:
            decoyfile = pybel.Outputfile("sdf", os.path.join(str(outputdir), ligand.title + "_decoys.sdf"), overwrite = True)
            for decoy in decoy_list:
                decoyfile.write(decoy.mol)
            decoyfile.close()
    return resultdict

def find_decoys(
                query_files
                ,db_files
                ,outputdir = '.'
                ,HBA_t = 0 #1
                ,HBD_t = 0#1
                ,ClogP_t = 1#1.5
                ,tanimoto_t = 0.9
                ,MW_t = 40
                ,RB_t = 0
                ,limit = 36
                ):
    """
    """
    print "Looking for decoys!"

    db_entry_gen = parse_db_files(db_files)

    ligands_dict = parse_query_files(query_files)

    for db_mol, filecount, db_file in db_entry_gen:
        #print db_mol.title
        yield filecount, db_file
        break_loop = 1
        for ligand in ligands_dict.iterkeys():
            if not limit  or (limit and len(ligands_dict[ligand]) <  limit):
                break_loop = 0
                if isdecoy(db_mol,ligand,HBA_t,HBD_t,ClogP_t,tanimoto_t,MW_t,RB_t ):
                    ligands_dict[ligand].append(db_mol)
                    #print tanimoto, db_mol.title, ligand.title
        if break_loop:
            break
    yield save_decoys(ligands_dict, outputdir), 0
    print "Done.\n"

if __name__ == '__main__':
    pass
    #TODO: OptParse
    #find_decoys('','')

