"""
Retreive Physical Group from xao
Mesh using gmsh

TODO:
test with an xao file with embedded cad data (use stringio to cad)
retreive volume names from yaml file
link with MeshData
remove unneeded class like NumModel, freesteam, pint and SimMaterial

see gmsh/api/python examples for that
ex also in https://www.pygimli.org/_examples_auto/1_meshing/plot_cad_tutorial.html
"""

import os

import re
import argparse
import math
import json

from io import StringIO
import yaml
from lxml import etree

import gmsh

from .Ring import *
from .Helix import *
from .InnerCurrentLead import *
from .OuterCurrentLead import *
from .Insert import *
from .Bitter import *
from .Supra import *
from .MSite import *

from .utils import load_Xao

def Supra_Gmsh(cad, gname, is2D, verbose):
    """ Load Supra cad """
    print("Supra_Gmsh:", cad={cad.name}, gname={gname})
    solid_names = []

    # # load yaml
    # from . import SupraStructure
    # hts = SupraStructure.HTSinsert()
    # hts.loadCfg(f'{cad.struct}')
    hts = cad.get_magnet_struct()
    cad.check_dimensions(hts)

    # TODO take into account supra detail
    if cad.detail == "None":
        solid_names.append(f"{cad.name}_S")
    else:

        n_dp = len(hts.dblpancakes)
        cadname = cad.struct.replace('.json', '')
        for i, dp in enumerate(hts.dblpancakes):
            dp_name = f'{cadname}_dp{i}'
            if cad.detail == 'dblpancake':
                solid_names.append(f'{cad.name}_{dp_name}')

            if cad.detail == 'pancake':
                solid_names.append(f'{dp_name}_p0')
                solid_names.append(f'{dp_name}_p1')
                solid_names.append(f'{dp_name}_i')
            if cad.detail == 'tape':
                solid_names.append(f'{dp_name}_p0_Mandrin')
                for j in range(dp.pancake.n):
                    solid_names.append(f'{dp_name}_p0_t{j}_SC')
                    solid_names.append(f'{dp_name}_p0_t{j}_Duromag')
                solid_names.append(f'{dp_name}_p1_Mandrin')
                for j in range(dp.pancake.n):
                    solid_names.append(f'{dp_name}_p1_t{j}_SC')
                    solid_names.append(f'{dp_name}_p1_t{j}_Duromag')
                solid_names.append(f'{dp_name}_i')

        for i, dp in enumerate(hts.dblpancakes):
            if i != n_dp-1:
                solid_names.append(f'{cadname}_i{i}')

    if verbose:
        print(f"Supra_Gmsh: solid_names {len(solid_names)}")
    print(f"Supra_Gmsh: {cad.name} done")
    return solid_names

def Bitter_Gmsh(cad, gname, is2D, verbose):
    """ Load Bitter cad """
    print(f"Bitter_Gmsh: cad={cad.name}, gname={gname}")
    solid_names = []

    if is2D:
        nsection = len(cad.axi.turns)
        # print(f"Bitter_Gmsh: {nsection}")
        for j in range(nsection):
            solid_names.append(f"{cad.name}_B{j+1}")
    else:
        solid_names.append(f"{cad.name}_B")
    if verbose:
        print(f"Bitter_Gmsh: solid_names {len(solid_names)}")
    return solid_names

def Helix_Gmsh(cad, gname, is2D, verbose):
    """ Load Helix cad """
    print(f"Helix_Gmsh: cad={cad.name}, gname={gname}")
    solid_names = []

    sInsulator = "Glue"
    nInsulators = 0
    nturns = cad.get_Nturns()
    if cad.m3d.with_shapes and cad.m3d.with_channels:
        sInsulator = "Kapton"
        htype = "HR"
        angle = cad.shape.angle
        nshapes = nturns * (360 / float(angle))
        if verbose:
            print("shapes: ", nshapes, math.floor(nshapes), math.ceil(nshapes))

        nshapes = (lambda x: math.ceil(x) if math.ceil(x) - x < x - math.floor(x) else math.floor(x))(nshapes)
        nInsulators = int(nshapes)
        print("nKaptons=", nInsulators)
    else:
        htype = "HL"
        nInsulators = 1
        if cad.dble:
            nInsulators = 2
        if verbose:
            print("helix:", gname, htype, nturns)

    if is2D:
        nsection = len(cad.axi.turns)
        solid_names.append(f"Cu{0}") # HP
        for j in range(nsection):
            solid_names.append(f"Cu{j+1}")
        solid_names.append(f"Cu{nsection+1}") # BP
    else:
        solid_names.append("Cu")
        # TODO tell HR from HL
        for j in range(nInsulators):
            solid_names.append(f"{sInsulator}{j}")

    if verbose:
        print(f"Helix_Gmsh[{htype}]: solid_names {len(solid_names)}")
    return solid_names

