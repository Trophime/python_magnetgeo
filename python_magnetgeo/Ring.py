#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Ring:

"""

import json
import yaml
from . import deserialize


class Ring(yaml.YAMLObject):
    """
    name :
    r :
    z :
    angle :
    BPside :
    fillets :
    """

    yaml_tag = "Ring"

    def __init__(
        self,
        name: str,
        r: list[float],
        z: list[float],
        n: int = 0,
        angle: float = 0,
        BPside: bool = True,
        fillets: bool = False,
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.n = n
        self.angle = angle
        self.BPside = BPside
        self.fillets = fillets

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, z=%r, n=%r, angle=%r, BPside=%r, fillets=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.z,
            self.n,
            self.angle,
            self.BPside,
            self.fillets,
        )

    def get_lc(self):
        return (self.r[1] - self.r[0]) / 10.0

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to dump Ring data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name.yaml}", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Ring data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.n = data.n
        self.angle = data.angle
        self.BPside = data.BPside
        self.fillets = data.fillets

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
        with open(f"{self.name}.json", "w") as ostream:
            jsondata = self.to_json()
            ostream.write(str(jsondata))

    def read_from_json(self):
        """
        read from json file
        """
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())


def Ring_constructor(loader, node):
    """
    build an ring object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    n = values["n"]
    angle = values["angle"]
    BPside = values["BPside"]
    fillets = values["fillets"]
    return Ring(name, r, z, n, angle, BPside, fillets)


yaml.add_constructor("!Ring", Ring_constructor)
