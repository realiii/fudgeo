# -*- coding: utf-8 -*-
"""
Geopackage
"""


from abc import ABCMeta, abstractmethod
from math import isnan, nan
from operator import itemgetter
from os import PathLike
from pathlib import Path
from sqlite3 import (
    PARSE_COLNAMES, PARSE_DECLTYPES, connect, register_adapter,
    register_converter)
from typing import Any, Optional, TYPE_CHECKING, Type, Union

# noinspection PyPackageRequirements
from numpy import int16, int32, int64, int8, uint16, uint32, uint64, uint8

from fudgeo.alias import FIELDS, FIELD_NAMES, INT, STRING
from fudgeo.constant import (
    COMMA_SPACE, FETCH_SIZE, FID, GPKG_EXT, MEMORY, SHAPE, SRS)
from fudgeo.context import ExecuteMany, ForeignKeys
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
    ADD_COLUMN, CHECK_SRS_EXISTS, CREATE_FEATURE_TABLE, CREATE_OGR_CONTENTS,
    CREATE_TABLE, DEFAULT_EPSG_RECS, DEFAULT_ESRI_RECS, DELETE_DATA_COLUMNS,
    DELETE_METADATA_REFERENCE, DELETE_OGR_CONTENTS, DROP_COLUMN,
    INSERT_GPKG_CONTENTS_SHORT, INSERT_GPKG_GEOM_COL, INSERT_GPKG_SRS,
    REMOVE_FEATURE_CLASS, REMOVE_OGR, REMOVE_TABLE, RENAME_DATA_COLUMNS,
    RENAME_FEATURE_CLASS, RENAME_METADATA_REFERENCE, RENAME_TABLE, SELECT_COUNT,
    SELECT_DATA_TYPE_AND_NAME, SELECT_DESCRIPTION, SELECT_EXTENT,
    SELECT_GEOMETRY_COLUMN, SELECT_GEOMETRY_TYPE, SELECT_HAS_ROWS,
    SELECT_HAS_ZM, SELECT_PRIMARY_KEY, SELECT_SPATIAL_REFERENCES, SELECT_SRS,
    SELECT_TABLES_BY_TYPE, TABLE_EXISTS, UPDATE_EXTENT,
    UPDATE_GPKG_OGR_CONTENTS)
from fudgeo.util import (
    check_geometry_name, check_primary_name, convert_datetime, escape_name,
    get_extent, now)


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


def _register_numpy_integers() -> None:
    """
    Register numpy integers
    """
    for int_type in (int8, int16, int32, int64,
                     uint8, uint16, uint32, uint64):
        register_adapter(int_type, int)
# End _register_numpy_integers function


def _add_st_functions(conn: 'Connection') -> None:
    """
    Add ST Functions
    """
    for name, func in ST_FUNCS.items():
        conn.create_function(name=name, narg=1, func=func)
# End _add_st_functions function