def Insert_Gmsh(cad, gname, is2D, verbose):
    """ Load Insert """
    print(f"Insert_Gmsh: cad={cad.name}, gname={gname}")
    solid_names = []
    ring_ids = {}

    NHelices = len(cad.Helices)
    NChannels = NHelices + 1 # To be updated if there is any htype==HR in Insert
    NIsolants = [] # To be computed depend on htype and dble
    for i, helix in enumerate(cad.Helices):
        hHelix = None
        Ninsulators = 0
        with open(helix+".yaml", 'r') as f:
            hHelix = yaml.load(f, Loader=yaml.FullLoader)

        h_solid_names = Helix_Gmsh(hHelix, gname, is2D, verbose)
        for k, sname in enumerate(h_solid_names):
            h_solid_names[k] = f"H{i+1}_{sname}"
        solid_names += h_solid_names
        ring_ids[helix] = f'H{i+1}'

    for i, ring in enumerate(cad.Rings):
        if verbose:
            print(f"ring: {ring}")
        solid_names.append(f"R{i+1}")
        ring_ids[ring] = f"R{i+1}"
    # print(f'Insert_Gmsh: ring_ids={ring_ids}')

    if not is2D:
        for i, Lead in enumerate(cad.CurrentLeads):
            with open(Lead+".yaml", 'r') as f:
                clLead = yaml.load(f, Loader=yaml.FullLoader)
            prefix = 'o'
            if isinstance(clLead, InnerCurrentLead):
                prefix = 'i'
            solid_names.append(f"{prefix}L{i+1}")

    if verbose:
        print(f"Insert_Gmsh: solid_names {len(solid_names)}")
    return (solid_names, NHelices, NChannels, NIsolants, ring_ids)

def Magnet_Gmsh(mname, cad, gname, is2D, verbose):
    """ Load Magnet cad """
    print(f"Magnet_Gmsh: mname={mname}, cad={cad}, gname={gname}")
    solid_names = []
    NHelices = []
    NChannels = []
    NIsolants = []
    Boxes = {}
    ring_ids = {}

    cfgfile = cad + ".yaml"
    with open(cfgfile, 'r') as cfgdata:
        pcad = yaml.load(cfgdata, Loader=yaml.FullLoader)
        pname = pcad.name

    # print('pcad: {pcad} type={type(pcad)}')
    if isinstance(pcad, Bitter):
        # TODO replace pname by f'{mname}_{pname}'
        if mname:
            pname = f'{mname}_{pcad.name}'
        solid_names += Bitter_Gmsh(pcad, pname, is2D, verbose)
        NHelices.append(0)
        NChannels.append(0)
        NIsolants.append(0)
        Boxes[pname] = ('Bitter', pcad.boundingBox())
        # TODO prepend name with part name
    elif isinstance(pcad, Supra):
        # TODO replace pname by f'{mname}_{pname}'
        if mname:
            pname = f'{mname}_{pname}'
        solid_names += Supra_Gmsh(pcad, pname, is2D, verbose)
        NHelices.append(0)
        NChannels.append(0)
        NIsolants.append(0)
        Boxes[pname] = ('Supra', pcad.boundingBox())
        # TODO prepend name with part name
    elif isinstance(pcad, Insert):
        # keep pname
        # print(f'Insert: {pname}')
        (_names, _NHelices, _NChannels, _NIsolants, ring_ids) = Insert_Gmsh(pcad, pname, is2D, verbose)
        solid_names += _names
        NHelices.append(_NHelices)
        NChannels.append(_NChannels)
        NIsolants.append(_NIsolants)
        Boxes[pname] = ('Insert', pcad.boundingBox())
        # print(f'Boxes[{pname}]={Boxes[pname]}')
        # TODO prepend name with part name
    if verbose:
        print(f"Magnet_Gmsh: {cad} Done [solids {len(solid_names)}]")
        print(f'Magnet_Gmsh: Boxes={Boxes}')
    return (solid_names, NHelices, NChannels, NIsolants, Boxes, ring_ids)

