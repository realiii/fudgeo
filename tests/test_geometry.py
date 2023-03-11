# -*- coding: utf-8 -*-
"""
Test Geometry
"""

from pytest import fixture, mark, raises


from tests.conversion.geo import (
    make_gpkg_geom_header, point_lists_to_gpkg_multi_line_string,
    point_lists_to_gpkg_multi_polygon, point_lists_to_gpkg_polygon,
    point_m_to_gpkg_point_m, point_to_gpkg_point, point_z_to_gpkg_point_z,
    point_zm_to_gpkg_point_zm, points_m_to_gpkg_line_string_m,
    points_to_gpkg_line_string, points_to_gpkg_multipoint,
    points_z_to_gpkg_line_string_z, points_zm_to_gpkg_line_string_zm)
from tests.conversion.wkb import (
    _linear_ring_m_to_wkb, _linear_ring_to_wkb, _linear_ring_z_to_wkb,
    _linear_ring_zm_to_wkb, multipoint_m_to_wkb_multipoint_m,
    multipoint_to_wkb_multipoint, multipoint_z_to_wkb_multipoint_z,
    multipoint_zm_to_wkb_multipoint_zm, point_lists_m_to_multi_line_string_m,
    point_lists_m_to_wkb_multipolygon_m, point_lists_m_to_wkb_polygon_m,
    point_lists_to_multi_line_string, point_lists_to_wkb_multipolygon,
    point_lists_to_wkb_polygon, point_lists_z_to_multi_line_string_z,
    point_lists_z_to_wkb_multipolygon_z, point_lists_z_to_wkb_polygon_z,
    point_lists_zm_to_multi_line_string_zm,
    point_lists_zm_to_wkb_multipolygon_zm, point_lists_zm_to_wkb_polygon_zm,
    point_m_to_wkb_point_m, point_to_wkb_point, point_z_to_wkb_point_z,
    point_zm_to_wkb_point_zm, points_m_to_wkb_line_string_m,
    points_to_wkb_line_string, points_z_to_wkb_line_string_z,
    points_zm_to_wkb_line_string_zm)
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, LinearRing, LinearRingM,
    LinearRingZ, LinearRingZM, MultiLineString, MultiLineStringM,
    MultiLineStringZ, MultiLineStringZM, MultiPoint, MultiPointM, MultiPointZ,
    MultiPointZM, MultiPolygon, MultiPolygonM, MultiPolygonZ, MultiPolygonZM,
    Point, PointM, PointZ, PointZM, Polygon, PolygonM, PolygonZ, PolygonZM,
    _unpack_header_srs_id_and_offset)


@fixture(scope='session')
def header():
    """
    Header
    """
    return make_gpkg_geom_header(4326)
# End header function


@mark.parametrize('pt', [Point(x=1, y=2), Point.from_tuple((1, 2))])
def test_point(header, pt):
    """
    Test Point
    """
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2
    assert pt.to_wkb() == point_to_wkb_point(*values)
    assert pt.to_gpkg() == point_to_gpkg_point(header, *values)
    assert Point.from_wkb(pt.to_wkb()) == pt
    assert Point.from_gpkg(pt.to_gpkg()) == pt
# End test_point function


@mark.parametrize('pt', [PointZ(x=1, y=2, z=3), PointZ.from_tuple((1, 2, 3))])
def test_point_z(header, pt):
    """
    Test Point Z
    """
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2, 3
    assert pt.to_wkb() == point_z_to_wkb_point_z(*values)
    assert pt.to_gpkg() == point_z_to_gpkg_point_z(header, *values)
    assert PointZ.from_wkb(pt.to_wkb()) == pt
    assert PointZ.from_gpkg(pt.to_gpkg()) == pt
# End test_point_z function


