# -*- coding: utf-8 -*-
"""
Geopackage
"""


from math import nan
from os import PathLike
from pathlib import Path
from sqlite3 import (
    PARSE_COLNAMES, PARSE_DECLTYPES, connect, register_adapter,
    register_converter)
from typing import Optional, TYPE_CHECKING, Type, Union

from fudgeo.alias import FIELDS, FIELD_NAMES, INT, STRING
from fudgeo.constant import COMMA_SPACE, GPKG_EXT, SHAPE
from fudgeo.enumeration import DataType, GPKGFlavors, GeometryType, SQLFieldType
from fudgeo.extension.metadata import (
    Metadata, add_metadata_extension, has_metadata_extension)
from fudgeo.extension.ogr import add_ogr_contents, has_ogr_contents
from fudgeo.extension.schema import (
    Schema, add_schema_extension, has_schema_extension)
from fudgeo.extension.spatial import ST_FUNCS, add_spatial_index
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiLineStringM, MultiLineStringZ, MultiLineStringZM, MultiPoint,
    MultiPointM, MultiPointZ, MultiPointZM, MultiPolygon, MultiPolygonM,
    MultiPolygonZ, MultiPolygonZM, Point, PointM, PointZ, PointZM, Polygon,
    PolygonM, PolygonZ, PolygonZM)
from fudgeo.sql import (
    CHECK_SRS_EXISTS, CREATE_FEATURE_TABLE, CREATE_OGR_CONTENTS, CREATE_TABLE,
    DEFAULT_EPSG_RECS, DEFAULT_ESRI_RECS, DELETE_DATA_COLUMNS,
    DELETE_METADATA_REFERENCE, DELETE_OGR_CONTENTS, INSERT_GPKG_CONTENTS_SHORT,
    INSERT_GPKG_GEOM_COL, INSERT_GPKG_SRS, REMOVE_FEATURE_CLASS, REMOVE_TABLE,
    SELECT_COUNT, SELECT_EXTENT, SELECT_GEOMETRY_COLUMN, SELECT_GEOMETRY_TYPE,
    SELECT_HAS_ZM, SELECT_PRIMARY_KEY, SELECT_SRS, SELECT_TABLES_BY_TYPE,
    TABLE_EXISTS, UPDATE_EXTENT)
