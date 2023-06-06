# -*- coding: utf-8 -*-
"""
Geopackage
"""


from datetime import datetime, timedelta, timezone
from math import nan
from os import PathLike
from pathlib import Path
from re import IGNORECASE, compile as recompile
from sqlite3 import (
    PARSE_COLNAMES, PARSE_DECLTYPES, connect,
    register_adapter, register_converter)
from typing import (
    Callable, Dict, List, Optional, TYPE_CHECKING, Tuple, Type, Union)

from fudgeo.enumeration import (
    DataType, GPKGFlavors, GeometryType, SQLFieldType)
from fudgeo.extension.ogr import add_ogr_contents, has_ogr_contents
from fudgeo.geometry import (
    Point, PointZ, PointM, PointZM, MultiPoint, MultiPointZ, MultiPointM,
    MultiPointZM, LineString, LineStringZ, LineStringM, LineStringZM,
    MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM,
    Polygon, PolygonZ, PolygonM, PolygonZM, MultiPolygon, MultiPolygonZ,
    MultiPolygonM, MultiPolygonZM)
from fudgeo.extension.spatial import ST_FUNCS, add_spatial_index
from fudgeo.sql import (
    CHECK_SRS_EXISTS, CREATE_FEATURE_TABLE, CREATE_OGR_CONTENTS, CREATE_TABLE,
    DEFAULT_EPSG_RECS, DEFAULT_ESRI_RECS, DELETE_METADATA_REFERENCE,
    DELETE_OGR_CONTENTS, INSERT_GPKG_CONTENTS_SHORT, INSERT_GPKG_GEOM_COL,
    INSERT_GPKG_SRS, REMOVE_FEATURE_CLASS, REMOVE_TABLE, SELECT_COUNT,
    SELECT_EXTENT, SELECT_GEOMETRY_COLUMN, SELECT_GEOMETRY_TYPE, SELECT_HAS_ZM,
    SELECT_PRIMARY_KEY, SELECT_SRS, SELECT_TABLES_BY_TYPE, TABLE_EXISTS,
    UPDATE_EXTENT)
from fudgeo.util import convert_datetime, escape_name, now


if TYPE_CHECKING:
    from sqlite3 import Connection, Cursor
    from fudgeo.geometry.base import AbstractGeometry


FIELDS = Union[Tuple['Field', ...], List['Field']]


def _adapt_geometry(val: 'AbstractGeometry') -> bytes:
    """
    Adapt Geometry to Geopackage
    """
    return val.to_gpkg()
# End _adapt_geometry function


def _register_geometry() -> None:
    """
    Register adapters and converters for geometry / geopackage
    """
    classes = (
        Point, PointZ, PointM, PointZM, MultiPoint, MultiPointZ, MultiPointM,
        MultiPointZM, LineString, LineStringZ, LineStringM, LineStringZM,
        MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM,
        Polygon, PolygonZ, PolygonM, PolygonZM, MultiPolygon, MultiPolygonZ,
        MultiPolygonM, MultiPolygonZM)
    for cls in classes:
        register_adapter(cls, _adapt_geometry)
        register_converter(cls.__name__, cls.from_gpkg)
# End _register_geometry function


def _add_st_functions(conn: 'Connection') -> None:
    """
    Add ST Functions
    """
    for name, func in ST_FUNCS.items():
        conn.create_function(name=name, narg=1, func=func)