@mark.parametrize('pt', [PointM(x=1, y=2, m=3), PointM.from_tuple((1, 2, 3))])
def test_point_m(header, pt):
    """
    Test Point M
    """
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2, 3
    assert pt.to_wkb() == point_m_to_wkb_point_m(*values)
    assert pt.to_gpkg() == point_m_to_gpkg_point_m(header, *values)
    assert PointM.from_wkb(pt.to_wkb()) == pt
    assert PointM.from_gpkg(pt.to_gpkg()) == pt
# End test_point_m function


@mark.parametrize('pt', [PointZM(x=1, y=2, z=3, m=4),
                         PointZM.from_tuple((1, 2, 3, 4))])
def test_point_zm(header, pt):
    """
    Test Point ZM
    """
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2, 3, 4
    assert pt.to_wkb() == point_zm_to_wkb_point_zm(*values)
    assert pt.to_gpkg() == point_zm_to_gpkg_point_zm(header, *values)
    assert PointZM.from_wkb(pt.to_wkb()) == pt
    assert PointZM.from_gpkg(pt.to_gpkg()) == pt
# End test_point_zm function


def test_multi_point(header):
    """
    Test multi point
    """
    values = [(0, 0), (1, 1)]
    pts = MultiPoint(values)
    with raises(AttributeError):
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts.to_wkb()
    assert wkb == multipoint_to_wkb_multipoint(values)
    assert MultiPoint.from_wkb(wkb) == pts
    gpkg = pts.to_gpkg()
    assert gpkg == points_to_gpkg_multipoint(header, values)
    assert MultiPoint.from_gpkg(gpkg) == pts
# End test_multi_point function


def test_multi_point_z(header):
    """
    Test multi point Z
    """
    values = [(0, 0, 0), (1, 1, 1)]
    pts = MultiPointZ(values)
    with raises(AttributeError):
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts.to_wkb()
    assert wkb == multipoint_z_to_wkb_multipoint_z(values)
    assert MultiPointZ.from_wkb(wkb) == pts
    assert MultiPointZ.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_z function


def test_multi_point_m(header):
    """
    Test multi point M
    """
    values = [(0, 0, 0), (1, 1, 1)]
    pts = MultiPointM(values)
    with raises(AttributeError):
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts.to_wkb()
    assert wkb == multipoint_m_to_wkb_multipoint_m(values)
    assert MultiPointM.from_wkb(wkb) == pts
    assert MultiPointM.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_m function


