# -*- coding: utf-8 -*-
"""
Geopackage
"""


from datetime import datetime
from math import nan
from os import PathLike
from pathlib import Path
from sqlite3 import (
    Connection, PARSE_COLNAMES, PARSE_DECLTYPES, connect, register_adapter,
    register_converter)
from typing import Dict, List, Optional, Tuple, Type, Union

from fudgeo.enumeration import (
    DataType, GPKGFlavors, GeometryType, SQLFieldType)
from fudgeo.geometry import (
    Point, PointZ, PointM, PointZM, MultiPoint, MultiPointZ, MultiPointM,
    MultiPointZM, LineString, LineStringZ, LineStringM, LineStringZM,
    MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM,
    Polygon, PolygonZ, MultiPolygon, MultiPolygonZ)
from fudgeo.sql import (
    CHECK_SRS_EXISTS, CREATE_FEATURE_TABLE, CREATE_TABLE, DEFAULT_EPSG_RECS,
    DEFAULT_ESRI_RECS, GPKG_OGR_CONTENTS_DELETE_TRIGGER,
    GPKG_OGR_CONTENTS_INSERT_TRIGGER, INSERT_GPKG_CONTENTS_SHORT,
    INSERT_GPKG_GEOM_COL, INSERT_GPKG_OGR_CONTENTS, INSERT_GPKG_SRS,
    SELECT_EXTENT, SELECT_HAS_ZM, SELECT_SRS, SELECT_TABLES_BY_TYPE,
    TABLE_EXISTS, UPDATE_EXTENT)


FIELDS = Union[Tuple['Field', ...], List['Field']]


COMMA_SPACE = ', '
GPKG_EXT = '.gpkg'
SHAPE = 'SHAPE'


