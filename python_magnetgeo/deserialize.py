#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides tools to un/serialize data from json
"""

from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D
from .Helix import Helix
from .Ring import Ring
from .InnerCurrentLead import InnerCurrentLead
from .OuterCurrentLead import OuterCurrentLead
from .Insert import Insert
from .Bitter import Bitter
from .Supra import Supra
from .Screen import Screen
from .MSite import MSite
from .Bitters import Bitters
from .Supras import Supras
from .Shape2D import Shape2D
from .tierod import Tierod
from .coolingslit import CoolingSlit


# From : http://chimera.labs.oreilly.com/books/1230000000393/ch06.html#_discussion_95
# Dictionary mapping names to known classes

classes = {
    "Shape": Shape,
    "ModelAxi": ModelAxi,
    "Model3D": Model3D,
    "Helix": Helix,
    "Ring": Ring,
    "InnerCurrentLead": InnerCurrentLead,
    "OuterCurrentLead": OuterCurrentLead,
    "Insert": Insert,
    "Bitter": Bitter,
    "Supra": Supra,
    "Screen": Screen,
    "Bitters": Bitters,
    "Supras": Supras,
    "MSite": MSite,
    "Shape2D": Shape2D,
    "Tierod": Tierod,
    "CoolingSlit": CoolingSlit,
}


def serialize_instance(obj):
    """
    serialize_instance of an obj
    """
    d = {"__classname__": type(obj).__name__}
    d.update(vars(obj))
    return d


def unserialize_object(d):
    """
    unserialize_instance of an obj
    """
    clsname = d.pop("__classname__", None)
    if clsname:
        cls = classes[clsname]
        obj = cls.__new__(cls)  # Make instance without calling __init__
        for key, value in d.items():
            setattr(obj, key, value)
        return obj
    else:
        return d