# End _add_st_functions function


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
        self._conn: Optional['Connection'] = None
    # End init built-in

    def __repr__(self) -> str:
        """
        String Representation
        """
        return f'GeoPackage(path={self._path!r})'
    # End repr built-in

    @property
    def path(self) -> Path:
        """
        Path
        """
        return self._path
    # End path property

    @property
    def connection(self) -> 'Connection':
        """
        Connection
        """
        if self._conn is None:
            self._conn = connect(
                str(self._path), isolation_level='EXCLUSIVE',
                detect_types=PARSE_DECLTYPES | PARSE_COLNAMES)
            _register_geometry()
            _add_st_functions(self._conn)
            register_converter('timestamp', _convert_datetime)
            register_converter('datetime', _convert_datetime)
        return self._conn
    # End connection property

    @classmethod
    def create(cls, path: Union[PathLike, str],
               flavor: str = GPKGFlavors.esri,
               ogr_contents: bool = False) -> 'GeoPackage':
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
            if ogr_contents:
                conn.execute(CREATE_OGR_CONTENTS)
        return cls(path)
    # End create method

    def check_srs_exists(self, srs_id: int) -> bool:
        """
        Check if a SpatialReferenceSystem already exists in the table.
        This is done purely by srs id because that is all ESRI looks at.
        """
        cursor = self.connection.execute(CHECK_SRS_EXISTS, (srs_id,))
        return bool(cursor.fetchall())
    # End check_srs_exists method

    def _check_table_exists(self, table_name: str) -> bool:
        """
        Check existence of table
        """
        cursor = self.connection.execute(TABLE_EXISTS, (table_name,))
        return bool(cursor.fetchall())
    # End _check_table_exists method

    def _validate_inputs(self, fields: FIELDS, name: str,
                         overwrite: bool) -> FIELDS:
        """
        Validate Inputs
        """
        if not fields:
            fields = ()
        if not overwrite and self._check_table_exists(name):
            raise ValueError(f'Table {name} already exists in {self._path}')
        return fields
    # End _validate_inputs method

    def create_feature_class(self, name: str, srs: 'SpatialReferenceSystem',
                             shape_type: str = GeometryType.point,
                             z_enabled: bool = False, m_enabled: bool = False,
                             fields: FIELDS = (), description: str = '',
                             overwrite: bool = False,
                             spatial_index: bool = False) -> 'FeatureClass':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return FeatureClass.create(
            geopackage=self, name=name, shape_type=shape_type, srs=srs,
            z_enabled=z_enabled, m_enabled=m_enabled, fields=fields,
            description=description, overwrite=overwrite,
            spatial_index=spatial_index)
    # End create_feature_class method

    def create_table(self, name: str, fields: FIELDS = (),
                     description: str = '', overwrite: bool = False) -> 'Table':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return Table.create(
            geopackage=self, name=name, fields=fields,
            description=description, overwrite=overwrite)
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

    @staticmethod
    def _column_names(fields: FIELDS) -> str:
        """
        Column Names
        """
        if not fields:
            return ''
        return f'{COMMA_SPACE}{COMMA_SPACE.join(repr(f) for f in fields)}'
    # End _column_names method

    @staticmethod
    def _drop(conn: 'Connection', sql: str, name: str, escaped_name: str,
              geom_name: str, has_ogr_contents: bool) -> None:
        """
        Drop Table from Geopackage
        """
        conn.executescript(sql.format(name, escaped_name, geom_name))
        if has_ogr_contents:
            conn.execute(DELETE_OGR_CONTENTS.format(name))
    # End _drop method

    @property
    def count(self) -> int:
        """
        Number of records
        """
        cursor = self.geopackage.connection.execute(
            SELECT_COUNT.format(self.escaped_name))
        count, = cursor.fetchone()
        return count
    # End count property

    @property
    def escaped_name(self) -> str:
        """
        Escaped Name
        """
        return _escape_name(self.name)
    # End escaped_name property

    @property
    def primary_key_field(self) -> Optional['Field']:
        """
        Primary Key Field
        """
        cursor = self.geopackage.connection.execute(
            SELECT_PRIMARY_KEY.format(self.name, SQLFieldType.integer))
        result = cursor.fetchone()
        if not result:
            return
        return Field(*result)
    # End primary_key_field property

    @property
    def fields(self) -> List['Field']:
        """
        Fields
        """
        cursor = self.geopackage.connection.execute(
            f"""PRAGMA table_info({self.escaped_name})""")
        return [Field(name=name, data_type=type_)
                for _, name, type_, _, _, _ in cursor.fetchall()]
    # End fields property

    @property
    def field_names(self) -> List[str]:
        """
        Field Names
        """
        return [f.name for f in self.fields]
    # End field_names property
# End BaseTable class


class Table(BaseTable):
    """
    GeoPackage Table
    """
    def __repr__(self) -> str:
        """
        String Representation
        """
        return f'Table(geopackage={self.geopackage!r}, name={self.name!r})'
    # End repr built-in

    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, fields: FIELDS,
               description: str = '', overwrite: bool = False) -> 'Table':
        """
        Create a regular non-spatial table in the geopackage
        """
        cols = cls._column_names(fields)
        with geopackage.connection as conn:
            escaped_name = _escape_name(name)
            has_contents = has_ogr_contents(conn)
            if overwrite:
                cls._drop(conn=conn, sql=REMOVE_TABLE, geom_name='',
                          name=name, escaped_name=escaped_name,
                          has_ogr_contents=has_contents)
            conn.execute(CREATE_TABLE.format(
                name=escaped_name, other_fields=cols))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.attributes, name, description, _now(), None))
            if has_contents:
                add_ogr_contents(conn, name=name, escaped_name=escaped_name)
        return cls(geopackage=geopackage, name=name)
    # End create method

    def drop(self) -> None:
        """
        Drop table from Geopackage
        """
        with self.geopackage.connection as conn:
            self._drop(conn=conn, sql=REMOVE_TABLE, geom_name='',
                       name=self.name, escaped_name=self.escaped_name,
                       has_ogr_contents=has_ogr_contents(conn))
    # End drop method
# End Table class


