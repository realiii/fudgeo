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
from fudgeo.geometry.util import Envelope, make_header, unpack_header
from tests.conversion.geo import (
    point_m_to_gpkg_point_m, point_to_gpkg_point, point_z_to_gpkg_point_z,
    point_zm_to_gpkg_point_zm)
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
    assert env_code == 0
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty, envelope_code=0)
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


@mark.parametrize('pt, values, wkb_func, gpkg_func', [
    (Point(x=1, y=2, srs_id=WGS84), (1, 2), point_to_wkb_point, point_to_gpkg_point),
    (Point.from_tuple((1, 2), srs_id=WGS84), (1, 2), point_to_wkb_point, point_to_gpkg_point),
    (PointZ(x=1, y=2, z=3, srs_id=WGS84), (1, 2, 3), point_z_to_wkb_point_z, point_z_to_gpkg_point_z),
    (PointZ.from_tuple((1, 2, 3), srs_id=WGS84), (1, 2, 3), point_z_to_wkb_point_z, point_z_to_gpkg_point_z),
    (PointM(x=1, y=2, m=3, srs_id=WGS84), (1, 2, 3), point_m_to_wkb_point_m, point_m_to_gpkg_point_m),
    (PointM.from_tuple((1, 2, 3), srs_id=WGS84), (1, 2, 3), point_m_to_wkb_point_m, point_m_to_gpkg_point_m),
    (PointZM(x=1, y=2, z=3, m=4, srs_id=WGS84), (1, 2, 3, 4), point_zm_to_wkb_point_zm, point_zm_to_gpkg_point_zm),
    (PointZM.from_tuple((1, 2, 3, 4), srs_id=WGS84), (1, 2, 3, 4), point_zm_to_wkb_point_zm, point_zm_to_gpkg_point_zm),
])
def test_point(header, pt, values, wkb_func, gpkg_func):
    """
    Test Point
    """
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pt.attribute = 10
    assert pt._to_wkb() == wkb_func(*values)
    assert pt.to_gpkg() == gpkg_func(header(0), *values)
    assert pt.__class__.from_gpkg(pt.to_gpkg()) == pt
# End test_point function


@mark.parametrize('cls, values, wkb_func, env_code, env', [
    (MultiPoint, [(0, 1), (10, 11)], multipoint_to_wkb_multipoint, 1, Envelope(code=1, min_x=0, max_x=10, min_y=1, max_y=11)),
    (MultiPointZ, [(0, 1, 2), (10, 11, 12)], multipoint_z_to_wkb_multipoint_z, 2, Envelope(code=2, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12)),
    (MultiPointM, [(0, 1, 2), (10, 11, 12)], multipoint_m_to_wkb_multipoint_m, 3, Envelope(code=3, min_x=0, max_x=10, min_y=1, max_y=11, min_m=2, max_m=12)),
    (MultiPointZM, [(0, 1, 2, 3), (10, 11, 12, 13)], multipoint_zm_to_wkb_multipoint_zm, 4, Envelope(code=4, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12, min_m=3, max_m=13)),
])
def test_multi_point(header, cls, values, wkb_func, env_code, env):
    """
    Test multi point
    """
    pts = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        pts.attribute = 10
    assert pts.coordinates == values
    assert pts._to_wkb() == wkb_func(values)
    gpkg = pts.to_gpkg()
    assert gpkg.startswith(header(env_code))
    assert cls.from_gpkg(gpkg) == pts
    assert pts.envelope == env
# End test_multi_point function


if __name__ == '__main__':  # pragma: no cover
    pass