def MSite_Gmsh(mdata, cad, gname, is2D, verbose):
    """
    Load MSite cad

    mdata: dict with mname and type
    """

    print("MSite_Gmsh:", cad)

    compound = []
    solid_names = []
    NHelices = []
    NChannels = []
    NIsolants = []
    Boxes = []
    ring_ids = {}

    # Get mnames from mdata dict
    if mdata:
        mnames = [*mdata]

    def ddd(cad_data, mname):
        (_names, _NHelices, _NChannels, _NIsolants, _Boxes, _ring_ids) = Magnet_Gmsh(mname, cad_data, gname, is2D, verbose)
        compound.append(cad_data)
        solid_names += _names
        NHelices += _NHelices
        NChannels += _NChannels
        NIsolants += _NIsolants
        Boxes.append(_Boxes)
        ring_ids.update(_ring_ids)
        # print(f"MSite_Gmsh: cad_data={cad_data}, _names={len(solid_names)}, solids={len(solid_names)}")

    i = 0
    if isinstance(cad.magnets, str):
        # mdata: 1 entry only
        if mdata:
            mname = mnames[i]
            i + 1
        else:
            mname = ""
        ddd(cad.magnets, mname)
        # print(f"MSite_Gmsh: cad.magnets={cad.magnets} solids={len(solid_names)}")
    elif isinstance(cad.magnets, list):
        # mdata: as many entries as in cad.magnets
        if mdata:
            mname = mnames[i]
            i + 1
        else:
            mname = ""
        for magnet in cad.magnets:
            ddd(magnet, mname)
            # print(f"MSite_Gmsh: magnet={magnet} solids={len(solid_names)}")
    elif isinstance(cad.magnets, dict):
        # mdata: as many entries as in cad.magnets
        if mdata:
            mname = mnames[i]
            i + 1
        else:
            mname = ""
        for key in cad.magnets:
            if isinstance(cad.magnets[key], str):
                ddd(cad.magnets[key], mname)
                # print(f"MSite_Gmsh: cad.magnets[key]={cad.magnets[key]} solids={len(solid_names)}")
            elif isinstance(cad.magnets[key], list):
                for mpart in cad.magnets[key]:
                    ddd(mpart, mname)
                    # print(f"MSite_Gmsh: mpart={mpart} solids={len(solid_names)}")

    if verbose:
        print(f"MSite_Gmsh: {cad} Done [solids {len(solid_names)}]")
    return (compound, solid_names, NHelices, NChannels, NIsolants, Boxes, ring_ids)

