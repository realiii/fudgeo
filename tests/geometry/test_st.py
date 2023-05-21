# -*- coding: utf-8 -*-
"""
Test ST Functions
"""


from math import nan

from pytest import mark

from fudgeo.constant import WGS84
from fudgeo.geometry import (
    LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon)
from fudgeo.geometry.st import (
    _st_is_empty, _st_max_x, _st_max_y, _st_min_x, _st_min_y)


@mark.parametrize('geom, expected', [
    (None, None),
    (Point(x=1, y=2, srs_id=WGS84), 0),
    (Point(x=nan, y=nan, srs_id=WGS84), 1),
    (Point.empty(WGS84), 1),
    (MultiPoint([(0, 0), (1, 1)], srs_id=WGS84), 0),
    (MultiPoint([], srs_id=WGS84), 1),
    (LineString([(0, 0), (1, 1)], srs_id=WGS84), 0),
    (LineString([], srs_id=WGS84), 1),
    (LineString.from_gpkg(b'GP\x00\x11\xe6\x10\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00'), 1),
    (MultiLineString([[(0, 0), (1, 1)]], srs_id=WGS84), 0),
    (MultiLineString([], srs_id=WGS84), 1),
    (MultiLineString.from_gpkg(b'GP\x00\x11\xe6\x10\x00\x00\x01\x05\x00\x00\x00\x00\x00\x00\x00'), 1),
    (Polygon([[(0, 0), (0, 1), (1, 1), (1, 0)]], srs_id=WGS84), 0),
    (Polygon([], srs_id=WGS84), 1),
    (Polygon.from_gpkg(b'GP\x00\x11\xe6\x10\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00'), 1),
    (MultiPolygon([[[(0, 0), (0, 1), (1, 1), (1, 0)]]], srs_id=WGS84), 0),
    (MultiPolygon([], srs_id=WGS84), 1),
    (MultiPolygon.from_gpkg(b'GP\x00\x11\xe6\x10\x00\x00\x01\x06\x00\x00\x00\x00\x00\x00\x00'), 1),
])
def test_st_is_empty(geom, expected):
    """
    Test ST is empty
    """
    if geom is not None:
        geom = geom.to_gpkg()
    assert _st_is_empty(geom) == expected
# End test_st_is_empty function


@mark.parametrize('geom, expected', [
    (Point.from_gpkg(b'GP\x00\x01\t\x12\x00\x00\x01\x01\x00\x00\x00\xd0]#\x93\x9d\xa3\\\xc0X\x9bq\x1a\xa2sI@'), (-114.55649259999996, -114.55649259999996, 50.90338450000007, 50.90338450000007)),
    (Point(x=1, y=2, srs_id=WGS84), (1, 1, 2, 2)),
    (MultiPoint([(0, 1), (2, 3)], srs_id=WGS84), (0, 2, 1, 3)),
    (LineString([(0, 1), (2, 3)], srs_id=WGS84), (0, 2, 1, 3)),
    (MultiLineString([[(0, 1), (2, 3)]], srs_id=WGS84), (0, 2, 1, 3)),
    (Polygon([[(0, 0.1), (0.2, 1.3), (1.4, 1.5), (1.6, 0.7)]], srs_id=WGS84), (0, 1.6, 0.1, 1.5)),
    (MultiPolygon([[[(0, 0.1), (0.2, 1.3), (1.4, 1.5), (1.6, 0.7)]]], srs_id=WGS84), (0, 1.6, 0.1, 1.5)),
])
def test_min_max(geom, expected):
    """
    Test min / max functions for x and y
    """
    geometry = bytes(geom.to_gpkg())
    min_x = _st_min_x(geometry)
    max_x = _st_max_x(geometry)
    min_y = _st_min_y(geometry)
    max_y = _st_max_y(geometry)
    assert (min_x, max_x, min_y, max_y) == expected
# End test_min_max function


if __name__ == '__main__':  # pragma: no cover
    pass
