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
    points_zm_to_wkb_line_string_zm)


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
    """
    return bytes(header + point_to_wkb_point(x, y))
# End point_to_gpkg_point


def point_z_to_gpkg_point_z(header, x, y, z):
    """
    Point to WKBPointZ
    """
    return bytes(header + point_z_to_wkb_point_z(x, y, z))
# End point_z_to_gpkg_point_z function


def point_m_to_gpkg_point_m(header, x, y, m):
    """
    Point to WKBPointM
    """
    return bytes(header + point_m_to_wkb_point_m(x, y, m))
# End point_m_to_gpkg_point_m function


def point_zm_to_gpkg_point_zm(header, x, y, z, m):
    """
    Point to WKBPointZM
    """
    return bytes(header + point_zm_to_wkb_point_zm(x, y, z, m))
# End point_zm_to_gpkg_point_zm function


def points_to_gpkg_line_string(header, points):
    """
    List of points to a gpkg blob
    """
    return bytes(header + points_to_wkb_line_string(points))
# End points_to_gpkg_line_string


def points_z_to_gpkg_line_string_z(header, points):
    """
    List of points z to a gpkg blob
    """
    return bytes(header + points_z_to_wkb_line_string_z(points))
# End points_to_gpkg_line_string


def points_m_to_gpkg_line_string_m(header, points):
    """
    List of points m to a gpkg blob
    """
    return bytes(header + points_m_to_wkb_line_string_m(points))
# End points_to_gpkg_line_string


def points_zm_to_gpkg_line_string_zm(header, points):
    """
    List of points zm to a gpkg blob
    """
    return bytes(header + points_zm_to_wkb_line_string_zm(points))
# End points_zm_to_gpkg_line_string_zm function


if __name__ == '__main__':
    pass
