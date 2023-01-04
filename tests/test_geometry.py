# -*- coding: utf-8 -*-
"""
Test Geometry
"""

from pytest import fixture, raises

from tests.conversion.geo import (
    make_gpkg_geom_header, point_lists_to_gpkg_multi_line_string,
    point_lists_to_gpkg_multi_polygon, point_lists_to_gpkg_polygon,
    point_m_to_gpkg_point_m, point_to_gpkg_point, point_z_to_gpkg_point_z,
    point_zm_to_gpkg_point_zm, points_m_to_gpkg_line_string_m,
    points_to_gpkg_line_string, points_to_gpkg_multipoint,
    points_z_to_gpkg_line_string_z, points_zm_to_gpkg_line_string_zm)
from tests.conversion.wkb import (
    _linear_ring_to_wkb, _linear_ring_z_to_wkb,
    multipoint_m_to_wkb_multipoint_m, multipoint_to_wkb_multipoint,
    multipoint_z_to_wkb_multipoint_z, multipoint_zm_to_wkb_multipoint_zm,
    point_lists_m_to_multi_line_string_m, point_lists_m_to_wkb_multipolygon_m,
    point_lists_m_to_wkb_polygon_m,
    point_lists_to_multi_line_string,
    point_lists_to_wkb_multipolygon, point_lists_to_wkb_polygon,
    point_lists_z_to_multi_line_string_z, point_lists_z_to_wkb_multipolygon_z,
    point_lists_z_to_wkb_polygon_z, point_lists_zm_to_multi_line_string_zm,
    point_lists_zm_to_wkb_multipolygon_zm, point_lists_zm_to_wkb_polygon_zm,
    point_m_to_wkb_point_m,
    point_to_wkb_point, point_z_to_wkb_point_z,
    point_zm_to_wkb_point_zm, points_m_to_wkb_line_string_m,
    points_to_wkb_line_string, points_z_to_wkb_line_string_z,
    points_zm_to_wkb_line_string_zm)
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, LinearRing, LinearRingZ,
    MultiLineString, MultiLineStringM, MultiLineStringZ, MultiLineStringZM,
    MultiPoint, MultiPointM, MultiPointZ, MultiPointZM, MultiPolygon,
    MultiPolygonM, MultiPolygonZ, MultiPolygonZM, Point, PointM, PointZ,
    PointZM, Polygon,
    PolygonM, PolygonZ,
    PolygonZM)


@fixture(scope='session')
def header():
    """
    Header
    """
    return make_gpkg_geom_header(4326)
# End header function


def test_point(header):
    """
    Test Point
    """
    pt = Point(x=1, y=2)
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2
    assert pt.to_wkb() == point_to_wkb_point(*values)
    assert pt.to_gpkg() == point_to_gpkg_point(header, *values)
    assert Point.from_wkb(pt.to_wkb()) == pt
    assert Point.from_gpkg(pt.to_gpkg()) == pt
# End test_point function


def test_point_z(header):
    """
    Test Point Z
    """
    pt = PointZ(x=1, y=2, z=3)
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2, 3
    assert pt.to_wkb() == point_z_to_wkb_point_z(*values)
    assert pt.to_gpkg() == point_z_to_gpkg_point_z(header, *values)
    assert PointZ.from_wkb(pt.to_wkb()) == pt
    assert PointZ.from_gpkg(pt.to_gpkg()) == pt
# End test_point_z function


def test_point_m(header):
    """
    Test Point M
    """
    pt = PointM(x=1, y=2, m=3)
    with raises(AttributeError):
        pt.attribute = 10
    values = 1, 2, 3
    assert pt.to_wkb() == point_m_to_wkb_point_m(*values)
    assert pt.to_gpkg() == point_m_to_gpkg_point_m(header, *values)
    assert PointM.from_wkb(pt.to_wkb()) == pt
    assert PointM.from_gpkg(pt.to_gpkg()) == pt
# End test_point_m function


def test_point_zm(header):
    """
    Test Point ZM
    """
    pt = PointZM(x=1, y=2, z=3, m=4)
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
    assert pts.to_wkb() == multipoint_to_wkb_multipoint(values)
    assert pts.to_gpkg() == points_to_gpkg_multipoint(header, values)
    assert MultiPoint.from_wkb(pts.to_wkb()) == pts
    assert MultiPoint.from_gpkg(pts.to_gpkg()) == pts
# End test_multi_point function


def test_multi_point_z(header):
    """
    Test multi point Z
    """
    values = [(0, 0, 0), (1, 1, 1)]
    pts = MultiPointZ(values)
    with raises(AttributeError):
        pts.attribute = 10
    assert pts.to_wkb() == multipoint_z_to_wkb_multipoint_z(values)
    assert MultiPointZ.from_wkb(pts.to_wkb()) == pts
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
    assert pts.to_wkb() == multipoint_m_to_wkb_multipoint_m(values)
    assert MultiPointM.from_wkb(pts.to_wkb()) == pts
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
    assert pts.to_wkb() == multipoint_zm_to_wkb_multipoint_zm(values)
    assert MultiPointZM.from_wkb(pts.to_wkb()) == pts
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
    assert line.to_wkb() == points_to_wkb_line_string(values)
    assert line.to_gpkg() == points_to_gpkg_line_string(header, values)
    assert LineString.from_wkb(line.to_wkb()) == line
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
    assert line.to_wkb() == points_z_to_wkb_line_string_z(values)
    assert line.to_gpkg() == points_z_to_gpkg_line_string_z(header, values)
    assert LineStringZ.from_wkb(line.to_wkb()) == line
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
    assert line.to_wkb() == points_m_to_wkb_line_string_m(values)
    assert line.to_gpkg() == points_m_to_gpkg_line_string_m(header, values)
    assert LineStringM.from_wkb(line.to_wkb()) == line
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
    assert line.to_wkb() == points_zm_to_wkb_line_string_zm(values)
    assert line.to_gpkg() == points_zm_to_gpkg_line_string_zm(header, values)
    assert LineStringZM.from_wkb(line.to_wkb()) == line
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
    assert ring.to_wkb() == _linear_ring_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRing.from_wkb(ring.to_wkb()) == ring
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
    assert ring.to_wkb() == _linear_ring_z_to_wkb(values)
    with raises(NotImplementedError):
        assert ring.to_gpkg()
    assert LinearRingZ.from_wkb(ring.to_wkb()) == ring
    with raises(NotImplementedError):
        assert LinearRingZ.from_gpkg(b'')
# End test_linear_ring_z function


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


if __name__ == '__main__':
    pass
