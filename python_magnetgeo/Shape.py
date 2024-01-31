#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""

import json
import yaml
from . import deserialize

# from Shape import *
# from ModelAxi import *
# from Model3D import *


class Shape(yaml.YAMLObject):
    """
    name :
    profile : name of the cut profile to be added
      if some ids are non-nul it means that micro-channels are to be added

    params :
      length : specify shape angular length in degree - single value or list
      angle : angle between 2 consecutive shape (in deg) - single value or list
      onturns : specify on which turns to add cuts - single value or list
      position : ABOVE|BELLOW|ALTERNATE
    """

    yaml_tag = "Shape"

    def __init__(
        self,
        name: str,
        profile: str,
        length: list[float] = [0.0],
        angle: list[float] = [0.0],
        onturns: list[int] = [1],
        position: str = "ABOVE",
    ):
        """
        initialize object
        """
        self.name = name
        self.profile = profile
        self.length = length
        self.angle = angle
        self.onturns = onturns
        self.position = position

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, profile=%r, length=%r, angle=%r, onturns=%r, position=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.profile,
                self.length,
                self.angle,
                self.onturns,
                self.position,
            )
        )

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


def Shape_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    profile = values["profile"]
    length = values["length"]
    angle = values["angle"]
    onturns = values["onturns"]
    position = values["position"]
    return Shape(name, profile, length, angle, onturns, position)


yaml.add_constructor(u"!Shape", Shape_constructor)
