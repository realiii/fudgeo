# -*- coding: utf-8 -*-
"""
Geometry
"""


from fudgeo.geometry.linestring import (
    LineString, LineStringZ, LineStringM, LineStringZM,
    MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM)
from fudgeo.geometry.point import (
    Point, PointZ, PointM, PointZM,
    MultiPoint, MultiPointZ, MultiPointM, MultiPointZM)
from fudgeo.geometry.polygon import (
    Polygon, PolygonZ, PolygonM, PolygonZM,
    MultiPolygon, MultiPolygonZ, MultiPolygonM, MultiPolygonZM)


__all__ = ['Point', 'PointZ', 'PointM', 'PointZM',
           'MultiPoint', 'MultiPointZ', 'MultiPointM', 'MultiPointZM',
           'LineString', 'LineStringZ', 'LineStringM', 'LineStringZM',
           'MultiLineString', 'MultiLineStringZ',
           'MultiLineStringM', 'MultiLineStringZM',
           'Polygon', 'PolygonZ', 'PolygonM', 'PolygonZM',
           'MultiPolygon', 'MultiPolygonZ',
           'MultiPolygonM', 'MultiPolygonZM']


if __name__ == '__main__':  # pragma: no cover
    pass
