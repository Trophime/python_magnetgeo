#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Site:

"""
from typing import Union, Optional, List

import os

import json
import yaml
from . import deserialize


class MSite(yaml.YAMLObject):
    """
    name :
    magnets : dict holding magnet list ("insert", "Bitter", "Supra")
    screens :
    """

    yaml_tag = "MSite"

    def __init__(
        self,
        name: str,
        magnets: Union[str, list, dict],
        screens: Optional[Union[str, list, dict]],
        z_offset: Optional[List[float]],
        r_offset: Optional[List[float]],
        paralax: Optional[List[float]],
    ) -> None:
        """
        initialize onject
        """
        self.name = name
        self.magnets = magnets
        self.screens = screens
        self.z_offset = z_offset
        self.r_offset = r_offset
        self.paralax = paralax

    def __repr__(self):
        """
        representation of object
        """
        return f"name: {self.name}, magnets:{self.magnets}, screens: {self.screens}, z_offset={self.z_offset}, r_offset={self.r_offset}, paralax_offset={self.paralax}"

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> dict:
        """
        get Channels def as dict
        """
        print(f"MSite/get_channels:")

        Channels = {}
        if isinstance(self.magnets, str):
            YAMLFile = f"{self.magnets}.yaml"
            with open(YAMLFile, "r") as f:
                Object = yaml.load(f, Loader=yaml.FullLoader)

            Channels[self.magnets] = Object.get_channels(self.name, hideIsolant, debug)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                magnet = self.magnets[key]
                if isinstance(magnet, str):
                    YAMLFile = f"{magnet}.yaml"
                    with open(YAMLFile, "r") as f:
                        Object = yaml.load(f, Loader=yaml.FullLoader)
                        print(f"{magnet}: {Object}")

                    Channels[key] = Object.get_channels(key, hideIsolant, debug)

                elif isinstance(magnet, list):
                    for part in magnet:
                        if isinstance(part, str):
                            YAMLFile = f"{part}.yaml"
                            with open(YAMLFile, "r") as f:
                                Object = yaml.load(f, Loader=yaml.FullLoader)
                                print(f"{part}: {Object}")
                        else:
                            raise RuntimeError(
                                f"MSite(magnets[{key}][{part}]): unsupported type of magnets ({type(part)})"
                            )

                        _list = Object.get_channels(key, hideIsolant, debug)
                        print(
                            f"MSite/get_channels: key={key} part={part} _list={_list}"
                        )
                        if key in Channels:
                            Channels[key].append(_list)
                        else:
                            Channels[key] = [_list]

                else:
                    raise RuntimeError(
                        f"MSite(magnets[{key}]): unsupported type of magnets ({type(magnet)})"
                    )
        else:
            raise RuntimeError(
                f"MSite: unsupported type of magnets ({type(self.magnets)})"
            )

        return Channels

    def get_isolants(self, mname: str, debug: bool = False) -> dict:
        """
        return isolants
        """
        return {}

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> List[str]:
        """
        return names for Markers
        """
        solid_names = []

        if isinstance(self.magnets, str):
            YAMLFile = f"{self.magnets}.yaml"
            with open(YAMLFile, "r") as f:
                Object = yaml.load(f, Loader=yaml.FullLoader)

            solid_names += Object.get_names(self.name, is2D, verbose)
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                magnet = self.magnets[key]
                if isinstance(magnet, str):
                    mObject = None
                    YAMLFile = f"{magnet}.yaml"
                    with open(YAMLFile, "r") as f:
                        mObject = yaml.load(f, Loader=yaml.FullLoader)
                        # print(f"{magnet}: {mObject}")

                    solid_names += mObject.get_names(key, is2D, verbose)

                elif isinstance(magnet, list):
                    for part in magnet:
                        if isinstance(part, str):
                            mObject = None
                            YAMLFile = f"{part}.yaml"
                            with open(YAMLFile, "r") as f:
                                mObject = yaml.load(f, Loader=yaml.FullLoader)
                                # print(f"{part}: {mObject}")

                            solid_names += mObject.get_names(
                                f"{key}_{mObject.name}", is2D, verbose
                            )
                        else:
                            raise RuntimeError(
                                f"MSite(magnets[{key}][{part}]): unsupported type of magnets ({type(part)})"
                            )

                else:
                    raise RuntimeError(
                        f"MSite/get_names (magnets[{key}]): unsupported type of magnets ({type(magnet)})"
                    )
        else:
            raise RuntimeError(
                f"MSite/get_names: unsupported type of magnets ({type(self.magnets)})"
            )

        # TODO add Screens

        if verbose:
            print(f"MSite/get_names: solid_names {len(solid_names)}")
        return solid_names

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump MSite data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception("Failed to load MSite data %s.yaml" % self.name)

        self.name = data.name
        self.magnets = data.magnets
        self.screens = data.screens

        # TODO: check that magnets are not interpenetring
        # define a boundingBox method for each type: Bitter, Supra, Insert

    def to_json(self):
        """
        convert from yaml to json
        """
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string):
        """
        convert from json to yaml
        """
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """
        write from json file
        """
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    def read_from_json(self):
        """
        read from json file
        """
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())

    def boundingBox(self) -> tuple:
        """"""
        zmin = None
        zmax = None
        rmin = None
        rmax = None

        def cboundingBox(rmin, rmax, zmin, zmax, r, z):
            if zmin == None:
                zmin = min(z)
                zmax = max(z)
                rmin = min(r)
                rmax = max(r)
            else:
                zmin = min(zmin, min(z))
                zmax = max(zmax, max(z))
                rmin = min(rmin, min(r))
                rmax = max(rmax, max(r))
            return (rmin, rmax, zmin, zmax)

        if isinstance(self.magnets, str):
            YAMLFile = os.path.join(f"{self.magnets}.yaml")
            with open(YAMLFile, "r") as istream:
                Object = yaml.load(istream, Loader=yaml.FullLoader)
                (r, z) = Object.boundingBox()
                (rmin, rmax, zmin, zmax) = cboundingBox(rmin, rmax, zmin, zmax, r, z)

        elif isinstance(self.magnets, list):
            for mname in self.magnets:
                YAMLFile = os.path.join(f"{mname}.yaml")
                with open(YAMLFile, "r") as istream:
                    Object = yaml.load(istream, Loader=yaml.FullLoader)
                    (r, z) = Object.boundingBox()
                    (rmin, rmax, zmin, zmax) = cboundingBox(
                        rmin, rmax, zmin, zmax, r, z
                    )
        elif isinstance(self.magnets, dict):
            for key in self.magnets:
                if isinstance(self.magnets[key], str):
                    YAMLFile = os.path.join(f"{self.magnets[key]}.yaml")
                    with open(YAMLFile, "r") as istream:
                        Object = yaml.load(istream, Loader=yaml.FullLoader)
                        (r, z) = Object.boundingBox()
                        (rmin, rmax, zmin, zmax) = cboundingBox(
                            rmin, rmax, zmin, zmax, r, z
                        )
                elif isinstance(self.magnets[key], list):
                    for mname in self.magnets[key]:
                        YAMLFile = os.path.join(f"{mname}.yaml")
                        with open(YAMLFile, "r") as istream:
                            Object = yaml.load(istream, Loader=yaml.FullLoader)
                            (r, z) = Object.boundingBox()
                            (rmin, rmax, zmin, zmax) = cboundingBox(
                                rmin, rmax, zmin, zmax, r, z
                            )
                else:
                    raise Exception(
                        f"magnets: unsupported type {type(self.magnets[key])}"
                    )
        else:
            raise Exception(f"magnets: unsupported type {type(self.magnets)}")

        return ([rmin, rmax], [zmin, zmax])


def MSite_constructor(loader, node):
    """
    build an site object
    """
    print(f"MSite_constructor")
    values = loader.construct_mapping(node)
    name = values["name"]
    magnets = values["magnets"]
    screens = values["screens"]
    z_offset = values["z_offset"]
    r_offset = values["r_offset"]
    paralax = values["paralax"]
    return MSite(name, magnets, screens, z_offset, r_offset, paralax)


yaml.add_constructor("!MSite", MSite_constructor)
