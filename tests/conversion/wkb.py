# -*- coding: utf-8 -*-
"""
Conversion Utils
"""
from sys import version_info
from struct import pack

BYTE_UINT = '<BI'

WKB_POINT_PRE = pack(BYTE_UINT, 1, 1)
WKB_POINTZ_PRE = pack(BYTE_UINT, 1, 1001)
WKB_POINTM_PRE = pack(BYTE_UINT, 1, 2001)
WKB_POINTZM_PRE = pack(BYTE_UINT, 1, 3001)

WKB_MULTI_POINT_PRE = pack(BYTE_UINT, 1, 4)
WKB_MULTI_POINT_Z_PRE = pack(BYTE_UINT, 1, 1004)
WKB_MULTI_POINT_M_PRE = pack(BYTE_UINT, 1, 2004)
WKB_MULTI_POINT_ZM_PRE = pack(BYTE_UINT, 1, 3004)

WKB_LINESTRING_PRE = pack(BYTE_UINT, 1, 2)
WKB_LINESTRINGZ_PRE = pack(BYTE_UINT, 1, 1002)
WKB_LINESTRINGM_PRE = pack(BYTE_UINT, 1, 2002)
WKB_LINESTRINGZM_PRE = pack(BYTE_UINT, 1, 3002)

WKB_MULTI_LINESTRING_PRE = pack(BYTE_UINT, 1, 5)
WKB_MULTI_LINESTRING_Z_PRE = pack(BYTE_UINT, 1, 1005)
WKB_MULTI_LINESTRING_M_PRE = pack(BYTE_UINT, 1, 2005)
WKB_MULTI_LINESTRING_ZM_PRE = pack(BYTE_UINT, 1, 3005)

WKB_POLY_PRE = pack(BYTE_UINT, 1, 3)
WKB_POLY_Z_PRE = pack(BYTE_UINT, 1, 1003)
WKB_POLY_M_PRE = pack(BYTE_UINT, 1, 2003)
WKB_POLY_ZM_PRE = pack(BYTE_UINT, 1, 3003)

WKB_MULTI_POLY_PRE = pack(BYTE_UINT, 1, 6)
WKB_MULTI_POLY_Z_PRE = pack(BYTE_UINT, 1, 1006)
WKB_MULTI_POLY_M_PRE = pack(BYTE_UINT, 1, 2006)
WKB_MULTI_POLY_ZM_PRE = pack(BYTE_UINT, 1, 3006)


EMPTY_B = ''
if version_info > (3,):
    EMPTY_B = b''


def _point_to_wkb(x, y):
    """
    Building Block Point X, Y

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :return: formatted string
    """
    return pack('<2d', x, y)
# End point_to_wkb function


def _point_z_to_wkb(x, y, z):
    """
    Building Block Point X, Y, Z

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param z: the z coord
    :type z: float
    :return: formatted string
    """
    return pack('<3d', x, y, z)
# End pointz_to_wkb function


def _point_m_to_wkb(x, y, m):
    """
    Building Block Point X, Y, M

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param m: the m coord
    :type m: float
    :return: formatted string
    """
    return pack('<3d', x, y, m)
# End point_m_to_wkb function


def _point_zm_to_wkb(x, y, z, m):
    """
    Building Block Point X, Y, Z, M

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param z: the z coord
    :type z: float
    :param m: the m coord
    :type m: float
    :return: formatted string
    """
    return pack('<4d', x, y, z, m)
# End point_zm_to_wkb function


def _linear_ring_to_wkb(points):
    """
    Building Block Linear Ring

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return pack('<I', len(points)) + EMPTY_B.join(
        (_point_to_wkb(x, y) for x, y in points))
# End linear_ring_to_wkb function


def _linear_ring_z_to_wkb(points):
    """
    Building Block Linear Ring Z

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return pack('<I', len(points)) + EMPTY_B.join(
        (_point_z_to_wkb(x, y, z) for x, y, z in points))
# End linear_ring_z_to_wkb


def _linear_ring_m_to_wkb(points):
    """
    Building Block Linear Ring M

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return pack('<I', len(points)) + EMPTY_B.join(
        (_point_m_to_wkb(x, y, m) for x, y, m in points))
# End linear_ring_m_to_wkb


def _linear_ring_zm_to_wkb(points):
    """
    Building Block Linear Ring ZM

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return pack('<I', len(points)) + EMPTY_B.join(
        (_point_zm_to_wkb(x, y, z, m) for x, y, z, m in points))
# End linear_ring_zm_to_wkb


def point_to_wkb_point(x, y):
    """
    Point to WKBPoint

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :return: formatted string
    :rtype: str
    """
    return WKB_POINT_PRE + _point_to_wkb(x, y)
