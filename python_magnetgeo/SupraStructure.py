"""
Define HTS insert geometry
"""
from typing import Self, Optional


def flatten(S: list) -> list:
    from pandas.core.common import flatten as pd_flatten

    return list(pd_flatten(S))


class tape:
    """
    HTS tape

    w: width
    h: height
    e: thickness of co-wound durnomag
    """

    def __init__(self, w: float = 0, h: float = 0, e: float = 0) -> None:
        self.w: float = w
        self.h: float = h
        self.e: float = e

    @classmethod
    def from_data(cls, data: dict) -> Self:
        w = h = e = 0
        if "w" in data:
            w: float = data["w"]
        if "h" in data:
            h: float = data["h"]
        if "e" in data:
            e: float = data["e"]
        return cls(w, h, e)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"tape(w={self.w}, h={self.h}, e={self.e}"

    def __str__(self) -> str:
        msg = "\n"
        msg += f"width: {self.w} [mm]\n"
        msg += f"height: {self.h} [mm]\n"
        msg += f"e: {self.e} [mm]\n"
        return msg

    def get_names(self, name: str, detail: str, verbose: bool = False) -> list[str]:
        _tape = f"{name}_SC"
        _e = f"{name}_Duromag"
        return [_tape, _e]

    def getH(self) -> float:
        """
        get tape height
        """
        return self.h

    def getW(self) -> float:
        """
        get total width
        """
        return self.w + self.e

    def getW_Sc(self) -> float:
        """
        get Sc width
        """
        return self.w

    def getW_Isolation(self) -> float:
        """
        get Isolation width
        """
        return self.e

    def getArea(self) -> float:
        """
        get tape cross section surface
        """
        return (self.w + self.e) * self.h

    def getFillingFactor(self) -> float:
        """
        get tape filling factor (aka ratio of superconductor over tape section)
        """
        return (self.w * self.h) / self.getArea()


class pancake:
    """
    Pancake structure

    r0:
    mandrin: mandrin (only for mesh purpose)
    tape: tape used for pancake
    n: number of tapes
    """

    def __init__(
        self, r0: float = 0, tape: tape = tape(), n: int = 0, mandrin: int = 0
    ) -> None:
        self.mandrin = mandrin
        self.tape = tape
        self.n = n
        self.r0 = r0

    @classmethod
    def from_data(cls, data={}) -> Self:
        r0 = 0
        n = 0
        t_ = tape()
        mandrin = 0
        if "r0" in data:
            r0 = data["r0"]
        if "mandrin" in data:
            mandrin = data["mandrin"]
        if "tape" in data:
            t_ = tape.from_data(data["tape"])
        if "ntapes" in data:
            n = data["ntapes"]
        return cls(r0, t_, n, mandrin)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return "pancake(r0={%r, n=%r, tape=%r, mandrin=%r)" % (
            self.r0,
            self.n,
            self.tape,
            self.mandrin,
        )

    def __str__(self) -> str:
        msg = "\n"
        msg += f"r0: {self.r0} [m]\n"
        msg += f"mandrin: {self.mandrin} [m]\n"
        msg += f"ntapes: {self.n} \n"
        msg += f"tape: {self.tape}***\n"
        return msg

    def get_names(
        self, name: str, detail: str, verbose: bool = False
    ) -> str | list[str]:
        if detail == "pancake":
            return name
        else:
            _mandrin = f"{name}_Mandrin"
            tape_ = self.tape
            tape_ids = []
            for i in range(self.n):
                tape_id = tape_.get_names(f"{name}_t{i}", detail)
                tape_ids.append(tape_id)

            if verbose:
                print(f"pancake: mandrin (1), tapes ({len(tape_ids)})")
            return flatten([[_mandrin], flatten(tape_ids)])
        pass

    def getN(self) -> int:
        """
        get number of tapes
        """
        return self.n

    def getTape(self) -> tape:
        """
        return tape object
        """
        return self.tape

    def getR0(self) -> float:
        """
        get pancake inner radius
        """
        return self.r0

    def getMandrin(self) -> float:
        """
        get pancake mandrin inner radius
        """
        return self.mandrin

    def getR1(self) -> float:
        """
        get pancake outer radius
        """
        return self.n * (self.tape.w + self.tape.e) + self.r0

    def getR(self) -> list[float]:
        """
        get list of tapes inner radius
        """
        r = []
        ri = self.getR0()
        dr = self.tape.w + self.tape.e
        for i in range(self.n):
            # print(f"r[{i}]={ri}, {ri+self.tape.w + self.tape.e/2.}")
            r.append(ri)
            ri += dr
        # print(f"r[-1]: {r[0]}, {r[-1]}, {r[-1]+self.tape.w + self.tape.e/2.}, {self.n}, {self.getR1()}")
        return r

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = self.n * self.tape.w * self.tape.h
        return S_tapes / self.getArea()

    def getW(self) -> float:
        return self.getR1() - self.getR0()

    def getH(self) -> float:
        return self.tape.getH()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()


