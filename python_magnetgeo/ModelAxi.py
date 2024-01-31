#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for Helix:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
* Shape: definition of Shape eventually added to the helical cut
"""
from typing import List

import json
import yaml
from . import deserialize


class ModelAxi(yaml.YAMLObject):
    """
    name :
    h :
    turns :
    pitch :
    """

    yaml_tag = "ModelAxi"

    def __init__(
        self,
        name: str = "",
        h: float = 0.0,
        turns: List[float] = [],
        pitch: List[float] = [],
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.h = h
        self.turns = turns
        self.pitch = pitch

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, h=%r, turns=%r, pitch=%r)" % (
            self.__class__.__name__,
            self.name,
            self.h,
            self.turns,
            self.pitch,
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

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return sum(self.turns)

    def compact(self, tol: float):
        def indices(lst: list, item: float):
            return [i for i, x in enumerate(lst) if abs(1 - item / x) <= tol]

        List = self.pitch
        duplicates = dict((x, indices(List, x)) for x in set(List) if List.count(x) > 1)
        # print(f"duplicates: {duplicates}")

        sum_index = {}
        for key in duplicates:
            index_fst = duplicates[key][0]
            sum_index[index_fst] = [index_fst]
            search_index = sum_index[index_fst]
            search_elem = search_index[-1]
            for index in duplicates[key]:
                # print(f"index={index}, search_elem={search_elem}")
                if index - search_elem == 1:
                    search_index.append(index)
                    search_elem = index
                else:
                    sum_index[index] = [index]
                    search_index = sum_index[index]
                    search_elem = search_index[-1]

        # print(f"sum_index: {sum_index}")

        remove_ids = []
        for i in sum_index:
            for item in sum_index[i]:
                if item != i:
                    remove_ids.append(item)

        new_pitch = [p for i, p in enumerate(self.pitch) if not i in remove_ids]
        # print(f"pitch={self.pitch}")
        # print(f"new_pitch={new_pitch}")

        new_turns = (
            self.turns
        )  # use deepcopy: import copy and copy.deepcopy(self.axi.turns)
        for i in sum_index:
            for item in sum_index[i]:
                new_turns[i] += self.turns[item]
        new_turns = [p for i, p in enumerate(self.turns) if not i in remove_ids]
        # print(f"turns={self.turns}")
        # print(f"new_turns={new_turns}")

        return new_turns, new_pitch

    def create_cut(
        self, format: str, z0: float, sign: int, name: str, append: bool = False
    ):
        """
        create cut file
        """

        dformat = {
            "salome": {"run": self.salome_cut, "extension": "_cut_salome.dat"},
        }

        try:
            format_cut = dformat[format]
        except:
            raise RuntimeError(
                f"create_cut: format={format} unsupported\nallowed formats are: {dformat.keys()}"
            )

        write_cut = format_cut["run"]
        ext = format_cut["extension"]
        filename = f"{name}{ext}"
        write_cut(z0, sign, filename, append)

    def salome_cut(self, z0: float, sign: int, filename: str, append: bool):
        """
        for salome
        see: MagnetTools/MagnetField/Stack.cc write_salome_paramfile L1011

        for case wwith shapes
        see README files in calcul19 ~/github/hifimanget/projects
        for example HR-54/README:
        H2: Shape_HR-54-116.dat - HR-54-254
        H1: Shape_HR-54-117.dat - HR-54-260

        run add_shape from magnettools

        add_shape --angle="30" --shape_angular_length=8 \
            --shape=HR-54-116 05012011Pbis_H2 --format=LNCMI --position="ABOVE"
        add_shape --angle="36" --shape_angular_length=13 \
            --shape=HR-54-116 05012011Pbis_H1 --format=LNCMI --position="ABOVE"
        """
        from math import pi

        z = z0
        theta = 0
        shape_id = 0
        tab = "\t"

        # 'x' create file, 'a' append to file, Append and Read (‘a+’)
        flag = "x"
        if append:
            flag = "a"
        with open(filename, flag) as f:
            f.write(f"#theta[rad]{tab}Shape_id[]{tab}tZ[mm]\n")
            f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")

            # TODO use compact to reduce size of cuts
            for i, (turn, pitch) in enumerate(zip(self.turns, self.pitch)):
                theta += turn * (2 * pi) * sign
                z -= turn * pitch
                f.write(f"{theta*(-sign):12.8f}{tab}{shape_id:8}{tab}{z:12.8f}\n")


def ModelAxi_constructor(loader, node):
    """
    build an ModelAxi object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    h = values["h"]
    turns = values["turns"]
    pitch = values["pitch"]
    return ModelAxi(name, h, turns, pitch)


yaml.add_constructor("!ModelAxi", ModelAxi_constructor)
