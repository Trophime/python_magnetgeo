#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definition for Bitter:

* Geom data: r, z
* Model Axi: definition of helical cut (provided from MagnetTools)
* Model 3D: actual 3D CAD
"""
from typing import List

import json
import yaml
from . import deserialize

from .ModelAxi import ModelAxi
from .coolingslit import CoolingSlit
from .tierod import Tierod


class Bitter(yaml.YAMLObject):
    """
    name :
    r :
    z :

    axi :
    coolingslits: [(r, angle, n, dh, sh, shape)]
    tierods: [r, n, shape]
    """

    yaml_tag = "Bitter"

    def __init__(
        self,
        name,
        r: List[float],
        z: List[float],
        odd: bool,
        axi: ModelAxi,
        coolingslits: List[CoolingSlit],
        tierod: Tierod,
        innerbore: float,
        outerbore: float,
    ) -> None:
        """
        initialize object
        """
        self.name = name
        self.r = r
        self.z = z
        self.odd = odd
        self.axi = axi
        self.innerbore = innerbore
        self.outerbore = outerbore
        self.coolingslits = coolingslits
        self.tierod = tierod

    def equivalent_eps(self, i: int):
        """
        eps: thickness of annular ring equivalent to n * coolingslit surface
        """
        from math import pi

        slit = self.coolingslits[i]
        x = slit.r
        eps = slit.n * slit.sh / (2 * pi * x)
        return eps

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[str]:
        """
        return channels
        """
        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Channels = [f"{prefix}Slit{0}"]
        n_slits = 0
        if self.coolingslits:
            n_slits = len(self.coolingslits)
            print(f"Bitter({self.name}): CoolingSlits={n_slits}")

            Channels += [f"{prefix}Slit{i+1}" for i in range(n_slits)]
        Channels += [f"{prefix}Slit{n_slits+1}"]
        print(f"Bitter({prefix}): {Channels}")
        return Channels

    def get_lc(self) -> float:
        lc = (self.r[1] - self.r[0]) / 10.0
        if self.coolingslits:
            x: float = self.r[0]
            dr: List[float] = []
            for slit in self.coolingslits:
                _x = slit.r
                dr.append(_x - x)
                x = _x
            dr.append(self.r[1] - x)
            # print(f"Bitter: dr={dr}")
            lc = min(dr) / 5.0

        return lc

    def get_isolants(self, mname: str, debug: bool = False) -> List[str]:
        """
        return isolants
        """
        return []

    def get_names(
        self, mname: str, is2D: bool = False, verbose: bool = False
    ) -> List[str]:
        """
        return names for Markers
        """
        tol = 1.0e-10
        solid_names = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Nslits = 0
        if self.coolingslits:
            Nslits = len(self.coolingslits)

        if is2D:
            nsection = len(self.axi.turns)
            if self.z[0] < -self.axi.h and abs(self.z[0] + self.axi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B0_Slit{i}")

            for j in range(nsection):
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{j+1}_Slit{i}")

            if self.z[1] > self.axi.h and abs(self.z[1] - self.axi.h) >= tol:
                for i in range(Nslits + 1):
                    solid_names.append(f"{prefix}B{nsection+1}_Slit{i}")
        else:
            solid_names.append(f"{prefix}B")
            solid_names.append(f"{prefix}Kapton")
        if verbose:
            print(f"Bitter/get_names: solid_names {len(solid_names)}")
        return solid_names

    def __repr__(self):
        """
        representation of object
        """
        return (
            "%s(name=%r, r=%r, z=%r, odd=%r, axi=%r, coolingslits=%r, tierod=%r, innerbore=%r, outerbore=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.r,
                self.z,
                self.odd,
                self.axi,
                self.coolingslits,
                self.tierod,
                self.innerbore,
                self.outerbore,
            )
        )

    def dump(self):
        """
        dump object to file
        """
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Bitter dump")

    def load(self):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Bitter data {self.name}.yaml")

        self.name = data.name
        self.r = data.r
        self.z = data.z
        self.odd = data.odd
        self.axi = data.axi
        self.coolingslits = data.coolingslits
        self.tierod = data.tierod
        self.innerbore = data.innerbore
        self.outerbore = data.outerbore

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
            ostream.write(jsondata)

    def read_from_json(self):
        """
        read from json file
        """
        with open(f"{self.name}.json", "r") as istream:
            jsondata = self.from_json(istream.read())

    def get_Nturns(self) -> float:
        """
        returns the number of turn
        """
        return self.axi.get_Nturns()

    def boundingBox(self) -> tuple:
        """
        return Bounding as r[], z[]
        """

        return (self.r, self.z)

    def intersect(self, r: List[float], z: List[float]) -> bool:
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

    def get_params(self, workingDir: str = ".") -> tuple:
        from math import pi

        tol = 1.0e-10

        Dh = [2 * (self.r[0] - self.innerbore)]
        Sh = [pi * (self.r[0] - self.innerbore) * (self.r[0] + self.innerbore)]
        filling_factor = [1]
        nslits = 0
        if self.coolingslits:
            nslits = len(self.coolingslits)
            Dh += [slit.dh for slit in self.coolingslits]
            # Dh += [2 * self.equivalent_eps(n) for n in range(len(self.coolingslits))]
            Sh += [slit.n * slit.sh for slit in self.coolingslits]

            # wetted perimeter per slit: (4*slit.sh)/slit.dh
            # wetted perimeter for annular ring: 2*pi*(slit.r-eps) + 2*pi*(slit.r+eps)
            # with eps = self.equivalent_eps(n)
            filling_factor += [
                slit.n * ((4 * slit.sh) / slit.dh) / (4 * pi * slit.r)
                for slit in self.coolingslits
            ]
        Dh += [2 * (self.outerbore - self.r[1])]
        Sh += [pi * (self.outerbore - self.r[1]) * (self.outerbore + self.r[1])]

        Zh = [self.z[0]]
        z = -self.axi.h
        if abs(self.z[0] - z) >= tol:
            Zh.append(z)
        for n, p in zip(self.axi.turns, self.axi.pitch):
            z += n * p
            Zh.append(z)
        if abs(self.z[1] - z) >= tol:
            Zh.append(self.z[1])
        print(f"Zh={Zh}")

        filling_factor.append(1)
        print(f"filling_factor={filling_factor}")

        # return (nslits, Dh, Sh, Zh)
        return (nslits, Dh, Sh, Zh, filling_factor)

    def create_cut(self, format: str):
        """
        create cut files
        """

        z0 = self.axi.h
        sign = 1
        if self.odd:
            sign = -1

        self.axi.create_cut(format, z0, sign, self.name)


def Bitter_constructor(loader, node):
    """
    build an bitter object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    r = values["r"]
    z = values["z"]
    odd = values["odd"]
    axi = values["axi"]
    coolingslits = values["coolingslits"]
    tierod = values["tierod"]
    innerbore = 0
    if "innerbore":
        innerbore = values["innerbore"]
    outerbore = 0
    if "outerbore":
        outerbore = values["outerbore"]

    return Bitter(name, r, z, odd, axi, coolingslits, tierod, innerbore, outerbore)


yaml.add_constructor("!Bitter", Bitter_constructor)

if __name__ == "__main__":
    from .Shape2D import Shape2D

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    dh = 4 * 1
    sh = 1 * 1
    tierod = Tierod(2, 20, dh, sh, Square)

    Square = Shape2D("square", [[0, 0], [1, 0], [1, 1], [0, 1]])
    slit1 = CoolingSlit(2, 5, 20, 0.1, 0.2, Square)
    slit2 = CoolingSlit(10, 5, 20, 0.1, 0.2, Square)
    coolingSlits = [slit1, slit2]

    Axi = ModelAxi("test", 0.9, [2], [0.9])

    innerbore = 1 - 0.01
    outerbore = 2 + 0.01
    bitter = Bitter(
        "B", [1, 2], [-1, 1], True, Axi, coolingSlits, tierod, innerbore, outerbore
    )
    bitter.dump()

    with open("B.yaml", "r") as f:
        bitter = yaml.load(f, Loader=yaml.FullLoader)

    print(bitter)
    for i, slit in enumerate(bitter.coolingslits):
        print(f"slit[{i}]: {slit}, shape={slit.shape}")
