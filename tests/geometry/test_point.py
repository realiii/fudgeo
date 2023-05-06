# -*- coding: utf-8 -*-
"""
Test Points
"""


from math import isnan

from pytest import mark, raises

from fudgeo.constant import WGS84
from fudgeo.geometry import (
    MultiPoint, MultiPointM, MultiPointZ, MultiPointZM, Point, PointM, PointZ,
    PointZM)
from fudgeo.geometry.util import make_header, unpack_header
from tests.conversion.geo import (
    point_m_to_gpkg_point_m, point_to_gpkg_point, point_z_to_gpkg_point_z,
    point_zm_to_gpkg_point_zm, points_to_gpkg_multipoint)
from tests.conversion.wkb import (
    multipoint_m_to_wkb_multipoint_m, multipoint_to_wkb_multipoint,
    multipoint_z_to_wkb_multipoint_z, multipoint_zm_to_wkb_multipoint_zm,
    point_m_to_wkb_point_m, point_to_wkb_point, point_z_to_wkb_point_z,
    point_zm_to_wkb_point_zm)


def test_empty_point_gpkg():
    """
    Test Empty Point from GeoPackage
    """
    data = b'GP\x00\x11\xe6\x10\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'
    srs_id, env_code, offset, is_empty = unpack_header(data[:8])
    assert srs_id == 4326
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty)
    assert header
    assert data[:len(header)] == header
    pt = Point.from_gpkg(data)
    assert pt.to_gpkg() == data
    assert isinstance(pt, Point)
    assert isnan(pt.x)
    assert isnan(pt.y)
# End test_empty_point_gpkg function


@mark.parametrize('cls, prefix, wkb', [
    (Point, True, b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointZ, True, b'\x01\xe9\x03\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointM, True, b'\x01\xd1\x07\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointZM, True, b'\x01\xb9\x0b\x00\x00\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (Point, False, b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointZ, False, b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointM, False, b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (PointZM, False, b'\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f')
])
def test_empty_point(cls, prefix, wkb):
    """
    Test Empty Point
    """
    geom = cls.empty(srs_id=WGS84)
    assert geom._to_wkb(use_prefix=prefix) == wkb
    assert isinstance(geom, cls)
    assert isnan(geom.x)
    assert isnan(geom.y)
    if hasattr(geom, 'z'):
        assert isnan(geom.z)
    if hasattr(geom, 'm'):
        assert isnan(geom.m)
# End test_empty_point function


@mark.parametrize('cls', [
    MultiPoint,
    MultiPointZ,
    MultiPointM,
    MultiPointZM
])
def test_empty_multi_point(cls):
    """
    Test Empty Multi Point
    """
    geom = cls([], srs_id=WGS84)
    assert isinstance(geom, cls)
    assert geom.coordinates == []
    assert geom.is_empty
# End test_empty_multi_point function


@mark.parametrize('pt', [Point(x=1, y=2, srs_id=WGS84),
                         Point.from_tuple((1, 2), srs_id=WGS84)])
def test_point(header, pt):
    """
    Test Point
    """
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pt.attribute = 10
    values = 1, 2
    assert pt._to_wkb() == point_to_wkb_point(*values)
    assert pt.to_gpkg() == point_to_gpkg_point(header, *values)
    assert Point.from_gpkg(pt.to_gpkg()) == pt
# End test_point function


@mark.parametrize('pt', [PointZ(x=1, y=2, z=3, srs_id=WGS84),
                         PointZ.from_tuple((1, 2, 3), srs_id=WGS84)])
def test_point_z(header, pt):
    """
    Test Point Z
    """
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pt.attribute = 10
    values = 1, 2, 3
    assert pt._to_wkb() == point_z_to_wkb_point_z(*values)
    assert pt.to_gpkg() == point_z_to_gpkg_point_z(header, *values)
    assert PointZ.from_gpkg(pt.to_gpkg()) == pt
# End test_point_z function


@mark.parametrize('pt', [PointM(x=1, y=2, m=3, srs_id=WGS84),
                         PointM.from_tuple((1, 2, 3), srs_id=WGS84)])
def test_point_m(header, pt):
    """
    Test Point M
    """
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pt.attribute = 10
    values = 1, 2, 3
    assert pt._to_wkb() == point_m_to_wkb_point_m(*values)
    assert pt.to_gpkg() == point_m_to_gpkg_point_m(header, *values)
    assert PointM.from_gpkg(pt.to_gpkg()) == pt
# End test_point_m function


@mark.parametrize('pt', [PointZM(x=1, y=2, z=3, m=4, srs_id=WGS84),
                         PointZM.from_tuple((1, 2, 3, 4), srs_id=WGS84)])
def test_point_zm(header, pt):
    """
    Test Point ZM
    """
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pt.attribute = 10
    values = 1, 2, 3, 4
    assert pt._to_wkb() == point_zm_to_wkb_point_zm(*values)
    assert pt.to_gpkg() == point_zm_to_gpkg_point_zm(header, *values)
    assert PointZM.from_gpkg(pt.to_gpkg()) == pt
# End test_point_zm function


def test_multi_point(header):
    """
    Test multi point
    """
    values = [(0, 0), (1, 1)]
    pts = MultiPoint(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts._to_wkb()
    assert wkb == multipoint_to_wkb_multipoint(values)
    gpkg = pts.to_gpkg()
    assert gpkg == points_to_gpkg_multipoint(header, values)
    assert MultiPoint.from_gpkg(gpkg) == pts
# End test_multi_point function


def test_multi_point_z(header):
    """
    Test multi point Z
    """
    values = [(0, 0, 0), (1, 1, 1)]
    pts = MultiPointZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts._to_wkb()
    assert wkb == multipoint_z_to_wkb_multipoint_z(values)
    assert MultiPointZ.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_z function


def test_multi_point_m(header):
    """
    Test multi point M
    """
    values = [(0, 0, 0), (1, 1, 1)]
    pts = MultiPointM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts._to_wkb()
    assert wkb == multipoint_m_to_wkb_multipoint_m(values)
    assert MultiPointM.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_m function


def test_multi_point_zm(header):
    """
    Test multi point ZM
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1)]
    pts = MultiPointZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts._to_wkb()
    assert wkb == multipoint_zm_to_wkb_multipoint_zm(values)
    assert MultiPointZM.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_zm function


if __name__ == '__main__':  # pragma: no cover
    pass
