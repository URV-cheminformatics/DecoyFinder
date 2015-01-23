INSTALL INSTRUCTIONS

For Windows users, all dependencies are included in the installer.

Ubuntu and Debian users can simply install the provided .deb package, all dependencies will
be automatically installed by the package manager

If you are running an OS for wich there are no DecoyFinder packages available, you must make sure you have all
the dependencies installed and then it should work from the generic (source) executing:
	python decoy_finder.py

Dependencies:
    - Python >= 2.5,  < 3
    - Cinfony
    - RDKit
    - PyQt4 >= 4.6
    - Qt >= 4.6 (sometimes included with PyQt)
Optional:
    - OpenBabel >= 2.3.0 with python bindings
    - pybel (included with OpenBabel python bindings; also part of cinfony)



