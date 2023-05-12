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
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, Envelope, make_header,
    unpack_header)
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
    assert not len(geom.coordinates)
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
    assert (pts.coordinates == values).all()
    assert pts._to_wkb() == wkb_func(values)
    gpkg = pts.to_gpkg()
    assert gpkg.startswith(header(env_code))
    from_gpkg_pts = cls.from_gpkg(gpkg)
    assert not from_gpkg_pts.is_empty
    assert from_gpkg_pts == pts
    assert pts.envelope == env
# End test_multi_point function


@mark.parametrize('cls, env_code, data', [
    (MultiPoint, 1, b'GP\x00\x03\xe6\x10\x00\x00B\xe6\x92\xf6{\xea`\xc0\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@ \xd2|\xf6\xa5&M@\x01\x04\x00\x00\x00\x03\x00\x00\x00\x01\x01\x00\x00\x00B\xe6\x92\xf6{\xea`\xc0P\x9d\x89N\xee\x88L@\x01\x01\x00\x00\x00F/=v\x14\xcd`\xc0 \xd2|\xf6\xa5&M@\x01\x01\x00\x00\x00\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@'),
    (MultiPoint, 1, b'GP\x00\x03\xe6\x10\x00\x00\xb8\x89x\xf0UD\\\xc0P\xe0`\x19\xe2\x1fU\xc0\x10\xc0@\\n\xa4A@8\r.\xe3\xc7\x07G@\x01\x04\x00\x00\x00\x03\x00\x00\x00\x01\x01\x00\x00\x00\xb8\x89x\xf0UD\\\xc08\r.\xe3\xc7\x07G@\x01\x01\x00\x00\x00\xdcR\x9b&\xf6\x96U\xc0\x10\xc0@\\n\xa4A@\x01\x01\x00\x00\x00P\xe0`\x19\xe2\x1fU\xc0H\x07Z\nS\x06C@'),
    (MultiPoint, 1, b'GP\x00\x03\xe6\x10\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0\xf4\xa5\x9d\xeb\x92\xecS\xc0\xb0C\t[u)D@@\xfb0f\xfe\x9bN@\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0@\xfb0f\xfe\x9bN@\x01\x01\x00\x00\x00\xa0\x1a\x89\xdfS\x02T\xc0\xb0C\t[u)D@\x01\x01\x00\x00\x00\xd4\x06\x9b\xf8\xb2\xf0S\xc0\xc0d0\x07\x806D@\x01\x01\x00\x00\x00\xf4\xa5\x9d\xeb\x92\xecS\xc0\xe8\x95\x1f\x16\xbc6D@'),
    (MultiPoint, 1, b'GP\x00\x03\xe6\x10\x00\x00\x1c\x06D\x9f\x07*\\\xc0\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x08K\xddQ\x80\xf3F@\x01\x04\x00\x00\x00\x04\x00\x00\x00\x01\x01\x00\x00\x00\x1c\x06D\x9f\x07*\\\xc0\x08K\xddQ\x80\xf3F@\x01\x01\x00\x00\x00\xf4\x9b\xb4i\xbf\xb1U\xc0\xd8\xd1\xc8\xecN\x15B@\x01\x01\x00\x00\x00\xdc\xc1z\x9c\x9c\xd7T\xc08\x1b\xb6\x90\xb4\xf9@@\x01\x01\x00\x00\x00\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@'),
    (MultiPoint, 1, b'GP\x00\x03\xe6\x10\x00\x00\x98T4\xd6>{Y\xc0\x10Ov3#wS\xc0P\x890Z\xd4\xe1?@\x002\xfdJ\x9b\x86D@\x01\x04\x00\x00\x00\t\x00\x00\x00\x01\x01\x00\x00\x00\x98T4\xd6>{Y\xc0@$q3u=C@\x01\x01\x00\x00\x00$\x1cz\x8b\x07\x00W\xc0\x002\xfdJ\x9b\x86D@\x01\x01\x00\x00\x00\x90 \\\x01\x05\x18V\xc0PC"\xa7\x8e;D@\x01\x01\x00\x00\x00\xb8\x9d\x0eH\x08\x8aU\xc0`ds\x89.2B@\x01\x01\x00\x00\x00\x88X\xc4\xb0CkU\xc0\xa8\xed\xd8\xd5\xd2\x10C@\x01\x01\x00\x00\x00\xe8\xd2&Q\xc6FU\xc0P\x890Z\xd4\xe1?@\x01\x01\x00\x00\x00<\xb5\x85\xdds1U\xc0\xa0\xb0\xd6S"\'@@\x01\x01\x00\x00\x00\xec\xac\x99YD#U\xc0\xe8\xab\x17\xc2\xf8\x05@@\x01\x01\x00\x00\x00\x10Ov3#wS\xc0Hz_\x9c\x85\xa6C@'),
    (MultiPointZ, 2, b'GP\x00\x05\xe6\x10\x00\x00B\xe6\x92\xf6{\xea`\xc0\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@ \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x80\x1c\xc8@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xec\x03\x00\x00\x03\x00\x00\x00\x01\xe9\x03\x00\x00B\xe6\x92\xf6{\xea`\xc0P\x9d\x89N\xee\x88L@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00F/=v\x14\xcd`\xc0 \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@\x00\x00\x00\x00\x80\x1c\xc8@'),
    (MultiPointZ, 2, b'GP\x00\x05\xe6\x10\x00\x00\xb8\x89x\xf0UD\\\xc0P\xe0`\x19\xe2\x1fU\xc0\x10\xc0@\\n\xa4A@8\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x80\x1c\xc8@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xec\x03\x00\x00\x03\x00\x00\x00\x01\xe9\x03\x00\x00\xb8\x89x\xf0UD\\\xc08\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xdcR\x9b&\xf6\x96U\xc0\x10\xc0@\\n\xa4A@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00P\xe0`\x19\xe2\x1fU\xc0H\x07Z\nS\x06C@\x00\x00\x00\x00\x80\x1c\xc8@'),
    (MultiPointZ, 2, b'GP\x00\x05\xe6\x10\x00\x00\x1c\x06D\x9f\x07*\\\xc0\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x80\x1c\xc8@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xec\x03\x00\x00\x04\x00\x00\x00\x01\xe9\x03\x00\x00\x1c\x06D\x9f\x07*\\\xc0\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xf4\x9b\xb4i\xbf\xb1U\xc0\xd8\xd1\xc8\xecN\x15B@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xdc\xc1z\x9c\x9c\xd7T\xc08\x1b\xb6\x90\xb4\xf9@@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x00\x00\x00\x00\x80\x1c\xc8@'),
    (MultiPointZ, 2, b'GP\x00\x05\xe6\x10\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0\xf4\xa5\x9d\xeb\x92\xecS\xc0\xb0C\t[u)D@@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x80\x1c\xc8@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xec\x03\x00\x00\x04\x00\x00\x00\x01\xe9\x03\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xa0\x1a\x89\xdfS\x02T\xc0\xb0C\t[u)D@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xd4\x06\x9b\xf8\xb2\xf0S\xc0\xc0d0\x07\x806D@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xf4\xa5\x9d\xeb\x92\xecS\xc0\xe8\x95\x1f\x16\xbc6D@\x00\x00\x00\x00\x80\x1c\xc8@'),
    (MultiPointZ, 2, b'GP\x00\x05\xe6\x10\x00\x00\x98T4\xd6>{Y\xc0\x10Ov3#wS\xc0P\x890Z\xd4\xe1?@\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x80\x1c\xc8@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xec\x03\x00\x00\t\x00\x00\x00\x01\xe9\x03\x00\x00\x98T4\xd6>{Y\xc0@$q3u=C@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00$\x1cz\x8b\x07\x00W\xc0\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\x90 \\\x01\x05\x18V\xc0PC"\xa7\x8e;D@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xb8\x9d\x0eH\x08\x8aU\xc0`ds\x89.2B@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\x88X\xc4\xb0CkU\xc0\xa8\xed\xd8\xd5\xd2\x10C@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xe8\xd2&Q\xc6FU\xc0P\x890Z\xd4\xe1?@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00<\xb5\x85\xdds1U\xc0\xa0\xb0\xd6S"\'@@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\xec\xac\x99YD#U\xc0\xe8\xab\x17\xc2\xf8\x05@@\x00\x00\x00\x00\x80\x1c\xc8@\x01\xe9\x03\x00\x00\x10Ov3#wS\xc0Hz_\x9c\x85\xa6C@\x00\x00\x00\x00\x80\x1c\xc8@'),
    (MultiPointM, 3, b'GP\x00\x07\xe6\x10\x00\x00B\xe6\x92\xf6{\xea`\xc0\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@ \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd4\x07\x00\x00\x03\x00\x00\x00\x01\xd1\x07\x00\x00B\xe6\x92\xf6{\xea`\xc0P\x9d\x89N\xee\x88L@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00F/=v\x14\xcd`\xc0 \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointM, 3, b'GP\x00\x07\xe6\x10\x00\x00\xb8\x89x\xf0UD\\\xc0P\xe0`\x19\xe2\x1fU\xc0\x10\xc0@\\n\xa4A@8\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd4\x07\x00\x00\x03\x00\x00\x00\x01\xd1\x07\x00\x00\xb8\x89x\xf0UD\\\xc08\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xdcR\x9b&\xf6\x96U\xc0\x10\xc0@\\n\xa4A@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00P\xe0`\x19\xe2\x1fU\xc0H\x07Z\nS\x06C@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointM, 3, b'GP\x00\x07\xe6\x10\x00\x00\x1c\x06D\x9f\x07*\\\xc0\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd4\x07\x00\x00\x04\x00\x00\x00\x01\xd1\x07\x00\x00\x1c\x06D\x9f\x07*\\\xc0\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xf4\x9b\xb4i\xbf\xb1U\xc0\xd8\xd1\xc8\xecN\x15B@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xdc\xc1z\x9c\x9c\xd7T\xc08\x1b\xb6\x90\xb4\xf9@@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointM, 3, b'GP\x00\x07\xe6\x10\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0\xf4\xa5\x9d\xeb\x92\xecS\xc0\xb0C\t[u)D@@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd4\x07\x00\x00\x04\x00\x00\x00\x01\xd1\x07\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xa0\x1a\x89\xdfS\x02T\xc0\xb0C\t[u)D@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xd4\x06\x9b\xf8\xb2\xf0S\xc0\xc0d0\x07\x806D@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xf4\xa5\x9d\xeb\x92\xecS\xc0\xe8\x95\x1f\x16\xbc6D@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointM, 3, b'GP\x00\x07\xe6\x10\x00\x00\x98T4\xd6>{Y\xc0\x10Ov3#wS\xc0P\x890Z\xd4\xe1?@\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd4\x07\x00\x00\t\x00\x00\x00\x01\xd1\x07\x00\x00\x98T4\xd6>{Y\xc0@$q3u=C@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00$\x1cz\x8b\x07\x00W\xc0\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\x90 \\\x01\x05\x18V\xc0PC"\xa7\x8e;D@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xb8\x9d\x0eH\x08\x8aU\xc0`ds\x89.2B@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\x88X\xc4\xb0CkU\xc0\xa8\xed\xd8\xd5\xd2\x10C@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xe8\xd2&Q\xc6FU\xc0P\x890Z\xd4\xe1?@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00<\xb5\x85\xdds1U\xc0\xa0\xb0\xd6S"\'@@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\xec\xac\x99YD#U\xc0\xe8\xab\x17\xc2\xf8\x05@@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xd1\x07\x00\x00\x10Ov3#wS\xc0Hz_\x9c\x85\xa6C@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointZM, 4, b'GP\x00\t\xe6\x10\x00\x00B\xe6\x92\xf6{\xea`\xc0\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@ \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xbc\x0b\x00\x00\x03\x00\x00\x00\x01\xb9\x0b\x00\x00B\xe6\x92\xf6{\xea`\xc0P\x9d\x89N\xee\x88L@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00F/=v\x14\xcd`\xc0 \xd2|\xf6\xa5&M@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xe8\xed\xe1(\xaf\x8b`\xc0h\x1aY\x0eA;L@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointZM, 4, b'GP\x00\t\xe6\x10\x00\x00\xb8\x89x\xf0UD\\\xc0P\xe0`\x19\xe2\x1fU\xc0\x10\xc0@\\n\xa4A@8\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xbc\x0b\x00\x00\x03\x00\x00\x00\x01\xb9\x0b\x00\x00\xb8\x89x\xf0UD\\\xc08\r.\xe3\xc7\x07G@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xdcR\x9b&\xf6\x96U\xc0\x10\xc0@\\n\xa4A@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00P\xe0`\x19\xe2\x1fU\xc0H\x07Z\nS\x06C@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointZM, 4, b'GP\x00\t\xe6\x10\x00\x00\x1c\x06D\x9f\x07*\\\xc0\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xbc\x0b\x00\x00\x04\x00\x00\x00\x01\xb9\x0b\x00\x00\x1c\x06D\x9f\x07*\\\xc0\x08K\xddQ\x80\xf3F@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xf4\x9b\xb4i\xbf\xb1U\xc0\xd8\xd1\xc8\xecN\x15B@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xdc\xc1z\x9c\x9c\xd7T\xc08\x1b\xb6\x90\xb4\xf9@@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xbc\xf9\xfb/\xb1~T\xc0P\xdc\x86\xf8\xd7\xbc@@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointZM, 4, b'GP\x00\t\xe6\x10\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0\xf4\xa5\x9d\xeb\x92\xecS\xc0\xb0C\t[u)D@@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xbc\x0b\x00\x00\x04\x00\x00\x00\x01\xb9\x0b\x00\x00\xa6\xfa\xb4\xdb\xc5\xbbb\xc0@\xfb0f\xfe\x9bN@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xa0\x1a\x89\xdfS\x02T\xc0\xb0C\t[u)D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xd4\x06\x9b\xf8\xb2\xf0S\xc0\xc0d0\x07\x806D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xf4\xa5\x9d\xeb\x92\xecS\xc0\xe8\x95\x1f\x16\xbc6D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
    (MultiPointZM, 4, b'GP\x00\t\xe6\x10\x00\x00\x98T4\xd6>{Y\xc0\x10Ov3#wS\xc0P\x890Z\xd4\xe1?@\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xbc\x0b\x00\x00\t\x00\x00\x00\x01\xb9\x0b\x00\x00\x98T4\xd6>{Y\xc0@$q3u=C@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00$\x1cz\x8b\x07\x00W\xc0\x002\xfdJ\x9b\x86D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\x90 \\\x01\x05\x18V\xc0PC"\xa7\x8e;D@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xb8\x9d\x0eH\x08\x8aU\xc0`ds\x89.2B@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\x88X\xc4\xb0CkU\xc0\xa8\xed\xd8\xd5\xd2\x10C@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xe8\xd2&Q\xc6FU\xc0P\x890Z\xd4\xe1?@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00<\xb5\x85\xdds1U\xc0\xa0\xb0\xd6S"\'@@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\xec\xac\x99YD#U\xc0\xe8\xab\x17\xc2\xf8\x05@@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f\x01\xb9\x0b\x00\x00\x10Ov3#wS\xc0Hz_\x9c\x85\xa6C@\x00\x00\x00\x00\x00\xd7\xb1@\x00\x00\x00\x00\x00\x00\xf8\x7f'),
])
def test_multi_point_envelope(cls, env_code, data):
    """
    Test Multi Point Envelope
    """
    multi = cls.from_gpkg(data)
    assert not multi.is_empty
    assert multi._env is not EMPTY_ENVELOPE
    assert multi.envelope.code == env_code
    multi._env = EMPTY_ENVELOPE
    assert multi._env is EMPTY_ENVELOPE
    assert multi.envelope is not EMPTY_ENVELOPE
    assert multi.envelope.code == env_code
    assert multi.to_gpkg() == data
# End test_multi_point_envelope function


if __name__ == '__main__':  # pragma: no cover
    pass