class isolation:
    """
    Isolation

    r0: inner radius of isolation structure
    w: widths of the different layers
    h: heights of the different layers
    """

    def __init__(self, r0: float = 0, w: list = [], h: list = []):
        self.r0 = r0
        self.w = w
        self.h = h

    @classmethod
    def from_data(cls, data: dict) -> Self:
        r0 = 0
        w = []
        h = []
        if "r0" in data:
            r0 = data["r0"]
        if "w" in data:
            w = data["w"]
        if "h" in data:
            h = data["h"]
        return cls(r0, w, h)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"isolation(r0={self.r0}, w={self.w}, h={self.h}"

    def __str__(self) -> str:
        msg = "\n"
        msg += f"r0: {self.r0} [mm]\n"
        msg += f"w: {self.w} \n"
        msg += f"h: {self.h} \n"
        return msg
        pass

    def get_names(self, name: str, detail: str, verbose: bool = False) -> str:
        return name

    def getR0(self) -> float:
        """
        return the inner radius of isolation
        """
        return self.r0

    def getW(self) -> float:
        """
        return the width of isolation
        """
        return max(self.w)

    def getH_Layer(self, i: int) -> float:
        """
        return the height of isolation layer i
        """
        return self.h[i]

    def getW_Layer(self, i: int) -> float:
        """
        return the width of isolation layer i
        """
        return self.w[i]

    def getH(self) -> float:
        """
        return the total heigth of isolation
        """
        return sum(self.h)

    def getLayer(self) -> int:
        """
        return the number of layer
        """
        return len(self.w)


class dblpancake:
    """
    Double Pancake structure

    z0: position of the double pancake (centered on isolation)
    pancake: pancake structure (assume that both pancakes have the same structure)
    isolation: isolation between pancakes
    """

    def __init__(
        self,
        z0: float,
        pancake: pancake = pancake(),
        isolation: isolation = isolation(),
    ):
        self.z0 = z0
        self.pancake = pancake
        self.isolation = isolation

    def __repr__(self) -> str:
        """
        representation of object
        """
        return f"dblpancake(z0={self.z0}, pancake={self.pancake}, isolation={self.isolation}"

    def __str__(self) -> str:
        msg = f"r0={self.pancake.getR0()}, "
        msg += f"r1={self.pancake.getR1()}, "
        msg += f"z1={self.getZ0() - self.getH()/2.}, "
        msg += f"z2={self.getZ0() + self.getH()/2.}"
        msg += f"(z0={self.getZ0()}, h={self.getH()})"
        return msg

    def get_names(
        self, name: str, detail: str, verbose: bool = False
    ) -> str | list[str]:
        if detail == "dblpancake":
            return name
        else:
            p_ids = []

            p_ = self.pancake
            _id = p_.get_names(f"{name}_p0", detail)
            p_ids.append(_id)

            dp_i = self.isolation
            if verbose:
                print(f"dblepancake.salome: isolation={dp_i}")
            _isolation_id = dp_i.get_names(f"{name}_i", detail)

            _id = p_.get_names(f"{name}_p1", detail)
            p_ids.append(_id)

            if verbose:
                print(
                    f"dblpancake: pancakes ({len(p_ids)}, {type(p_ids[0])}), isolations (1)"
                )
            if isinstance(p_ids[0], list):
                return flatten([flatten(p_ids), [_isolation_id]])
            else:
                return flatten([p_ids, [_isolation_id]])

    def getPancake(self):
        """
        return pancake object
        """
        return self.pancake

    def getIsolation(self):
        """
        return isolation object
        """
        return self.isolation

    def setZ0(self, z0) -> None:
        self.z0 = z0

    def setPancake(self, pancake) -> None:
        self.pancake = pancake

    def setIsolation(self, isolation) -> None:
        self.isolation = isolation

    def getFillingFactor(self) -> float:
        """
        ratio of the surface occupied by the tapes / total surface
        """
        S_tapes = 2.0 * self.pancake.n * self.pancake.tape.w * self.pancake.tape.h
        return S_tapes / self.getArea()

    def getR0(self) -> float:
        return self.pancake.getR0()

    def getR1(self) -> float:
        return self.pancake.getR1()

    def getZ0(self) -> float:
        return self.z0

    def getW(self) -> float:
        return self.pancake.getW()

    def getH(self) -> float:
        return 2.0 * self.pancake.getH() + self.isolation.getH()

    def getArea(self) -> float:
        return (self.pancake.getR1() - self.pancake.getR0()) * self.getH()