class AbstractGeoPackage(metaclass=ABCMeta):
    """
    Abstract GeoPackage
    """
    def __init__(self, path: Union[PathLike, str]) -> None:
        """
        Initialize the AbstractGeoPackage class
        """
        super().__init__()
        self._path: Union[Path, str] = path
        self._conn: Optional['Connection'] = None
    # End init built-in

    def __getitem__(self, item: str) -> Optional[Union['Table', 'FeatureClass']]:
        """
        Get Item
        """
        cursor = self.connection.execute(SELECT_DATA_TYPE_AND_NAME, (item,))
        if not (result := cursor.fetchone()):
            return None
        if None in result:
            return None
        data_type, name = result
        if data_type == DataType.attributes:
            return Table(geopackage=self, name=name)
        elif data_type == DataType.features:
            return FeatureClass(geopackage=self, name=name)
        return None
    # End get_item built-in

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
        if not overwrite and self.exists(name):
            raise ValueError(f'Table {name} already exists in {self.path}')
        return fields
    # End _validate_inputs method

    def _get_table_objects(self, cls: Type['BaseTable'],
                           data_type: str) -> dict[str, 'BaseTable']:
        """
        Get Table Objects
        """
        cursor = self.connection.execute(
            SELECT_TABLES_BY_TYPE, (data_type,))
        return {name: cls(self, name) for name, in cursor.fetchall()}
    # End _get_table_objects method

    def _configure_connection(self, db: str) -> None:
        """
        Configure Connection
        """
        conn = connect(
            db, isolation_level='EXCLUSIVE',
            detect_types=PARSE_DECLTYPES | PARSE_COLNAMES)
        self._register_functions(conn)
        self._conn = conn
    # End _configure_connection method

    @staticmethod
    def _register_functions(connection: 'Connection') -> None:
        """
        Register Functions / Functionality
        """
        connection.execute("""PRAGMA foreign_keys = true""")
        _register_geometry()
        _register_numpy_integers()
        _add_st_functions(connection)
        register_converter('timestamp', convert_datetime)
        register_converter('datetime', convert_datetime)
    # End _register_functions method

    @property
    @abstractmethod
    def path(self) -> Union[Path, str]:
        """
        Path
        """
        pass
    # End path property

    @property
    def connection(self) -> 'Connection':
        """
        Connection
        """
        if self._conn is None:
            self._configure_connection(str(self.path))
        return self._conn
    # End connection property

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

    @abstractmethod
    def exists(self, table_name: str) -> bool:
        """
        Check if the table exists in the GeoPackage
        """
        pass
    # End exists method

    def create_feature_class(self, name: str, srs: 'SpatialReferenceSystem',
                             shape_type: str = GeometryType.point,
                             z_enabled: bool = False, m_enabled: bool = False,
                             fields: FIELDS = (), description: str = '',
                             overwrite: bool = False,
                             spatial_index: bool = False,
                             geom_name: str = SHAPE,
                             pk_name: STRING = FID) -> 'FeatureClass':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return FeatureClass.create(
            geopackage=self, name=name, shape_type=shape_type, srs=srs,
            z_enabled=z_enabled, m_enabled=m_enabled, fields=fields,
            description=description, overwrite=overwrite,
            spatial_index=spatial_index, geom_name=geom_name, pk_name=pk_name)
    # End create_feature_class method

    def create_table(self, name: str, fields: FIELDS = (),
                     description: str = '', overwrite: bool = False,
                     pk_name: STRING = FID) -> 'Table':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return Table.create(
            geopackage=self, name=name, fields=fields,
            description=description, overwrite=overwrite, pk_name=pk_name)
    # End create_feature_class method

    @property
    def tables(self) -> dict[str, 'Table']:
        """
        Tables in the GeoPackage
        """
        return self._get_table_objects(
            Table, data_type=DataType.attributes)
    # End tables property

    @property
    def feature_classes(self) -> dict[str, 'FeatureClass']:
        """
        Feature Classes in the GeoPackage
        """
        return self._get_table_objects(
            FeatureClass, data_type=DataType.features)
    # End feature_classes property

    @property
    def spatial_references(self) -> dict[int, 'SpatialReferenceSystem']:
        """
        Spatial References in the GeoPackage
        """
        cursor = self.connection.execute(SELECT_SPATIAL_REFERENCES)
        references = [SpatialReferenceSystem(*record)
                      for record in cursor.fetchall()]
        return {srs.srs_id: srs for srs in references}
    # End spatial_references property

    @property
    def metadata(self) -> Optional[Metadata]:
        """
        Metadata for the Geopackage, None if Metadata extension not enabled.
        """
        if not self.is_metadata_enabled:
            return None
        return Metadata(geopackage=self)
    # End metadata property

    @property
    def schema(self) -> Optional[Schema]:
        """
        Schema for the Geopackage, None if Schema extension not enabled.
        """
        if not self.is_schema_enabled:
            return None
        return Schema(geopackage=self)
    # End schema property

    @staticmethod
    def _build_geopackage(path: str, flavor: str, ogr_contents: bool,
                          enable_metadata: bool, enable_schema: bool) \
            -> 'Connection':
        """
        Build Geopackage Structure and Return a Connection
        """
        if flavor == GPKGFlavors.esri:
            defaults = DEFAULT_ESRI_RECS
        else:
            defaults = DEFAULT_EPSG_RECS
        with connect(path, isolation_level='EXCLUSIVE',
                     detect_types=PARSE_DECLTYPES | PARSE_COLNAMES) as conn:
            with Path(__file__).parent.joinpath('geopkg.sql').open() as fin:
                conn.executescript(fin.read())
            conn.executemany(INSERT_GPKG_SRS, defaults)
            if ogr_contents:
                conn.execute(CREATE_OGR_CONTENTS)
            if enable_metadata:
                add_metadata_extension(conn)
            if enable_schema:
                add_schema_extension(conn)
        return conn
    # End _build_geopackage method
