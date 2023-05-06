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
from fudgeo.geometry.util import make_header, unpack_header
from tests.conversion.geo import (
    point_lists_to_gpkg_multi_polygon, point_lists_to_gpkg_polygon)
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
    srs_id, offset, is_empty = unpack_header(data[:8])
    assert srs_id == 4326
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty)
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


def test_linear_ring(header):
    """
    Test linear ring wkb
    """
    values = [(0, 0), (1, 1), (2, 0), (0, 0)]
    ring = LinearRing(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring._to_wkb()
    assert wkb == _linear_ring_to_wkb(values)
# End test_linear_ring function


def test_linear_ring_z(header):
    """
    Test linear ring Z wkb
    """
    values = [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)]
    ring = LinearRingZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring._to_wkb()
    assert wkb == _linear_ring_z_to_wkb(values)
# End test_linear_ring_z function


def test_linear_ring_m(header):
    """
    Test linear ring M wkb
    """
    values = [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)]
    ring = LinearRingM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring._to_wkb()
    assert wkb == _linear_ring_m_to_wkb(values)
# End test_linear_ring_m function


def test_linear_ring_zm(header):
    """
    Test linear ring ZM wkb
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1), (2, 0, 2, 0), (0, 0, 0, 0)]
    ring = LinearRingZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring._to_wkb()
    assert wkb == _linear_ring_zm_to_wkb(values)
# End test_linear_ring_zm function


def test_polygon(header):
    """
    Test polygon wkb
    """
    values = [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
              [(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]]
    poly = Polygon(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_to_wkb_polygon(values)
    assert poly.to_gpkg() == point_lists_to_gpkg_polygon(header, values)
    assert Polygon.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon function


def test_polygon_z(header):
    """
    Test polygon Z wkb
    """
    values = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    poly = PolygonZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_z_to_wkb_polygon_z(values)
    assert PolygonZ.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon_z function


def test_polygon_m(header):
    """
    Test polygon M wkb
    """
    values = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    poly = PolygonM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_m_to_wkb_polygon_m(values)
    assert PolygonM.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon_m function


def test_polygon_zm(header):
    """
    Test polygon ZM wkb
    """
    values = [[(0, 0, 0, 0), (0, 1, 1, 10), (1, 1, 1, 20),
               (1, 0, 1, 30), (0, 0, 0, 40)],
              [(5, 5, 5, 50), (5, 15, 10, 60), (15, 15, 15, 70),
               (15, 5, 20, 80), (5, 5, 5, 90)]]
    poly = PolygonZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_zm_to_wkb_polygon_zm(values)
    assert PolygonZM.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon_zm function


def test_multi_polygon(header):
    """
    Test multi polygon wkb
    """
    values = [[[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]],
              [[(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]],
              [[(7, 7), (7, 17), (17, 17), (7, 7)]]]
    poly = MultiPolygon(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_to_wkb_multipolygon(values)
    assert poly.to_gpkg() == point_lists_to_gpkg_multi_polygon(header, values)
    assert MultiPolygon.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon function


def test_multi_polygon_z(header):
    """
    Test multi polygon Z wkb
    """
    values = [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]],
              [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]]
    poly = MultiPolygonZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_z_to_wkb_multipolygon_z(values)
    assert MultiPolygonZ.from_gpkg(poly.to_gpkg()) == poly
# End test_multi_polygon_z function


def test_multi_polygon_m(header):
    """
    Test multi polygon M wkb
    """
    values = [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]],
              [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]]
    poly = MultiPolygonM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_m_to_wkb_multipolygon_m(values)
    assert MultiPolygonM.from_gpkg(poly.to_gpkg()) == poly
# End test_multi_polygon_m function


def test_multi_polygon_zm(header):
    """
    Test multi polygon ZM wkb
    """
    values = [[[(0, 0, 0, 10), (0, 1, 1, 20), (1, 1, 1, 30), (1, 0, 1, 40),
                (0, 0, 0, 50)]],
              [[(5, 5, 5, 60), (5, 15, 10, 70), (15, 15, 15, 80),
                (15, 5, 20, 90), (5, 5, 5, 100)]]]
    poly = MultiPolygonZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        poly.attribute = 10
    assert poly._to_wkb() == point_lists_zm_to_wkb_multipolygon_zm(values)
    assert MultiPolygonZM.from_gpkg(poly.to_gpkg()) == poly
# End test_multi_polygon_zm function


if __name__ == '__main__':  # pragma: no cover
    pass
