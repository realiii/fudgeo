# -*- coding: utf-8 -*-
"""
Test LineString
"""

from pytest import mark, raises

from fudgeo.constant import HEADER_OFFSET, WGS84
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiLineStringM, MultiLineStringZ, MultiLineStringZM)
from fudgeo.geometry.util import Envelope, make_header, unpack_header
from tests.conversion.geo import (
    points_m_to_gpkg_line_string_m, points_to_gpkg_line_string,
    points_z_to_gpkg_line_string_z, points_zm_to_gpkg_line_string_zm)
from tests.conversion.wkb import (
    point_lists_m_to_multi_line_string_m, point_lists_to_multi_line_string,
    point_lists_z_to_multi_line_string_z,
    point_lists_zm_to_multi_line_string_zm, points_m_to_wkb_line_string_m,
    points_to_wkb_line_string, points_z_to_wkb_line_string_z,
    points_zm_to_wkb_line_string_zm)


def test_empty_linestring_gpkg():
    """
    Test empty LineString GeoPackage
    """
    data = b'GP\x00\x11\xe6\x10\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00'
    srs_id, env_code, offset, is_empty = unpack_header(data[:8])
    assert srs_id == 4326
    assert env_code == 0
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty, envelope_code=0)
    assert header
    assert data[:len(header)] == header
    line = LineString.from_gpkg(data)
    assert line.to_gpkg() == data
    assert isinstance(line, LineString)
    assert line.coordinates == []
# End test_empty_linestring_gpkg function


@mark.parametrize('cls, wkb', [
    (LineString, b'\x01\x02\x00\x00\x00\x00\x00\x00\x00'),
    (LineStringZ, b'\x01\xea\x03\x00\x00\x00\x00\x00\x00'),
    (LineStringM, b'\x01\xd2\x07\x00\x00\x00\x00\x00\x00'),
    (LineStringZM, b'\x01\xba\x0b\x00\x00\x00\x00\x00\x00'),
])
def test_empty_line_string(cls, wkb):
    """
    Test Empty LineString
    """
    geom = cls([], srs_id=WGS84)
    assert geom._to_wkb() == wkb
    assert isinstance(geom, cls)
    assert geom.coordinates == []
# End test_empty_line_string function


@mark.parametrize('cls, wkb', [
    (MultiLineString, b'\x01\x05\x00\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringZ, b'\x01\xed\x03\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringM, b'\x01\xd5\x07\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringZM, b'\x01\xbd\x0b\x00\x00\x00\x00\x00\x00')
])
def test_empty_multi_line_string(cls, wkb):
    """
    Test Empty MultiLineString
    """
    geom = cls([], srs_id=WGS84)
    assert geom._to_wkb() == wkb
    assert isinstance(geom, cls)
    assert geom.lines == []
# End test_empty_multi_line_string function


@mark.parametrize('cls, values, env_code, wkb_func, gpkg_func, env', [
    (LineString, [(0, 1), (10, 11)], 1, points_to_wkb_line_string, points_to_gpkg_line_string, Envelope(code=1, min_x=0, max_x=10, min_y=1, max_y=11)),
    (LineStringZ, [(0, 1, 2), (10, 11, 12)], 2, points_z_to_wkb_line_string_z, points_z_to_gpkg_line_string_z, Envelope(code=2, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12)),
    (LineStringM, [(0, 1, 2), (10, 11, 12)], 3, points_m_to_wkb_line_string_m, points_m_to_gpkg_line_string_m, Envelope(code=3, min_x=0, max_x=10, min_y=1, max_y=11, min_m=2, max_m=12)),
    (LineStringZM, [(0, 1, 2, 3), (10, 11, 12, 13)], 4, points_zm_to_wkb_line_string_zm, points_zm_to_gpkg_line_string_zm, Envelope(code=4, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12, min_m=3, max_m=13)),
])
def test_line_string(header, cls, values, env_code, wkb_func, gpkg_func, env):
    """
    Test line string wkb
    """
    line = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert line.coordinates == values
    assert line._to_wkb() == wkb_func(values)
    legacy = gpkg_func(header(env_code), values)
    gpkg = line.to_gpkg()
    assert len(gpkg) > len(legacy)
    assert gpkg.startswith(legacy[:HEADER_OFFSET])
    assert gpkg.endswith(legacy[HEADER_OFFSET:])
    assert cls.from_gpkg(gpkg) == line
    assert not line.is_empty
    assert line.envelope == env
# End test_line_string function


@mark.parametrize('cls, values, env_code, wkb_func, env', [
    (MultiLineString, [[(0, 0), (1, 1)], [(10, 12), (15, 16)], [(45, 55), (75, 85)], [(4.4, 5.5), (7.7, 8.8)]],
     1, point_lists_to_multi_line_string, Envelope(code=1, min_x=0, max_x=75, min_y=0, max_y=85)),
    (MultiLineStringZ, [[(0, 0, 0), (1, 1, 1)], [(10, 12, 13), (15, 16, 17)], [(45, 55, 65), (75, 85, 95)], [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]],
     2, point_lists_z_to_multi_line_string_z, Envelope(code=2, min_x=0, max_x=75, min_y=0, max_y=85, min_z=0, max_z=95)),
    (MultiLineStringM, [[(0, 0, 0), (1, 1, 1)], [(10, 12, 13), (15, 16, 17)], [(45, 55, 65), (75, 85, 95)], [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]],
     3, point_lists_m_to_multi_line_string_m, Envelope(code=3, min_x=0, max_x=75, min_y=0, max_y=85, min_m=0, max_m=95)),
    (MultiLineStringZM, [[(0, 0, 0, 0), (1, 1, 1, 1)], [(10, 12, 13, 14), (15, 16, 17, 18)], [(45, 55, 65, 75), (75, 85, 95, 105)], [(4.4, 5.5, 6.6, 7.7), (7.7, 8.8, 9.9, 10.1)]],
     4, point_lists_zm_to_multi_line_string_zm, Envelope(code=4, min_x=0, max_x=75, min_y=0, max_y=85, min_z=0, max_z=95, min_m=0, max_m=105)),
])
def test_multi_line_string(header, cls, values, env_code, wkb_func, env):
    """
    Test multi line string wkb
    """
    multi = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    assert multi._to_wkb() == wkb_func(values)
    gpkg = multi.to_gpkg()
    assert cls.from_gpkg(gpkg) == multi
    assert gpkg.startswith(header(env_code))
    assert not multi.is_empty
    assert multi.envelope == env
# End test_multi_line_string function


if __name__ == '__main__':  # pragma: no cover
    pass
