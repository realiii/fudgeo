# -*- coding: utf-8 -*-
"""
Test LineString with Shapely
"""


from math import isnan

from pytest import mark
try:
    from shapely.coordinates import get_coordinates
    from shapely.geometry import (
        LineString as ShapelyLineString,
        MultiLineString as ShapelyMultiLineString)
    from shapely.io import from_wkb
except ImportError:
    get_coordinates = None
    ShapelyLineString = ShapelyMultiLineString = None
    from_wkb = None


from fudgeo.constant import WGS84
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiLineStringM, MultiLineStringZ, MultiLineStringZM)
from fudgeo.geometry.util import EMPTY_ENVELOPE, Envelope
from tests.geo import (
    points_m_to_gpkg_line_string_m, points_to_gpkg_line_string,
    points_z_to_gpkg_line_string_z, points_zm_to_gpkg_line_string_zm)
from tests.wkb import (
    point_lists_m_to_multi_line_string_m, point_lists_to_multi_line_string,
    point_lists_z_to_multi_line_string_z,
    point_lists_zm_to_multi_line_string_zm, points_m_to_wkb_line_string_m,
    points_to_wkb_line_string, points_z_to_wkb_line_string_z,
    points_zm_to_wkb_line_string_zm)


pytestmark = [mark.shapely]


def test_empty_linestring_gpkg():
    """
    Test empty LineString GeoPackage
    """
    data = b'GP\x00\x11\xe6\x10\x00\x00\x01\x02\x00\x00\x00\x00\x00\x00\x00'
    line = LineString.from_gpkg(data)
    assert line.to_gpkg() == data
    assert isinstance(line, LineString)
    assert not len(line.coordinates)

    sline = from_wkb(line.wkb)
    assert isinstance(sline, ShapelyLineString)
    assert sline.is_empty
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
    line = cls([], srs_id=WGS84)
    assert isinstance(line, cls)
    assert line.wkb == wkb
    assert not len(line.coordinates)

    sline = from_wkb(line.wkb)
    assert isinstance(sline, ShapelyLineString)
    assert sline.is_empty
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
    lines = cls([], srs_id=WGS84)
    assert isinstance(lines, cls)
    assert lines.wkb == wkb
    assert not lines.lines

    slines = from_wkb(lines.wkb)
    assert isinstance(slines, ShapelyMultiLineString)
    assert slines.is_empty
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
    assert (line.coordinates == values).all()
    assert line.wkb == wkb_func(values)

    sline = from_wkb(line.wkb)
    assert isinstance(sline, ShapelyLineString)
    assert not sline.is_empty
    coordinates = get_coordinates(sline, include_z=True, include_m=True)
    compares = [tuple(c for c in coords if not isnan(c)) for coords in coordinates]
    assert compares == values
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
    sline = from_wkb(line.wkb)
    assert isinstance(sline, ShapelyLineString)
    assert not sline.is_empty
    assert not sline.has_z
    assert not sline.has_m
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
    lines = cls(values, srs_id=WGS84)
    assert isinstance(lines, cls)
    assert lines.wkb == wkb_func(values)

    slines = from_wkb(lines.wkb)
    assert isinstance(slines, ShapelyMultiLineString)
    assert not slines.is_empty

    if env_code == 1:
        assert not slines.has_z
        assert not slines.has_m
    elif env_code == 2:
        assert slines.has_z
        assert not slines.has_m
    elif env_code == 3:
        assert not slines.has_z
        assert slines.has_m
    else:
        assert slines.has_z
        assert slines.has_m

    coordinates = get_coordinates(slines, include_z=True, include_m=True)
    compares = [tuple(c for c in coords if not isnan(c)) for coords in coordinates]
    assert compares == sum(values, [])
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


if __name__ == '__main__':  # pragma: no cover
    pass
