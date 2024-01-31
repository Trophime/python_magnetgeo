#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Provides definiton for 2D Shape:

* Geom data: x, y
"""
from typing import List

import yaml


class Shape2D(yaml.YAMLObject):
    """
    name :

    params :
      x, y: list of points
    """

    yaml_tag = "Shape2D"

    def __init__(self, name: str, pts: List[List[float]]):
        """
        initialize object
        """
        self.name = name
        self.pts = pts

    def __repr__(self):
        """
        representation of object
        """
        return "%s(name=%r, pts=%r)" % (self.__class__.__name__, self.name, self.pts)

    def dump(self, name: str):
        """
        dump object to file
        """
        try:
            with open(f"{name}.yaml", "w") as ostream:
                yaml.dump(self, stream=ostream)
        except:
            raise Exception("Failed to Shape2D dump")

    def load(self, name: str):
        """
        load object from file
        """
        data = None
        try:
            with open(f"{name}.yaml", "r") as istream:
                data = yaml.load(stream=istream, Loader=yaml.FullLoader)
        except:
            raise Exception(f"Failed to load Shape2D data {name}.yaml")

        self.name = name
        self.pts = data.pts



def Shape_constructor(loader, node):
    """
    build an Shape object
    """
    values = loader.construct_mapping(node)
    name = values["name"]
    pts = values["pts"]
    return Shape2D(name, pts)


yaml.add_constructor(u"!Shape2D", Shape_constructor)

def create_circle(r: float, n: int = 20) -> Shape2D:
    from math import pi, cos, sin
    
    if n < 0:
        raise RuntimeError(f'create_rectangle: n got {n}, expect a positive integer')
    
    name = f'circle-{2*r}-mm'
    pts = []
    theta = 2 * pi / float(n)
    for i in range(n):
        x = r * cos(i* theta)
        y = r * sin(i * theta)
        pts.append([x,y])

    return Shape2D(name, pts)

def create_rectangle(x: float, y: float, dx: float, dy: float, fillet: int = 0) -> Shape2D:
    from math import pi, cos, sin
    
    if fillet < 0:
        raise RuntimeError(f'create_rectangle: fillet got {fillet}, expect a positive integer')

    name = f'rectangle-{dx}-{dy}-mm'
    if fillet == 0:
        pts = [
            [x,y],
            [x+dx, y],
            [x+dx, y+dy],
            [x, y+dy]
        ]
    else:

        pts = [ [x,y] ]
        theta = pi / float(fillet)
        xc = (x+dx)/2.
        yc = y
        r = dx/2.
        for i in range(fillet):
            _x = xc + r * cos(pi + i * theta)
            _y = yc + r * cos(pi + i * theta)
            pts.append([_x, _y])
        yc = y+dy
        for i in range(fillet):
            _x = xc + r * cos(i * theta)
            _y = yc + r * cos(i * theta)
            pts.append([_x, _y])
        
    return Shape2D(name, pts)

def create_angularslit(x: float, angle: float, dx: float, n: int = 10, fillet: int = 0) -> Shape2D:
    from math import pi, cos, sin
    
    if fillet < 0:
        raise RuntimeError(f'create_angularslit: fillet got {fillet}, expect a positive integer')
    if n < 0:
        raise RuntimeError(f'create_angularslit: n got {n}, expect a positive integer')

    name = f'angularslit-{dx}-{angle}-mm'

    pts = []
    theta = angle * pi / float(n)
    theta_ = pi / float(fillet)
    r = x
    r_ = dx/2.

    for i in range(n):
        x = r * cos(angle/2. - i * theta)
        y = r * sin(angle/2. - i * theta)
        pts.append([x, y])
        
    if fillet > 0:
        xc = (r + dx) * cos(-angle/2.) / 2
        yc = (r + dx) * sin(-angle/2.) / 2
        r_ = dx/2.
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            pts.append([_x, _y])
            
    r = x + dx
    for i in range(n):
        x = r * cos(-angle/2. + i * theta)
        y = r * sin(-angle/2. + i * theta)
        pts.append([x, y])
        
    if fillet > 0:
        xc = (r + dx) * cos(angle/2.) / 2
        yc = (r + dx) * sin(angle/2.) / 2
        for i in range(fillet):
            _x = xc + r_ * cos(pi + i * theta)
            _y = yc + r_ * cos(pi + i * theta)
            pts.append([_x, _y])
        
    return Shape2D(name, pts)

