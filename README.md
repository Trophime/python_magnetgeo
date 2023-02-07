---
title: Python Magnet Geometry
---

[![image](https://img.shields.io/pypi/v/python_magnetgeo.svg)](https://pypi.python.org/pypi/python_magnetgeo)

[![image](https://img.shields.io/travis/Trophime/python_magnetgeo.svg)](https://travis-ci.com/Trophime/python_magnetgeo)

[![Documentation Status](https://readthedocs.org/projects/python-magnetgeo/badge/?version=latest)](https://python-magnetgeo.readthedocs.io/en/latest/?version=latest)

[![Updates](https://pyup.io/repos/github/Trophime/python_magnetgeo/shield.svg)](https://pyup.io/repos/github/Trophime/python_magnetgeo/)

Python Magnet Geometry contains magnet geometrical models

-   Free software: MIT license
-   Documentation: <https://python-magnetgeo.readthedocs.io>.

Features
========

-   Define Magnet geometry as yaml files
-   Load/Create CAD and Mesh with Salome (see hifimagnet.salome)
-   Create Gmsh mesh from Salome XAO format

INSTALL
=======

To install in a python virtual env

```
python -m venv --system-site-packages magnetgeo-env
source ./magnetgeo-env/bin/activate
pip install -r requirements.txt
```

Examples
========

```
python3 -m python_magnetgeo.xao --wd /data/geometries test-Axi.xao --geo test.yaml mesh --group CoolingChannels
python3 -m python_magnetgeo.xao --wd /data/geometries M9_HLtest-Axi.xao --geo M9_HLtest.yaml mesh --group CoolingChannels
python3 -m python_magnetgeo.xao --wd /data/geometries Pancakes-pancake-Axi.xao --geo HTS-pancake-test.yaml [mesh []]
```

Credits
=======

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
