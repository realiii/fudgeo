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
    attribute: ClassVar[str] = 'attribute'
    attribute_type: ClassVar[str] = 'attributeType'
    catalog: ClassVar[str] = 'catalog'
    collection_hardware: ClassVar[str] = 'collectionHardware'
    collection_session: ClassVar[str] = 'collectionSession'
    dataset: ClassVar[str] = 'dataset'
    dimension_group: ClassVar[str] = 'dimensionGroup'
    feature: ClassVar[str] = 'feature'
    feature_type: ClassVar[str] = 'featureType'
    field_session: ClassVar[str] = 'fieldSession'
    model: ClassVar[str] = 'model'
    non_geographic_dataset: ClassVar[str] = 'nonGeographicDataset'
    schema: ClassVar[str] = 'schema'
    series: ClassVar[str] = 'series'
    service: ClassVar[str] = 'service'
    software: ClassVar[str] = 'software'
    style: ClassVar[str] = 'style'
    taxonomy: ClassVar[str] = 'taxonomy'
    tile: ClassVar[str] = 'tile'
    undefined: ClassVar[str] = 'undefined'
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


class ConstraintType:
    """
    Constraint Type
    """
    enum: ClassVar[str] = 'enum'
    glob: ClassVar[str] = 'glob'
    range_: ClassVar[str] = 'range'
# End ConstraintType class


if __name__ == '__main__':  # pragma: no cover
    pass
