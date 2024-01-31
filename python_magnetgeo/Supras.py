#!/usr/bin/env python3
# encoding: UTF-8

"""defines Supra Insert structure"""

import json
import yaml
from . import deserialize


class Supras(yaml.YAMLObject):
    """
    name :
    magnets :

    innerbore:
    outerbore:
    """

    yaml_tag = "Supras"

    def __init__(
        self, name: str, magnets: list, innerbore: float, outerbore: float
    ) -> None:
        """constructor"""
        self.name = name
        self.magnets = magnets
        self.innerBore = innerbore
        self.outerBore = outerbore

    def __repr__(self):
        """representation"""
        return "%s(name=%r, magnets=%r, innerbore=%r, outerbore=%r)" % (
            self.__class__.__name__,
            self.name,
            self.magnets,
            self.innerbore,
            self.outerbore,
        )

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        return {}

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        return isolants
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> list[str]:
        """
        return names for Markers
        """
        solid_names = []
        if isinstance(self.magnets, str):
            YAMLFile = f"{self.magnets}.yaml"
            with open(YAMLFile, "r") as f:
                Object = yaml.load(f, Loader=yaml.FullLoader)

            solid_names += Object.get_names(self.name, is2D, verbose)
        elif isinstance(self.magnets, list):
            for magnet in self.magnets:
                YAMLFile = f"{magnet}.yaml"
                with open(YAMLFile, "r") as f:
                    Object = yaml.load(f, Loader=yaml.FullLoader)

                solid_names += Object.get_names(magnet, is2D, verbose)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                magnet = self.magnets[key]
                YAMLFile = f"{magnet}.yaml"
                with open(YAMLFile, "r") as f:
                    Object = yaml.load(f, Loader=yaml.FullLoader)

                solid_names += Object.get_names(self.name, is2D, verbose)
        else:
            raise RuntimeError(
                f"Supras/get_names: unsupported type of magnets ({type(self.magnets)})"
            )

        if verbose:
            print(f"Supras_Gmsh: solid_names {len(solid_names)}")
        return solid_names

    def dump(self):
        """dump to a yaml file name.yaml"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Supras dump")

    def load(self):
        """load from a yaml file"""
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Insert data {self.name}.yaml")

        self.name = data.name
        self.magnets = data.magnets

        self.innerbore = data.innerbore
        self.outerbore = data.outerbore

    def to_json(self):
        """convert from yaml to json"""
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string: str):
        """get from json"""
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """write to a json file"""
        with open(f"{self.name}.son", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    def read_from_json(self):
        """read from a json file"""
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())

    ###################################################################
    #
    #
    ###################################################################

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]

        so far exclude Leads
        """

        rb = [0, 0]
        zb = [0, 0]

        for i, mname in enumerate(self.magnets):
            Supra = None
            with open(f"{mname}.yaml", "r") as f:
                Supra = yaml.load(f, Loader=yaml.FullLoader)

            if i == 0:
                rb = Supra.r
                zb = Supra.z

            rb[0] = min(rb[0], Supra.r[0])
            zb[0] = min(zb[0], Supra.z[0])
            rb[1] = max(rb[1], Supra.r[1])
            zb[1] = max(zb[1], Supra.z[1])

        return (rb, zb)

    def intersect(self, r, z):
        """
        Check if intersection with rectangle defined by r,z is empty or not

        return False if empty, True otherwise
        """

        (r_i, z_i) = self.boundingBox()

        # TODO take into account Mandrin and Isolation even if detail="None"
        collide = False
        isR = abs(r_i[0] - r[0]) < abs(r_i[1] - r_i[0] + r[0] + r[1]) / 2.0
        isZ = abs(z_i[0] - z[0]) < abs(z_i[1] - z_i[0] + z[0] + z[1]) / 2.0
        if isR and isZ:
            collide = True
        return collide

    def Create_AxiGeo(self, AirData):
        """
        create Axisymetrical Geo Model for gmsh

        return
        H_ids, BC_ids, Air_ids, BC_Air_ids
        """
        pass


def Supras_constructor(loader, node):
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    innerbore = 0
    if "innerbore":
        innerbore = values["innerbore"]
    outerbore = 0
    if "outerbore":
        outerbore = values["outerbore"]
    return Supras(name, magnets, innerbore, outerbore)


yaml.add_constructor("!Supras", Supras_constructor)
