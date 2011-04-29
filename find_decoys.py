#!/usr/bin/env python
#-*- coding:utf-8 -*-

#Condicions per al decoy respecte el lligand actiu:
# - Tanimoto MACCS < 0,9
# - HBA 0 (+-1)
# - ClogP  +-1 (+- 1.5)
# - HBD 0 (+-1)
# - Molecular weight +/-40 Da
# - exact same number of rotational bonds

import pybel, os

##### Aquesta part és necessària per a poder fer servir MACCS fingerprinting des de python
pybel.fps.append("MACCS")
pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)
#####

outputdir = '.'

#Establim intervals de tolerància per defecte:

HBA_t = 0 #1
HBD_t = 0#1
ClogP_t = 1#1.5
tanimoto_t = 0,9
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
        self.clogp = mol.calcdesc(['LogP'])['LogP']
        self.mw = mol.molwt
        self.rot = mol.OBMol.NumRotors()
        self.title = mol.title
    def __str__(self):
        return "Title: %s; HBA: %s; HBD: %s; CLogP: %s; MW:%s \n" % (self.title, self.hba, self.hbd, self.clogp, self.mw)

def get_fileformat(file): #TODO: fileformat guessing
    """
    """
    return 'sdf' #stub

def parse_db_files(filelist):
    """
    """

    for dbfile in filelist:
        mols = pybel.readfile(get_fileformat(dbfile), dbfile)
        for mol in mols:
            yield ComparableMol(mol)

def parse_query_files(filelist):
    """
    """
    query_dict = {}
    for file in filelist:
        mols = pybel.readfile(get_fileformat(file), file)
        for mol in mols:
            query_dict[ComparableMol(mol)] = []
    return query_dict


def find_decoys(): #TODO: implementar opcions/variables
    """
    """
    #TODO: OptParse
    #TODO: GUI
    db_entry_gen = parse_db_files(["/home/ssorgatem/uni/PEI/ZINC/10_p0.101.sdf.gz"])

    testfile = "/home/ssorgatem/uni/PEI/trypsin_ligands.sdf.gz" #STUB!
    query_files_list = [testfile]

    ligands_dict = parse_query_files(query_files_list)

    for db_mol in db_entry_gen:
        for ligand in ligands_dict.iterkeys():
            tanimoto = db_mol.fp | ligand.fp
            if  tanimoto < tanimoto_t \
            and ligand.hba - HBA_t <= db_mol.hba <= ligand.hba + HBA_t\
            and ligand.hbd - HBD_t <= db_mol.hbd <= ligand.hbd + HBD_t\
            and ligand.clogp - ClogP_t <= db_mol.clogp <= ligand.clogp + ClogP_t \
            and ligand.mw - MW_t <= db_mol.mw <= ligand.mw + MW_t \
            and ligand.rot - RB_t <= db_mol.rot <= ligand.rot + RB_t \
            :
                ligands_dict[ligand].append(db_mol)
                #print tanimoto, db_mol.title, ligand.title
    for ligand in ligands_dict.iterkeys():
        decoy_list = ligands_dict[ligand]
        print ligand.title, len(decoy_list), "decoys found"
        if decoy_list:
            decoyfile = pybel.Outputfile("sdf", os.path.join(outputdir, ligand.title + "_decoys.sdf"), overwrite = True)
            for decoy in decoy_list:
                decoyfile.write(decoy.mol)
    print "Done."

if __name__ == '__main__':
    find_decoys()

