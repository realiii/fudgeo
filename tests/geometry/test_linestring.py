# -*- coding: utf-8 -*-
"""
Test LineString
"""

from pytest import mark, raises

from fudgeo.constant import WGS84
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiLineStringM, MultiLineStringZ, MultiLineStringZM)
from fudgeo.geometry.util import make_header, unpack_header
from tests.conversion.geo import (
    point_lists_to_gpkg_multi_line_string, points_m_to_gpkg_line_string_m,
    points_to_gpkg_line_string, points_z_to_gpkg_line_string_z,
    points_zm_to_gpkg_line_string_zm)
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
    srs_id, offset, is_empty = unpack_header(data[:8])
    assert srs_id == 4326
    assert offset == 8
    assert is_empty
    header = make_header(srs_id, is_empty)
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


def test_line_string(header):
    """
    Test line string wkb
    """
    values = [(0, 0), (1, 1)]
    line = LineString(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert line.coordinates == values
    wkb = line._to_wkb()
    assert wkb == points_to_wkb_line_string(values)
    assert line.to_gpkg() == points_to_gpkg_line_string(header, values)
    assert LineString.from_gpkg(line.to_gpkg()) == line
# End test_line_string function


def test_line_string_z(header):
    """
    Test line string Z wkb
    """
    values = [(0, 0, 0), (1, 1, 1)]
    line = LineStringZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert line.coordinates == values
    wkb = line._to_wkb()
    assert wkb == points_z_to_wkb_line_string_z(values)
    assert line.to_gpkg() == points_z_to_gpkg_line_string_z(header, values)
    assert LineStringZ.from_gpkg(line.to_gpkg()) == line
# End test_line_string_z function


def test_line_string_m(header):
    """
    Test line string M wkb
    """
    values = [(0, 0, 0), (1, 1, 1)]
    line = LineStringM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert line.coordinates == values
    wkb = line._to_wkb()
    assert wkb == points_m_to_wkb_line_string_m(values)
    assert line.to_gpkg() == points_m_to_gpkg_line_string_m(header, values)
    assert LineStringM.from_gpkg(line.to_gpkg()) == line
# End test_line_string_m function


def test_line_string_zm(header):
    """
    Test line string ZM wkb
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1)]
    line = LineStringZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert line.coordinates == values
    wkb = line._to_wkb()
    assert wkb == points_zm_to_wkb_line_string_zm(values)
    assert line.to_gpkg() == points_zm_to_gpkg_line_string_zm(header, values)
    assert LineStringZM.from_gpkg(line.to_gpkg()) == line
# End test_line_string_zm function


def test_multi_line_string(header):
    """
    Test multi line string wkb
    """
    values = [[(0, 0), (1, 1)],
              [(10, 12), (15, 16)],
              [(45, 55), (75, 85)],
              [(4.4, 5.5), (7.7, 8.8)]]
    multi = MultiLineString(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    assert multi._to_wkb() == point_lists_to_multi_line_string(values)
    assert multi.to_gpkg() == (
        point_lists_to_gpkg_multi_line_string(header, values))
    assert MultiLineString.from_gpkg(multi.to_gpkg()) == multi
# End test_multi_line_string function


def test_multi_line_string_z(header):
    """
    Test multi line string Z wkb
    """
    values = [[(0, 0, 0), (1, 1, 1)],
              [(10, 12, 13), (15, 16, 17)],
              [(45, 55, 65), (75, 85, 95)],
              [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]]
    multi = MultiLineStringZ(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    assert multi._to_wkb() == point_lists_z_to_multi_line_string_z(values)
    assert MultiLineStringZ.from_gpkg(multi.to_gpkg()) == multi
# End test_multi_line_string_z function


def test_multi_line_string_m(header):
    """
    Test multi line string M wkb
    """
    values = [[(0, 0, 0), (1, 1, 1)],
              [(10, 12, 13), (15, 16, 17)],
              [(45, 55, 65), (75, 85, 95)],
              [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]]
    multi = MultiLineStringM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    assert multi._to_wkb() == point_lists_m_to_multi_line_string_m(values)
    assert MultiLineStringM.from_gpkg(multi.to_gpkg()) == multi
# End test_multi_line_string_m function


def test_multi_line_string_zm(header):
    """
    Test multi line string ZM wkb
    """
    values = [[(0, 0, 0, 0), (1, 1, 1, 1)],
              [(10, 12, 13, 14), (15, 16, 17, 18)],
              [(45, 55, 65, 75), (75, 85, 95, 105)],
              [(4.4, 5.5, 6.6, 7.7), (7.7, 8.8, 9.9, 10.1)]]
    multi = MultiLineStringZM(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    assert multi._to_wkb() == point_lists_zm_to_multi_line_string_zm(values)
    assert MultiLineStringZM.from_gpkg(multi.to_gpkg()) == multi
# End test_multi_line_string_zm function


if __name__ == '__main__':  # pragma: no cover
    pass
