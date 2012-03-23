#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
#       mol2db.py is part of Decoy Finder
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
import glob, time
import mysql.connector as mysql
import sqlite3

insert_template = """REPLACE INTO Molecules (`inchikey`, `maccs`, `rotatable_bonds`, `weight`, `logp`, `hba`, `hbd`, `mol`, `tpsa`) VALUES ("%s", "%s", %s, %s, %s, %s,%s, "%s", %s);"""

filelist = glob.glob('ZINC_0.9_2/*.sdf')

#filelist = ['/home/adria/ZINC.sdf']

if __name__ == "__main__":
    dblist = set()
    sqlitedb = sqlite3.connect('sql/decoyfinder.db')
    lcur = sqlitedb.cursor()
    sqlfile = open('sql/molecules_sqlite.sql', 'rb')
    lcur.execute(sqlfile.read())
    sqlfile.close()
    sqlitedb.commit()
    lcur.close()
    dblist.add(sqlitedb)
#    mysqldb = mysql.Connect(host="10.30.233.105"
#                                     ,user="adria"
#                                     ,password="decoyfinder")
#    mysqldb = mysql.Connect(host="localhost"
#                                     ,user="adria"
#                                     ,password="decoyfinder")
#    mcur = mysqldb.cursor()
#    sqlfile = open('sql/molecules.sql', 'rb')
#    mcur.execute(sqlfile.read())
#    sqlfile.close()
#    mysqldb.commit()
#    mcur.close()
#    dblist.add(mysqldb)
#
    sl_known_keys = set()
    ms_known_keys = set()
    cur = sqlitedb.cursor()
    cur.execute("""SELECT inchikey FROM Molecules;""")
    for row in cur:
        sl_known_keys.update(row)
    cur.close()
#    cur = mysqldb.cursor()
#    cur.execute("""SELECT inchikey FROM Molecules;""")
#    for row in cur:
#        ms_known_keys.update(row)
#    cur.close()
    known_keys = sl_known_keys #&  ms_known_keys
#    if not known_keys:
#
#
#        for key in sl_known_keys:
#            cur = sqlitedb.cursor()
#            cur.execute("""SELECT `inchikey`, `maccs`, `rotatable_bonds`, `weight`, `logp`, `hba`, `hbd`, `mol`, `tpsa` FROM Molecules WHERE inchikey = '%s'""" % key)
#            insert_str = insert_template % cur.fetchone()
#            print insert_str
#            cur2 = mysqldb.cursor()
#            cur2.execute(insert_str)
#            cur2.close()
#            mysqldb.commit()
#            time.sleep(1)
#            cur.close()
#        cur = mysqldb.cursor()
#        for key in ms_known_keys:
#            cur.execute("""SELECT `inchikey`, `maccs`, `rotatable_bonds`, `weight`, `logp`, `hba`, `hbd`, `mol`, `tpsa` FROM Molecules WHERE inchikey = '%s'""" % key)
#            insert_str = insert_template % cur.fetchone()
#            cur2 = sqlitedb.cursor()
#            cur2.execute(insert_str)
#            cur2.close()
#        cur.close()
#        sqlitedb.commit()
#        known_keys = ms_known_keys | sl_known_keys

    recordcount = 0
    LASTCOMMIT = 0
    COMMIT = 0
    for file in filelist:
        finished = file + '_finished'
        if os.path.exists(finished):
            continue
        print '####################################%s##################################' % file
        mols = pybel.readfile('sdf', file)
        for mol in mols:
            #print 'emmagatzemant en MDL MOL'
            mdlmol = mol.write('mol')
            #print 'calculant inchikey'
            inchikey = mol.write('inchikey').strip()[:25]
            if inchikey in known_keys:
                print len(known_keys)
                known_keys.discard(inchikey)
                continue
            tries = 0
            while tries <3:
                try:
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
                    recordcount +=1
                    break
                except Exception, e:
                    tries +=1
                    mol = pybel.readstring('sdf', mdlmol)
            else:
                continue
            #print "fent l'insert"
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
            if recordcount - LASTCOMMIT > 999:
                    COMMIT = 2
                    LASTCOMMIT = recordcount
            for db in dblist:
                cursor = None
                try:
                    cursor = db.cursor()
                    #print "Executing:"
#                   print insert_str
                    cursor.execute(insert_str)
                    #db.commit()
                    cursor.close()
                except Exception, e:
                    print e
                finally:
                    if cursor:
                        cursor.close()

                if COMMIT:
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
        open(finished, 'wb').write('')
    print 'tancant...'
    for db in dblist:
        db.close()
    print 'fet'
