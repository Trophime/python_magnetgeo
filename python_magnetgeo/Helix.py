#!/usr/bin/env python3
#-*- coding:utf-8 -*-

"""
Provides definition for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""
from typing import List, Type

import math
import json
import yaml
from . import deserialize

from .Shape import Shape
from .ModelAxi import ModelAxi
from .Model3D import Model3D

class Helix(yaml.YAMLObject):
    """
    name :
    r :
    z :
    cutwidth:
    dble :
    odd :

    axi :
    m3d :
    shape :
    """

    yaml_tag = 'Helix'

    def __init__(self, name: str, r: List[float], z: List[float], cutwidth: float, odd: bool, dble: bool, axi: ModelAxi, m3d: Model3D, shape: Shape) -> None:
        """
        initialize object
        """
        self.name = name
        self.dble = dble
        self.odd = odd
        self.r = r
        self.z = z
        self.cutwidth = cutwidth
        self.axi = axi
        self.m3d = m3d
        self.shape = shape

    def get_type(self) -> str:
        if self.m3d.with_shapes and self.m3d.with_channels:
            return "HR"
        return "HL"

    def get_lc(self) -> float:
        return (self.r[1] - self.r[0] ) / 10.

    def get_names(self, mname: str, is2D: bool, verbose: bool = False) -> List[str]:
        """
        return names for Markers
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f'{mname}_'

        sInsulator = "Glue"
        nInsulators = 0
        nturns = self.get_Nturns()
        if self.m3d.with_shapes and self.m3d.with_channels:
            sInsulator = "Kapton"
            htype = "HR"
            angle = self.shape.angle
            nshapes = nturns * (360 / float(angle[0])) # only one angle to be checked
            if verbose:
                print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (
                lambda x: math.ceil(x)
                if math.ceil(x) - x < x - math.floor(x)
                else math.floor(x)
            )(nshapes)
            nInsulators = int(nshapes)
            print("nKaptons=", nInsulators)
        else:
            htype = "HL"
            nInsulators = 1
            if self.dble:
                nInsulators = 2
            if verbose:
                print("helix:", self.name, htype, nturns)

        if is2D:
            nsection = len(self.axi.turns)
            solid_names.append(f"{prefix}Cu{0}")  # HP
            for j in range(nsection):
                solid_names.append(f"{prefix}Cu{j+1}")
            solid_names.append(f"{prefix}Cu{nsection+1}")  # BP
        else:
            solid_names.append("Cu")
            # TODO tell HR from HL
            for j in range(nInsulators):
                solid_names.append(f"{sInsulator}{j}")

        if verbose:
            print(f"Helix_Gmsh[{htype}]: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, odd=%r, dble=%r, r=%r, z=%r, cutwidth=%r, axi=%r, m3d=%r, shape=%r)" % \
               (self.__class__.__name__,
                self.name,
                self.odd,
                self.dble,
                self.r,
                self.z,
                self.cutwidth,
                self.axi,
                self.m3d,
                self.shape
               )

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f'{self.name}.yaml', 'w') as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Helix dump")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f'{self.name}.yaml', 'r') as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception("Failed to load Helix data %s.yaml"%self.name)

        self.name = data.name
        self.dble = data.dble
        self.odd = data.odd
        self.r = data.r
        self.z = data.z
        self.cutwidth = data.cutwidth
        self.axi = data.axi
        self.m3d = data.m3d
        self.shape = data.shape

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(self, default=deserialize.serialize_instance, sort_keys=True, indent=4)


    def from_json(self, string: str):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """
        write from json file
        """
        with open(f'{self.name}.json', 'w') as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    def read_from_json(self):
        """
        read from json file
        """
        with open(f'{self.name}.json', 'r') as istream:
            jsondata = self.from_json(istream.read())

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return self.axi.get_Nturns()

    def create_cut(self, format: str):
        """
        create cut files
        """

        z0 = self.axi.h
        sign = 1
        if self.odd:
            sign = -1

        self.axi.create_cut(format, z0, sign, self.name)

        if self.m3d.with_shapes:
            angles = ' '.join(f'{t:4.2f}' for t in self.shape.angle if t != 0)
            cmd = f'add_shape --angle=\"{angles}\" --shape_angular_length={self.shape.length} --shape={self.shape.name} --format={format} --position=\"{self.shape.position}\"'
            print(f'create_cut: with_shapes not implemented - shall run {cmd}')


    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """
        return (self.r, self.z)

    def htype(self):
        """
        return the type of Helix (aka HR or HL)
        """
        if self.dble:
            return "HL"
        else:
            return "HR"

    def insulators(self):
        """
        return name and number of insulators depending on htype
        """

        sInsulator = "Glue"
        nInsulators = 1
        if self.htype() == "HL":
            nInsulators = 2
        else:
            sInsulator = "Kapton"
            angle = self.shape.angle
            nshapes = self.get_Nturns() * (360 / float(angle[0]))
            # print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

            nshapes = (lambda x: math.ceil(x) if math.ceil(x) - x < x - math.floor(x) else math.floor(x))(nshapes)
            nInsulators = int(nshapes)
            # print("nKaptons=", nInsulators)

        return (sInsulator, nInsulators)

def Helix_constructor(loader, node):
    """
    build an helix object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    dble = values["dble"]
    cutwidth = values["cutwidth"]
    axi = values["axi"]
    m3d = values["m3d"]
    shape = values["shape"]

    return Helix(name, r, z, cutwidth, odd, dble, axi, m3d, shape)

yaml.add_constructor(u'!Helix', Helix_constructor)

