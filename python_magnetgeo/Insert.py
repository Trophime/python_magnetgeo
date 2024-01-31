#!/usr/bin/env python3
# encoding: UTF-8

"""defines Insert structure"""
from typing import List

import math
import datetime
import json
import yaml
from . import deserialize
from . import InnerCurrentLead


def filter(data: List[float], tol: float) -> List[float]:
    result = []
    ndata = len(data)
    for i in range(ndata):
        result += [
            j for j in range(i, ndata) if i != j and abs(data[i] - data[j]) <= tol
        ]
    # print(f"duplicate index: {result}")

    # remove result from data
    return [data[i] for i in range(ndata) if not i in result]


class Insert(yaml.YAMLObject):
    """
    name :
    Helices :
    Rings :
    CurrentLeads :

    HAngles :
    RAngles :

    innerbore:
    outerbore:
    """

    yaml_tag = "Insert"

    def __init__(
        self,
        name,
        Helices=[],
        Rings=[],
        CurrentLeads=[],
        HAngles=[],
        RAngles=[],
        innerbore=None,
        outerbore=None,
    ):
        """constructor"""
        self.name = name
        self.Helices = Helices
        self.HAngles = HAngles
        for Angle in self.HAngles:
            print("Angle: ", Angle)
        self.Rings = Rings
        self.RAngles = RAngles
        self.CurrentLeads = CurrentLeads
        self.innerBore = innerbore
        self.outerBore = outerbore

    def get_channels(
        self, mname: str, hideIsolant: bool = True, debug: bool = False
    ) -> List[list]:
        """
        return channels
        """

        prefix = ""
        if mname:
            prefix = f"{mname}_"

        Channels = []
        NHelices = len(self.Helices)
        NChannels = NHelices + 1  # To be updated if there is any htype==HR in Insert

        for i in range(0, NChannels):
            names = []
            inames = []
            if i == 0:
                names.append(f"{prefix}R{i+1}_R0n")  # check Ring nummerotation
            if i >= 1:
                names.append(f"{prefix}H{i}_rExt")
                if not hideIsolant:
                    isolant_names = [f"{prefix}H{i}_IrExt"]
                    kapton_names = [f"{prefix}H{i}_kaptonsIrExt"]  # Only for HR
                    names = names + isolant_names + kapton_names
            if i >= 2:
                names.append(f"{prefix}R{i-1}_R1n")
            if i < NChannels:
                names.append(f"{prefix}H{i+1}_rInt")
                if not hideIsolant:
                    isolant_names = [f"{prefix}H{i+1}_IrInt"]
                    kapton_names = [f"{prefix}H{i+1}_kaptonsIrInt"]  # Only for HR
                    names = names + isolant_names + kapton_names

            # Better? if i+1 < nchannels:
            if i != 0 and i + 1 < NChannels:
                names.append(f"{prefix}R{i}_CoolingSlits")
                names.append(f"{prefix}R{i+1}_R0n")
            Channels.append(names)
            #
            # For the moment keep iChannel_Submeshes into
            # iChannel_Submeshes.append(inames)

        if debug:
            print("Channels:")
            for channel in Channels:
                print(f"\t{channel}")
        return Channels

    def get_isolants(self, mname: str, debug: bool = False):
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
        prefix = ""
        if mname:
            prefix = f"{mname}_"
        solid_names = []

        NHelices = len(self.Helices)
        NChannels = NHelices + 1  # To be updated if there is any htype==HR in Insert
        NIsolants = []  # To be computed depend on htype and dble
        for i, helix in enumerate(self.Helices):
            hHelix = None
            Ninsulators = 0
            with open(f"{helix}.yaml", "r") as f:
                hHelix = yaml.load(f, Loader=yaml.FullLoader)

            if is2D:
                h_solid_names = hHelix.get_names(f"{prefix}H{i+1}", is2D, verbose)
                solid_names += h_solid_names
            else:
                solid_names.append(f"H{i+1}")

        for i, ring in enumerate(self.Rings):
            if verbose:
                print(f"ring: {ring}")
            solid_names.append(f"{prefix}R{i+1}")
        # print(f'Insert_Gmsh: ring_ids={ring_ids}')

        if not is2D:
            for i, Lead in enumerate(self.CurrentLeads):
                with open(Lead + ".yaml", "r") as f:
                    clLead = yaml.load(f, Loader=yaml.FullLoader)
                prefix = "o"
                if isinstance(clLead, InnerCurrentLead.InnerCurrentLead):
                    prefix = "i"
                solid_names.append(f"{prefix}L{i+1}")

        if verbose:
            print(f"Insert_Gmsh: solid_names {len(solid_names)}")
        return solid_names

    def get_nhelices(self):
        """
        return names for Markers
        """

        return len(self.Helices)

    def __repr__(self):
        """representation"""
        return (
            "%s(name=%r, Helices=%r, Rings=%r, CurrentLeads=%r, HAngles=%r, RAngles=%r, innerbore=%r, outerbore=%r)"
            % (
                self.__class__.__name__,
                self.name,
                self.Helices,
                self.Rings,
                self.CurrentLeads,
                self.HAngles,
                self.RAngles,
                self.innerbore,
                self.outerbore,
            )
        )

    def dump(self):
        """dump to a yaml file name.yaml"""
        try:
            with open(f"{self.name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            print("Failed to Insert dump")

    def load(self):
        """load from a yaml file"""
        data = None
        try:
            with open(f"{self.name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception("Failed to load Insert data %s" % (self.name + ".yaml"))

        self.name = data.name
        self.Helices = data.Helices
        self.HAngles = data.HAngles
        self.RAngles = data.RAngles
        self.Rings = data.Rings
        self.CurrentLeads = data.CurrentLeads

        self.innerbore = data.innerbore
        self.outerbore = data.outerbore

    def to_json(self):
        """convert from yaml to json"""
        return json.dumps(
            self, default=deserialize.serialize_instance, sort_keys=True, indent=4
        )

    def from_json(self, string):
        """get from json"""
        return json.loads(string, object_hook=deserialize.unserialize_object)

    def write_to_json(self):
        """write to a json file"""
        ostream = open(self.name + ".json", "w")
        jsondata = self.to_json()
        ostream.write(str(jsondata))
        ostream.close()

    def read_from_json(self):
        """read from a json file"""
        istream = open(self.name + ".json", "r")
        jsondata = self.from_json(istream.read())
        print(type(jsondata))
        istream.close()

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

        for i, name in enumerate(self.Helices):
            Helix = None
            with open(name + ".yaml", "r") as f:
                Helix = yaml.load(f, Loader=yaml.FullLoader)

            if i == 0:
                rb = Helix.r
                zb = Helix.z

            rb[0] = min(rb[0], Helix.r[0])
            zb[0] = min(zb[0], Helix.z[0])
            rb[1] = max(rb[1], Helix.r[1])
            zb[1] = max(zb[1], Helix.z[1])

        ring_dz_max = 0
        for i, name in enumerate(self.Rings):
            Ring = None
            with open(name + ".yaml", "r") as f:
                Ring = yaml.load(f, Loader=yaml.FullLoader)

            ring_dz_max = abs(Ring.z[-1] - Ring.z[0])

        zb[0] -= ring_dz_max
        zb[1] += ring_dz_max

        # TODO add Leads

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
        H_ids, R_ids, BC_ids, Air_ids, BC_Air_ids
        """
        import getpass

        UserName = getpass.getuser()

        geofilename = self.name + "_axi.geo"
        geofile = open(geofilename, "w")

        # Preambule
        geofile.write(f"//{self.name}\n")
        geofile.write("// AxiSymetrical Geometry Model\n")
        geofile.write(f"//{UserName}\n")
        geofile.write(f"//{datetime.datetime.now().strftime('%y-%m-%d %Hh%M')}\n")
        geofile.write("\n")

        # Mesh Preambule
        geofile.write("// Mesh Preambule\n")
        geofile.write("Mesh.Algorithm=3;\n")
        geofile.write("Mesh.RecombinationAlgorithm=0; // Deactivate Blossom support\n")
        geofile.write(
            "Mesh.RemeshAlgorithm=1; //(0=no split, 1=automatic, 2=automatic only with metis)\n"
        )
        geofile.write("Mesh.RemeshParametrization=0; //\n\n")

        # Define Parameters
        geofile.write("//Geometric Parameters\n")
        onelab_r0 = 'DefineConstant[ r0_H%d = {%g, Name "Geom/H%d/Rint"} ];\n'  # should add a min and a max
        onelab_r1 = 'DefineConstant[ r1_H%d = {%g, Name "Geom/H%d/Rext"} ];\n'
        onelab_z0 = 'DefineConstant[ z0_H%d = {%g, Name "Geom/H%d/Zinf"} ];\n'  #  should add a min and a max
        onelab_z1 = 'DefineConstant[ z1_H%d = {%g, Name "Geom/H%d/Zsup"} ];\n'
        onelab_lc = 'DefineConstant[ lc_H%d = {%g, Name "Geom/H%d/lc"} ];\n'
        onelab_z_R = 'DefineConstant[ dz_R%d = {%g, Name "Geom/R%d/dz"} ];\n'
        onelab_lc_R = 'DefineConstant[ lc_R%d = {%g, Name "Geom/R%d/lc"} ];\n'

        # Define Geometry
        onelab_point = "Point(%d)= {%s,%g, 0.0, lc_H%d};\n"
        onelab_pointx = "Point(%d)= {%s,%s, 0.0, lc_H%d};\n"
        onelab_point_gen = "Point(%d)= {%s,%s, 0.0, %s};\n"
        onelab_line = "Line(%d)= {%d, %d};\n"
        onelab_circle = "Circle(%d)= {%d, %d, %d};\n"
        onelab_lineloop = "Line Loop(%d)= {%d, %d, %d, %d};\n"
        onelab_lineloop_R = "Line Loop(%d)= {%d, %d, %d, %d, %d, %d, %d, %d};\n"
        onelab_planesurf = "Plane Surface(%d)= {%d};\n"
        onelab_phys_surf = "Physical Surface(%d) = {%d};\n"

        H_ids = []  # gsmh ids for Helix
        Rint_ids = []
        Rext_ids = []
        BP_ids = []
        HP_ids = []
        dH_ids = []

        point = 1
        line = 1
        lineloop = 1
        planesurf = 1

        for i, name in enumerate(self.Helices):
            H = []
            Rint = []
            Rext = []
            BP = []
            HP = []
            dH = []

            Helix = None
            with open(name + ".yaml", "r") as f:
                Helix = yaml.load(f, Loader=yaml.FullLoader)
            geofile.write(f"// H{i+1} : {Helix.name}\n")
            geofile.write(onelab_r0 % (i + 1, Helix.r[0], i + 1))
            geofile.write(onelab_r1 % (i + 1, Helix.r[1], i + 1))
            geofile.write(onelab_z0 % (i + 1, Helix.z[0], i + 1))
            geofile.write(onelab_z1 % (i + 1, Helix.z[1], i + 1))
            geofile.write(onelab_lc % (i + 1, (Helix.r[1] - Helix.r[0]) / 5.0, i + 1))

            axi = Helix.axi  # h, turns, pitch

            geofile.write(onelab_pointx % (point, f"r0_H{i+1}", f"z0_H{i+1}", i + 1))
            geofile.write(
                onelab_pointx % (point + 1, f"r1_H{i+1}", f"z0_H{i+1}", i + 1)
            )
            geofile.write(onelab_point % (point + 2, f"r1_H{i+1}", -axi.h, i + 1))
            geofile.write(onelab_point % (point + 3, f"r0_H{i+1}", -axi.h, i + 1))

            geofile.write(onelab_line % (line, point, point + 1))
            geofile.write(onelab_line % (line + 1, point + 1, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, point + 3))
            geofile.write(onelab_line % (line + 3, point + 3, point))
            BP_ids.append(line)
            Rint.append(line + 3)
            Rext.append(line + 1)
            dH.append([line + 3, line, line + 1])

            geofile.write(
                onelab_lineloop % (lineloop, line, line + 1, line + 2, line + 3)
            )
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            H.append(planesurf)
            dH.append(lineloop)

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

            z = Helix.z[0]
            dz = 2 * axi.h / float(len(axi.pitch))
            z = -axi.h
            for n, p in enumerate(axi.pitch):
                geofile.write(onelab_point % (point, "r0_H%d" % (i + 1), z, i + 1))
                geofile.write(onelab_point % (point + 1, "r1_H%d" % (i + 1), z, i + 1))
                geofile.write(
                    onelab_point % (point + 2, "r1_H%d" % (i + 1), z + dz, i + 1)
                )
                geofile.write(
                    onelab_point % (point + 3, "r0_H%d" % (i + 1), z + dz, i + 1)
                )

                geofile.write(onelab_line % (line, point, point + 1))
                geofile.write(onelab_line % (line + 1, point + 1, point + 2))
                geofile.write(onelab_line % (line + 2, point + 2, point + 3))
                geofile.write(onelab_line % (line + 3, point + 3, point))
                Rint.append(line + 3)
                Rext.append(line + 1)

                geofile.write(
                    onelab_lineloop % (lineloop, line, line + 1, line + 2, line + 3)
                )
                geofile.write(onelab_planesurf % (planesurf, lineloop))
                geofile.write(onelab_phys_surf % (planesurf, planesurf))
                H.append(planesurf)
                dH.append(lineloop)

                point += 4
                line += 4
                lineloop += 1
                planesurf += 1

                z += dz

            geofile.write(onelab_point % (point, "r0_H%d" % (i + 1), axi.h, i + 1))
            geofile.write(onelab_point % (point + 1, "r1_H%d" % (i + 1), axi.h, i + 1))
            geofile.write(
                onelab_pointx
                % (point + 2, "r1_H%d" % (i + 1), "z1_H%d" % (i + 1), i + 1)
            )
            geofile.write(
                onelab_pointx
                % (point + 3, "r0_H%d" % (i + 1), "z1_H%d" % (i + 1), i + 1)
            )

            geofile.write(onelab_line % (line, point, point + 1))
            geofile.write(onelab_line % (line + 1, point + 1, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, point + 3))
            geofile.write(onelab_line % (line + 3, point + 3, point))

            geofile.write(
                onelab_lineloop % (lineloop, line, line + 1, line + 2, line + 3)
            )
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            H.append(planesurf)
            Rint.append(line + 3)
            Rext.append(line + 1)

            # dH.append(Rext)
            # dH.append([line+1,line+2, line+3])
            # for id in reversed(Rint):
            #     dH.append([id])
            dH.append(lineloop)

            H_ids.append(H)
            HP_ids.append(line + 2)
            Rint_ids.append(Rint)
            Rext_ids.append(Rext)

            dH_ids.append(
                dH
            )  #### append(reduce(operator.add, dH)) #other way to flatten dH : list(itertools.chain(*dH))
            geofile.write("\n")

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

        # Add Rings
        Ring_ids = []
        HP_Ring_ids = []
        BP_Ring_ids = []
        dR_ids = []

        H0 = 0
        H1 = 1
        for i, name in enumerate(self.Rings):
            R = []
            Rint = []
            Rext = []
            BP = []
            HP = []

            Ring = None
            with open(name + ".yaml", "r") as f:
                Ring = yaml.load(f, Loader=yaml.FullLoader)
            geofile.write(
                "// R%d [%d, H%d] : %s\n" % (i + 1, H0 + 1, H1 + 1, Ring.name)
            )
            geofile.write(onelab_z_R % (i + 1, (Ring.z[1] - Ring.z[0]), i + 1))
            geofile.write(onelab_lc_R % (i + 1, (Ring.r[3] - Ring.r[0]) / 5.0, i + 1))

            if Ring.BPside:
                geofile.write(
                    onelab_pointx
                    % (point, "r0_H%d" % (H0 + 1), "z1_H%d" % (H0 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 1, "r1_H%d" % (H0 + 1), "z1_H%d" % (H0 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 2, "r0_H%d" % (H1 + 1), "z1_H%d" % (H1 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 3, "r1_H%d" % (H1 + 1), "z1_H%d" % (H1 + 1), i + 1)
                )

                geofile.write(
                    onelab_pointx
                    % (
                        point + 4,
                        "r1_H%d" % (H1 + 1),
                        "z1_H%d+dz_R%d" % (H1 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 5,
                        "r0_H%d" % (H1 + 1),
                        "z1_H%d+dz_R%d" % (H1 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 6,
                        "r1_H%d" % (H0 + 1),
                        "z1_H%d+dz_R%d" % (H0 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 7,
                        "r0_H%d" % (H0 + 1),
                        "z1_H%d+dz_R%d" % (H0 + 1, i + 1),
                        i + 1,
                    )
                )
            else:
                geofile.write(
                    onelab_pointx
                    % (
                        point,
                        "r0_H%d" % (H0 + 1),
                        "z0_H%d-dz_R%d" % (H0 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 1,
                        "r1_H%d" % (H0 + 1),
                        "z0_H%d-dz_R%d" % (H0 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 2,
                        "r0_H%d" % (H1 + 1),
                        "z0_H%d-dz_R%d" % (H1 + 1, i + 1),
                        i + 1,
                    )
                )
                geofile.write(
                    onelab_pointx
                    % (
                        point + 3,
                        "r1_H%d" % (H1 + 1),
                        "z0_H%d-dz_R%d" % (H1 + 1, i + 1),
                        i + 1,
                    )
                )

                geofile.write(
                    onelab_pointx
                    % (point + 4, "r1_H%d" % (H1 + 1), "z0_H%d" % (H1 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 5, "r0_H%d" % (H1 + 1), "z0_H%d" % (H1 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 6, "r1_H%d" % (H0 + 1), "z0_H%d" % (H0 + 1), i + 1)
                )
                geofile.write(
                    onelab_pointx
                    % (point + 7, "r0_H%d" % (H0 + 1), "z0_H%d" % (H0 + 1), i + 1)
                )

            geofile.write(onelab_line % (line, point, point + 1))
            geofile.write(onelab_line % (line + 1, point + 1, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, point + 3))
            geofile.write(onelab_line % (line + 3, point + 3, point + 4))
            geofile.write(onelab_line % (line + 4, point + 4, point + 5))
            geofile.write(onelab_line % (line + 5, point + 5, point + 6))
            geofile.write(onelab_line % (line + 6, point + 6, point + 7))
            geofile.write(onelab_line % (line + 7, point + 7, point))

            if Ring.BPside:
                HP_Ring_ids.append([line + 4, line + 5, line + 6])
            else:
                BP_Ring_ids.append([line + 4, line + 5, line + 6])

            geofile.write(
                onelab_lineloop_R
                % (
                    lineloop,
                    line,
                    line + 1,
                    line + 2,
                    line + 3,
                    line + 4,
                    line + 5,
                    line + 6,
                    line + 7,
                )
            )
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Ring_ids.append(planesurf)

            Rint_ids[H0].append(line + 7)
            Rext_ids[H1].append(line + 3)
            dR_ids.append(lineloop)

            H0 = H1
            H1 += 1

            point += 8
            line += 8
            lineloop += 1
            planesurf += 1

        # create physical lines
        for i, r_ids in enumerate(Rint_ids):
            geofile.write('Physical Line("H%dChannel0") = {' % (i + 1))
            for id in r_ids:
                geofile.write("%d" % id)
                if id != r_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        for i, r_ids in enumerate(Rext_ids):
            geofile.write('Physical Line("H%dChannel1") = {' % (i + 1))
            for id in r_ids:
                geofile.write("%d" % id)
                if id != r_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        geofile.write('Physical Line("HP_H%d") = ' % (0))
        geofile.write("{%d};\n" % HP_ids[0])

        if len(self.Helices) % 2 == 0:
            geofile.write('Physical Line("HP_H%d") = ' % (len(self.Helices)))
            geofile.write("{%d};\n" % HP_ids[-1])
        else:
            geofile.write('Physical Line("BP_H%d") = ' % (len(self.Helices)))
            geofile.write("{%d};\n" % BP_ids[-1])

        for i, _ids in enumerate(HP_Ring_ids):
            geofile.write('Physical Line("HP_R%d") =  {' % (i + 1))
            for id in _ids:
                geofile.write("%d" % id)
                if id != _ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        for i, _ids in enumerate(BP_Ring_ids):
            geofile.write('Physical Line("BP_R%d") =  {' % (i + 1))
            for id in _ids:
                geofile.write("%d" % id)
                if id != _ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

        # BC_ids should contains "H%dChannel%d", "HP_R%d" and "BP_R%d"
        BC_ids = []

        # Air
        Air_ids = []
        BC_Air_ids = []
        if AirData:
            Axis_ids = []
            Infty_ids = []

            geofile.write("// Define Air\n")
            onelab_r_air = 'DefineConstant[ r_Air = {%g, Name "Geom/Air/factor_R"} ];\n'
            onelab_z_air = 'DefineConstant[ z_Air = {%g, Name "Geom/Air/factor_Z"} ];\n'  #  should add a min and a max
            onelab_lc_air = 'DefineConstant[ lc_Air = {%g, Name "Geom/Air/lc"} ];\n'
            geofile.write(onelab_r_air % (1.2))
            geofile.write(onelab_z_air % (1.2))
            geofile.write(onelab_lc_air % (2))

            H0 = 0
            Hn = len(self.Helices) - 1

            geofile.write(onelab_pointx % (point, "0", f"z_Air * z0_H{H0+1}", H0 + 1))
            geofile.write(
                onelab_pointx
                % (
                    point + 1,
                    f"r_Air * r1_H{Hn+1}",
                    "z_Air * z0_H%d" % (H0 + 1),
                    H0 + 1,
                )
            )
            geofile.write(
                onelab_pointx
                % (
                    point + 2,
                    f"r_Air * r1_H{Hn+1}",
                    "z_Air * z1_H%d" % (Hn + 1),
                    Hn + 1,
                )
            )
            geofile.write(
                onelab_pointx % (point + 3, f"0", "z_Air * z1_H{Hn+1}", Hn + 1)
            )

            geofile.write(onelab_line % (line, point, point + 1))
            geofile.write(onelab_line % (line + 1, point + 1, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, point + 3))
            geofile.write(onelab_line % (line + 3, point + 3, point))
            Axis_ids.append(line + 3)

            geofile.write(
                onelab_lineloop % (lineloop, line, line + 1, line + 2, line + 3)
            )
            geofile.write("Plane Surface(%d)= {%d, " % (planesurf, lineloop))
            for _ids in H_ids:
                for _id in _ids:
                    geofile.write(f"{-_id}")
            for _id in dR_ids:
                geofile.write(f"{-_id}")
                if _id != dR_ids[-1]:
                    geofile.write(",")
            Air_ids.append(planesurf)

            geofile.write("};\n")
            # geofile.write(onelab_planesurf%(planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))

            dAir = lineloop
            axis_HP = point
            axis_BP = point + 3
            Air_line = line

            point += 4
            line += 4
            lineloop += 1
            planesurf += 1

            # Define Infty
            geofile.write("// Define Infty\n")
            onelab_rint_infty = (
                'DefineConstant[ Val_Rint = {%g, Name "Geom/Infty/Val_Rint"} ];\n'
            )
            onelab_rext_infty = (
                'DefineConstant[ Val_Rext = {%g, Name "Geom/Infty/Val_Rext"} ];\n'
            )
            onelab_lc_infty = (
                'DefineConstant[ lc_infty = {%g, Name "Geom/Infty/lc_inft"} ];\n'
            )
            onelab_point_infty = "Point(%d)= {%s,%s, 0.0, %s};\n"
            geofile.write(onelab_rint_infty % (4))
            geofile.write(onelab_rext_infty % (5))
            geofile.write(onelab_lc_infty % (100))

            center = point
            geofile.write(onelab_point_gen % (center, "0", "0", "lc_Air"))
            point += 1

            Hn = len(self.Helices)

            geofile.write(
                onelab_point_gen % (point, "0", f"-Val_Rint * r1_H{Hn}", "lc_infty")
            )
            geofile.write(
                onelab_point_gen % (point + 1, f"Val_Rint * r1_H{Hn}", "0", "lc_infty")
            )
            geofile.write(
                onelab_point_gen % (point + 2, "0", f"Val_Rint * r1_H{Hn}", "lc_infty")
            )

            geofile.write(onelab_circle % (line, point, center, point + 1))
            geofile.write(onelab_circle % (line + 1, point + 1, center, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, axis_BP))
            geofile.write(onelab_line % (line + 3, axis_HP, point))
            Axis_ids.append(line + 2)
            Axis_ids.append(line + 3)

            geofile.write("Line Loop(%d) = {" % lineloop)
            geofile.write("%d, " % line)
            geofile.write("%d, " % (line + 1))
            geofile.write("%d, " % (line + 2))
            geofile.write("%d, " % (-(Air_line + 2)))
            geofile.write("%d, " % (-(Air_line + 1)))
            geofile.write("%d, " % (-(Air_line)))
            geofile.write("%d};\n " % (line + 3))

            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Air_ids.append(planesurf)

            axis_HP = point
            axis_BP = point + 2
            Air_line = line

            point += 3
            line += 4
            lineloop += 1
            planesurf += 1

            geofile.write(
                onelab_point_gen % (point, "0", "-Val_Rext * r1_H%d" % Hn, "lc_infty")
            )
            geofile.write(
                onelab_point_gen
                % (point + 1, "Val_Rext * r1_H%d" % Hn, "0", "lc_infty")
            )
            geofile.write(
                onelab_point_gen
                % (point + 2, "0", "Val_Rext * r1_H%d" % Hn, "lc_infty")
            )

            geofile.write(onelab_circle % (line, point, center, point + 1))
            geofile.write(onelab_circle % (line + 1, point + 1, center, point + 2))
            geofile.write(onelab_line % (line + 2, point + 2, axis_BP))
            geofile.write(onelab_line % (line + 3, axis_HP, point))
            Axis_ids.append(line + 2)
            Axis_ids.append(line + 3)
            Infty_ids.append(line)
            Infty_ids.append(line + 1)

            geofile.write("Line Loop(%d) = {" % lineloop)
            geofile.write("%d, " % line)
            geofile.write("%d, " % (line + 1))
            geofile.write("%d, " % (line + 2))
            geofile.write("%d, " % (-(Air_line + 1)))
            geofile.write("%d, " % (-(Air_line)))
            geofile.write("%d};\n " % (line + 3))
            geofile.write(onelab_planesurf % (planesurf, lineloop))
            geofile.write(onelab_phys_surf % (planesurf, planesurf))
            Air_ids.append(planesurf)

            # Add Physical Lines
            geofile.write('Physical Line("Axis") =  {')
            for id in Axis_ids:
                geofile.write("%d" % id)
                if id != Axis_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

            geofile.write('Physical Line("Infty") =  {')
            for id in Infty_ids:
                geofile.write("%d" % id)
                if id != Infty_ids[-1]:
                    geofile.write(",")
            geofile.write("};\n")

            # BC_Airs_ids should contains "Axis" and "Infty"

        # coherence
        geofile.write("\nCoherence;\n")
        geofile.close()

        return (H_ids, Ring_ids, BC_ids, Air_ids, BC_Air_ids)

    def get_params(self, workingDir: str = ".") -> tuple:
        """
        get params

        NHelices,
        NRings,
        NChannels,
        Nsections

        R1
        R2
        Z1
        Z2
        Dh,
        Sh,
        Zh
        """

        tol = 1.0e-6

        NHelices = len(self.Helices)
        NRings = len(self.Rings)
        NChannels = NChannels = NHelices + 1

        Nsections = []
        Nturns_h = []
        R1 = []
        R2 = []
        Nsections = []
        Nturns_h = []
        Dh = []
        Sh = []

        Zh = []
        for i, helix in enumerate(self.Helices):
            hhelix = None
            with open(f"{workingDir}/{helix}.yaml", "r") as f:
                hhelix = yaml.load(f, Loader=yaml.FullLoader)
            n_sections = len(hhelix.axi.turns)
            Nsections.append(n_sections)
            Nturns_h.append(hhelix.axi.turns)

            R1.append(hhelix.r[0])
            R2.append(hhelix.r[1])

            z = -hhelix.axi.h
            (turns, pitch) = hhelix.axi.compact(tol)

            tZh = []
            tZh.append(hhelix.z[0])
            tZh.append(z)
            for n, p in zip(turns, pitch):
                z += n * p
                tZh.append(z)
            tZh.append(hhelix.z[1])
            Zh.append(tZh)
            # print(f"Zh[{i}]: {Zh[-1]}")

        Ri = self.innerbore
        Re = self.outerbore

        for i in range(NHelices):
            Dh.append(2 * (R1[i] - Ri))
            Sh.append(math.pi * (R1[i] - Ri) * (R1[i] + Ri))

            Ri = R2[i]

        Zr = []
        for i, ring in enumerate(self.Rings):
            hring = None
            with open(f"{workingDir}/{ring}.yaml", "r") as f:
                hring = yaml.load(f, Loader=yaml.FullLoader)

            dz = abs(hring.z[1] - hring.z[0])
            if i % 2 == 1:
                # print(f"Ring[{i}]: minus dz_ring={dz} to Zh[i][0]")
                Zr.append(Zh[i][0] - dz)

            if i % 2 == 0:
                # print(f"Ring[{i}]: add dz={dz} to Zh[i][-1]")
                Zr.append(Zh[i][-1] + dz)
        # print(f"Zr: {Zr}")

        # get Z per Channel for Tw(z) estimate
        Zc = []
        Zi = []
        for i in range(NChannels - 1):
            nZh = Zh[i] + Zi
            # print(f"C{i}:")
            if i >= 0 and i < NChannels - 2:
                # print(f"\tR{i}")
                nZh.append(Zr[i])
            if i >= 1 and i < NChannels - 2:
                # print(f"\tR{i-1}")
                nZh.append(Zr[i - 1])
            if i >= 2 and i < NChannels - 2:
                # print(f"\tR{i-2}")
                nZh.append(Zr[i - 2])

            nZh.sort()
            Zc.append(filter(nZh, tol))
            # remove duplicates (requires to have a compare method with a tolerance: |z[i] - z[j]| <= tol means z[i] == z[j])
            Zi = Zh[i]

            # print(f"Zh[{i}]={Zh[i]}")
            # print(f"Zc[{i}]={Zc[-1]}")

        # Add latest Channel: Zh[-1] + R[-1]
        nZh = Zh[-1] + [Zr[-1]]
        nZh.sort()
        Zc.append(filter(nZh, tol))
        nZh = []

        Zmin = 0
        Zmax = 0
        for i, _z in enumerate(Zc):
            Zmin = min(Zmin, min(_z))
            Zmax = max(Zmax, max(_z))
            # print(f"Zc[Channel{i}]={_z}")
        # print(f"Zmin={Zmin}")
        # print(f"Zmax={Zmax}")

        Dh.append(2 * (Re - Ri))
        Sh.append(math.pi * (Re - Ri) * (Re + Ri))
        return (NHelices, NRings, NChannels, Nsections, R1, R2, Dh, Sh, Zc)


def Insert_constructor(loader, node):
    print("Insert_constructor")
    values = loader.construct_mapping(node)
    name = values["name"]
    Helices = values["Helices"]
    HAngles = values["HAngles"]
    RAngles = values["RAngles"]
    Rings = values["Rings"]
    CurrentLeads = values["CurrentLeads"]
    innerbore = values["innerbore"]
    outerbore = values["outerbore"]
    return Insert(
        name, Helices, Rings, CurrentLeads, HAngles, RAngles, innerbore, outerbore
    )


yaml.add_constructor("!Insert", Insert_constructor)
