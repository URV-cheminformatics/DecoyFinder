#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       find_decoys.py is part of Decoy Finder
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

import pybel

import mysql.connector
import sqlite3

insert_template = """REPLACE INTO Molecules (`inchikey`, `maccs`, `rotatable_bonds`, `weight`, `logp`, `hba`, `hbd`, `mol`, `tpsa`) VALUES ("%s", "%s", %s, %s, %s, %s,%s, "%s", %s);"""

filelist = ['/home/ssorgatem/uni/PEI/ZINC/3_p1.0.sdf', ]

if __name__ == "__main__":
    sqlitedb = sqlite3.connect('sql/decoyfinder.db')
    lcur = sqlitedb.cursor()
    sqlfile = open('sql/molecules_sqlite.sql', 'rb')
    lcur.execute(sqlfile.read())
    sqlfile.close()
    sqlitedb.commit()
    lcur.close()

    mysqldb = mysql.connector.Connect(host="localhost"
                                 ,user="root"
                                 ,password="")
  #                               ,database="decoyfinder")
    mcur = mysqldb.cursor()
    sqlfile = open('sql/molecules.sql', 'rb')
    mcur.execute(sqlfile.read())
    sqlfile.close()
    mysqldb.commit()
    mcur.close()
    recordcount = 0
    for file in filelist:
        mols = pybel.readfile('sdf', file)
        for mol in mols:
            inchikey = mol.write('inchikey').strip()[:25]
            mdlmol = mol.write('mol')
            maccs = repr(mol.calcfp('MACCS').bits)
            rotatable_bonds = str(mol.OBMol.NumRotors())
            weight = str(mol.molwt)
            hba = str(mol.calcdesc(['HBA2'])['HBA2'])
            hbd = str(mol.calcdesc(['HBD'])['HBD'])
            logp = str(mol.calcdesc(['logP'])['logP'])
            tpsa = str(mol.calcdesc(['TPSA'])['TPSA'])
            recordcount +=1
            insert_str = insert_template % (inchikey
                                                            , maccs
                                                            , rotatable_bonds
                                                            , weight
                                                            , logp
                                                            , hba
                                                            , hbd
                                                            , mdlmol
                                                            , tpsa
                                                            )
            for db in (sqlitedb, mysqldb):
                cursor = db.cursor()
#                print "Executing:"
#                print insert_str
                cursor.execute(insert_str)
                db.commit()
                cursor.close()
            print recordcount,
    print 'tancant...'
    for db in (sqlitedb, mysqldb):
        db.close()
    print 'fet'