# End point_to_wkb_point


def point_z_to_wkb_point_z(x, y, z):
    """
    Point to WKBPointZ

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param z: the z coord
    :type z: float
    :return: formatted string
    :rtype: str
    """
    return WKB_POINTZ_PRE + _point_z_to_wkb(x, y, z)
# End point_z_to_wkb_point_z function


def point_m_to_wkb_point_m(x, y, m):
    """
    Point to WKBPointM

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param m: the m coord
    :type m: float
    :return: formatted string
    :rtype: str
    """
    return WKB_POINTM_PRE + _point_m_to_wkb(x, y, m)
# End point_m_to_wkb_point_m function


def point_zm_to_wkb_point_zm(x, y, z, m):
    """
    Point to WKBPointZM

    :param x: the x coord
    :type x: float
    :param y: the y coord
    :type y: float
    :param z: the z coord
    :type z: float
    :param m: the m coord
    :type m: float
    :return: formatted string
    :rtype: str
    """
    return WKB_POINTZM_PRE + _point_zm_to_wkb(x, y, z, m)
# End point_zm_to_wkb_point_zm function


def multipoint_to_wkb_multipoint(points):
    """
    Multipoint to WKBMultiPoint
    """
    return (WKB_MULTI_POINT_PRE + pack('<I', len(points)) +
            EMPTY_B.join((point_to_wkb_point(x, y) for x, y in points)))
# End multipoint_to_wkb_multipoint function


def multipoint_z_to_wkb_multipoint_z(points):
    """
    Multipoint to WKBMultiPoint
    """
    return (WKB_MULTI_POINT_Z_PRE + pack('<I', len(points)) +
            EMPTY_B.join((point_z_to_wkb_point_z(x, y, z) for x, y, z in points)))
# End multipoint_z_to_wkb_multipoint_z function


def multipoint_m_to_wkb_multipoint_m(points):
    """
    Multipoint to WKBMultiPoint
    """
    return (WKB_MULTI_POINT_M_PRE + pack('<I', len(points)) +
            EMPTY_B.join((point_m_to_wkb_point_m(x, y, m) for x, y, m in points)))
# End multipoint_m_to_wkb_multipoint_m function


def multipoint_zm_to_wkb_multipoint_zm(points):
    """
    Multipoint to WKBMultiPoint
    """
    return (WKB_MULTI_POINT_ZM_PRE + pack('<I', len(points)) +
            EMPTY_B.join((point_zm_to_wkb_point_zm(x, y, z, m) for x, y, z, m in points)))
# End multipoint_z_to_wkb_multipoint_z function


def points_to_wkb_line_string(points):
    """
    Points to WKB LineString

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_LINESTRING_PRE + pack('<I', len(points)) +
            EMPTY_B.join((_point_to_wkb(x, y) for x, y in points)))
# End points_to_wkb_line_string


def points_z_to_wkb_line_string_z(points):
    """
    Points to WKB LineString Z

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_LINESTRINGZ_PRE + pack('<I', len(points)) +
            EMPTY_B.join((_point_z_to_wkb(x, y, z) for x, y, z in points)))
# End points_to_wkb_line_string


def points_m_to_wkb_line_string_m(points):
    """
    Points to WKB LineString M

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_LINESTRINGM_PRE + pack('<I', len(points)) +
            EMPTY_B.join((_point_m_to_wkb(x, y, m) for x, y, m in points)))
# End points_to_wkb_line_string


def points_zm_to_wkb_line_string_zm(points):
    """
    Points to WKB LineString ZM

    :param points: Points in the ring
    :type points: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_LINESTRINGZM_PRE + pack('<I', len(points)) +
            EMPTY_B.join((
                _point_zm_to_wkb(x, y, z, m) for x, y, z, m in points)))
# End point_zm_to_wkb_line_string_zm function


def point_lists_to_multi_line_string(point_lists):
    """
    Point lists to WKB MultiLineString

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]] is a multi line

    """
    return (WKB_MULTI_LINESTRING_PRE + pack('<I', len(point_lists)) +
            EMPTY_B.join((
                points_to_wkb_line_string(ring) for ring in point_lists)))
# End point_lists_to_multi_line_String function


def point_lists_z_to_multi_line_string_z(point_lists):
    """
    Point lists to WKB MultiLineString

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]] is a multi line

    """
    return (WKB_MULTI_LINESTRING_Z_PRE + pack('<I', len(point_lists)) +
            EMPTY_B.join((
                points_z_to_wkb_line_string_z(ring) for ring in point_lists)))
