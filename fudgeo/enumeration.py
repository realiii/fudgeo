# -*- coding: utf-8 -*-
"""
Enums
"""


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


if __name__ == '__main__':
    pass
