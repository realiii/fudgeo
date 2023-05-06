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
    Connection, Cursor, DatabaseError, OperationalError, PARSE_COLNAMES,
    PARSE_DECLTYPES, connect, register_adapter, register_converter)
from typing import Callable, Dict, List, Optional, Tuple, Type, Union

from fudgeo.enumeration import (
    DataType, GPKGFlavors, GeometryType, SQLFieldType)
from fudgeo.geometry import (
    Point, PointZ, PointM, PointZM, MultiPoint, MultiPointZ, MultiPointM,
    MultiPointZM, LineString, LineStringZ, LineStringM, LineStringZM,
    MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM,
    Polygon, PolygonZ, PolygonM, PolygonZM, MultiPolygon, MultiPolygonZ,
    MultiPolygonM, MultiPolygonZM)
from fudgeo.sql import (
    CHECK_SRS_EXISTS, CREATE_FEATURE_TABLE, CREATE_OGR_CONTENTS, CREATE_TABLE,
    DEFAULT_EPSG_RECS, DEFAULT_ESRI_RECS, DELETE_OGR_CONTENTS,
    GPKG_OGR_CONTENTS_DELETE_TRIGGER, GPKG_OGR_CONTENTS_INSERT_TRIGGER,
    HAS_OGR_CONTENTS, INSERT_GPKG_CONTENTS_SHORT, INSERT_GPKG_GEOM_COL,
    INSERT_GPKG_OGR_CONTENTS, INSERT_GPKG_SRS, KEYWORDS, REMOVE_FEATURE_CLASS,
    REMOVE_TABLE, SELECT_EXTENT, SELECT_GEOMETRY_COLUMN, SELECT_GEOMETRY_TYPE,
    SELECT_HAS_ZM, SELECT_SRS, SELECT_TABLES_BY_TYPE, TABLE_EXISTS,
    UPDATE_EXTENT)


FIELDS = Union[Tuple['Field', ...], List['Field']]
NAME_MATCHER: Callable = recompile(r'^[A-Z]\w*$', IGNORECASE).match


COMMA_SPACE = ', '
GPKG_EXT = '.gpkg'
SHAPE = 'SHAPE'


def _escape_name(name: str) -> str:
    """
    Escape Name
    """
    if name.upper() in KEYWORDS or not NAME_MATCHER(name):
        name = f'"{name}"'
    return name
# End _escape_name function


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


def _convert_datetime(val: bytes) -> datetime:
    """
    Heavily Influenced by convert_timestamp from ../sqlite3/dbapi2.py,
    Added in support for timezone handling although the practice should
    be to resolve to UTC.
    """
    colon = b':'
    dash = b'-'
    # To split timestamps like that b'2022-09-06T13:50:33'
    for separator in (b' ', b'T'):
        try:
            dt, tm = val.split(separator)
            break
        except ValueError:
            pass
    else:
        raise Exception(f"Could not split datetime: '{val}'")
    year, month, day = map(int, dt.split(dash))
    tm, *micro = tm.split(b'.')
    tz = []
    factor = 0
    for token, scale in zip((b'+', dash), (1, -1)):
        if token in tm:
            tm, *tz = tm.split(token)
            factor = scale
            break
    hours, minutes, seconds = map(int, tm.split(colon))
    try:
        micro = int('{:0<6.6}'.format(micro[0].decode())) if micro else 0
    except (ValueError, TypeError):
        micro = 0
    if tz:
        tz_hr, *tz_min = map(int, tz[0].split(colon))
        tz_min = tz_min[0] if tz_min else 0
        tzinfo = timezone(timedelta(
            hours=factor * tz_hr, minutes=factor * tz_min))
    else:
        tzinfo = None
    return datetime(year, month, day, hours, minutes, seconds,
                    micro, tzinfo=tzinfo)
# End _convert_datetime function


