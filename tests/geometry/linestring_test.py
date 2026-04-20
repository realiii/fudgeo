# -*- coding: utf-8 -*-
"""
Test LineString
"""

from pytest import mark, raises

from fudgeo.constant import HEADER_OFFSET, WGS84
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiLineStringM, MultiLineStringZ, MultiLineStringZM)
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, Envelope, make_header,
    unpack_header)
from tests.geo import (
    points_m_to_gpkg_line_string_m, points_to_gpkg_line_string,
    points_z_to_gpkg_line_string_z, points_zm_to_gpkg_line_string_zm)
from tests.wkb import (
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
    assert not len(line.coordinates)
# End test_empty_linestring_gpkg function


@mark.parametrize('cls, wkb, data', [
    (LineString, b'\x01\x02\x00\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00'),
    (LineStringZ, b'\x01\xea\x03\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xea\x03\x00\x00\x00\x00\x00\x00'),
    (LineStringM, b'\x01\xd2\x07\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xd2\x07\x00\x00\x00\x00\x00\x00'),
    (LineStringZM, b'\x01\xba\x0b\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xba\x0b\x00\x00\x00\x00\x00\x00'),
])
def test_empty_line_string(cls, wkb, data):
    """
    Test Empty LineString
    """
    geom = cls([], srs_id=WGS84)
    ary = bytearray()
    assert geom._to_wkb(ary) == wkb
    assert isinstance(geom, cls)
    assert not len(geom.coordinates)
    assert geom._is_empty is None
    assert geom.is_empty is True
    assert geom.to_gpkg() == data
    geom = cls.from_gpkg(data)
    assert geom._is_empty is True
    assert geom.is_empty is True
# End test_empty_line_string function


@mark.parametrize('cls, wkb, data', [
    (MultiLineString, b'\x01\x05\x00\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\x05\x00\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringZ, b'\x01\xed\x03\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xed\x03\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringM, b'\x01\xd5\x07\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xd5\x07\x00\x00\x00\x00\x00\x00'),
    (MultiLineStringZM, b'\x01\xbd\x0b\x00\x00\x00\x00\x00\x00', b'GP\x00\x11\xe6\x10\x00\x00\x01\xbd\x0b\x00\x00\x00\x00\x00\x00')
])
def test_empty_multi_line_string(cls, wkb, data):
    """
    Test Empty MultiLineString
    """
    geom = cls([], srs_id=WGS84)
    ary = bytearray()
    assert geom._to_wkb(ary) == wkb
    assert isinstance(geom, cls)
    assert geom.lines == []
    assert geom._is_empty is None
    assert geom.is_empty is True
    assert geom.to_gpkg() == data
    geom = cls.from_gpkg(data)
    assert geom._is_empty is True
    assert geom.is_empty is True
# End test_empty_multi_line_string function


@mark.parametrize('cls, values, env_code, wkb_func, gpkg_func, env', [
    (LineString, [(0, 1), (10, 11)], 1, points_to_wkb_line_string, points_to_gpkg_line_string, Envelope(code=1, srs_id=-1, min_x=0, max_x=10, min_y=1, max_y=11)),
    (LineStringZ, [(0, 1, 2), (10, 11, 12)], 2, points_z_to_wkb_line_string_z, points_z_to_gpkg_line_string_z, Envelope(code=2, srs_id=-1, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12)),
    (LineStringM, [(0, 1, 2), (10, 11, 12)], 3, points_m_to_wkb_line_string_m, points_m_to_gpkg_line_string_m, Envelope(code=3, srs_id=-1, min_x=0, max_x=10, min_y=1, max_y=11, min_m=2, max_m=12)),
    (LineStringZM, [(0, 1, 2, 3), (10, 11, 12, 13)], 4, points_zm_to_wkb_line_string_zm, points_zm_to_gpkg_line_string_zm, Envelope(code=4, srs_id=-1, min_x=0, max_x=10, min_y=1, max_y=11, min_z=2, max_z=12, min_m=3, max_m=13)),
])
def test_line_string(header, cls, values, env_code, wkb_func, gpkg_func, env):
    """
    Test line string wkb
    """
    line = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        line.attribute = 10
    assert (line.coordinates == values).all()
    ary = bytearray()
    assert line._to_wkb(ary) == wkb_func(values)
    legacy = gpkg_func(header(env_code), values)
    gpkg = line.to_gpkg()
    assert len(gpkg) > len(legacy)
    assert gpkg.startswith(legacy[:HEADER_OFFSET])
    assert gpkg.endswith(legacy[HEADER_OFFSET:])
    from_gpkg = cls.from_gpkg(gpkg)
    assert not from_gpkg.is_empty
    assert from_gpkg == line
    assert not line.is_empty
    assert line.envelope == env
    geo = line.__geo_interface__
    assert geo['type'] == 'LineString'
    assert geo['coordinates'] == tuple(values)
    assert geo['bbox'] == env.bounding_box
    assert sum(1 for _ in line) == len(values)
# End test_line_string function


@mark.parametrize('data', [
    b'GP\x00\x03\xe6\x10\x00\x00t\xc8\t\x1dX\x87]\xc0\xc0\x7f\x1a\xf4N\x87]\xc0P\xea\x17\xcep\xdf@@0F\x87\xa1\x84\xdf@@\x01\x02\x00\x00\x00\x02\x00\x00\x00\xc0\x7f\x1a\xf4N\x87]\xc00F\x87\xa1\x84\xdf@@t\xc8\t\x1dX\x87]\xc0P\xea\x17\xcep\xdf@@',
    b'GP\x00\x03\xe6\x10\x00\x00\xc0\x7f\x1a\xf4N\x87]\xc0\x9c82\xefN\x87]\xc00F\x87\xa1\x84\xdf@@@3\xf1\xa9\x84\xdf@@\x01\x02\x00\x00\x00\x02\x00\x00\x00\x9c82\xefN\x87]\xc0@3\xf1\xa9\x84\xdf@@\xc0\x7f\x1a\xf4N\x87]\xc00F\x87\xa1\x84\xdf@@',
    b"GP\x00\x03\xe6\x10\x00\x00\x9c82\xefN\x87]\xc0\xc42]\x85=\x87]\xc0@3\xf1\xa9\x84\xdf@@\xf8T'j\xa0\xdf@@\x01\x02\x00\x00\x00\x02\x00\x00\x00\xc42]\x85=\x87]\xc0\xf8T'j\xa0\xdf@@\x9c82\xefN\x87]\xc0@3\xf1\xa9\x84\xdf@@",
    b'GP\x00\x03\xe6\x10\x00\x00\xeco\x91\xfayC[\xc0\x00\xa8V\x1d\x01C[\xc0\xc0u&#\x9d\xe3@@\xa0\xf4\x88\xb5\x9e\xe3@@\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\xa8V\x1d\x01C[\xc0\xc0u&#\x9d\xe3@@\xeco\x91\xfayC[\xc0\xa0\xf4\x88\xb5\x9e\xe3@@',
    b'GP\x00\x03\xe6\x10\x00\x00\x00\xd5L\xb2F\x86]\xc0\xa4`\x92lC\x86]\xc0\x80\xf8\xf4\xa3\xa4\xe3@@h\xa4\xc3\xb5\xad\xe3@@\x01\x02\x00\x00\x00\x02\x00\x00\x00\xa4`\x92lC\x86]\xc0h\xa4\xc3\xb5\xad\xe3@@\x00\xd5L\xb2F\x86]\xc0\x80\xf8\xf4\xa3\xa4\xe3@@',
])
def test_line_string_envelope(data):
    """
    Test Line String Envelope
    """
    line = LineString.from_gpkg(data)
    assert line._env is not EMPTY_ENVELOPE
    assert line.envelope.code == 1
    line._env = EMPTY_ENVELOPE
    assert line._env is EMPTY_ENVELOPE
    assert line.envelope is not EMPTY_ENVELOPE
    assert line.envelope.code == 1
    assert line.to_gpkg() == data
# End test_line_string_envelope function


@mark.parametrize('cls, values, env_code, wkb_func, env', [
    (MultiLineString, [[(0, 0), (1, 1)], [(10, 12), (15, 16)], [(45, 55), (75, 85)], [(4.4, 5.5), (7.7, 8.8)]],
     1, point_lists_to_multi_line_string, Envelope(code=1, srs_id=-1, min_x=0, max_x=75, min_y=0, max_y=85)),
    (MultiLineStringZ, [[(0, 0, 0), (1, 1, 1)], [(10, 12, 13), (15, 16, 17)], [(45, 55, 65), (75, 85, 95)], [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]],
     2, point_lists_z_to_multi_line_string_z, Envelope(code=2, srs_id=-1, min_x=0, max_x=75, min_y=0, max_y=85, min_z=0, max_z=95)),
    (MultiLineStringM, [[(0, 0, 0), (1, 1, 1)], [(10, 12, 13), (15, 16, 17)], [(45, 55, 65), (75, 85, 95)], [(4.4, 5.5, 6.6), (7.7, 8.8, 9.9)]],
     3, point_lists_m_to_multi_line_string_m, Envelope(code=3, srs_id=-1, min_x=0, max_x=75, min_y=0, max_y=85, min_m=0, max_m=95)),
    (MultiLineStringZM, [[(0, 0, 0, 0), (1, 1, 1, 1)], [(10, 12, 13, 14), (15, 16, 17, 18)], [(45, 55, 65, 75), (75, 85, 95, 105)], [(4.4, 5.5, 6.6, 7.7), (7.7, 8.8, 9.9, 10.1)]],
     4, point_lists_zm_to_multi_line_string_zm, Envelope(code=4, srs_id=-1, min_x=0, max_x=75, min_y=0, max_y=85, min_z=0, max_z=95, min_m=0, max_m=105)),
])
def test_multi_line_string(header, cls, values, env_code, wkb_func, env):
    """
    Test multi line string wkb
    """
    multi = cls(values, srs_id=WGS84)
    with raises(AttributeError):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        multi.attribute = 10
    ary = bytearray()
    assert multi._to_wkb(ary) == wkb_func(values)
    gpkg = multi.to_gpkg()
    from_gpkg = cls.from_gpkg(gpkg)
    assert not from_gpkg.is_empty
    assert from_gpkg == multi
    assert gpkg.startswith(header(env_code))
    assert not multi.is_empty
    assert multi.envelope == env
    geo = multi.__geo_interface__
    assert geo['type'] == 'MultiLineString'
    assert geo['coordinates'] == tuple(tuple(v) for v in values)
    assert geo['bbox'] == env.bounding_box
    assert sum(1 for _ in multi) == len(values)
# End test_multi_line_string function


@mark.parametrize('data', [
    b'GP\x00\x03\xe6\x10\x00\x00t\xc8\t\x1dX\x87]\xc0\xc0\x7f\x1a\xf4N\x87]\xc0P\xea\x17\xcep\xdf@@0F\x87\xa1\x84\xdf@@\x01\x05\x00\x00\x00\x01\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\xc0\x7f\x1a\xf4N\x87]\xc00F\x87\xa1\x84\xdf@@t\xc8\t\x1dX\x87]\xc0P\xea\x17\xcep\xdf@@',
    b'GP\x00\x03\xe6\x10\x00\x00\xc0\x7f\x1a\xf4N\x87]\xc0\x9c82\xefN\x87]\xc00F\x87\xa1\x84\xdf@@@3\xf1\xa9\x84\xdf@@\x01\x05\x00\x00\x00\x01\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\x9c82\xefN\x87]\xc0@3\xf1\xa9\x84\xdf@@\xc0\x7f\x1a\xf4N\x87]\xc00F\x87\xa1\x84\xdf@@',
    b"GP\x00\x03\xe6\x10\x00\x00\x9c82\xefN\x87]\xc0\xc42]\x85=\x87]\xc0@3\xf1\xa9\x84\xdf@@\xf8T'j\xa0\xdf@@\x01\x05\x00\x00\x00\x01\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\xc42]\x85=\x87]\xc0\xf8T'j\xa0\xdf@@\x9c82\xefN\x87]\xc0@3\xf1\xa9\x84\xdf@@",
    b'GP\x00\x03\xe6\x10\x00\x00\xeco\x91\xfayC[\xc0\x00\xa8V\x1d\x01C[\xc0\xc0u&#\x9d\xe3@@\xa0\xf4\x88\xb5\x9e\xe3@@\x01\x05\x00\x00\x00\x01\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\x00\xa8V\x1d\x01C[\xc0\xc0u&#\x9d\xe3@@\xeco\x91\xfayC[\xc0\xa0\xf4\x88\xb5\x9e\xe3@@',
    b'GP\x00\x03\xe6\x10\x00\x00\x00\xd5L\xb2F\x86]\xc0\xa4`\x92lC\x86]\xc0\x80\xf8\xf4\xa3\xa4\xe3@@h\xa4\xc3\xb5\xad\xe3@@\x01\x05\x00\x00\x00\x01\x00\x00\x00\x01\x02\x00\x00\x00\x02\x00\x00\x00\xa4`\x92lC\x86]\xc0h\xa4\xc3\xb5\xad\xe3@@\x00\xd5L\xb2F\x86]\xc0\x80\xf8\xf4\xa3\xa4\xe3@@',
])
def test_multi_line_string_envelope(data):
    """
    Test multi line string envelope
    """
    multi = MultiLineString.from_gpkg(data)
    assert multi._env is not EMPTY_ENVELOPE
    assert multi.envelope.code == 1
    multi._env = EMPTY_ENVELOPE
    assert multi._env is EMPTY_ENVELOPE
    assert multi.envelope is not EMPTY_ENVELOPE
    assert multi.envelope.code == 1
    assert multi.to_gpkg() == data
# End test_multi_line_string_envelope function


@mark.parametrize('cls, coords1, coords2', [
    (LineString, [(0, 1), (10, 11)], [(0.1, 1.2), (10.3, 11.4)]),
    (LineStringZ, [(0, 1, 2), (10, 11, 12)], [(0, 1, 2.5), (10, 11, 12.5)]),
    (LineStringM, [(0, 1, 2), (10, 11, 12)], [(0, 1.5, 2), (10, 11.5, 12)]),
    (LineStringZM, [(0, 1, 2, 3), (10, 11, 12, 13)], [(0, 1, 2, 3), (4, 5, 6, 7)]),
])
def test_update_from_wkb_line_string(cls, coords1, coords2):
    """
    Test update_from_wkb line string
    """
    line1 = cls(coords1, srs_id=4326)
    line2 = cls(coords2, srs_id=4326)
    assert line1 != line2
    line3 = cls.from_wkb(line2.wkb, srs_id=line2.srs_id)
    assert line2 is not line3
    assert line1 != line3
    assert line2 == line3
# End test_update_from_wkb_line_string function


@mark.parametrize('cls, coords1, coords2', [
    (MultiLineString, [(0, 1), (10, 11)], [(0.1, 1.2), (10.3, 11.4)]),
    (MultiLineStringZ, [(0, 1, 2), (10, 11, 12)], [(0, 1, 2.5), (10, 11, 12.5)]),
    (MultiLineStringM, [(0, 1, 2), (10, 11, 12)], [(0, 1.5, 2), (10, 11.5, 12)]),
    (MultiLineStringZM, [(0, 1, 2, 3), (10, 11, 12, 13)], [(0, 1, 2, 3), (4, 5, 6, 7)]),
])
def test_update_from_wkb_multi_line_string(cls, coords1, coords2):
    """
    Test update_from_wkb multi line string
    """
    line1 = cls([coords1], srs_id=4326)
    line2 = cls([coords2], srs_id=4326)
    assert line1 != line2
    line3 = line1.from_wkb(line2.wkb, srs_id=line2.srs_id)
    assert line2 is not line3
    assert line1 != line3
    assert line2 == line3
# End test_update_from_wkb_multi_line_string function


if __name__ == '__main__':  # pragma: no cover
    pass