def test_multi_point_zm(header):
    """
    Test multi point ZM
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1)]
    pts = MultiPointZM(values)
    with raises(AttributeError):
        pts.attribute = 10
    assert pts.coordinates == values
    wkb = pts.to_wkb()
    assert wkb == multipoint_zm_to_wkb_multipoint_zm(values)
    assert MultiPointZM.from_wkb(wkb) == pts
    assert MultiPointZM.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point_zm function


def test_line_string(header):
    """
    Test line string wkb
    """
    values = [(0, 0), (1, 1)]
    line = LineString(values)
    with raises(AttributeError):
        line.attribute = 10
    assert line.coordinates == values
    wkb = line.to_wkb()
    assert wkb == points_to_wkb_line_string(values)
    assert line.to_gpkg() == points_to_gpkg_line_string(header, values)
    assert LineString.from_wkb(wkb) == line
    assert LineString.from_gpkg(line.to_gpkg()) == line
# End test_line_string function


def test_line_string_z(header):
    """
    Test line string Z wkb
    """
    values = [(0, 0, 0), (1, 1, 1)]
    line = LineStringZ(values)
    with raises(AttributeError):
        line.attribute = 10
    assert line.coordinates == values
    wkb = line.to_wkb()
    assert wkb == points_z_to_wkb_line_string_z(values)
    assert line.to_gpkg() == points_z_to_gpkg_line_string_z(header, values)
    assert LineStringZ.from_wkb(wkb) == line
    assert LineStringZ.from_gpkg(line.to_gpkg()) == line
# End test_line_string_z function


def test_line_string_m(header):
    """
    Test line string M wkb
    """
    values = [(0, 0, 0), (1, 1, 1)]
    line = LineStringM(values)
    with raises(AttributeError):
        line.attribute = 10
    assert line.coordinates == values
    wkb = line.to_wkb()
    assert wkb == points_m_to_wkb_line_string_m(values)
    assert line.to_gpkg() == points_m_to_gpkg_line_string_m(header, values)
    assert LineStringM.from_wkb(wkb) == line
    assert LineStringM.from_gpkg(line.to_gpkg()) == line
# End test_line_string_m function


def test_line_string_zm(header):
    """
    Test line string ZM wkb
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1)]
    line = LineStringZM(values)
    with raises(AttributeError):
        line.attribute = 10
    assert line.coordinates == values
    wkb = line.to_wkb()
    assert wkb == points_zm_to_wkb_line_string_zm(values)
    assert line.to_gpkg() == points_zm_to_gpkg_line_string_zm(header, values)
    assert LineStringZM.from_wkb(wkb) == line
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
    multi = MultiLineString(values)
    with raises(AttributeError):
        multi.attribute = 10
    assert multi.to_wkb() == point_lists_to_multi_line_string(values)
    assert multi.to_gpkg() == point_lists_to_gpkg_multi_line_string(header, values)
    assert MultiLineString.from_wkb(multi.to_wkb()) == multi
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
    multi = MultiLineStringZ(values)
    with raises(AttributeError):
        multi.attribute = 10
    assert multi.to_wkb() == point_lists_z_to_multi_line_string_z(values)
    assert MultiLineStringZ.from_wkb(multi.to_wkb()) == multi
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
    multi = MultiLineStringM(values)
    with raises(AttributeError):
        multi.attribute = 10
    assert multi.to_wkb() == point_lists_m_to_multi_line_string_m(values)
    assert MultiLineStringM.from_wkb(multi.to_wkb()) == multi
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
    multi = MultiLineStringZM(values)
    with raises(AttributeError):
        multi.attribute = 10
    assert multi.to_wkb() == point_lists_zm_to_multi_line_string_zm(values)
    assert MultiLineStringZM.from_wkb(multi.to_wkb()) == multi
    assert MultiLineStringZM.from_gpkg(multi.to_gpkg()) == multi
# End test_multi_line_string_zm function


def test_linear_ring(header):
    """
    Test linear ring wkb
    """
    values = [(0, 0), (1, 1), (2, 0), (0, 0)]
    ring = LinearRing(values)
    with raises(AttributeError):
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring.to_wkb()
    assert wkb == _linear_ring_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRing.from_wkb(wkb) == ring
    with raises(NotImplementedError):
        assert LinearRing.from_gpkg(b'')
# End test_linear_ring function


def test_linear_ring_z(header):
    """
    Test linear ring Z wkb
    """
    values = [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)]
    ring = LinearRingZ(values)
    with raises(AttributeError):
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring.to_wkb()
    assert wkb == _linear_ring_z_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRingZ.from_wkb(wkb) == ring
    with raises(NotImplementedError):
        assert LinearRingZ.from_gpkg(b'')
# End test_linear_ring_z function


def test_linear_ring_m(header):
    """
    Test linear ring M wkb
    """
    values = [(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 0, 0)]
    ring = LinearRingM(values)
    with raises(AttributeError):
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring.to_wkb()
    assert wkb == _linear_ring_m_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRingM.from_wkb(wkb) == ring
    with raises(NotImplementedError):
        assert LinearRingM.from_gpkg(b'')
# End test_linear_ring_m function


def test_linear_ring_zm(header):
    """
    Test linear ring ZM wkb
    """
    values = [(0, 0, 0, 0), (1, 1, 1, 1), (2, 0, 2, 0), (0, 0, 0, 0)]
    ring = LinearRingZM(values)
    with raises(AttributeError):
        ring.attribute = 10
    assert ring.coordinates == values
    wkb = ring.to_wkb()
    assert wkb == _linear_ring_zm_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRingZM.from_wkb(wkb) == ring
    with raises(NotImplementedError):
        assert LinearRingZM.from_gpkg(b'')