def _register_geometry():
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
        self._conn: Optional[Connection] = None
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
    def connection(self) -> Connection:
        """
        Connection
        """
        if self._conn is None:
            self._conn = connect(
                str(self._path), isolation_level='EXCLUSIVE',
                detect_types=PARSE_DECLTYPES | PARSE_COLNAMES)
            _register_geometry()
            register_converter('timestamp', _convert_datetime)
            register_converter('datetime', _convert_datetime)
        return self._conn
    # End connection property

    @classmethod
    def create(cls, path: Union[PathLike, str],
               flavor: str = GPKGFlavors.esri,
               ogr_contents: bool = True) -> 'GeoPackage':
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
                             overwrite: bool = False) -> 'FeatureClass':
        """
        Creates a feature class in the GeoPackage per the options given.
        """
        fields = self._validate_inputs(fields, name, overwrite)
        return FeatureClass.create(
            geopackage=self, name=name, shape_type=shape_type, srs=srs,
            z_enabled=z_enabled, m_enabled=m_enabled, fields=fields,
            description=description, overwrite=overwrite)
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

    @property
    def escaped_name(self) -> str:
        """
        Escaped Name
        """
        return _escape_name(self.name)
    # End escaped_name property

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
        cols = f', {", ".join(repr(f) for f in fields)}' if fields else ''
        with geopackage.connection as conn:
            escaped_name = _escape_name(name)
            has_ogr_contents = _has_ogr_contents(conn)
            if overwrite:
                conn.executescript(REMOVE_TABLE.format(name, escaped_name))
                if has_ogr_contents:
                    conn.execute(DELETE_OGR_CONTENTS.format(name))
            conn.execute(CREATE_TABLE.format(
                name=escaped_name, other_fields=cols))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.attributes, name, description, _now(), None))
            if has_ogr_contents:
                _add_ogr_contents(conn, name=name, escaped_name=escaped_name)
        return cls(geopackage=geopackage, name=name)
    # End create method

    def drop(self) -> None:
        """
        Drop table from Geopackage
        """
        with self.geopackage.connection as conn:
            conn.executescript(
                REMOVE_TABLE.format(self.name, self.escaped_name))
            if _has_ogr_contents(conn):
                conn.execute(DELETE_OGR_CONTENTS.format(self.name))
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

    @classmethod
    def create(cls, geopackage: GeoPackage, name: str, shape_type: str,
               srs: 'SpatialReferenceSystem', z_enabled: bool = False,
               m_enabled: bool = False, fields: FIELDS = (),
               description: str = '',
               overwrite: bool = False) -> 'FeatureClass':
        """
        Create Feature Class
        """
        cols = f', {", ".join(repr(f) for f in fields)}' if fields else ''
        with geopackage.connection as conn:
            escaped_name = _escape_name(name)
            has_ogr_contents = _has_ogr_contents(conn)
            if overwrite:
                conn.executescript(
                    REMOVE_FEATURE_CLASS.format(name, escaped_name))
                if has_ogr_contents:
                    conn.execute(DELETE_OGR_CONTENTS.format(name))
            conn.execute(CREATE_FEATURE_TABLE.format(
                name=escaped_name, feature_type=shape_type, other_fields=cols))
            if not geopackage.check_srs_exists(srs.srs_id):
                conn.execute(INSERT_GPKG_SRS, srs.as_record())
            conn.execute(INSERT_GPKG_GEOM_COL,
                         (name, SHAPE, shape_type, srs.srs_id,
                          int(z_enabled), int(m_enabled)))
            conn.execute(INSERT_GPKG_CONTENTS_SHORT, (
                name, DataType.features, name, description, _now(), srs.srs_id))
            if has_ogr_contents:
                _add_ogr_contents(conn, name=name, escaped_name=escaped_name)
        return cls(geopackage=geopackage, name=name)
    # End create method

    def drop(self) -> None:
        """
        Drop feature class from Geopackage
        """
        with self.geopackage.connection as conn:
            conn.executescript(
                REMOVE_FEATURE_CLASS.format(self.name, self.escaped_name))
            if _has_ogr_contents(conn):
                conn.execute(DELETE_OGR_CONTENTS.format(self.name))
    # End drop method

    @staticmethod
    def _check_result(cursor: Cursor) -> Optional[str]:
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


def _has_ogr_contents(conn: 'Connection') -> bool:
    """
    Has gpkg_ogr_contents table
    """
    try:
        cursor = conn.execute(HAS_OGR_CONTENTS)
    except (DatabaseError, OperationalError):
        return False
    return bool(cursor.fetchone())
# End _has_ogr_contents function


def _add_ogr_contents(conn: Connection, name: str, escaped_name: str) -> None:
    """
    Add OGR Contents Table Entry and Triggers
    """
    conn.execute(INSERT_GPKG_OGR_CONTENTS, (name, 0))
    conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.format(name, escaped_name))
    conn.execute(GPKG_OGR_CONTENTS_DELETE_TRIGGER.format(name, escaped_name))
# End _add_ogr_contents function


if __name__ == '__main__':
    pass