class FeatureClass(BaseTable):
    """
    GeoPackage Feature Class
    """
    def __repr__(self) -> str:
        """
        String Representation
        """
        return (f'FeatureClass(geopackage={self.geopackage!r}, '
                f'name={self.name!r})')
    # End repr built-in

    @staticmethod
    def _find_geometry_column_name(geopackage: 'GeoPackage', name: str) -> str:
        """
        Find Geometry Column Name for an Existing Feature Class
        """
        sans_case = {k.casefold(): v
                     for k, v in geopackage.feature_classes.items()}
        existing = sans_case.get(name.casefold())
        if not existing:
            return ''
        return existing.geometry_column_name
    # End _find_geometry_column_name method

    def add_spatial_index(self) -> bool:
        """
        Add Spatial Index if does not already exist
        """
        if self.has_spatial_index:
            return False
        with self.geopackage.connection as conn:
            add_spatial_index(conn=conn, feature_class=self)
        return True
    # End add_spatial_index method

    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, shape_type: str,
               srs: 'SpatialReferenceSystem', z_enabled: bool = False,
               m_enabled: bool = False, fields: FIELDS = (),
               description: str = '', overwrite: bool = False,
               spatial_index: bool = False) -> 'FeatureClass':
        """
        Create Feature Class
        """
        cols = cls._column_names(fields)
        with geopackage.connection as conn:
            escaped_name = _escape_name(name)
            has_contents = has_ogr_contents(conn)
            if overwrite:
                geom_name = cls._find_geometry_column_name(geopackage, name)
                cls._drop(conn=conn, sql=REMOVE_FEATURE_CLASS,
                          name=name, escaped_name=escaped_name,
                          geom_name=geom_name,
                          has_ogr_contents=has_contents)
            conn.execute(CREATE_FEATURE_TABLE.format(
                name=escaped_name, feature_type=shape_type, other_fields=cols))
            if not geopackage.check_srs_exists(srs.srs_id):
                conn.execute(INSERT_GPKG_SRS, srs.as_record())
            conn.execute(INSERT_GPKG_GEOM_COL,
                         (name, SHAPE, shape_type, srs.srs_id,
                          int(z_enabled), int(m_enabled)))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.features, name, description, _now(), srs.srs_id))
            if has_contents:
                add_ogr_contents(conn, name=name, escaped_name=escaped_name)
            feature_class = cls(geopackage=geopackage, name=name)
            if spatial_index:
                add_spatial_index(conn=conn, feature_class=feature_class)
        return feature_class
    # End create method

    def drop(self) -> None:
        """
        Drop feature class from Geopackage
        """
        with self.geopackage.connection as conn:
            self._drop(conn=conn, sql=REMOVE_FEATURE_CLASS,
                       geom_name=self.geometry_column_name,
                       name=self.name, escaped_name=self.escaped_name,
                       has_ogr_contents=has_ogr_contents(conn))
    # End drop method

    @staticmethod
    def _check_result(cursor: 'Cursor') -> Optional[str]:
        """
        Check Result
        """
        result = cursor.fetchone()
        if not result:
            return
        if None in result:
            return
        value, = result
        return value
    # End _check_result method

    @property
    def geometry_column_name(self) -> Optional[str]:
        """
        Geometry Column Name
        """
        cursor = self.geopackage.connection.execute(
            SELECT_GEOMETRY_COLUMN, (self.name,))
        return self._check_result(cursor)
    # End geometry_column_name property

    @property
    def geometry_type(self) -> Optional[str]:
        """
        Geometry Type
        """
        cursor = self.geopackage.connection.execute(
            SELECT_GEOMETRY_TYPE, (self.name,))
        return self._check_result(cursor)
    # End geometry_type property

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
    def has_spatial_index(self) -> bool:
        """
        Has Spatial Index
        """
        table_name = f'rtree_{self.name}_{self.geometry_column_name}'
        cursor = self.geopackage.connection.execute(TABLE_EXISTS, (table_name,))
        return bool(cursor.fetchall())
    # End has_spatial_index property

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
                 definition: str, description: str = '',
                 srs_id: Optional[int] = None) -> None:
        """
        Initialize the SpatialReferenceSystem class
        """
        super(SpatialReferenceSystem, self).__init__()
        self.name: str = name
        self.organization: str = organization
        self.org_coord_sys_id: int = org_coord_sys_id
        self._srs_id: int = org_coord_sys_id if srs_id is None else srs_id
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

    @property
    def escaped_name(self) -> str:
        """
        Escaped Name, only adds quotes if needed
        """
        return _escape_name(self.name)
    # End escaped_name property

    def __repr__(self) -> str:
        """
        String representation
        """
        types = SQLFieldType.blob, SQLFieldType.text
        if self.size and self.data_type in types:
            return f'{self.escaped_name} {self.data_type}{self.size}'
        return f'{self.escaped_name} {self.data_type}'
    # End repr built-in
# End Field class


if __name__ == '__main__':
    pass