def main():
    tags = {}

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("--mdata", help="specify magnet data", type=json.loads)
    parser.add_argument("--debug", help="activate debug", action='store_true')
    parser.add_argument("--verbose", help="activate verbose", action='store_true')
    parser.add_argument("--env", help="load settings.env", action="store_true")
    parser.add_argument("--wd", help="set a working directory", type=str, default="")

    subparsers = parser.add_subparsers(title="commands", dest="command", help='sub-command help')

    # parser_cfg = subparsers.add_parser('cfg', help='cfg help')
    parser_mesh = subparsers.add_parser('mesh', help='mesh help')
    parser_adapt = subparsers.add_parser('adapt', help='adapt help')

    parser_mesh.add_argument("--geo", help="specifiy geometry yaml file (use Auto to automatically retreive yaml filename fro xao, default is None)", type=str, default="None")

    parser_mesh.add_argument("--algo2d", help="select an algorithm for 2d mesh", type=str,
                             choices=['MeshAdapt', 'Automatic', 'Initial', 'Delaunay', 'Frontal-Delaunay', 'BAMG'], default='Delaunay')
    parser_mesh.add_argument("--algo3d", help="select an algorithm for 3d mesh", type=str,
                             choices=['Delaunay', 'Initial', 'Frontal', 'MMG3D', 'HXT', 'None'], default='None')
    parser_mesh.add_argument(
        "--lc", help="specify characteristic lengths (Magnet1, Magnet2, ..., Air (aka default))", type=float, nargs='+', metavar='LC')
    parser_mesh.add_argument("--scaling", help="scale to m (default unit is mm)", action='store_true')
    parser_mesh.add_argument("--dry-run", help="mimic mesh operation without actually meshing", action='store_true')

    # TODO add similar option to salome HIFIMAGNET plugins
    parser_mesh.add_argument("--group", help="group selected items in mesh generation (Eg Isolants, Leads, CoolingChannels)", nargs='+', metavar='BC', type=str)
    parser_mesh.add_argument("--hide", help="hide selected items in mesh generation (eg Isolants)", nargs='+', metavar='Domain', type=str)

    parser_adapt.add_argument(
        "--bgm", help="specify a background mesh", type=str, default=None)
    parser_adapt.add_argument(
        "--estimator", help="specify an estimator (pos file)", type=str, default=None)

    args = parser.parse_args()
    if args.debug:
        print(args)

    cwd = os.getcwd()
    if args.wd:
        os.chdir(args.wd)

    if args.mdata:
        print(f'mdata={args.mdata}')
        # return 1

    hideIsolant = False
    groupIsolant = False
    groupLeads = False
    groupCoolingChannels = False

    is2D = False
    GeomParams = {
        'Solid': (3, 'solids'),
        'Face': (2, "face")
    }

    # check if Axi is in input_file to see wether we are working with a 2D or 3D geometry
    if "Axi" in args.input_file:
        print("2D geometry detected")
        is2D = True
        GeomParams['Solid'] = (2, 'faces')
        GeomParams['Face'] = (1, 'edge')

    if args.command == 'mesh':
        if args.hide:
            hideIsolant = ("Isolants" in args.hide)
        if args.group:
            groupIsolant = ("Isolants" in args.group)
            groupLeads = ("Leads" in args.group)
            groupCoolingChannels = ("CoolingChannels" in args.group)

    print("hideIsolant:", hideIsolant)
    print("groupIsolant:", groupIsolant)
    print("groupLeads:", groupLeads)
    print("groupCoolingChannels:", groupCoolingChannels)

    MeshAlgo2D = {
        'MeshAdapt' : 1,
        'Automatic' : 2,
        'Initial' : 3,
        'Delaunay' : 5,
        'Frontal-Delaunay' : 6,
        'BAMG' : 7
    }

    MeshAlgo3D = {
        'Delaunay' : 1, 'Initial' : 3, 'Frontal' : 4, 'MMG3D': 7, 'HXT' : 10
    }

    # init gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    # (0: silent except for fatal errors, 1: +errors, 2: +warnings, 3: +direct, 4: +information, 5: +status, 99: +debug)
    gmsh.option.setNumber("General.Verbosity", 0)
    if args.debug or args.verbose:
        gmsh.option.setNumber("General.Verbosity", 2)

    file = args.input_file # r"HL-31_H1.xao"
    (gname, tree, volumes) = load_Xao(file, GeomParams, args.debug)

    # Loading yaml file to get infos on volumes
    cfgfile = ""
    solid_names = []
    bc_names = []

    innerLead_exist = False
    outerLead_exist = False
    NHelices = 0
    NChannels = 0
    Boxes = []
    ring_ids = None

    if args.command == 'mesh':
        if args.geo != "None":
            cfgfile = args.geo
        if args.geo == 'Auto':
            cfgfile = gname+".yaml"
        print("cfgfile:", cfgfile)

    compound = []
    if cfgfile:
        cad = None
        with open(cfgfile, 'r') as cfgdata:
            cad = yaml.load(cfgdata, Loader=yaml.FullLoader)

        # print(f"cfgfile: {cad} type: {type(cad)}")
        # TODO get solid names (see Salome HiFiMagnet plugin)
        if isinstance(cad, MSite):
            if args.verbose: print("load cfg MSite")
            (compound, _names, NHelices, NChannels, NIsolants, _Boxes, ring_ids) = MSite_Gmsh(args.mdata, gname, is2D, args.verbose)
            # print(f'_Boxes: {_Boxes}, {len(_Boxes)}')
            Boxes = _Boxes
            solid_names += _names
        elif isinstance(cad, Bitter):
            if args.verbose: print("load cfg Bitter")
            solid_names += Bitter_Gmsh(cad, gname, is2D, args.verbose)
            Boxes.append({cad.name: ('Bitter', cad.boundingBox())})
        elif isinstance(cad, Supra):
            if args.verbose: print("load cfg Supra")
            solid_names += Supra_Gmsh(cad, gname, is2D, args.verbose)
            Boxes.append({cad.name: ('Supra', cad.boundingBox())})
        elif isinstance(cad, Insert):
            if args.verbose: print("load cfg Insert")
            (_names, NHelices, NChannels, NIsolants, ring_ids) = Insert_Gmsh(cad, gname, is2D, args.verbose)
            Boxes.append({cad.name: ('Insert', cad.boundingBox())})
            solid_names += _names
        elif isinstance(cad, Helix):
            if args.verbose: print("load cfg Helix")
            solid_names += Helix_Gmsh(cad, gname, is2D, args.verbose)
            Boxes.append({cad.name: ('Helix', cad.boundingBox())})
        else:
            raise Exception(f"unsupported type of cad {type(cad)}")

        if "Air" in args.input_file:
            solid_names.append("Air")
            if hideIsolant:
                raise Exception("--hide Isolants cannot be used since cad contains Air region")

    # print(f"solid_names[{len(solid_names)}]: {solid_names}")

    # print(f"GeomParams['Solid'][0]: {GeomParams['Solid'][0]}")
    # print(f"gmsh solids: {len(gmsh.model.getEntities(2))}")
    nsolids = len(gmsh.model.getEntities(GeomParams['Solid'][0]))
    assert (len(solid_names) == nsolids), f"Wrong number of solids: in yaml {len(solid_names)} in gmsh {nsolids}"
    # print(len(solid_names), nsolids)

    print(f"compound = {compound}")
    print(f"NHelices = {NHelices}")
    print(f"NChannels = {NChannels}")
    print(f"Boxes = {Boxes}")
    print(f"ring_ids = {ring_ids}")

    # use yaml data to identify solids id...
    # Insert solids: H1_Cu, H1_Glue0, H1_Glue1, H2_Cu, ..., H14_Glue1, R1, R2, ..., R13, InnerLead, OuterLead, Air
    # HR: Cu, Kapton0, Kapton1, ... KaptonXX
    if args.verbose:
        print("Get solids:")
    tr_subelements = tree.xpath('//'+GeomParams['Solid'][1])
    stags = {}
    for i, sgroup in enumerate(tr_subelements):
        # print("solids=", sgroup.attrib['count'])

        for j, child in enumerate(sgroup):
            sname = solid_names[j]
            oname = sname
            # print(f'sname={sname}: child.attrib={child.attrib}')
            if 'name' in child.attrib and child.attrib['name'] != "":
                sname = child.attrib['name'].replace("from_", '')
                # print(f'sname={sname}')
                if sname.startswith("Ring-H"):
                    sname = ring_ids[sname]

            indices = int(child.attrib['index'])+1
            if args.verbose:
                print(f'sname[{j}]: oname={oname}, sname={sname}, child.attrib={child.attrib}, solid_name={solid_names[j]}, indices={indices}')

            skip = False
            if hideIsolant and ("Isolant" in sname or "Glue" in sname or "Kapton" in sname):
                if args.verbose:
                    print("skip isolant: ", sname)
                skip = True

            # TODO if groupIsolant and "glue" in sname:
            #    sname = remove latest digit from sname
            if groupIsolant and  ("Isolant" in sname or "Glue" in sname or "Kapton" in sname):
                sname = re.sub(r'\d+$', '', sname)

            if not skip:
                if sname in stags:
                    stags[sname].append(indices)
                else:
                    stags[sname] = [indices]

    # Physical Volumes
    if args.verbose:
        print("Solidtags:")
    for stag in stags:
        pgrp = gmsh.model.addPhysicalGroup(GeomParams['Solid'][0], stags[stag])
        gmsh.model.setPhysicalName(GeomParams['Solid'][0], pgrp, stag)
        if args.verbose:
            print(stag, ":", stags[stag], pgrp)

    # TODO review if several insert in msite
    # so far assume only one insert that appears as first magnets
    Channel_Submeshes = []
    if isinstance(NChannels, int):
        _NChannels = NChannels
    elif isinstance(NChannels, list):
        _NChannels = NChannels[0]
    for i in range(0, _NChannels):
        names = []
        inames = []
        if i == 0:
            names.append(f"R{i+1}_R0n") # check Ring nummerotation
        if i >= 1:
            names.append(f"H{i}_rExt")
            if not hideIsolant:
                isolant_names = [f"H{i}_IrExt"]
                kapton_names = [f"H{i}_kaptonsIrExt"]
                names = names + isolant_names + kapton_names
                # inames = inames + isolant_names + kapton_names
        if i >= 2:
            names.append(f"R{i-1}_R1n")
        if i < _NChannels:
            names.append(f"H{i+1}_rInt")
            if not hideIsolant:
                isolant_names = [f"H{i+1}_IrInt"]
                kapton_names = [f"H{i+1}_kaptonsIrInt"]
                names = names + isolant_names + kapton_names
                # inames = inames + isolant_names + kapton_names
        # Better? if i+1 < nchannels:
        if i != 0 and i+1 < _NChannels:
            names.append(f"R{i}_CoolingSlits")
            names.append(f"R{i}_R0n")
        Channel_Submeshes.append(names)
        #
        # For the moment keep iChannel_Submeshes into
        # iChannel_Submeshes.append(inames)

    if args.debug:
        print("Channel_Submeshes:")
        for channel in Channel_Submeshes:
            print(f'\t{channel}')

    # get groups
    if args.verbose:
        print("Get BC groups")
    tr_elements = tree.xpath('//group')

    if args.debug:
        print('Ring_ids')
        for rkey in ring_ids:
            print(f'rkey={rkey}, rvalue={ring_ids[rkey]}')

    bctags = {}
    for i, group in enumerate(tr_elements):
        #print(etree.tostring(group))
        #print("group:", group.keys())

        ## dimension: "solid", "face", "edge"
        if args.debug:
            print("name=", group.attrib['name'], group.attrib['dimension'], group.attrib['count'])

        indices = []
        if group.attrib['dimension'] == GeomParams['Face'][1]:
            for child in group:
                indices.append(int(child.attrib['index'])+1)

            # get bc name
            insert_id = gname.replace("_withAir", "")
            sname = group.attrib['name'].replace(insert_id+"_", "")
            sname = sname.replace('===', '_')

            if args.debug:
                print("sname=", sname)

            if not ring_ids is None:
                if sname.endswith('_rInt') or sname.endswith('_rExt'):
                    for rkey in ring_ids:
                        # print(f'rkey={rkey}, rvalue={ring_ids[rkey]}')
                        if sname.startswith(rkey):
                            sname = sname.replace(rkey, ring_ids[rkey])
                
                if sname.startswith('Ring-H'):
                    #print(f"=== {sname} ===")
                    for rkey in ring_ids:
                        # print(f'rkey={rkey}, rvalue={ring_ids[rkey]}')
                        if sname.startswith(rkey):
                            sname = sname.replace(rkey, ring_ids[rkey])
                    #print(f"Ring BC: {sname}")

            sname = sname.replace("Air_","")
            if args.debug:
                print(sname, indices, insert_id)

            skip = False
            # remove unneeded surfaces for Rings: BP for even rings and HP for odd rings
            if sname.startswith('Ring'):
                num = int(sname.split('_')[0].replace('R', ''))
                if num % 2 == 0 and 'BP' in sname:
                    skip = True
                if num % 2 != 0 and 'HP' in sname:
                    skip = True

            # keep only H0_V0 if no innerlead otherwise keep Lead_V0
            # keep only H14_V1 if not outerlead otherwise keep outerlead V1
            # print(innerLead_exist, re.search('H\d+_V0',sname))
            if innerLead_exist:
                match = re.search('H\d+_V0', sname)
                if match or (sname.startswith("Inner") and sname.endswith("V1")):
                    skip = True
            else:
                match = re.search('H\d+_V0', sname)
                if match:
                    num = int(sname.split('_')[0].replace('H', ''))
                    if num != 1:
                        skip = True
            if outerLead_exist:
                match = re.search('H\d+_V1', sname)
                if match:
                    skip = True
                if sname.startswith("Outer") and sname.endswith("V1"):
                    skip = True
            else:
                match = re.search('H\d+_V1', sname)
                if match:
                    num = int(sname.split('_')[0].replace('H', ''))
                    if num != NHelices:
                        skip = True

            # groupCoolingChannels option (see Tools_SMESH::CreateChannelSubMeshes for HL and for HR ??) + watch out when hideIsolant is True
            # TODO case of HR: group HChannel and muChannel per Helix
            if groupCoolingChannels:
                for j, channel_id in enumerate(Channel_Submeshes):
                    for cname in channel_id:
                        if sname.endswith(cname):
                            sname = f"Channel{j}"
                            break

                # TODO make it more genral
                # so far assume only one insert and  insert is the 1st compound
                if compound:
                    if sname.startswith(compound[0]):
                        if "_rInt" in sname or "_rExt" in sname:
                            skip = True
                        if "_IrInt" in sname or "_IrExt" in sname:
                            skip = True
                        if "_iRint" in sname or "_iRext" in sname:
                            skip = True
                else:
                    if "_rInt" in sname or "_rExt" in sname:
                        skip = True
                    if "_IrInt" in sname or "_IrExt" in sname:
                        skip = True
                    if "_iRint" in sname or "_iRext" in sname:
                        skip = True

            # if hideIsolant remove "iRint"|"iRext" in Bcs otherwise sname: do not record physical surface for Interface
            if hideIsolant:
                if 'IrInt' in sname or 'IrExt' in sname:
                    skip = True
                if 'iRint' in sname or 'iRext' in sname:
                    skip = True
                if 'Interface' in sname:
                    if groupIsolant:
                        sname = re.sub(r'\d+$', '', sname)

            if groupIsolant:
                if ('IrInt' in sname or 'IrExt' in sname):
                    sname = re.sub(r'\d+$', '', sname)
                if ('iRint' in sname or 'iRext' in sname):
                    sname = re.sub(r'\d+$', '', sname)
                    # print("groupBC:", sname)
                if 'Interface' in sname:
                    # print("groupBC: skip ", sname)
                    skip = True

            if args.debug:
                print("name=", group.attrib['name'], group.attrib['dimension'], group.attrib['count'], f"sname={sname}", "skip=", skip)
            if not skip:
                if not sname in bctags:
                    bctags[sname] = indices
                else:
                    for index in indices:
                        bctags[sname].append(index)

    # Physical Surfaces
    if args.verbose:
        print("BCtags:")
    for bctag in bctags:
        pgrp = gmsh.model.addPhysicalGroup(GeomParams['Face'][0], bctags[bctag])
        gmsh.model.setPhysicalName(GeomParams['Face'][0], pgrp, bctag)
        if args.verbose:
            print(bctag, bctags[bctag], pgrp)

    Origin = gmsh.model.occ.addPoint(0, 0, 0, 0.1, 0)

    # Generate the mesh and write the mesh file
    gmsh.model.occ.synchronize()

    # TODO write a template geo gmsh file for later use(gname + ".geo")

    # TODO: get solid id for glue
    # Get Helical cuts EndPoints
    EndPoints_tags = [0]
    VPoints_tags = []

    if isinstance(cad, Insert) or isinstance(cad, Helix):
        # TODO: loop over tag from Glue or Kaptons (here [2, 3])
        glue_tags = [i+1  for i, name in enumerate(solid_names) if ("Isolant" in name or ("Glue" in name or "Kapton" in name))]
        if args.verbose:
            print("glue_tags: ", glue_tags)
        for tag in glue_tags:
            if args.verbose:
                print(f"BC glue[{tag}:", gmsh.model.getBoundary([(GeomParams['Solid'][0], tag)]))
            for (dim, tag) in gmsh.model.getBoundary([(GeomParams['Solid'][0], tag)]):
                gtype = gmsh.model.getType(dim, tag)
                if gtype == "Plane":
                    Points = gmsh.model.getBoundary([(GeomParams['Face'][0], tag)], recursive=True)
                    for p in Points:
                        EndPoints_tags.append(p[1])
            print("EndPoints:", EndPoints_tags)

        """
        # TODO: get solid id for Helix (here [1])
        cu_tags = [i  for i,name in enumerate(solid_names) if name.startswith('H') and "Cu" in name]
        # TODO: for shape force also the mesh to be finer near shapes
        # How to properly detect shapes in brep ???
        # Get V0/V1 EndPoints
        # Eventually add point from V probes see: https://www.pygimli.org/_examples_auto/1_meshing/plot_cad_tutorial.html
        for (dim, tag) in gmsh.model.getBoundary([(3,1)]):
            type = gmsh.model.getType(dim, tag)
            if type == "Plane":
                Points = gmsh.model.getBoundary([(2, tag)], recursive=True)
                    for p in Points:
                        if not p[1] in EndPoints_tags:
                            VPoints_tags.append(p[1])
        """
        print("VPoints:", VPoints_tags)

    if args.command == 'mesh' and not args.dry_run:

        lcs = []
        if args.debug:
            print('args.lc={args.lc}')

        # if not mesh characteristic length is given
        if not args.lc is None:
            if not isinstance(args.lc, list):
                lcs.append(args.lc)
            else:
                lcs = args.lc

        unit = 1
        # load brep file into gmsh
        if args.scaling:
            unit = 0.001
            gmsh.option.setNumber("Geometry.OCCScaling", unit)

        if not lcs:
            print('Mesh Length Characteristics:')
            # print(f'Boxes: {Boxes}, type={type(Boxes)}')
            for box in Boxes:
                for item in box:
                    # print(f'{item}: box[item]={box[item]}')
                    cadtype, (r, z) = box[item]
                    r1 = float(r[1])
                    r0 = float(r[0])
                    lcs.append((r1-r0)/30.) # r,z are in mm in yaml files
                    print(f'\t{item}: {lcs[-1]}')
            if "Air" in args.input_file:
                lcs.append(lcs[-1]*20)
                print(f'Air: {lcs[-1]}')
        else:
            # print(f'Boxes: {Boxes}')
            nboxes = len(Boxes)
            if "Air" in args.input_file:
                assert (nboxes == len(lcs)-1), f"Wrong number of mesh length size: {len(Boxes)} magnets whereas lcs contains {len(lcs)-1} mesh size"
            else:
                assert (nboxes == len(lcs)), f"Wrong number of mesh length size: {len(Boxes)} magnets whereas lcs contains {len(lcs)} mesh size"

        # load brep file into gmsh
        if args.scaling:
            unit = 0.001
            gmsh.option.setNumber("Geometry.OCCScaling", unit)

        # Assign a mesh size to all the points:
        lcar1 = lcs[-1]
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lcar1)

        # Get points from Physical volumes
        # from volume name use correct lc characteristic
        z_eps = 1.e-6
        for i, box in enumerate(Boxes):
            for key in box:
                mtype = box[key][0]
                # print(f'box[{i}]={key} mtype={mtype} lc={lcs[i]} boundingbox={box[key][1]}')
                (r, z) = box[key][1]
                if mtype == 'Supra':
                    z[0] *= 1.1
                    z[1] *= 1.1

                ov = gmsh.model.getEntitiesInBoundingBox(r[0], z[0], -z_eps, r[1], z[1], z_eps, 0)
                gmsh.model.mesh.setSize(ov, lcs[i])

        # LcMax -                         /------------------
        #                               /
        #                             /
        #                           /
        # LcMin -o----------------/
        #        |                |       |
        #      Point           DistMin DistMax
        # Field 1: Distance to electrodes

        if EndPoints_tags:
            gmsh.model.mesh.field.add("Distance", 1)
            gmsh.model.mesh.field.setNumbers(1, "NodesList", EndPoints_tags)

            # Field 2: Threshold that dictates the mesh size of the background field
            gmsh.model.mesh.field.add("Threshold", 2)
            gmsh.model.mesh.field.setNumber(2, "IField", 1)
            gmsh.model.mesh.field.setNumber(2, "LcMin", lcar1/20.)
            gmsh.model.mesh.field.setNumber(2, "LcMax", lcar1)
            gmsh.model.mesh.field.setNumber(2, "DistMin", 5*unit)
            gmsh.model.mesh.field.setNumber(2, "DistMax", 10*unit)
            gmsh.model.mesh.field.setNumber(2, "StopAtDistMax", 15*unit)
            gmsh.model.mesh.field.setAsBackgroundMesh(2)

            # gmsh.model.mesh.field.add("Distance", 3)
            # gmsh.model.mesh.field.setNumbers(3, "NodesList", VPoints_tags)

            # # Field 3: Threshold that dictates the mesh size of the background field
            # gmsh.model.mesh.field.add("Threshold", 4)
            # gmsh.model.mesh.field.setNumber(4, "IField", 3)
            # gmsh.model.mesh.field.setNumber(4, "LcMin", lcar1/3.)
            # gmsh.model.mesh.field.setNumber(4, "LcMax", lcar1)
            # gmsh.model.mesh.field.setNumber(4, "DistMin", 0.2)
            # gmsh.model.mesh.field.setNumber(4, "DistMax", 1.5)
            # gmsh.model.mesh.field.setNumber(4, "StopAtDistMax", 1)

            # # Let's use the minimum of all the fields as the background mesh field:
            # gmsh.model.mesh.field.add("Min", 5)
            # gmsh.model.mesh.field.setNumbers(5, "FieldsList", [2, 4])
            # gmsh.model.mesh.field.setAsBackgroundMesh(5)

        if args.algo2d != 'BAMG':
            gmsh.option.setNumber("Mesh.Algorithm", MeshAlgo2D[args.algo2d])
        else:
            # # They can also be set for individual surfaces, e.g. for using `MeshAdapt' on
            gindex = len(stags) + len(bctags)
            for tag in range(len(stags), gindex):
                print(f"Apply BAMG on tag={tag}")
                gmsh.model.mesh.setAlgorithm(2, tag, MeshAlgo2D[args.algo2d])

        if args.algo3d != 'None':
            gmsh.option.setNumber("Mesh.Algorithm3D", MeshAlgo3D[args.algo3d])
            gmsh.model.mesh.generate(3)
        else:
            gmsh.model.mesh.generate(2)

        meshname = gname
        if is2D:
            meshname += "-Axi"
        if "Air" in args.input_file:
            meshname += "_withAir"
        print(f'Save mesh {meshname}.msh to {os.getcwd()}')
        gmsh.write(f'{meshname}.msh')

    if args.command == 'adapt':
        print("adapt mesh not implemented yet")
    gmsh.finalize()
    return 0

if __name__ == "__main__":
    main()