from fudgeo.util import check_geometry_name, convert_datetime, escape_name, now


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection, Cursor
    from fudgeo.geometry.base import AbstractGeometry


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
            self._conn.execute("""PRAGMA foreign_keys = true""")
            _register_geometry()
            _add_st_functions(self._conn)
            register_converter('timestamp', convert_datetime)
            register_converter('datetime', convert_datetime)
        return self._conn
    # End connection property

    @classmethod
    def create(cls, path: Union[PathLike, str], flavor: str = GPKGFlavors.esri,
               ogr_contents: bool = False, enable_metadata: bool = False,
               enable_schema: bool = False) -> 'GeoPackage':
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
            if enable_metadata:
                add_metadata_extension(conn)
            if enable_schema:
                add_schema_extension(conn)
        return cls(path)
    # End create method

    def add_spatial_reference(self, srs: 'SpatialReferenceSystem') -> None:
        """
        Add Spatial Reference
        """
        if self.check_srs_exists(srs.srs_id):
            return
        with self.connection as conn:
            conn.execute(INSERT_GPKG_SRS, srs.as_record())
    # End add_spatial_reference method

    def check_srs_exists(self, srs_id: int) -> bool:
        """
        Check if a SpatialReferenceSystem already exists in the table.
        Done purely by srs id here but could be done via wkt on definition.
        """
        cursor = self.connection.execute(CHECK_SRS_EXISTS, (srs_id,))
        return bool(cursor.fetchall())
    # End check_srs_exists method

    def enable_metadata_extension(self) -> bool:
        """
        Enable Metadata Extension in the Geopackage.  Short circuit if
        already enabled.
        """
        if self.is_metadata_enabled:
            return True
        with self.connection as conn:
            add_metadata_extension(conn=conn)
        return True
    # End enable_metadata_extension method

    def enable_schema_extension(self) -> bool:
        """
        Enable Schema Extension in the Geopackage.  Short circuit if
        already enabled.
        """
        if self.is_schema_enabled:
            return True
        with self.connection as conn:
            add_schema_extension(conn=conn)
        return True
    # End enable_schema_extension method

    @property
    def is_metadata_enabled(self) -> bool:
        """
        Is Metadata Extension Enabled
        """
        return has_metadata_extension(self.connection)
    # End is_metadata_enabled property

    @property
    def is_schema_enabled(self) -> bool:
        """
        Is Schema Extension Enabled
        """
        return has_schema_extension(self.connection)
    # End is_schema_enabled property

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
                             spatial_index: bool = False,
                             geom_name: str = SHAPE) -> 'FeatureClass':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return FeatureClass.create(
            geopackage=self, name=name, shape_type=shape_type, srs=srs,
            z_enabled=z_enabled, m_enabled=m_enabled, fields=fields,
            description=description, overwrite=overwrite,
            spatial_index=spatial_index, geom_name=geom_name)
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
    def tables(self) -> dict[str, 'Table']:
        """
        Tables in the GeoPackage
        """
        # noinspection PyTypeChecker
        return self._get_table_objects(Table, DataType.attributes)
    # End tables property

    @property
    def feature_classes(self) -> dict[str, 'FeatureClass']:
        """
        Feature Classes in the GeoPackage
        """
        # noinspection PyTypeChecker
        return self._get_table_objects(FeatureClass, DataType.features)
    # End feature_classes property

    def _get_table_objects(self, cls: Type['BaseTable'],
                           data_type: str) -> dict[str, 'BaseTable']:
        """
        Get Table Objects
        """
        cursor = self.connection.execute(
            SELECT_TABLES_BY_TYPE, (data_type,))
        return {name: cls(self, name) for name, in cursor.fetchall()}
    # End _get_table_objects method

    @property
    def metadata(self) -> Optional[Metadata]:
        """
        Metadata for the Geopackage, None if Metadata extension not enabled.
        """
        if not self.is_metadata_enabled:
            return
        return Metadata(geopackage=self)
    # End metadata property

    @property
    def schema(self) -> Optional[Schema]:
        """
        Schema for the Geopackage, None if Schema extension not enabled.
        """
        if not self.is_schema_enabled:
            return
        return Schema(geopackage=self)
    # End schema property
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
              geom_name: str, delete_ogr_contents: bool,
              delete_metadata: bool, delete_schema: bool) -> None:
        """
        Drop Table from Geopackage
        """
        conn.executescript(sql.format(name, escaped_name, geom_name))
        if delete_ogr_contents:
            conn.execute(DELETE_OGR_CONTENTS.format(name))
        if delete_metadata:
            conn.execute(DELETE_METADATA_REFERENCE.format(name))
        if delete_schema:
            conn.execute(DELETE_DATA_COLUMNS.format(name))
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
        return escape_name(self.name)
    # End escaped_name property

    @property
    def primary_key_field(self) -> Optional['Field']:
        """
        Primary Key Field
        """
        cursor = self.geopackage.connection.execute(
            SELECT_PRIMARY_KEY.format(self.name, SQLFieldType.integer))
        result = cursor.fetchone()
        if not result:  # pragma: no cover
            return
        return Field(*result)
    # End primary_key_field property

    @property
    def fields(self) -> list['Field']:
        """
        Fields
        """
        cursor = self.geopackage.connection.execute(
            f"""PRAGMA table_info({self.escaped_name})""")
        return [Field(name=name, data_type=type_)
                for _, name, type_, _, _, _ in cursor.fetchall()]
    # End fields property

    @property
    def field_names(self) -> list[str]:
        """
        Field Names
        """
        return [f.name for f in self.fields]
    # End field_names property

    def _remove_special(self, fields: list['Field']) -> list['Field']:
        """
        Remove Special Fields
        """
        key_field = self.primary_key_field
        if key_field:
            while key_field in fields:
                fields.remove(key_field)
        return fields
    # End _remove_special method

    def _validate_fields(self, fields: Union[FIELDS, FIELD_NAMES]) -> list['Field']:
        """
        Validate Input Fields
        """
        keepers = []
        field_lookup = {f.name.casefold(): f for f in self.fields}
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        for f in fields:
            if not isinstance(f, (Field, str)):
                continue
            name = getattr(f, 'name', f).casefold()
            field = field_lookup.get(name)
            if field is None:
                continue
            keepers.append(field)
        return self._remove_special(keepers)
    # End _validate_fields method

    def _execute_select(self, field_names: str, where_clause: str,
                        limit: INT) -> 'Cursor':
        """
        Builds the SELECT statement and Executes, returning a cursor
        """
        # noinspection SqlNoDataSourceInspection
        sql = f"""SELECT {field_names} FROM {self.escaped_name}"""
        if where_clause:
            sql = f"""{sql} WHERE {where_clause}"""
        if limit and limit > 0:
            sql = f"""{sql} LIMIT {limit}"""
        return self.geopackage.connection.execute(sql)
    # End _execute_select method

    def _include_primary(self, fields: list['Field']) -> list['Field']:
        """
        Include Primary Field
        """
        key_field = self.primary_key_field
        if key_field:
            fields = [key_field, *fields]
        return fields
    # End _include_primary method
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
            escaped_name = escape_name(name)
            has_contents = has_ogr_contents(conn)
            if overwrite:
                cls._drop(conn=conn, sql=REMOVE_TABLE, geom_name='',
                          name=name, escaped_name=escaped_name,
                          delete_ogr_contents=has_contents,
                          delete_metadata=geopackage.is_metadata_enabled,
                          delete_schema=geopackage.is_schema_enabled)
            conn.execute(CREATE_TABLE.format(
                name=escaped_name, other_fields=cols))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.attributes, name, description, now(), None))
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
                       delete_ogr_contents=has_ogr_contents(conn),
                       delete_metadata=self.geopackage.is_metadata_enabled,
                       delete_schema=self.geopackage.is_schema_enabled)
    # End drop method

    def select(self, fields: Union[FIELDS, FIELD_NAMES] = (),
               where_clause: str = '', include_primary: bool = False,
               limit: INT = None) -> 'Cursor':
        """
        Builds a SELECT statement from fields, where clause, and options.
        Returns a cursor for the SELECT statement.

        The fail-over SELECT statement will return ROWID, this happens when
        no (valid) fields / field names provided and no primary key included
        or there is no primary key.
        """
        fields = self._validate_fields(fields)
        if include_primary:
            fields = self._include_primary(fields)
        if not fields:
            field_names = 'ROWID'
        else:
            field_names = COMMA_SPACE.join(f.escaped_name for f in fields)
        return self._execute_select(
            field_names=field_names, where_clause=where_clause, limit=limit)
    # End select method
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
               spatial_index: bool = False,
               geom_name: str = SHAPE) -> 'FeatureClass':
        """
        Create Feature Class
        """
        cols = cls._column_names(fields)
        with geopackage.connection as conn:
            escaped_name = escape_name(name)
            geom_name = check_geometry_name(geom_name)
            has_contents = has_ogr_contents(conn)
            if overwrite:
                current_name = cls._find_geometry_column_name(geopackage, name)
                cls._drop(
                    conn=conn, sql=REMOVE_FEATURE_CLASS, name=name,
                    escaped_name=escaped_name, geom_name=current_name,
                    delete_ogr_contents=has_contents,
                    delete_metadata=geopackage.is_metadata_enabled,
                    delete_schema=geopackage.is_schema_enabled)
            conn.execute(CREATE_FEATURE_TABLE.format(
                name=escaped_name, geom_name=geom_name,
                feature_type=shape_type, other_fields=cols))
            if not geopackage.check_srs_exists(srs.srs_id):
                conn.execute(INSERT_GPKG_SRS, srs.as_record())
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.features, name, description, now(), srs.srs_id))
            conn.execute(INSERT_GPKG_GEOM_COL,
                         (name, geom_name, shape_type, srs.srs_id,
                          int(z_enabled), int(m_enabled)))
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
                       delete_ogr_contents=has_ogr_contents(conn),
                       delete_metadata=self.geopackage.is_metadata_enabled,
                       delete_schema=self.geopackage.is_schema_enabled)
    # End drop method

    @staticmethod
    def _check_result(cursor: 'Cursor') -> STRING:
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
    def geometry_column_name(self) -> STRING:
        """
        Geometry Column Name
        """
        cursor = self.geopackage.connection.execute(
            SELECT_GEOMETRY_COLUMN, (self.name,))
        return self._check_result(cursor)
    # End geometry_column_name property

    @property
    def geometry_type(self) -> STRING:
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
    def spatial_index_name(self) -> STRING:
        """
        Spatial Index Name (escaped) if present, None otherwise
        """
        if not self.has_spatial_index:
            return
        return escape_name(self._spatial_index_name)
    # End spatial_index_name property

    @property
    def _spatial_index_name(self) -> str:
        """
        Spatial Index Name
        """
        return f'rtree_{self.name}_{self.geometry_column_name}'
    # End _spatial_index_name property

    @property
    def has_spatial_index(self) -> bool:
        """
        Has Spatial Index
        """
        cursor = self.geopackage.connection.execute(
            TABLE_EXISTS, (self._spatial_index_name,))
        return bool(cursor.fetchall())
    # End has_spatial_index property

    @property
    def extent(self) -> tuple[float, float, float, float]:
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
    def extent(self, value: tuple[float, float, float, float]) -> None:
        if not isinstance(value, (tuple, list)):  # pragma: nocover
            raise ValueError('Please supply a tuple or list of values')
        if not len(value) == 4:  # pragma: nocover
            raise ValueError('The tuple/list of values must have four values')
        with self.geopackage.connection as conn:
            conn.execute(UPDATE_EXTENT, tuple([*value, self.name]))
    # End extent property

    def _remove_special(self, fields: list['Field']) -> list['Field']:
        """
        Remove Special Fields
        """
        fields = super()._remove_special(fields)
        geom_name = (self.geometry_column_name or '').casefold()
        if geom_name:
            fields = [f for f in fields if f.name.casefold() != geom_name]
        return fields
    # End _remove_special method

    def select(self, fields: Union[FIELDS, FIELD_NAMES] = (),
               where_clause: str = '', include_geometry: bool = True,
               include_primary: bool = False, limit: INT = None) -> 'Cursor':
        """
        Builds a SELECT statement from fields, where clause, and options.
        Returns a cursor for the SELECT statement.

        The fail-over SELECT statement will return ROWID, this happens when
        no (valid) fields / field names provided, no primary key included
        or there is no primary key, and no geometry included.
        """
        fields = self._validate_fields(fields)
        if include_primary:
            fields = self._include_primary(fields)
        field_names = COMMA_SPACE.join(f.escaped_name for f in fields)
        if include_geometry:
            geom = f'{self.geometry_column_name} "[{self.geometry_type}]"'
            if field_names:
                field_names = f'{geom}{COMMA_SPACE}{field_names}'
            else:
                field_names = geom
        if not field_names:
            field_names = 'ROWID'
        return self._execute_select(
            field_names=field_names, where_clause=where_clause, limit=limit)
    # End select method