# End AbstractGeoPackage class


class GeoPackage(AbstractGeoPackage):
    """
    GeoPackage
    """
    def __init__(self, path: Union[PathLike, str]) -> None:
        """
        Initialize the GeoPackage class
        """
        super().__init__(Path(path))
    # End init built-in

    def __repr__(self) -> str:
        """
        String Representation
        """
        return f'GeoPackage(path={self.path!r})'
    # End repr built-in

    @property
    def path(self) -> Path:
        """
        Path
        """
        return self._path
    # End path property

    def exists(self, table_name: str) -> bool:
        """
        Check if the table exists in the GeoPackage
        """
        if not table_name:
            return False
        if not self.path.is_file():
            return False
        return self._check_table_exists(table_name)
    # End exists method

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
        cls._build_geopackage(
            path=str(path), flavor=flavor, ogr_contents=ogr_contents,
            enable_metadata=enable_metadata, enable_schema=enable_schema)
        return cls(path)
    # End create method
# End GeoPackage class


class MemoryGeoPackage(AbstractGeoPackage):
    """
    In Memory GeoPackage
    """
    def __init__(self) -> None:
        """
        Initialize the MemoryGeoPackage class
        """
        super().__init__(MEMORY)
    # End init built-in

    @property
    def connection(self) -> Optional['Connection']:
        """
        Connection
        """
        return self._conn

    @connection.setter
    def connection(self, value: 'Connection') -> None:
        self._conn = value
    # End connection property

    @property
    def path(self) -> str:
        """
        Path
        """
        return MEMORY
    # End path property

    def exists(self, table_name: str) -> bool:
        """
        Check if the table exists in the GeoPackage
        """
        if not table_name:
            return False
        if self.path != MEMORY:
            return False
        return self._check_table_exists(table_name)
    # End exists method

    # noinspection PyUnusedLocal
    @classmethod
    def create(cls, path: str = MEMORY, flavor: str = GPKGFlavors.esri,
               ogr_contents: bool = False, enable_metadata: bool = False,
               enable_schema: bool = False) -> 'MemoryGeoPackage':
        """
        Create a new Memory based GeoPackage
        """
        conn = cls._build_geopackage(
            path=MEMORY, flavor=flavor, ogr_contents=ogr_contents,
            enable_metadata=enable_metadata, enable_schema=enable_schema)
        gpkg = cls()
        gpkg.connection = conn
        gpkg._register_functions(conn)
        return gpkg
    # End create method
