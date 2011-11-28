INSTALL INSTRUCTIONS

For Windows users, all dependencies are included in the installer.

Ubuntu 11.10 and Debian testing users can simply install the provided .deb package, all dependencies will 
be automatically installed by the package manager

Users of older Ubuntu releases shold manually (or using a .deb package for a newer Ubuntu release) install 
OpenBabel =>2.3.0 and install the PyQt4 version of DecoyFinder 

If you are running an OS for wich there are no DecoyFinder packages available, you must make sure you have all 
the dependencies installed and then it should work from the generic (source) executing:
	python decoy_finder.py

Dependencies:
    - Python >= 2.5,  < 3
    - OpenBabel >= 2.3.0 with python bindings
    - pybel (usually included with OpenBabel python bindings; also part of cinfony)
    - PySide >= 1.0 (or PyQt4 >= 4.6 for PyQt4 version)
    - Qt >= 4.6 (sometimes included with PySide or PyQt)



