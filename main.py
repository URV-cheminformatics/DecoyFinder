#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pybel

##### Aquesta part és necessària per a poder fer servir MACCS fingerprinting des de python
pybel.fps.append("MACCS")
pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)
#####





mol = pybel.readstring("smi", "CCCC(=O)Cl")
print mol.calcfp("MACCS").bits
