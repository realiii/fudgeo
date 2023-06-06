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
    esri: ClassVar[str] = 'ESRI'
    epsg: ClassVar[str] = 'EPSG'
# End GPKGFlavors class


class DataType:
    """
    Allowed Data Type values
    """
    features: ClassVar[str] = 'features'
    attributes: ClassVar[str] = 'attributes'
    tiles: ClassVar[str] = 'tiles'
# End DataType class


class GeometryType:
    """
    Allowed Geometry Type values
    """
    point: ClassVar[str] = 'POINT'
    linestring: ClassVar[str] = 'LINESTRING'
    polygon: ClassVar[str] = 'POLYGON'
    multi_point: ClassVar[str] = 'MULTIPOINT'
    multi_linestring: ClassVar[str] = 'MULTILINESTRING'
    multi_polygon: ClassVar[str] = 'MULTIPOLYGON'
# End GeometryType class


class SQLFieldType(GeometryType):
    """
    SQL Field Types
    """
    boolean: ClassVar[str] = 'BOOLEAN'
    tinyint: ClassVar[str] = 'TINYINT'
    smallint: ClassVar[str] = 'SMALLINT'
    mediumint: ClassVar[str] = 'MEDIUMINT'
    integer: ClassVar[str] = 'INTEGER'
    float: ClassVar[str] = 'FLOAT'
    double: ClassVar[str] = 'DOUBLE'
    real: ClassVar[str] = 'REAL'
    text: ClassVar[str] = 'TEXT'
    blob: ClassVar[str] = 'BLOB'
    date: ClassVar[str] = 'DATE'
    timestamp: ClassVar[str] = 'TIMESTAMP'
    datetime: ClassVar[str] = 'DATETIME'
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


class MetadataScope:
    """
    Metadata Scope
    """
    undefined: ClassVar[str] = 'undefined'
    field_session: ClassVar[str] = 'fieldSession'
    collection_session: ClassVar[str] = 'collectionSession'
    series: ClassVar[str] = 'series'
    dataset: ClassVar[str] = 'dataset'
    feature_type: ClassVar[str] = 'featureType'
    feature: ClassVar[str] = 'feature'
    attribute_type: ClassVar[str] = 'attributeType'
    attribute: ClassVar[str] = 'attribute'
    tile: ClassVar[str] = 'tile'
    model: ClassVar[str] = 'model'
    catalog: ClassVar[str] = 'catalog'
    schema: ClassVar[str] = 'schema'
    taxonomy: ClassVar[str] = 'taxonomy'
    software: ClassVar[str] = 'software'
    service: ClassVar[str] = 'service'
    collection_hardware: ClassVar[str] = 'collectionHardware'
    non_geographic_dataset: ClassVar[str] = 'nonGeographicDataset'
    dimension_group: ClassVar[str] = 'dimensionGroup'
    style: ClassVar[str] = 'style'
# End MetadataScope class


class MetadataReferenceScope:
    """
    Metadata Reference Scope
    """
    geopackage: ClassVar[str] = 'geopackage'
    table: ClassVar[str] = 'table'
    column: ClassVar[str] = 'column'
    row: ClassVar[str] = 'row'
    row_col: ClassVar[str] = 'row/col'
# End MetadataReferenceScope class


if __name__ == '__main__':
    pass
