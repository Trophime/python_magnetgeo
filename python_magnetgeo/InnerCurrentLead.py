#!/usr/bin/env python3
# encoding: UTF-8

"""
Provides Inner and OuterCurrentLead class
"""

import json
import yaml


class InnerCurrentLead(yaml.YAMLObject):
    """
    name :
    r : [R0, R1]
    h :
    holes: [H_Holes, Shift_from_Top, Angle_Zero, Angle, Angular_Position, N_Holes]
    support: [R2, DZ]
    fillet:
    """

    yaml_tag = "InnerCurrentLead"

    def __init__(
        self,
        name: str,
        r: list[float],
        h: float = 0.0,
        holes: list = [],
        support: list = [],
        fillet: bool = False,
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.h = h
        self.holes = holes
        self.support = support
        self.fillet = fillet

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, r=%r, h=%r, holes=%r, support=%r, fillet=%r)" % (
            self.__class__.__name__,
            self.name,
            self.r,
            self.h,
            self.holes,
            self.support,
            self.fillet,
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            yaml.dump(self, open(f"{self.name}.yaml", "w"))
        except:
            raise Exception("Failed to dump InnerCurrentLead data")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load InnerCurrentLead data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.h = data.h
        self.holes = data.holes
        self.support = data.support
        self.fillet = data.fillet

    def to_json(self):
        """
        convert from yaml to json
        """
        from . import deserialize

        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def write_to_json(self):
        """
        write from json file
        """
        jsondata = self.to_json()
        try:
            with open(f"{self.name}.json", "w") as ofile:
                ofile.write(str(jsondata))
        except:
            raise Exception(f"Failed to write to {self.name}.json")

    @classmethod
    def from_json(cls, filename: str, debug: bool = False):
        """
        convert from json to yaml
        """
        from . import deserialize

        if debug:
            print(f'InnerCurrentLead.from_json: filename={filename}')
        with open(filename, "r") as istream:
            return json.loads(istream.read(), object_hook=deserialize.unserialize_object)


def InnerCurrentLead_constructor(loader, node):
    """
    build an inner object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    h = values["h"]
    holes = values["holes"]
    support = values["support"]
    fillet = values["fillet"]
    return InnerCurrentLead(name, r, h, holes, support, fillet)


yaml.add_constructor("!InnerCurrentLead", InnerCurrentLead_constructor)

#
# To operate from command line

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name",
        help="name of the inner currentlead model to be stored",
        type=str,
        nargs="?",
    )
    parser.add_argument("--tojson", help="convert to json", action="store_true")
    args = parser.parse_args()

    if not args.name:
        r = [38.6 / 2.0, 48.4 / 2.0]
        h = 480.0
        bars = [123, 12, 90, 60, 45, 3]
        support = [24.2, 0]
        lead = InnerCurrentLead("Inner", r, 480.0, bars, support, False)
        lead.dump()
    else:
        lead = None
        with open(args.name, "r") as f:
            lead = yaml.load(f, Loader=yaml.FullLoader)
        print("lead=", lead)

    if args.tojson:
        lead.write_to_json()