class HTSinsert:
    """
    HTS insert

    dblpancakes: stack of double pancakes
    isolation: stack of isolations between double pancakes

    TODO: add possibility to use 2 different pancake
    """

    def __init__(
        self,
        name: str = "",
        z0: float = 0,
        h: float = 0,
        r0: float = 0,
        r1: float = 0,
        z1: float = 0,
        n: int = 0,
        dblpancakes: list[dblpancake] = [],
        isolations: list[isolation] = [],
    ):
        self.name = name
        self.z0 = z0
        self.h = h
        self.r0 = r0
        self.r1 = r1
        self.z1 = z1
        self.n = n
        self.dblpancakes = dblpancakes
        self.isolations = isolations

    @classmethod
    def fromcfg(
        cls,
        inputcfg: str,
        directory: Optional[str] = None,
        debug: Optional[bool] = False,
    ):
        """create from a file"""
        import json

        filename = inputcfg
        if directory is not None:
            filename = f"{directory}/{filename}"
        print(f"SupraStructure:fromcfg({filename})")

        with open(filename) as f:
            data = json.load(f)
            if debug:
                print("HTSinsert data:", data)

            """
            print("List main keys:")
            for key in data:
                print("key:", key)
            """

            mytape = None
            if "tape" in data:
                mytape = tape.from_data(data["tape"])

            mypancake = pancake()
            if "pancake" in data:
                mypancake = pancake.from_data(data["pancake"])
                if debug:
                    print(f"mypancake={mypancake}")

            myisolation = isolation()
            if "isolation" in data:
                myisolation = isolation.from_data(data["isolation"])
                if debug:
                    print(f"myisolation={myisolation}")

            z = 0
            r0 = r1 = z0 = z1 = h = 0
            n = 0
            dblpancakes = []
            isolations = []
            if "dblpancakes" in data:
                if debug:
                    print("DblPancake data:", data["dblpancakes"])

                # if n defined use the same pancakes and isolations
                # else loop to load pancake and isolation structure definitions
                if "n" in data["dblpancakes"]:
                    n = data["dblpancakes"]["n"]
                    if debug:
                        print(f"Loading {n} similar dblpancakes, z={z}")
                    if "isolation" in data["dblpancakes"]:
                        dpisolation = isolation.from_data(
                            data["dblpancakes"]["isolation"]
                        )
                    else:
                        dpisolation = myisolation
                    if debug:
                        print(f"dpisolation={dpisolation}")

                    for i in range(n):
                        dp = dblpancake(z, mypancake, myisolation)
                        if debug:
                            print(f"dp={dp}")

                        dblpancakes.append(dp)
                        isolations.append(dpisolation)

                        if debug:
                            print(f"dblpancake[{i}]:")

                        z += dp.getH()
                        # print(f'z={z} dp_H={dp.getH()}')
                        if i != n - 1:
                            z += dpisolation.getH()  # isolation between D
                        # print(f'z={z} dp_i={dpisolation.getH()}')

                    h = z
                    # print(f"h= {self.h} [mm] = {z}")

                    r0 = dblpancakes[0].getR0()
                    r1 = dblpancakes[0].getR0() + dblpancakes[0].getW()
                else:
                    if debug:
                        print(f"Loading different dblpancakes, z={z}")
                    n = 0
                    for dp in data["dblpancakes"]:
                        n += 1
                        if debug:
                            print("dp:", dp, data["dblpancakes"][dp]["pancake"])
                        mypancake = pancake.from_data(
                            data["dblpancakes"][dp]["pancake"]
                        )

                        if "isolation" in data["isolations"][dp]:
                            dpisolation = isolation.from_data(
                                data["isolations"][dp]["isolation"]
                            )
                        else:
                            dpisolation = myisolation
                        isolations.append(dpisolation)

                        dp_ = dblpancake(z, mypancake, myisolation)
                        r0 = min(r0, dp_.getR0())
                        r1 = max(r1, dp_.pancake.getR1())
                        dblpancakes.append(dp_)
                        if debug:
                            print(f"mypancake: {mypancake}")
                            print(f"dpisolant: {dpisolation}")
                            print(f"dp: {dp_}")

                        z += dp_.getH()
                        z += myisolation.getH()  # isolation between DP

                    h = z - myisolation.getH()
                    # print(f"h= {self.h} [mm] = {z}-{myisolation.getH()} ({self.n} dblpancakes)")

            # shift insert by z0-z/2.
            z1 = z0 - h / 2.0
            z = z1
            # print(f'shift insert by {z} = {self.z0}-{self.h}/2.')
            for i in range(len(dblpancakes)):
                _h = dblpancakes[i].getH()
                dblpancakes[i].setZ0(z + _h / 2.0)
                # print(f'dp[{i}]: z0={z+_h/2.}, z1={z}, z2={z+_h}')
                z += _h + myisolation.getH()

            if debug:
                print("=== Load cfg:")
                print(f"r0= {r0} [mm]")
                print(f"r1= {r1} [mm]")
                print(f"z1= {z0-h/2.} [mm]")
                print(f"z2= {z0+h/2.} [mm]")
                print(f"z0= {z0} [mm]")
                print(f"h= {h} [mm]")
                print(f"n= {len(dblpancakes)}")

                for i, dp in enumerate(dblpancakes):
                    print(f"dblpancakes[{i}]: {dp}")
                print("===")

            name = inputcfg.replace(".json", "")
            return cls(name, z0, h, r0, r1, z1, n, dblpancakes, isolations)

    def __repr__(self) -> str:
        """
        representation of object
        """
        return (
            "htsinsert(name=%s, r0=%r, r1=%r, z0=%r, h=%r, n=%r, dblpancakes=%r, isolations=%r)"
            % (
                self.name,
                self.r0,
                self.r1,
                self.z0,
                self.h,
                self.n,
                self.dblpancakes,
                self.isolations,
            )
        )

    def get_names(self, mname: str, detail: str, verbose: bool = False) -> list[str]:
        dp_ids = []
        i_ids = []

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        n_dp = len(self.dblpancakes)
        for i, dp in enumerate(self.dblpancakes):
            if verbose:
                print(f"HTSInsert.names: dblpancakes[{i}]: dp={dp}")

            dp_name = f"{prefix}dp{i}"
            dp_id = dp.get_names(dp_name, detail, verbose)
            dp_ids.append(dp_id)

            if i != n_dp - 1:
                dp_i = self.isolations[i]

                _name = f"{prefix}i{i}"
                _id = dp_i.get_names(_name, detail, verbose)
                i_ids.append(_id)

        if detail == "dblpancake":
            return flatten([dp_ids, i_ids])
        else:
            return flatten([flatten(dp_ids), i_ids])

    def setDblpancake(self, dblpancake):
        self.dblpancakes.append(dblpancake)

    def setIsolation(self, isolation):
        self.isolations.append(isolation)

    def setZ0(self, z0: float):
        self.z0 = z0

    def getZ0(self) -> float:
        """
        returns the bottom altitude of de SuperConductor insert
        """
        return self.z0

    def getZ1(self) -> float:
        """
        returns the top altitude of de SuperConductor insert
        """
        return self.z1

    def getH(self) -> float:
        """
        returns the height of de SuperConductor insert
        """

        return self.h

    def getR0(self) -> float:
        """
        returns the inner radius of de SuperConductor insert
        """
        return self.r0

    def getR1(self) -> float:
        """
        returns the outer radius of de SuperConductor insert
        """
        return self.r1

    def getN(self) -> int:
        """
        returns the number of dbl pancakes
        """
        return self.n

    def getNtapes(self) -> list:
        """
        returns the number of tapes as a list
        """
        n_ = []
        for dp in self.dblpancakes:
            n_.append(dp.getPancake().getN())
        return n_

    def getHtapes(self) -> list:
        """
        returns the width of SC tapes
        either as an float or a list
        """
        w_tapes = []
        for dp in self.dblpancakes:
            w_tapes.append(dp.pancake.getTape().getH())
        return w_tapes

    def getWtapes_SC(self) -> list:
        """
        returns the width of SC tapes as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.pancake.getTape().getW_Sc())
        return w_

    def getWtapes_Isolation(self) -> list:
        """
        returns the width of isolation between tapes as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.pancake.getTape().getW_Isolation())
        return w_

    def getMandrinPancake(self) -> list:
        """
        returns the width of Mandrin as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getPancake().getMandrin())
        return w_

    def getWPancake(self) -> list:
        """
        returns the width of pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getPancake().getW())
        return w_

    def getWPancake_Isolation(self) -> list:
        """
        returns the width of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.isolation.getW())
        return w_

    def getR0Pancake_Isolation(self) -> list:
        """
        returns the inner radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getR0())
        return w_

    def getR1Pancake_Isolation(self) -> list:
        """
        returns the external radius of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getR0() + dp.getIsolation().getW())
        return w_

    def getHPancake_Isolation(self) -> list:
        """
        returns the height of isolation between pancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getIsolation().getH())
        return w_

    def getWDblPancake(self) -> list:
        """
        returns the width of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getW())
        return w_

    def getHDblPancake(self) -> list:
        """
        returns the height of dblpancake as a list
        """
        w_ = []
        for dp in self.dblpancakes:
            w_.append(dp.getH())
        return w_

    def getR0_Isolation(self) -> list:
        """
        returns the inner radius of isolation between dbl pancake as a list
        """
        w_ = []
        for isolant in self.isolations:
            w_.append(isolant.getR0())
        return w_

    def getR1_Isolation(self) -> list:
        """
        returns the external radius of isolation between dbl pancake as a list
        """
        w_ = []
        for isolant in self.isolations:
            w_.append(isolant.getR0() + isolant.getH())
        return w_

    def getW_Isolation(self) -> list:
        """
        returns the width of isolation between dbl pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append(isolant.getW())
        return w_

    def getH_Isolation(self) -> list:
        """
        returns the height of isolation between dbl pancakes
        """
        w_ = []
        for isolant in self.isolations:
            w_.append(isolant.getH())
        return w_

    def getFillingFactor(self) -> float:
        S_tapes = 0
        for dp in self.dblpancakes:
            S_tapes += dp.pancake.n * 2 * dp.pancake.tape.w * dp.pancake.tape.h
        return S_tapes / self.getArea()

    def getArea(self) -> float:
        return (self.getR1() - self.getR0()) * self.getH()

    def get_lc(self):
        _i = self.isolations[0].getH() / 3.0
        _dp = self.dblpancakes[0].getH() / 10.0
        _p = self.dblpancakes[0].pancake.getH() / 10.0
        _i_dp = self.dblpancakes[0].isolation.getH() / 3.0
        _Mandrin = (
            abs(
                self.dblpancakes[0].pancake.getMandrin()
                - self.dblpancakes[0].pancake.getR0()
            )
            / 3.0
        )
        _Sc = self.dblpancakes[0].pancake.tape.getW_Sc() / 5.0
        _Du = self.dblpancakes[0].pancake.tape.getW_Isolation() / 3.0
        return (_i, _dp, _p, _i_dp, _Mandrin, _Sc, _Du)

    # TODO move the template in a well defined directory (defined in config file for magnetgeo)
    def template_gmsh(self, name: str, detail: str) -> None:
        """
        generate a geo gmsh file

        option = dblpancake|pancake|tape control the precision of the model
        """

        details = {"tape": 0, "pancake": 1, "dblpancake": 2, "None": 3}

        print("ISolations:", len(self.isolations))
        print("=== Save to geo gmsh: NB use gmsh 4.9 or later")
        import getpass

        UserName = getpass.getuser()

        max_mandrin = max(self.getMandrinPancake())
        min_r_ = min(self.getR0Pancake_Isolation())
        min_r_dp = min(self.getR0_Isolation())
        xmin = min(self.getR0() - max_mandrin, min_r_dp, min_r_)

        rmin = min(self.getR0() - max_mandrin, min_r_dp, min_r_)
        rmax = 0
        for i, dp in enumerate(self.dblpancakes):
            r_dp = self.isolations[i].getR0()
            r_ = dp.getIsolation().getR0()
            rmax = max(rmax, dp.getPancake().getR0(), r_dp, r_)
        if rmax > self.getR0():
            print(f"ATTENTION rmax={rmax} > r0={self.getR0()}")
        """
        # To be checked if r_ and/or r_dp > r0
        for r in r_dp:
            if r > r0:
                ...
        for r in r_:
            if r > r0:
                ...
        """

        xmax = 0
        for i, dp in enumerate(self.dblpancakes):
            r_dp = self.isolations[i].getR0() + self.isolations[i].getW()
            r_ = dp.getIsolation().getR0() + dp.getIsolation().getW()
            xmax = max(xmax, r_dp, r_)

        # Some data will be stored as list (str(...)
        data_dict = {
            "detail": details[detail],
            "z0": self.getZ0() - self.getH() / 2.0,
            "r0": self.getR0(),
            "z1": self.getZ0() + self.getH() / 2.0,
            "r1": self.getR1(),
            "n_dp": self.getN(),
            "e_dp": str(self.getWDblPancake()).replace("[", "{").replace("]", "}"),
            "h_dp": str(self.getHDblPancake()).replace("[", "{").replace("]", "}"),
            "h_dp_isolation": str(self.getH_Isolation())
            .replace("[", "{")
            .replace("]", "}"),
            "r_dp": str(self.getR0_Isolation()).replace("[", "{").replace("]", "}"),
            "e_p": str(self.getWPancake()).replace("[", "{").replace("]", "}"),
            "e_dp_isolation": str(self.getW_Isolation())
            .replace("[", "{")
            .replace("]", "}"),
            "mandrin": str(self.getMandrinPancake())
            .replace("[", "{")
            .replace("]", "}"),
            "h_tape": str(self.getHtapes()).replace("[", "{").replace("]", "}"),
            "h_isolation": str(self.getHPancake_Isolation())
            .replace("[", "{")
            .replace("]", "}"),
            "r_": str(self.getR0Pancake_Isolation())
            .replace("[", "{")
            .replace("]", "}"),
            "e_isolation": str(self.getWPancake_Isolation())
            .replace("[", "{")
            .replace("]", "}"),
            "n_t": str(self.getNtapes()).replace("[", "{").replace("]", "}"),
            "e_t": str(self.getWtapes_Isolation()).replace("[", "{").replace("]", "}"),
            "w_t": str(self.getWtapes_SC()).replace("[", "{").replace("]", "}"),
            "emin": min(self.getWtapes_Isolation()),
            "xmin": xmin,
            "rmin": rmin,
            "rmax": rmax,
            "xmax": xmax,
        }

        # Load template file (TODO use jinja2 instead? or chevron)
        import chevron

        geofile = chevron.render("template-hts.mustache", data_dict)

        # print("geofile:", geofile)
        geofilename = name + "_hts_axi.geo"
        with open(geofilename, "x") as f:
            f.write(geofile)

        return