# End MemoryGeoPackage class


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

    def __bool__(self) -> bool:
        """
        Boolean
        """
        return self.exists
    # End bool built-in

    def __len__(self) -> int:
        """
        Length
        """
        return self.count
    # End len built-in

    @staticmethod
    def _column_names_types(fields: FIELDS) -> str:
        """
        Column Names and Types
        """
        if not fields:
            return ''
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        return f'{COMMA_SPACE}{COMMA_SPACE.join(repr(f) for f in fields)}'
    # End _column_names_types method

    @staticmethod
    def _drop(conn: 'Connection', sql: str, name: str, escaped_name: str,
              geom_name: str, has_ogr: bool, has_meta: bool,
              has_schema: bool) -> None:
        """
        Drop Table from Geopackage
        """
        conn.executescript(sql.format(name, escaped_name, geom_name))
        if has_ogr:
            conn.execute(DELETE_OGR_CONTENTS.format(name))
        if has_meta:
            conn.execute(DELETE_METADATA_REFERENCE.format(name))
        if has_schema:
            conn.execute(DELETE_DATA_COLUMNS.format(name))
    # End _drop method

    def _rename(self, conn: 'Connection', sql: str, new_name: str,
                escaped_new_name, has_ogr: bool) -> None:
        """
        Rename Table or Feature Class
        """
        count = 0
        if has_ogr:
            conn.executescript(REMOVE_OGR.format(self.name))
            count = self.count
        with ForeignKeys(conn):
            conn.executescript(sql.format(
                self.name, self.escaped_name,
                getattr(self, 'geometry_column_name', ''),
                new_name, escaped_new_name))
        if has_ogr:
            add_ogr_contents(
                conn=conn, name=new_name, escaped_name=escaped_new_name)
            conn.execute(UPDATE_GPKG_OGR_CONTENTS, (count, new_name))
        if self.geopackage.is_metadata_enabled:
            conn.execute(RENAME_METADATA_REFERENCE.format(new_name, self.name))
        if self.geopackage.is_schema_enabled:
            conn.execute(RENAME_DATA_COLUMNS.format(new_name, self.name))
        self.name = new_name
    # End _rename method

    @staticmethod
    def _check_result(cursor: 'Cursor') -> Any:
        """
        Check Result
        """
        if not (result := cursor.fetchone()):
            return None
        if None in result:
            return None
        value, = result
        return value
    # End _check_result method

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

    @staticmethod
    def _validate_overwrite(geopackage: GeoPackage, name: str,
                            overwrite: bool) -> None:
        """
        Validate Overwrite
        """
        if not overwrite and geopackage.exists(name):
            raise ValueError(
                f'Table {name} already exists in {geopackage.path}')
    # End _validate_overwrite method

    @staticmethod
    def _validate_same(source: 'BaseTable', target: 'BaseTable') -> None:
        """
        Validate Same Table
        """
        if source.name.casefold() != target.name.casefold():
            return
        if not isinstance(source.geopackage, type(target.geopackage)):
            return
        if isinstance(path := source.geopackage.path, Path):
            if not path.samefile(target.geopackage.path):
                return
        raise ValueError(f'Cannot copy table {source.name} to itself')
    # End _validate_same method

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
    def exists(self) -> bool:
        """
        True if the Table exists, False otherwise.
        """
        if not self.geopackage:
            return False
        return self.geopackage.exists(self.name)
    # End exists property

    @property
    def is_empty(self) -> bool:
        """
        True if there are rows in the table / features in the feature class
        """
        cursor = self.geopackage.connection.execute(
            SELECT_HAS_ROWS.format(self.escaped_name))
        result, = cursor.fetchone()
        return not bool(result)
    # End is_empty property

    @property
    def primary_key_field(self) -> Optional['Field']:
        """
        Primary Key Field
        """
        cursor = self.geopackage.connection.execute(
            SELECT_PRIMARY_KEY.format(self.name, SQLFieldType.integer))
        result = cursor.fetchone()
        if not result:  # pragma: no cover
            return None
        return Field(*result,  is_nullable=False)
    # End primary_key_field property

    @property
    def fields(self) -> list['Field']:
        """
        Fields
        """
        fields = []
        cursor = self.geopackage.connection.execute(
            f"""PRAGMA table_info({self.escaped_name})""")
        for _, name, type_, not_nullable, default, _ in cursor.fetchall():
            fields.append(Field(
                name=name, data_type=type_, is_nullable=not bool(not_nullable),
                default=default))
        return fields
    # End fields property

    @property
    def field_names(self) -> list[str]:
        """
        Field Names
        """
        return [f.name for f in self.fields]
    # End field_names property

    def add_fields(self, fields: FIELDS) -> bool:
        """
        Add Fields, requires field objects for full definition, does not
        support overwrite of existing fields.
        """
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        names = {n.casefold() for n in self.field_names}
        names.update([f.escaped_name.casefold() for f in self.fields])
        fields = [f for f in fields if
                  f.name.casefold() not in names and
                  f.escaped_name.casefold() not in names]
        if not fields:
            return False
        with self.geopackage.connection as conn:
            for field in fields:
                conn.execute(ADD_COLUMN.format(
                    self.escaped_name, repr(field)))
        return True
    # End add_fields method

    def drop_fields(self, fields: Union[FIELDS, FIELD_NAMES]) -> bool:
        """
        Drop Fields, can use field objects or field names.  Special fields
        cannot be removed using this method.  Removing fields which participate
        in indexes or foreign keys etc. may raise an exception.
        """
        if not (fields := self._validate_fields(fields)):
            return False
        with self.geopackage.connection as conn:
            for field in fields:
                conn.execute(DROP_COLUMN.format(
                    self.escaped_name, field.escaped_name))
        return True
    # End drop_fields method

    @property
    def description(self) -> STRING:
        """
        Description
        """
        cursor = self.geopackage.connection.execute(
            SELECT_DESCRIPTION, (self.name,))
        return self._check_result(cursor)
    # End description property
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

    def _make_copy_sql(self, target: 'Table', where_clause: str) \
            -> tuple[str, str]:
        """
        Make Copy SQL, INSERT and SELECT statements
        """
        fields = self._remove_special(self.fields)
        columns = COMMA_SPACE.join([f.escaped_name for f in fields])
        # noinspection SqlNoDataSourceInspection
        select_sql = f"""SELECT {columns} FROM {self.escaped_name}"""
        if where_clause:
            select_sql = f"""{select_sql} WHERE {where_clause}"""
        # noinspection SqlNoDataSourceInspection
        insert_sql = f"""INSERT INTO {target.escaped_name}({columns}) 
                         VALUES ({COMMA_SPACE.join('?' * len(fields))})"""
        return insert_sql, select_sql
    # End _make_copy_sql method

    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, fields: FIELDS,
               description: str = '', overwrite: bool = False,
               pk_name: STRING = FID) -> 'Table':
        """
        Create a regular non-spatial table in the geopackage
        """
        cls._validate_overwrite(geopackage, name=name, overwrite=overwrite)
        cols = cls._column_names_types(fields)
        with geopackage.connection as conn:
            escaped_name = escape_name(name)
            pk_name = check_primary_name(pk_name)
            has_ogr = has_ogr_contents(conn)
            if overwrite:
                cls._drop(
                    conn=conn, sql=REMOVE_TABLE, geom_name='', name=name,
                    escaped_name=escaped_name, has_ogr=has_ogr,
                    has_meta=geopackage.is_metadata_enabled,
                    has_schema=geopackage.is_schema_enabled)
            conn.execute(CREATE_TABLE.format(
                name=escaped_name, pk_name=pk_name, other_fields=cols))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.attributes, name, description, now(), None))
            if has_ogr:
                add_ogr_contents(conn, name=name, escaped_name=escaped_name)
        return cls(geopackage=geopackage, name=name)
    # End create method

    def drop(self) -> None:
        """
        Drop table from Geopackage
        """
        with self.geopackage.connection as conn:
            self._drop(
                conn=conn, sql=REMOVE_TABLE, geom_name='', name=self.name,
                escaped_name=self.escaped_name, has_ogr=has_ogr_contents(conn),
                has_meta=self.geopackage.is_metadata_enabled,
                has_schema=self.geopackage.is_schema_enabled)
    # End drop method

    def rename(self, name: str) -> None:
        """
        Rename Table
        """
        self._validate_overwrite(self.geopackage, name=name, overwrite=False)
        with self.geopackage.connection as conn:
            self._rename(
                conn=conn, sql=RENAME_TABLE, new_name=name,
                escaped_new_name=escape_name(name),
                has_ogr=has_ogr_contents(conn))
    # End rename method

    def copy(self, name: str, description: str = '',
             where_clause: str = '', overwrite: bool = False,
             geopackage: Optional[GeoPackage] = None) -> 'Table':
        """
        Copy the structure and content of a table.  Create a new table or
        overwrite an existing.  Use a where clause to limit the records.
        Output table can be in a different geopackage.
        """
        if not geopackage:
            geopackage = self.geopackage
        self._validate_same(source=self, target=Table(geopackage, name=name))
        self._validate_overwrite(geopackage, name=name, overwrite=overwrite)
        target = self.create(
            geopackage=geopackage, name=name,
            fields=self._remove_special(self.fields),
            description=description or self.description, overwrite=overwrite)
        insert_sql, select_sql = self._make_copy_sql(target, where_clause)
        cursor = self.geopackage.connection.execute(select_sql)
        with target.geopackage.connection as connection:
            while records := cursor.fetchmany(FETCH_SIZE):
                connection.executemany(insert_sql, records)
        return target
    # End copy method

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
        if existing is None:
            return ''
        return existing.geometry_column_name
    # End _find_geometry_column_name method

    @property
    def _spatial_index_name(self) -> str:
        """
        Spatial Index Name
        """
        return f'rtree_{self.name}_{self.geometry_column_name}'
    # End _spatial_index_name property

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

    def _make_copy_sql(self, target: 'FeatureClass', where_clause: str) \
            -> tuple[str, str]:
        """
        Make Copy SQL, INSERT and SELECT statements
        """
        target_geom = target.geometry_column_name
        source_geom = f'{self.geometry_column_name} "[{self.geometry_type}]"'
        fields = self._remove_special(self.fields)
        columns = COMMA_SPACE.join([f.escaped_name for f in fields])
        if columns:
            # noinspection SqlNoDataSourceInspection
            select_sql = f"""SELECT {source_geom}{COMMA_SPACE}{columns} 
                             FROM {self.escaped_name}"""
            # noinspection SqlNoDataSourceInspection
            insert_sql = f"""
                INSERT INTO {target.escaped_name}({target_geom}{COMMA_SPACE}{columns}) 
                VALUES ({COMMA_SPACE.join('?' * (len(fields) + 1))})"""
        else:
            # noinspection SqlNoDataSourceInspection
            select_sql = f"""SELECT {source_geom} FROM {self.escaped_name}"""
            # noinspection SqlNoDataSourceInspection
            insert_sql = f"""INSERT INTO {target.escaped_name}({target_geom}) 
                             VALUES (?)"""
        if where_clause:
            select_sql = f"""{select_sql} WHERE {where_clause}"""
        return insert_sql, select_sql
    # End _make_copy_sql method

    def _shared_create(self, name: str, description: str = '',
                       where_clause: str = '', overwrite: bool = False,
                       geopackage: Optional[GeoPackage] = None,
                       geom_name: STRING = None, pk_name: STRING = None,
                       **kwargs) -> tuple[str, str, 'FeatureClass']:
        """
        Shared Steps for Creating a Feature Class during Copy / Explode
        """
        if not geopackage:
            geopackage = self.geopackage
        self._validate_same(
            source=self, target=FeatureClass(geopackage, name=name))
        self._validate_overwrite(geopackage, name=name, overwrite=overwrite)
        target = self.create(
            geopackage=geopackage, name=name, shape_type=self.shape_type,
            srs=kwargs.get(SRS) or self.spatial_reference_system,
            fields=self._remove_special(self.fields),
            description=description or self.description, overwrite=overwrite,
            z_enabled=self.has_z, m_enabled=self.has_m,
            spatial_index=self.has_spatial_index,
            geom_name=geom_name or self.geometry_column_name,
            pk_name=pk_name or self.primary_key_field.name
        )
        insert_sql, select_sql = self._make_copy_sql(target, where_clause)
        return insert_sql, select_sql, target
    # End _shared_create method

    def _update_srs_id(self, features: list, srs_id: int, parts: bool) -> None:
        """
        Update the spatial reference system id of geometries if needed.
        """
        if srs_id == self.spatial_reference_system.srs_id:
            return
        if parts and self.is_multi_part:
            for geoms, *_ in features:
                geoms.srs_id = srs_id
                for geom in geoms:
                    geom.srs_id = srs_id
        else:
            for geom, *_ in features:
                geom.srs_id = srs_id
    # End _update_srs_id method

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
               spatial_index: bool = False, geom_name: str = SHAPE,
               pk_name: STRING = FID) -> 'FeatureClass':
        """
        Create Feature Class
        """
        cls._validate_overwrite(geopackage, name=name, overwrite=overwrite)
        cols = cls._column_names_types(fields)
        with geopackage.connection as conn:
            escaped_name = escape_name(name)
            geom_name = check_geometry_name(geom_name)
            pk_name = check_primary_name(pk_name)
            has_ogr = has_ogr_contents(conn)
            if overwrite:
                current_name = cls._find_geometry_column_name(geopackage, name)
                cls._drop(
                    conn=conn, sql=REMOVE_FEATURE_CLASS, name=name,
                    escaped_name=escaped_name, geom_name=current_name,
                    has_ogr=has_ogr, has_meta=geopackage.is_metadata_enabled,
                    has_schema=geopackage.is_schema_enabled)
            conn.execute(CREATE_FEATURE_TABLE.format(
                name=escaped_name, pk_name=pk_name, geom_name=geom_name,
                feature_type=shape_type, other_fields=cols))
            if not geopackage.check_srs_exists(srs.srs_id):
                conn.execute(INSERT_GPKG_SRS, srs.as_record())
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.features, name, description, now(), srs.srs_id))
            conn.execute(INSERT_GPKG_GEOM_COL,
                         (name, geom_name, shape_type, srs.srs_id,
                          int(z_enabled), int(m_enabled)))
            if has_ogr:
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
            self._drop(
                conn=conn, sql=REMOVE_FEATURE_CLASS,
                geom_name=self.geometry_column_name, name=self.name,
                escaped_name=self.escaped_name, has_ogr=has_ogr_contents(conn),
                has_meta=self.geopackage.is_metadata_enabled,
                has_schema=self.geopackage.is_schema_enabled)
    # End drop method

    def rename(self, name: str) -> None:
        """
        Rename Feature Class
        """
        self._validate_overwrite(self.geopackage, name=name, overwrite=False)
        with self.geopackage.connection as conn:
            has_index = self.has_spatial_index
            self._rename(
                conn=conn, sql=RENAME_FEATURE_CLASS, new_name=name,
                escaped_new_name=escape_name(name),
                has_ogr=has_ogr_contents(conn))
            if has_index:
                self.add_spatial_index()
    # End rename method

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
    def shape_type(self) -> STRING:
        """
        Shape Type
        """
        if not (geom_type := self.geometry_type):
            return None
        return geom_type.upper().rstrip('ZM')
    # End shape_type property

    @property
    def is_multi_part(self) -> bool:
        """
        Is Multi Part Geometry
        """
        return self.shape_type in {
            GeometryType.multi_point, GeometryType.multi_linestring,
            GeometryType.multi_polygon}
    # End is_multi_part property

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
            return None
        return escape_name(self._spatial_index_name)
    # End spatial_index_name property

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
        value = [None if v is None or isnan(v) else v for v in value]
        with self.geopackage.connection as conn:
            conn.execute(UPDATE_EXTENT, tuple([*value, self.name]))
    # End extent property

    def copy(self, name: str, description: str = '', where_clause: str = '',
             overwrite: bool = False, geopackage: Optional[GeoPackage] = None,
             geom_name: STRING = None, pk_name: STRING = None,
             **kwargs) -> 'FeatureClass':
        """
        Copy the structure and content of a feature class.  Create a new
        feature class or overwrite an existing.  Use a where clause to limit
        the features.  Output feature class can be in a different geopackage.

        When a feature class has a custom SRS and copying from one geopackage
        to another geopackage there is a possibility that the embedded SRS ID
        of the geometry will be incorrect in the target geopackage.
        """
        insert_sql, select_sql, target = self._shared_create(
            name=name, description=description, where_clause=where_clause,
            overwrite=overwrite, geopackage=geopackage, geom_name=geom_name,
            pk_name=pk_name, **kwargs)
        cursor = self.geopackage.connection.execute(select_sql)
        with (target.geopackage.connection as connection,
              ExecuteMany(connection=connection, table=target) as executor):
            srs_id = target.spatial_reference_system.srs_id
            while features := cursor.fetchmany(FETCH_SIZE):
                self._update_srs_id(features, srs_id=srs_id, parts=False)
                executor(sql=insert_sql, data=features)
            target.extent = get_extent(target)
        return target
    # End copy method

    def explode(self, name: str, overwrite: bool = False,
                geopackage: Optional[GeoPackage] = None,
                **kwargs) -> 'FeatureClass':
        """
        Explode feature class containing MultiPart geometry in a new feature
        class in the same or a different GeoPackage.  If the feature class
        does not contain a MultiPart geometry then a copy of the feature
        class is made.

        When a feature class has a custom SRS and copying / exploding from one
        geopackage to another geopackage there is a possibility that the
        embedded SRS ID of the geometry will be incorrect in the
        target geopackage.
        """
        if not self.is_multi_part:
            return self.copy(
                name, overwrite=overwrite, geopackage=geopackage, **kwargs)
        insert_sql, select_sql, target = self._shared_create(
            name=name, overwrite=overwrite, geopackage=geopackage, **kwargs)
        cursor = self.geopackage.connection.execute(select_sql)
        with (target.geopackage.connection as connection,
              ExecuteMany(connection=connection, table=target) as executor):
            srs_id = target.spatial_reference_system.srs_id
            while features := cursor.fetchmany(FETCH_SIZE):
                self._update_srs_id(features, srs_id=srs_id, parts=True)
                rows = []
                for geoms, *values in features:
                    rows.extend((geom, *values) for geom in geoms)
                executor(sql=insert_sql, data=rows)
            target.extent = self.extent
        return target
    # End explode method

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
        if srs_id is None:
            srs_id = org_coord_sys_id
        self._srs_id: int = srs_id
        self.definition: str = definition
        self.description: str = description
    # End init built-in

    def __eq__(self, other: 'SpatialReferenceSystem') -> bool:
        """
        Equals
        """
        if not isinstance(other, SpatialReferenceSystem):
            return NotImplemented
        getter = itemgetter(*(1, 2, 3, 4))
        return getter(self.as_record()) == getter(other.as_record())
    # End eq built-in

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
    def __init__(self, name: str, data_type: str, size: INT = None,
                 is_nullable: bool = True, default: Any = None) -> None:
        """
        Initialize the Field class
        """
        super().__init__()
        self.name: str = name
        self.data_type: str = data_type
        self.size: INT = size
        self.is_nullable: bool = is_nullable
        self.default: Any = default
    # End init built-in

    def __repr__(self) -> str:
        """
        String representation
        """
        definition = f'{self.escaped_name} {self.data_type}'
        is_type = self.data_type in (SQLFieldType.blob, SQLFieldType.text)
        if self.size and is_type:
            definition = f'{definition}({self.size})'
        if default := self.default:
            if is_type:
                default = f"'{default}'"
            definition = f'{definition} default {default}'
        if not self.is_nullable:
            definition = f'{definition} NOT NULL'
        return definition
    # End repr built-in

    def __eq__(self, other: 'Field') -> bool:
        """
        Equality Implementation
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return repr(self).casefold() == repr(other).casefold()
    # End eq built-int

    def __hash__(self) -> int:
        """
        Hash Implementation
        """
        return hash(repr(self).casefold())
    # End hash built-in

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
