# -*- coding: utf-8 -*-
"""
Convert to Geopackage Geometry Blobs
"""

from struct import pack

from fudgeo.constant import GP_MAGIC
from tests.conversion.wkb import (
    point_to_wkb_point, point_z_to_wkb_point_z, point_m_to_wkb_point_m,
    point_zm_to_wkb_point_zm, points_to_wkb_line_string,
    points_z_to_wkb_line_string_z, points_m_to_wkb_line_string_m,
    points_zm_to_wkb_line_string_zm, point_lists_to_wkb_polygon,
    point_lists_to_wkb_multipolygon, multipoint_to_wkb_multipoint,
    point_lists_to_multi_line_string)


def make_gpkg_geom_header(srs_id, env_code):
    """
    Make a Geopackage geometry binary header
    """
    magic, version, flags = GP_MAGIC, 0, 1
    flags |= (env_code << 1)
    return pack('<2s2bi', magic, version, flags, srs_id)
# End make_gpkg_geom_header function


def point_to_gpkg_point(header, x, y):
    """
    Point to WKBPoint

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param header: the binary header, see "make_gpkg_geom_header"
    :return: the WKB
    """
    return bytes(header + point_to_wkb_point(x, y))
# End point_to_gpkg_point


def point_z_to_gpkg_point_z(header, x, y, z):
    """
    Point to WKBPointZ

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param z: z coord
    :type z: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return bytes(header + point_z_to_wkb_point_z(x, y, z))
# End point_z_to_gpkg_point_z function


def point_m_to_gpkg_point_m(header, x, y, m):
    """
    Point to WKBPointM

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param m: m coord
    :type m: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return bytes(header + point_m_to_wkb_point_m(x, y, m))
# End point_m_to_gpkg_point_m function


def point_zm_to_gpkg_point_zm(header, x, y, z, m):
    """
    Point to WKBPointZM

    :param x: x coord
    :type x: float
    :param y: y coord
    :type y: float
    :param z: z coord
    :type z: float
    :param m: m coord
    :type m: float
    :param header: the binary header, see "make_gpkg_geom_header"
    """
    return bytes(header + point_zm_to_wkb_point_zm(x, y, z, m))
# End point_zm_to_gpkg_point_zm function


def points_to_gpkg_multipoint(header, points):
    """
    List of points to a gpkg multi point blob
    """
    return bytes(header + multipoint_to_wkb_multipoint(points))
# End points_to_gpkg_multi_point function


def points_to_gpkg_line_string(header, points):
    """
    List of points to a gpkg blob

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: list of points making up the line
    :type points: list
    :return:
    """
    return bytes(header + points_to_wkb_line_string(points))
# End points_to_gpkg_line_string


def points_z_to_gpkg_line_string_z(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return bytes(header + points_z_to_wkb_line_string_z(points))
# End points_to_gpkg_line_string


def points_m_to_gpkg_line_string_m(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return bytes(header + points_m_to_wkb_line_string_m(points))
# End points_to_gpkg_line_string


def points_zm_to_gpkg_line_string_zm(header, points):
    """

    :param header: the binary header, see "make_gpkg_geom_header"
    :param points: List of points making up the line
    :type points: list
    :return:
    """
    return bytes(header + points_zm_to_wkb_line_string_zm(points))
# End points_zm_to_gpkg_line_string_zm function


def point_lists_to_gpkg_multi_line_string(header, point_lists):
    """

    :param header:
    :param point_lists:
    :return:
    """
    return bytes(header + point_lists_to_multi_line_string(point_lists))
# End point_lists_to_gpkg_multi_line_string function


def point_lists_to_gpkg_polygon(header, ring_point_lists):
    """
    Ring point lists should be lists of points representing poly rings.

    # NOTE!! You MUST close the polygon or ArcMap will be unhappy!

    i.e. [[(x, y), (x, y), ..],[(x, y), (x, y)...]]

    :param header: the binary header, see "make_gpkg_geom_header"
    :param ring_point_lists: List of rings in the polygon
    :type ring_point_lists: list
    :return:
    """
    return bytes(header + point_lists_to_wkb_polygon(ring_point_lists))
# End point_lists_to_wkb_polygon function


def point_lists_to_gpkg_multi_polygon(header, list_of_polys):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]
    """
    return bytes(header + point_lists_to_wkb_multipolygon(list_of_polys))
# End point_lists_to_gpkg_multi_polygon function


def point_lists_z_to_gpkg_multi_polygon_z(header, list_of_polys):
    """
    This is a list (polygons) which are lists of rings which are lists of points
    Point lists should be lists of points representing poly rings.

    i.e. [[[(x, y), (x, y), ..],[(x, y), (x, y)...]],[etc]]
    """
    return bytes(header + point_lists_to_wkb_multipolygon(list_of_polys))
# End point_lists_z_to_gpkg_multi_polygon_z function


if __name__ == '__main__':
    pass
