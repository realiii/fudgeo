# -*- coding: utf-8 -*-
"""
Enums
"""


from typing import ClassVar


class GPKGFlavors:
    """
    Geopackage Flavors mostly meaning which default srs definitions to use.
    Basically which 4326 definition to insert into the SRS table to start with.
    """
    esri = 'ESRI'
    epsg = 'EPSG'
# End GPKGFlavors class


class DataType:
    """
    Allowed Data Type values
    """
    features = 'features'
    attributes = 'attributes'
    tiles = 'tiles'
# End DataType class


class GeometryType:
    """
    Allowed Geometry Type values
    """
    point = 'POINT'
    linestring = 'LINESTRING'
    polygon = 'POLYGON'
    multi_point = 'MULTIPOINT'
    multi_linestring = 'MULTILINESTRING'
    multi_polygon = 'MULTIPOLYGON'
# End GeometryType class


class SQLFieldType(GeometryType):
    """
    SQL Field Types
    """
    boolean = 'BOOLEAN'
    tinyint = 'TINYINT'
    smallint = 'SMALLINT'
    mediumint = 'MEDIUMINT'
    integer = 'INTEGER'
    float = 'FLOAT'
    double = 'DOUBLE'
    real = 'REAL'
    text = 'TEXT'
    blob = 'BLOB'
    date = 'DATE'
    timestamp = 'TIMESTAMP'
    datetime = 'DATETIME'
# End SQLFieldType class


class EnvelopeCode:
    """
    Envelope Code
    """
    empty: ClassVar[int] = 0
    xy: ClassVar[int] = 1
    xyz: ClassVar[int] = 2
    xym: ClassVar[int] = 3
    xyzm: ClassVar[int] = 4
# End EnvelopeCode class


if __name__ == '__main__':
    pass
