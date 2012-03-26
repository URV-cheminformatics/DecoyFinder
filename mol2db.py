#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       decoy_finder.py is part of Decoy Finder
#
#       Copyright 2011-2012 Adrià Cereto Massagué <adrian.cereto@urv.cat>
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

import pybel, os
import glob, time
import sqlite3
import zlib
import multiprocessing

insert_template = """REPLACE INTO Molecules (`inchikey`, `smiles`,`maccs`, `rotatable_bonds`, `weight`, `logp`, `hba`, `hbd`, `mol`, `tpsa`) VALUES (?, ?, ?,?, ?, ?, ?,?, ?, ?);"""

filelist = glob.glob('ZINC_0.9_2/*.sdf')

#filelist = ['/home/adria/ZINC.sdf']

def calcdesc(mdlmol):
    #print 'emmagatzemant en MDL MOL'
    #print 'calculant inchikey'
    tries = 0
    while tries <2:
        try:
            mol = pybel.readstring('mol', mdlmol)
            cmol = zlib.compress(mdlmol, 9)
            inchikey = mol.write('inchikey').strip()[:25]
            smiles = mol.write('can').split('\t')[0].strip()
            #print 'Calculant HBA'
            hba = str(mol.calcdesc(['HBA2'])['HBA2'])
            #print 'Calculant HBD'
            hbd = str(mol.calcdesc(['HBD'])['HBD'])
            #print 'Calculant logP'
            logp = str(mol.calcdesc(['logP'])['logP'])
            #print 'Calculant TPSA'
            tpsa = str(mol.calcdesc(['TPSA'])['TPSA'])
            #print 'calculant fingerprint'
            maccs = repr(mol.calcfp('MACCS').bits)
            #print 'calculant enllaços rotacionals'
            rotatable_bonds = str(mol.OBMol.NumRotors())
            #print 'calculant PM'
            weight = str(mol.molwt)
            break
        except Exception, e:
            tries +=1
    #print "fent l'insert"
    return [inchikey
                , smiles
                , maccs
                , rotatable_bonds
                , weight
                , logp
                , hba
                , hbd
                , cmol
                , tpsa
                ]
    return insert_str

if __name__ == "__main__":
    dblist = set()
    sqlitedb = sqlite3.connect('sql/decoyfinder_idx.dfdb')
    lcur = sqlitedb.cursor()
    sqlfile = open('sql/molecules_sqlite.sql', 'rb')
    lcur.executescript(sqlfile.read())
    sqlfile.close()
    sqlitedb.commit()
    lcur.close()
    dblist.add(sqlitedb)
    recordcount = 0
    LASTCOMMIT = 0
    COMMIT = 0
    for file in filelist:
        finished = file + '_finished'
        if os.path.exists(finished):
            continue
        print '####################################%s##################################' % file
        mols = (mol.write('mol') for mol in pybel.readfile('sdf', file))
        pool = multiprocessing.Pool()
        for val_tupl in pool.imap_unordered(calcdesc, mols):
        #for val_tupl in (calcdesc(mol) for mol in mols):
            if val_tupl:
                recordcount +=1
                val_tupl[-2] = buffer(val_tupl[-2])
            else:
                continue
            if recordcount - LASTCOMMIT > 1999:
                    COMMIT = len(dblist)
                    LASTCOMMIT = recordcount
            for db in dblist:
                cursor = None
                try:
                    cursor = db.cursor()
                    #print "Executing:"
#                   print insert_str
                    cursor.execute(insert_template, val_tupl)
                    #db.commit()
                    cursor.close()
                except Exception, e:
                    print e
                finally:
                    if cursor:
                        cursor.close()
                if COMMIT > 0:
                    COMMIT -= 1
                    tries = 0
                    while tries < 3:
                        try:
                            db.commit()
                            break
                        except:
                            tries +=1
                            time.sleep(1)
                    else:
                        print 'Unable to commit changes!'
            print recordcount
        pool.terminate()
        pool.join()
        open(finished, 'wb').write('')
    print 'tancant...'
    for db in dblist:
        db.commit()
        db.close()
    print 'fet'