# End test_linear_ring_zm function


def test_polygon(header):
    """
    Test polygon wkb
    """
    values = [[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
              [(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]]
    poly = Polygon(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_to_wkb_polygon(values)
    assert poly.to_gpkg() == point_lists_to_gpkg_polygon(header, values)
    assert Polygon.from_wkb(poly.to_wkb()) == poly
    assert Polygon.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon function


def test_polygon_z(header):
    """
    Test polygon Z wkb
    """
    values = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    poly = PolygonZ(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_z_to_wkb_polygon_z(values)
    assert PolygonZ.from_wkb(poly.to_wkb()) == poly
    assert PolygonZ.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon_z function


def test_polygon_m(header):
    """
    Test polygon M wkb
    """
    values = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    poly = PolygonM(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_m_to_wkb_polygon_m(values)
    assert PolygonM.from_wkb(poly.to_wkb()) == poly
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
    poly = PolygonZM(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_zm_to_wkb_polygon_zm(values)
    assert PolygonZM.from_wkb(poly.to_wkb()) == poly
    assert PolygonZM.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon_zm function


def test_multi_polygon(header):
    """
    Test multi polygon wkb
    """
    values = [[[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]],
              [[(5, 5), (5, 15), (15, 15), (15, 5), (5, 5)]],
              [[(7, 7), (7, 17), (17, 17), (7, 7)]]]
    poly = MultiPolygon(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_to_wkb_multipolygon(values)
    assert poly.to_gpkg() == point_lists_to_gpkg_multi_polygon(header, values)
    assert MultiPolygon.from_wkb(poly.to_wkb()) == poly
    assert MultiPolygon.from_gpkg(poly.to_gpkg()) == poly
# End test_polygon function


def test_multi_polygon_z(header):
    """
    Test multi polygon Z wkb
    """
    values = [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]],
              [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]]
    poly = MultiPolygonZ(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_z_to_wkb_multipolygon_z(values)
    assert MultiPolygonZ.from_wkb(poly.to_wkb()) == poly
    assert MultiPolygonZ.from_gpkg(poly.to_gpkg()) == poly
# End test_multi_polygon_z function


def test_multi_polygon_m(header):
    """
    Test multi polygon M wkb
    """
    values = [[[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)]],
              [[(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]]
    poly = MultiPolygonM(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_m_to_wkb_multipolygon_m(values)
    assert MultiPolygonM.from_wkb(poly.to_wkb()) == poly
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
    poly = MultiPolygonZM(values)
    with raises(AttributeError):
        poly.attribute = 10
    assert poly.to_wkb() == point_lists_zm_to_wkb_multipolygon_zm(values)
    assert MultiPolygonZM.from_wkb(poly.to_wkb()) == poly
    assert MultiPolygonZM.from_gpkg(poly.to_gpkg()) == poly
# End test_multi_polygon_zm function


@mark.parametrize('cls, srs_id, offset, data', [
    (MultiPolygon, 4617, 8, b"GP\x00\x01\t\x12\x00\x00\x01\x06\x00\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@"),
    (MultiPolygonZ, 4617, 8, b"GP\x00\x01\t\x12\x00\x00\x01\xee\x03\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\x80\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@"),
    (MultiPolygonM, 4617, 8, b"GP\x00\x01\t\x12\x00\x00\x01\xd6\x07\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00@\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygonZM, 4617, 8, b"GP\x00\x01\t\x12\x00\x00\x01\xbe\x0b\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\xc0\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygon, 4617, 40, b'GP\x00\x03\t\x12\x00\x00`v`Jn\xd8[\xc0L/\x9d{\xb4\xd7[\xc0\x18\xbe\x9c~\xf5\xedH@\xb0p\x15\xd5l\xefH@\x01\x06\x00\x00\x00\x03\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00L/\x9d{\xb4\xd7[\xc0xom\x97\xec\xeeH@\xe4\x12\xa2\xd7\xfa\xd7[\xc0X\x00\xd6\xf4\xea\xeeH@L\x98\xe6\x0c\xfb\xd7[\xc0@1\x90\x0c\xde\xeeH@<\x1aN\x99\x1b\xd8[\xc0\xd0aA\xab\xdd\xeeH@\xf0\xad\xb41\x1b\xd8[\xc0\xa0\x97\xa1\x96\x8b\xeeH@@\x08#QC\xd8[\xc0\x18\xabP\xee\x88\xeeH@\x8c/\xa1\x82C\xd8[\xc0\x10)\x9abi\xeeH@<\x85\xc8\x8e2\xd8[\xc0\xd0\xc4\xbe\xaep\xeeH@\xd0I\xb6\xba\x1c\xd8[\xc0H\x82\x98:~\xeeH@L~\x8bN\x16\xd8[\xc0p\xa1\xae\xff\x84\xeeH@\xd0`\x1a\x86\x0f\xd8[\xc0x\x11s\xa4\x8e\xeeH@\xb0)\xb21\n\xd8[\xc0\x10|\xd9\xd1\x93\xeeH@\xbc\xe9L\x90\xc7\xd7[\xc0@0\x80\xf0\xa1\xeeH@ XU/\xbf\xd7[\xc0\x90q\xa3m\xa1\xeeH@H\xb4\xe4\xf1\xb4\xd7[\xc0p\x1d\xfa\x93\x9d\xeeH@L/\x9d{\xb4\xd7[\xc0xom\x97\xec\xeeH@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\xc8\x027\x9cC\xd8[\xc0\x10\x15\xd2\xd0\xf5\xedH@LW\x1csC\xd8[\xc0@\xffe\xadW\xeeH@\x1c\xd6\n\x89j\xd8[\xc0x\xa2\x96\xe6V\xeeH@\xb0\xd7`\x86k\xd8[\xc0  vK\x17\xeeH@\xcc8\x1e}]\xd8[\xc0\xd0\xec=\xa6\xff\xedH@tXM|Z\xd8[\xc0h:\xbe\x07\xf9\xedH@`"\xeffW\xd8[\xc0\x18\xbe\x9c~\xf5\xedH@\xc8\x027\x9cC\xd8[\xc0\x10\x15\xd2\xd0\xf5\xedH@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x008\xa4\x18 Q\xd8[\xc0H\x92\xfe\x03Q\xefH@D\xc5\xff\x1dQ\xd8[\xc0\xb0p\x15\xd5l\xefH@\x04\x80*n\\\xd8[\xc0 \x88\x1b\xa6l\xefH@8\xf7\xb2Hn\xd8[\xc0\xd0\xd1w\x12l\xefH@`v`Jn\xd8[\xc0h\xf3`AP\xefH@8\xa4\x18 Q\xd8[\xc0H\x92\xfe\x03Q\xefH@'),
    (MultiPolygonZ, 4617, 56, b"GP\x00\x05\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\xc0\x9f\x1a/\xdd^@\x01\xee\x03\x00\x00\x01\x00\x00\x00\x01\xeb\x03\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@"),
    (MultiPolygonM, 4617, 40, b"GP\x00\x03\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x01\xd6\x07\x00\x00\x01\x00\x00\x00\x01\xd3\x07\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygonZM, 4617, 56, b"GP\x00\x05\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\xc0\x9f\x1a/\xdd^@\x01\xbe\x0b\x00\x00\x01\x00\x00\x00\x01\xbb\x0b\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
])
def test_geometry_header(cls, srs_id, offset, data):
    """
    Test geometry header
    """
    sid, off = _unpack_header_srs_id_and_offset(data[:8])
    assert sid == srs_id
    assert off == offset
    geom = cls.from_gpkg(data)
    assert isinstance(geom, cls)
# End test_geometry_header function


if __name__ == '__main__':
    pass
