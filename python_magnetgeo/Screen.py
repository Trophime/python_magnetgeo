#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Screen:

* Geom data: r, z
"""

import json
import yaml
from . import deserialize


class Screen(yaml.YAMLObject):
    """
    name :
    r :
    z :
    """

    yaml_tag = "Screen"

    def __init__(self, name: str, r: list[float], z: list[float]):
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z

    def get_lc(self):
        return (self.r[1] - self.r[0]) / 10.0

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> list:
        return []

    def get_isolants(self, mname: str, debug: bool = False):
        """
        return isolants
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
        """
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        solid_names.append(f"{prefix}{self.name}_Screen")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            ostream = open(self.name + ".yaml", "w")
            yaml.dump(self, stream=ostream)
            ostream.close()
        except:
            raise Exception("Failed to Screen dump")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Screen data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string: str):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """
        write from json file
        """
        ostream = open(self.name + ".json", "w")
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    def read_from_json(self):
        """
        read from json file
        """
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """
        # TODO take into account Mandrin and Isolation even if detail="None"
        return (self.r, self.z)

    def intersect(self, r: list[float], z: list[float]) -> bool:
        """
        Check if intersection with rectangle defined by r,z is empty or not

        return False if empty, True otherwise
        """

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(self.r[0] - r[0]) < abs(self.r[1] - self.r[0] + r[0] + r[1]) / 2.0
        isZ = abs(self.z[0] - z[0]) < abs(self.z[1] - self.z[0] + z[0] + z[1]) / 2.0
        if isR and isZ:
            collide = True
        return collide


def Screen_constructor(loader, node):
    """
    build an screen object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    return Screen(name, r, z)


yaml.add_constructor("!Screen", Screen_constructor)
