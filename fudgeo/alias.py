# -*- coding: utf-8 -*-
"""
Type Hint Aliases
"""


from datetime import datetime
from typing import Optional, TYPE_CHECKING, Union


if TYPE_CHECKING:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from fudgeo.geopkg import FeatureClass, Field, Table
    # noinspection PyUnresolvedReferences
    from fudgeo.extension.metadata import (
        GeoPackageReference, TableReference, ColumnReference,
        RowReference, RowColumnReference)
    # noinspection PyUnresolvedReferences
    from fudgeo.extension.schema import (
        EnumerationConstraint, GlobConstraint, RangeConstraint)
    # noinspection PyUnresolvedReferences
    from fudgeo.geometry.linestring import (
        LineString, LineStringZ, LineStringM, LineStringZM)
    # noinspection PyUnresolvedReferences
    from fudgeo.geometry.polygon import (
        LinearRing, LinearRingZ, LinearRingM, LinearRingZM,
        Polygon, PolygonZ, PolygonM, PolygonZM)


INT = Optional[int]
BOOL = Optional[bool]
DATE = Optional[datetime]
FLOAT = Optional[float]
STRING = Optional[str]
BYTE_ARRAY = Optional[bytearray]


TABLE = Union['Table', 'FeatureClass']
FIELDS = Union[tuple['Field', ...], list['Field']]
FIELD_NAMES = Union[tuple[str, ...], list[str]]


REFERENCE_RECORD = tuple[
    str, STRING, STRING, INT, datetime, int, INT]
REFERENCE = Union[
    'GeoPackageReference', 'TableReference', 'ColumnReference',
    'RowReference', 'RowColumnReference']
REFERENCES = Union[REFERENCE, tuple[REFERENCE, ...], list[REFERENCE]]


RECORDS = list[
    tuple[str, str, STRING, FLOAT, INT, FLOAT, INT, STRING]]
CONSTRAINT = Union[
    'EnumerationConstraint', 'GlobConstraint', 'RangeConstraint']
CONSTRAINTS = Union[
    CONSTRAINT, list[CONSTRAINT], tuple[CONSTRAINT, ...]]


NONES = tuple[None, None, None, None]
DOUBLE = tuple[float, float]
TRIPLE = tuple[float, float, float]
QUADRUPLE = tuple[float, float, float, float]
COORDINATES = Union[list[DOUBLE], list[TRIPLE], list[QUADRUPLE]]


GEOMS = Union[
    list['LineString'], list['LinearRing'], list['Polygon']]
GEOMS_Z = Union[
    list['LineStringZ'], list['LinearRingZ'], list['PolygonZ']]
GEOMS_M = Union[
    list['LineStringM'], list['LinearRingM'], list['PolygonM']]
GEOMS_ZM = Union[
    list['LineStringZM'], list['LinearRingZM'], list['PolygonZM']]


if __name__ == '__main__':  # pragma: no cover
    pass
