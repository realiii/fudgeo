# -*- coding: utf-8 -*-
"""
Test Polygons
"""

from pytest import mark, raises

from fudgeo.constant import WGS84
from fudgeo.geometry import (
    MultiPolygon, MultiPolygonM, MultiPolygonZ, MultiPolygonZM, Polygon,
    PolygonM, PolygonZ, PolygonZM)
from fudgeo.geometry.polygon import (
    LinearRing, LinearRingM, LinearRingZ, LinearRingZM)
from fudgeo.geometry.util import Envelope, make_header, unpack_header
from tests.conversion.wkb import (
    _linear_ring_m_to_wkb, _linear_ring_to_wkb, _linear_ring_z_to_wkb,
    _linear_ring_zm_to_wkb, point_lists_m_to_wkb_multipolygon_m,
    point_lists_m_to_wkb_polygon_m, point_lists_to_wkb_multipolygon,
    point_lists_to_wkb_polygon, point_lists_z_to_wkb_multipolygon_z,
    point_lists_z_to_wkb_polygon_z, point_lists_zm_to_wkb_multipolygon_zm,
    point_lists_zm_to_wkb_polygon_zm)


def test_empty_polygon_gpkg():
    """
    Test empty Polygon GeoPackage
    """
    data = b'GP\x00\x11\xe6\x10\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00'
    srs_id, env_code, offset, is_empty = unpack_header(data[:8])
    assert srs_id == 4326
    assert env_code == 0
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty, envelope_code=0)
    assert header
    assert data[:len(header)] == header
    poly = Polygon.from_gpkg(data)
    assert poly.to_gpkg() == data
    assert isinstance(poly, Polygon)
    assert poly.rings == []
# End test_empty_polygon_gpkg function


@mark.parametrize('cls, wkb', [
    (Polygon, b'\x01\x03\x00\x00\x00\x00\x00\x00\x00'),
    (PolygonZ, b'\x01\xeb\x03\x00\x00\x00\x00\x00\x00'),
    (PolygonM, b'\x01\xd3\x07\x00\x00\x00\x00\x00\x00'),
    (PolygonZM, b'\x01\xbb\x0b\x00\x00\x00\x00\x00\x00')
])
def test_empty_polygon(cls, wkb):
    """
    Test Empty Polygon
    """
    geom = cls([], srs_id=WGS84)
    assert geom._to_wkb() == wkb
    assert isinstance(geom, cls)
    assert geom.rings == []
# End test_empty_polygon function


@mark.parametrize('cls, wkb', [
    (MultiPolygon, b'\x01\x06\x00\x00\x00\x00\x00\x00\x00'),
    (MultiPolygonZ, b'\x01\xee\x03\x00\x00\x00\x00\x00\x00'),
    (MultiPolygonM, b'\x01\xd6\x07\x00\x00\x00\x00\x00\x00'),
    (MultiPolygonZM, b'\x01\xbe\x0b\x00\x00\x00\x00\x00\x00')
])
def test_empty_multi_polygon(cls, wkb):
    """
    Test Empty Multi Polygon
    """
    geom = cls([], srs_id=WGS84)
    assert geom._to_wkb() == wkb
    assert isinstance(geom, cls)
    assert geom.polygons == []
# End test_empty_multi_polygon function


@mark.parametrize('cls, values, env_code, wkb_func, env', [
    (LinearRing, [(0, 0), (1, 1), (2, 0), (0, 0)], 1, _linear_ring_to_wkb, Envelope(code=1, min_x=0, max_x=2, min_y=0, max_y=1)),
    (LinearRingZ, [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)], 2, _linear_ring_z_to_wkb, Envelope(code=2, min_x=0, max_x=2, min_y=0, max_y=1, min_z=0, max_z=2)),
    (LinearRingM, [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)], 3, _linear_ring_m_to_wkb, Envelope(code=3, min_x=0, max_x=2, min_y=0, max_y=1, min_m=0, max_m=2)),
    (LinearRingZM, [(0, 0, 0, 0), (1, 1, 1, 1), (2, 0, 2, 0), (0, 0, 0, 0)], 4, _linear_ring_zm_to_wkb, Envelope(code=4, min_x=0, max_x=2, min_y=0, max_y=1, min_z=0, max_z=2, min_m=0, max_m=1)),
])
def test_linear_ring(cls, values, env_code, wkb_func, env):
    """
    Test linear ring wkb
    """
    ring = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring._to_wkb()
    assert wkb == wkb_func(values)
    assert not ring.is_empty
    assert ring.envelope == env