# End point_lists_z_to_multi_line_string_z function


def point_lists_m_to_multi_line_string_m(point_lists):
    """
    Point lists to WKB MultiLineString

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]] is a multi line

    """
    return (WKB_MULTI_LINESTRING_M_PRE + pack('<I', len(point_lists)) +
            EMPTY_B.join((
                points_m_to_wkb_line_string_m(ring) for ring in point_lists)))
# End point_lists_m_to_multi_line_string_m function


def point_lists_zm_to_multi_line_string_zm(point_lists):
    """
    Point lists to WKB MultiLineString

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]] is a multi line

    """
    return (WKB_MULTI_LINESTRING_ZM_PRE + pack('<I', len(point_lists)) +
            EMPTY_B.join((
                points_zm_to_wkb_line_string_zm(ring) for ring in point_lists)))
# End point_lists_m_to_multi_line_string_m function


def point_lists_to_wkb_polygon(ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param ring_point_lists: List of List of Points
    :type ring_point_lists: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_POLY_PRE + pack('<I', len(ring_point_lists)) +
            EMPTY_B.join((
                _linear_ring_to_wkb(ring) for ring in ring_point_lists)))
# End point_lists_to_wkb_polygon function


def point_lists_z_to_wkb_polygon_z(ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param ring_point_lists: List of List of Points
    :type ring_point_lists: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_POLY_Z_PRE + pack('<I', len(ring_point_lists)) +
            EMPTY_B.join((
                _linear_ring_z_to_wkb(ring) for ring in ring_point_lists)))
# End point_lists_z_to_wkb_polygon_z function


def point_lists_m_to_wkb_polygon_m(ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param ring_point_lists: List of List of Points
    :type ring_point_lists: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_POLY_M_PRE + pack('<I', len(ring_point_lists)) +
            EMPTY_B.join((
                _linear_ring_m_to_wkb(ring) for ring in ring_point_lists)))
# End point_lists_m_to_wkb_polygon_m function


def point_lists_zm_to_wkb_polygon_zm(ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param ring_point_lists: List of List of Points
    :type ring_point_lists: list
    :return: formatted string
    :rtype: str
    """
    return (WKB_POLY_ZM_PRE + pack('<I', len(ring_point_lists)) +
            EMPTY_B.join((
                _linear_ring_zm_to_wkb(ring) for ring in ring_point_lists)))
# End point_lists_zm_to_wkb_polygon_zm function


def point_lists_to_wkb_multipolygon(polygon_ring_lists):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]

    :param polygon_ring_lists: List of List of List of points
    :type polygon_ring_lists: list
    :return: formatted string
    :rtype: str
    """
    num = pack('<I', len(polygon_ring_lists))
    out = EMPTY_B
    for point_list in polygon_ring_lists:
        out += point_lists_to_wkb_polygon(point_list)
    return WKB_MULTI_POLY_PRE + num + out
# End point_lists_to_wkb_polygon function


def point_lists_z_to_wkb_multipolygon_z(polygon_ring_lists):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]

    :param polygon_ring_lists: List of List of List of points
    :type polygon_ring_lists: list
    :return: formatted string
    :rtype: str
    """
    num = pack('<I', len(polygon_ring_lists))
    out = EMPTY_B
    for point_list in polygon_ring_lists:
        out += point_lists_z_to_wkb_polygon_z(point_list)
    return WKB_MULTI_POLY_Z_PRE + num + out
# End point_lists_z_to_wkb_multipolygon_z function


def point_lists_m_to_wkb_multipolygon_m(polygon_ring_lists):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]

    :param polygon_ring_lists: List of List of List of points
    :type polygon_ring_lists: list
    :return: formatted string
    :rtype: str
    """
    num = pack('<I', len(polygon_ring_lists))
    out = EMPTY_B
    for point_list in polygon_ring_lists:
        out += point_lists_m_to_wkb_polygon_m(point_list)
    return WKB_MULTI_POLY_M_PRE + num + out
# End point_lists_m_to_wkb_multipolygon_m function


def point_lists_zm_to_wkb_multipolygon_zm(polygon_ring_lists):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]

    :param polygon_ring_lists: List of List of List of points
    :type polygon_ring_lists: list
    :return: formatted string
    :rtype: str
    """
    num = pack('<I', len(polygon_ring_lists))
    out = EMPTY_B
    for point_list in polygon_ring_lists:
        out += point_lists_zm_to_wkb_polygon_zm(point_list)
    return WKB_MULTI_POLY_ZM_PRE + num + out
# End point_lists_zm_to_wkb_multipolygon_zm function


if __name__ == '__main__':
    pass