# End FeatureClass class


class SpatialReferenceSystem:
    """
    Spatial Reference System
    """
    def __init__(self, name: str, organization: str, org_coord_sys_id: int,
                 definition: str, description: str = '',
                 srs_id: INT = None) -> None:
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

    def as_record(self) -> tuple[str, int, str, int, str, str]:
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
    def __init__(self, name: str, data_type: str, size: INT = None) -> None:
        """
        Initialize the Field class
        """
        super().__init__()
        self.name: str = name
        self.data_type: str = data_type
        self.size: INT = size
    # End init built-in

    def __repr__(self) -> str:
        """
        String representation
        """
        types = SQLFieldType.blob, SQLFieldType.text
        if self.size and self.data_type in types:
            return f'{self.escaped_name} {self.data_type}{self.size}'
        return f'{self.escaped_name} {self.data_type}'
    # End repr built-in

    def __eq__(self, other: 'Field') -> bool:
        """
        Equality Implementation
        """
        if not isinstance(other, Field):
            return NotImplemented
        return repr(self).casefold() == repr(other).casefold()
    # End eq built-int

    @property
    def escaped_name(self) -> str:
        """
        Escaped Name, only adds quotes if needed
        """
        return escape_name(self.name)
    # End escaped_name property
# End Field class


if __name__ == '__main__':  # pragma: no cover
    pass