# End test_linear_ring function


@mark.parametrize('cls, values, env_code, wkb_func, env', [
    (Polygon, [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)], [(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]],
     1, point_lists_to_wkb_polygon, Envelope(code=1, min_x=0, max_x=15, min_y=0, max_y=15)),
    (PolygonZ, [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)], [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]],
     2, point_lists_z_to_wkb_polygon_z, Envelope(code=2, min_x=0, max_x=15, min_y=0, max_y=15, min_z=0, max_z=20)),
    (PolygonM, [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)], [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]],
     3, point_lists_m_to_wkb_polygon_m, Envelope(code=3, min_x=0, max_x=15, min_y=0, max_y=15, min_m=0, max_m=20)),
    (PolygonZM, [[(0, 0, 0, 0), (0, 1, 1, 10), (1, 1, 1, 20), (1, 0, 1, 30), (0, 0, 0, 40)], [(5, 5, 5, 50), (5, 15, 10, 60), (15, 15, 15, 70), (15, 5, 20, 80), (5, 5, 5, 90)]],
     4, point_lists_zm_to_wkb_polygon_zm, Envelope(code=4, min_x=0, max_x=15, min_y=0, max_y=15, min_z=0, max_z=20, min_m=0, max_m=90)),
])
def test_polygon(header, cls, values, env_code, wkb_func, env):
    """
    Test polygon wkb
    """
    poly = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == wkb_func(values)
    gpkg = poly.to_gpkg()
    assert gpkg.startswith(header(env_code))
    assert cls.from_gpkg(gpkg) == poly
    assert not poly.is_empty
    assert poly.envelope == env
# End test_polygon function


@mark.parametrize('cls, values, env_code, wkb_func, env', [
    (MultiPolygon, [[[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]], [[(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]], [[(7, 7), (7, 17), (17, 17), (7, 7)]]],
     1, point_lists_to_wkb_multipolygon, Envelope(code=1, min_x=0, max_x=17, min_y=0, max_y=17)),
    (MultiPolygonZ, [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]], [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]],
     2, point_lists_z_to_wkb_multipolygon_z, Envelope(code=2, min_x=0, max_x=15, min_y=0, max_y=15, min_z=0, max_z=20)),
    (MultiPolygonM, [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]], [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]],
     3, point_lists_m_to_wkb_multipolygon_m, Envelope(code=3, min_x=0, max_x=15, min_y=0, max_y=15, min_m=0, max_m=20)),
    (MultiPolygonZM, [[[(0, 0, 0, 10), (0, 1, 1, 20), (1, 1, 1, 30), (1, 0, 1, 40), (0, 0, 0, 50)]], [[(5, 5, 5, 60), (5, 15, 10, 70), (15, 15, 15, 80), (15, 5, 20, 90), (5, 5, 5, 100)]]],
     4, point_lists_zm_to_wkb_multipolygon_zm, Envelope(code=4, min_x=0, max_x=15, min_y=0, max_y=15, min_z=0, max_z=20, min_m=10, max_m=100)),
])
def test_multi_polygon(header, cls, values, env_code, wkb_func, env):
    """
    Test multi polygon wkb
    """
    poly = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == wkb_func(values)
    gpkg = poly.to_gpkg()
    assert gpkg.startswith(header(env_code))
    assert cls.from_gpkg(gpkg) == poly
    assert not poly.is_empty
    assert poly.envelope == env
# End test_multi_polygon function


if __name__ == '__main__':  # pragma: no cover
    pass