def _now() -> str:
    """
    Formatted Now
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
# End _now method


def _adapt_geometry(val) -> bytes:
    """
    Adapt Geometry to Geopackage
    """
    return val.to_gpkg()
# End _adapt_geometry function


def _register_geometry():
    """
    Register adapters and converters for geometry / geopackage
    """
    classes = (
        Point, PointZ, PointM, PointZM, MultiPoint, MultiPointZ, MultiPointM,
        MultiPointZM, LineString, LineStringZ, LineStringM, LineStringZM,
        MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM,
        Polygon, PolygonZ, MultiPolygon, MultiPolygonZ)
    for cls in classes:
        register_adapter(cls, _adapt_geometry)
        register_converter(cls.__name__, cls.from_gpkg)
# End _register_geometry function


class GeoPackage:
    """
    GeoPackage
    """
    def __init__(self, path: Union[PathLike, str]) -> None:
        """
        Initialize the GeoPackage class
        """
        super().__init__()
        self._path: Path = Path(path)
        self._conn: Connection = connect(
            str(path), isolation_level='EXCLUSIVE',
            detect_types=PARSE_DECLTYPES | PARSE_COLNAMES)
        _register_geometry()
    # End init built-in

    @property
    def path(self) -> Path:
        """
        Path
        """
        return self._path
    # End path property

    @property
    def connection(self) -> Connection:
        """
        Connection
        """
        return self._conn
    # End connection property

    @classmethod
    def create(cls, path: Union[PathLike, str],
               flavor: str = GPKGFlavors.esri) -> 'GeoPackage':
        """
        Create a new GeoPackage
        """
        path = Path(path).with_suffix(GPKG_EXT)
        if path.is_file():
            raise ValueError(f'GeoPackage already exists: {path}')
        if not path.parent.is_dir():
            raise ValueError(f'Folder does not exist: {path.parent}')
        if flavor == GPKGFlavors.esri:
            defaults = DEFAULT_ESRI_RECS
        else:
            defaults = DEFAULT_EPSG_RECS
        with connect(str(path), isolation_level='EXCLUSIVE') as conn:
            with Path(__file__).parent.joinpath('geopkg.sql').open() as fin:
                conn.executescript(fin.read())
            conn.executemany(INSERT_GPKG_SRS, defaults)
        return cls(path)
    # End create method

    def check_srs_exists(self, srs_id: int) -> bool:
        """
        Check if a SpatialReferenceSystem already exists in the table.
        This is done purely by srs id because that is all ESRI looks at.
        """
        cursor = self._conn.execute(CHECK_SRS_EXISTS, (srs_id,))
        return bool(cursor.fetchall())
    # End check_srs_exists method

    def _check_table_exists(self, table_name: str) -> bool:
        """
        Check existence of table
        """
        cursor = self._conn.execute(TABLE_EXISTS, (table_name,))
        return bool(cursor.fetchall())
    # End _check_table_exists method

    def _validate_inputs(self, fields: FIELDS, name: str) -> FIELDS:
        """
        Validate Inputs
        """
        if not fields:
            fields = ()
        if self._check_table_exists(name):
            raise ValueError(f'Table {name} already exists in {self._path}')
        return fields
    # End _validate_inputs method

    def create_feature_class(self, name: str, srs: 'SpatialReferenceSystem',
                             shape_type: str = GeometryType.point,
                             z_enabled: bool = False, m_enabled: bool = False,
                             fields: FIELDS = (),
                             description: str = '') -> 'FeatureClass':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name)
        return FeatureClass.create(
            geopackage=self, name=name, shape_type=shape_type, srs=srs,
            z_enabled=z_enabled, m_enabled=m_enabled, fields=fields,
            description=description)
    # End create_feature_class method

    def create_table(self, name: str, fields: FIELDS = (),
                     description: str = '') -> 'Table':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name)
        return Table.create(
            geopackage=self, name=name, fields=fields, description=description)
    # End create_feature_class method

    @property
    def tables(self) -> Dict[str, 'Table']:
        """
        Tables in the GeoPackage
        """
        # noinspection PyTypeChecker
        return self._get_table_objects(Table, DataType.attributes)
    # End tables property

    @property
    def feature_classes(self) -> Dict[str, 'FeatureClass']:
        """
        Feature Classes in the GeoPackage
        """
        # noinspection PyTypeChecker
        return self._get_table_objects(FeatureClass, DataType.features)
    # End feature_classes property

    def _get_table_objects(self, cls: Type['BaseTable'],
                           data_type: str) -> Dict[str, 'BaseTable']:
        """
        Get Table Objects
        """
        cursor = self.connection.execute(
            SELECT_TABLES_BY_TYPE, (data_type,))
        return {name: cls(self, name) for name, in cursor.fetchall()}
    # End _get_table_objects method
# End GeoPackage class


class BaseTable:
    """
    Base Geopackage Table
    """
    def __init__(self, geopackage: GeoPackage, name: str) -> None:
        """
        Initialize the BaseTable class
        """
        super().__init__()
        self.geopackage: GeoPackage = geopackage
        self.name: str = name
    # End init built-in
# End BaseTable class


class Table(BaseTable):
    """
    GeoPackage Table
    """
    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, fields: FIELDS,
               description: str = '') -> 'Table':
        """
        Create a regular non-spatial table in the geopackage
        """
        cols = f', {", ".join(repr(f) for f in fields)}' if fields else ''
        with geopackage.connection as conn:
            conn.execute(CREATE_TABLE.format(name=name, other_fields=cols))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.attributes, name, description, _now(), None))
            conn.execute(INSERT_GPKG_OGR_CONTENTS, (name, 0))
            conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.format(name))
            conn.execute(GPKG_OGR_CONTENTS_DELETE_TRIGGER.format(name))
        return cls(geopackage=geopackage, name=name)
    # End create_table method
# End Table class


class FeatureClass(BaseTable):
    """
    GeoPackage Feature Class
    """
    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, shape_type: str,
               srs: 'SpatialReferenceSystem', z_enabled: bool = False,
               m_enabled: bool = False, fields: FIELDS = (),
               description: str = '') -> 'FeatureClass':
        """
        Create Feature Class
        """
        cols = f', {", ".join(repr(f) for f in fields)}' if fields else ''
        with geopackage.connection as conn:
            conn.execute(CREATE_FEATURE_TABLE.format(
                name=name, feature_type=shape_type, other_fields=cols))
            if not geopackage.check_srs_exists(srs.srs_id):
                conn.execute(INSERT_GPKG_SRS, srs.as_record())
            conn.execute(INSERT_GPKG_GEOM_COL,
                         (name, SHAPE, shape_type, srs.srs_id,
                          int(z_enabled), int(m_enabled)))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.features, name, description, _now(), srs.srs_id))
            conn.execute(INSERT_GPKG_OGR_CONTENTS, (name, 0))
            conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.format(name))
            conn.execute(GPKG_OGR_CONTENTS_DELETE_TRIGGER.format(name))
        return cls(geopackage=geopackage, name=name)
    # End create method

    @property
    def spatial_reference_system(self) -> 'SpatialReferenceSystem':
        """
        Spatial Reference System
        """
        cursor = self.geopackage.connection.execute(SELECT_SRS, (self.name,))
        return SpatialReferenceSystem(*cursor.fetchone())
    # End spatial_reference_system property

    @property
    def has_z(self) -> bool:
        """
        Has Z
        """
        cursor = self.geopackage.connection.execute(
            SELECT_HAS_ZM, (self.name,))
        z, _ = cursor.fetchone()
        return bool(z)
    # End has_z property

    @property
    def has_m(self) -> bool:
        """
        Has M
        """
        cursor = self.geopackage.connection.execute(
            SELECT_HAS_ZM, (self.name,))
        _, m = cursor.fetchone()
        return bool(m)
    # End has_m property

    @property
    def extent(self) -> Tuple[float, float, float, float]:
        """
        Extent property
        """
        empty = nan, nan, nan, nan
        cursor = self.geopackage.connection.execute(SELECT_EXTENT, (self.name,))
        result = cursor.fetchone()
        if not result:
            return empty
        if None in result:
            return empty
        return result

    @extent.setter
    def extent(self, value: Tuple[float, float, float, float]) -> None:
        if not isinstance(value, (tuple, list)):  # pragma: nocover
            raise ValueError('Please supply a tuple or list of values')
        if not len(value) == 4:  # pragma: nocover
            raise ValueError('The tuple/list of values must have four values')
        with self.geopackage.connection as conn:
            conn.execute(UPDATE_EXTENT, tuple([*value, self.name]))
    # End extent property
# End FeatureClass class


class SpatialReferenceSystem:
    """
    Spatial Reference System
    """
    def __init__(self, name: str, organization: str, org_coord_sys_id: int,
                 definition: str, description: str = '') -> None:
        """
        Initialize the SpatialReferenceSystem class
        """
        super(SpatialReferenceSystem, self).__init__()
        self.name: str = name
        self.organization: str = organization
        self.org_coord_sys_id: int = org_coord_sys_id
        self._srs_id: int = org_coord_sys_id
        self.definition: str = definition
        self.description: str = description
    # End init built-in

    @property
    def srs_id(self) -> int:
        """
        Spatial Reference System ID
        """
        return self._srs_id

    @srs_id.setter
    def srs_id(self, value: int) -> None:
        self._srs_id = value
    # End srs_id property

    def as_record(self) -> Tuple[str, int, str, int, str, str]:
        """
        Record of the Spatial Reference System
        """
        return (self.name, self.srs_id, self.organization,
                self.org_coord_sys_id, self.definition, self.description)
    # End as_record method
# End SpatialReferenceSystem class


class Field:
    """
    Field Object for GeoPackage
    """
    def __init__(self, name: str, data_type: str,
                 size: Optional[int] = None) -> None:
        """
        Initialize the Field class
        """
        super().__init__()
        self.name: str = name
        self.data_type: str = data_type
        self.size: Optional[int] = size
    # End init built-in

    def __repr__(self) -> str:
        """
        String representation
        """
        types = SQLFieldType.blob, SQLFieldType.text
        if self.size and self.data_type in types:
            return f'{self.name} {self.data_type}{self.size}'
        return f'{self.name} {self.data_type}'
    # End repr built-in
# End Field class


if __name__ == '__main__':
    pass
