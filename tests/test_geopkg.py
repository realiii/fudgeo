# -*- coding: utf-8 -*-
"""
Test GeoPackage
"""
import sys
from datetime import datetime, timedelta, timezone
from math import isnan
from random import randint, choice
from string import ascii_uppercase, digits

from pytest import mark, raises

from fudgeo.enumeration import GeometryType, SQLFieldType
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiPoint, MultiPolygon, Point, Polygon, PolygonM)
from fudgeo.geopkg import (
    FeatureClass, Field, GeoPackage, SHAPE, SpatialReferenceSystem, Table,
    _convert_datetime)
from fudgeo.sql import SELECT_SRS
from tests.crs import WGS_1984_UTM_Zone_23N

INSERT_ROWS = """
    INSERT INTO {} (SHAPE, "int.fld", text_fld, test_fld_size, test_bool) 
    VALUES (?, ?, ?, ?, ?)
"""

INSERT_SHAPE = """INSERT INTO {} (SHAPE) VALUES (?)"""
SELECT_FID_SHAPE = """SELECT fid, SHAPE "[{}]" FROM {}"""


def random_points_and_attrs(count, srs_id):
    """
    Generate Random Points and attrs (Use some UTM Zone)
    """
    points = generate_utm_points(count, srs_id)
    rows = []
    for p in points:
        rand_str = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
        rand_bool = bool(randint(0, 1))
        rand_int = randint(0, 1000)
        rows.append((p, rand_int, rand_str, rand_str, rand_bool))
    return rows
# End random_points_and_attrs function


def generate_utm_points(count, srs_id):
    """
    Generate UTM points in the boundaries of the UTM coordinate space
    """
    eastings = [randint(300000, 700000) for _ in range(count)]
    northings = [randint(0, 4000000) for _ in range(count)]
    return [Point(x=easting, y=northing, srs_id=srs_id)
            for easting, northing in zip(eastings, northings)]
# End generate_utm_points function


def test_create_geopackage(tmp_path):
    """
    Test create geopackage
    """
    path = tmp_path.joinpath('does_not_exist', 'abc')
    with raises(ValueError):
        GeoPackage.create(path)
    path = tmp_path / 'abc'
    geo = GeoPackage.create(path)
    assert geo.path.is_file()
    assert isinstance(geo, GeoPackage)
    with raises(ValueError):
        GeoPackage.create(path)
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_create_geopackage function


def test_create_table(tmp_path, fields):
    """
    Create Table
    """
    path = tmp_path / 'tbl'
    geo = GeoPackage.create(path)
    name = 'SELECT'
    table = geo.create_table(name, fields)
    field_names = ', '.join(f.escaped_name for f in fields)
    assert isinstance(table, Table)
    with raises(ValueError):
        geo.create_table(name, fields)
    conn = geo.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {table.escaped_name}""")
    count, = cursor.fetchone()
    assert count == 0
    now = datetime.now()
    eee_datetime = now + timedelta(days=1)
    fff_datetime = now + timedelta(days=2)
    records = [
        (1, 'asdf', 'longer than 10 characters', 123.456, eee_datetime, fff_datetime),
        (2, 'qwerty', 'not much longer than 10', 987.654, now + timedelta(days=100), now + timedelta(days=200))]
    sql = f"""INSERT INTO {table.escaped_name} ({field_names}) VALUES (?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, records)
    conn.commit()
    cursor = conn.execute(f"""SELECT count(fid) FROM {table.escaped_name}""")
    count, = cursor.fetchone()
    assert count == 2
    *_, eee, select = fields
    cursor = conn.execute(f"""SELECT {eee.name} FROM {table.escaped_name}""")
    value, = cursor.fetchone()
    assert isinstance(value, datetime)
    assert value == eee_datetime
    cursor = conn.execute(f"""SELECT {select.escaped_name} FROM {table.escaped_name}""")
    value, = cursor.fetchone()
    assert isinstance(value, datetime)
    assert value == fff_datetime
    table = geo.create_table('ANOTHER')
    assert isinstance(table, Table)
    cursor = conn.execute(
        """SELECT count(type) FROM sqlite_master WHERE type = 'trigger'""")
    count, = cursor.fetchone()
    assert count == 4
    conn.close()
    if path.exists():
        path.unlink()
# End test_create_table function


def test_create_table_drop_table(tmp_path, fields):
    """
    Create Table, overwrite Table, and Drop Table
    """
    path = tmp_path / 'tbl_drop'
    geo = GeoPackage.create(path)
    name = 'SELECT'
    table = geo.create_table(name, fields)
    assert isinstance(table, Table)
    tbl = geo.create_table(name, fields, overwrite=True)
    conn = geo.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {table.escaped_name}""")
    count, = cursor.fetchone()
    assert count == 0
    sql = """SELECT count(type) FROM sqlite_master WHERE type = 'trigger'"""
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == 2
    tbl.drop()
    assert not geo._check_table_exists(name)
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == 0
    conn.close()
    if path.exists():
        path.unlink()
# End test_create_table_drop_table function


def test_create_feature_class(tmp_path, fields):
    """
    Create Feature Class
    """
    path = tmp_path / 'fc'
    geo = GeoPackage.create(path)
    name = 'SELECT'
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fc = geo.create_feature_class(name, srs=srs, fields=fields)
    assert isinstance(fc, FeatureClass)
    with raises(ValueError):
        geo.create_feature_class(name, srs=srs, fields=fields)
    cursor = geo.connection.execute(f"""SELECT count(fid) FROM {fc.escaped_name}""")
    count, = cursor.fetchone()
    assert count == 0
    fc = geo.create_feature_class('ANOTHER', srs=srs)
    assert isinstance(fc, FeatureClass)
    cursor = geo.connection.execute(
        """SELECT count(type) FROM sqlite_master WHERE type = 'trigger'""")
    count, = cursor.fetchone()
    assert count == 4
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_create_feature_class function


def test_create_feature_drop_feature(tmp_path, fields):
    """
    Create Feature Class, Overwrite it, and then Drop it
    """
    path = tmp_path / 'fc_drop'
    geo = GeoPackage.create(path)
    name = 'SELECT'
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fc = geo.create_feature_class(name, srs=srs, fields=fields)
    assert isinstance(fc, FeatureClass)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, overwrite=True)
    cursor = geo.connection.execute(f"""SELECT count(fid) FROM {fc.escaped_name}""")
    count, = cursor.fetchone()
    assert count == 0
    sql = """SELECT count(type) FROM sqlite_master WHERE type = 'trigger'"""
    cursor = geo.connection.execute(sql)
    count, = cursor.fetchone()
    assert count == 2
    fc.drop()
    assert not geo._check_table_exists(name)
    cursor = geo.connection.execute(sql)
    count, = cursor.fetchone()
    assert count == 0
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_create_feature_drop_feature function


def test_tables_and_feature_classes(tmp_path, fields):
    """
    Test tables and feature classes
    """
    path = tmp_path / 'list'
    geo = GeoPackage.create(path)
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    for c in 'ABC':
        geo.create_feature_class(c, srs=srs, fields=fields)
    assert set(geo.feature_classes) == set('ABC')
    assert isinstance(geo.feature_classes['A'], FeatureClass)
    for c in 'DEF':
        geo.create_table(c, fields=fields)
    assert set(geo.tables) == set('DEF')
    assert isinstance(geo.tables['F'], Table)
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_tables_and_feature_classes function


@mark.parametrize('name, geom, has_z, has_m, type_', [
    ('test_points', GeometryType.point, False, False, 'Point'),
    ('test_points_z', GeometryType.point, True, False, 'PointZ'),
    ('test_points_m', GeometryType.point, False, True, 'PointM'),
    ('test_points_zm', GeometryType.point, True, True, 'PointZM'),
    ('test_lines', GeometryType.linestring, False, False, 'LineString'),
    ('test_lines_z', GeometryType.linestring, True, False, 'LineStringZ'),
    ('test_lines_m', GeometryType.linestring, False, True, 'LineStringM'),
    ('test_lines_zm', GeometryType.linestring, True, True, 'LineStringZM'),
    ('test_polygons', GeometryType.polygon, False, False, 'Polygon'),
    ('test_polygons_z', GeometryType.polygon, True, False, 'PolygonZ'),
    ('test_polygons_m', GeometryType.polygon, False, True, 'PolygonM'),
    ('test_polygons_zm', GeometryType.polygon, True, True, 'PolygonZM'),
])
def test_create_feature_class_options(setup_geopackage, name, geom, has_z, has_m, type_):
    """
    Test creating feature classes with different shape options
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        name, shape_type=geom, srs=srs, fields=fields,
        m_enabled=has_m, z_enabled=has_z)
    assert isinstance(fc, FeatureClass)
    conn = gpkg.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 0
    assert fc.spatial_reference_system.srs_id == 32623
    assert fc.has_z is has_z
    assert fc.has_m is has_m
    assert fc.geometry_column_name == SHAPE
    assert fc.geometry_type == type_
# End test_create_feature_class_options function


def test_select_srs(setup_geopackage):
    """
    Test select srs
    """
    _, gpkg, srs, fields = setup_geopackage
    name = 'SELECT'
    fc = gpkg.create_feature_class(
        name, shape_type=GeometryType.polygon, srs=srs, fields=fields)
    assert isinstance(fc, FeatureClass)
    conn = gpkg.connection
    cursor = conn.execute(SELECT_SRS, (name,))
    _, _, org_id, _, _, srs_id = cursor.fetchone()
    epsg = 32623
    assert org_id == epsg
    assert org_id == srs_id
    cursor = conn.execute(SELECT_SRS, (name.upper(),))
    _, _, org_id, _, _, srs_id = cursor.fetchone()
    assert org_id == epsg
    assert org_id == srs_id
# End test_select_srs function


def test_insert_point_rows(setup_geopackage):
    """
    Test Insert Point Rows
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.point)
    assert isinstance(fc, FeatureClass)
    count = 10000
    rows = random_points_and_attrs(count, srs.srs_id)
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS.format(fc.escaped_name), rows)
        cursor = conn.execute(f"""SELECT count(fid) from {fc.escaped_name}""")
        row_count, = cursor.fetchone()
    assert row_count == count
    with gpkg.connection as conn:
        cursor = conn.execute(f"""SELECT SHAPE FROM {fc.escaped_name} LIMIT 10""")
        points = [rec[0] for rec in cursor.fetchall()]
    assert all([isinstance(pt, Point) for pt in points])
    assert all(pt.srs_id == srs.srs_id for pt in points)
    assert all(isnan(v) for v in fc.extent)
    fc.extent = (300000, 1, 700000, 4000000)
    assert (300000, 1, 700000, 4000000) == fc.extent
# End test_insert_point_rows function


def _insert_shape_and_fetch(gpkg, geom, name):
    with gpkg.connection as conn:
        conn.execute(INSERT_SHAPE.format(name), (geom,))
        cursor = conn.execute(SELECT_FID_SHAPE.format(geom.__class__.__name__, name))
        return cursor.fetchall()


@mark.parametrize('rings', [
    [[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)]],
    [[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)],
     [(400000, 100000), (600000, 100000), (600000, 3900000), (400000, 3900000), (400000, 100000)]],
])
def test_insert_poly(setup_geopackage, rings):
    """
    Test create a feature class and insert a polygon
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.polygon)
    geom = Polygon(rings, srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, poly = result[0]
    assert isinstance(poly, Polygon)
    assert poly == geom
# End test_insert_poly function


def test_insert_multi_poly(setup_geopackage):
    """
    Test create a feature class with "multi polygons"
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.multi_polygon)
    polys = [[[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1),
               (300000, 1)]],
             [[(100000, 1000000), (100000, 2000000), (200000, 2000000),
               (200000, 1000000), (100000, 1000000)]]]
    geom = MultiPolygon(polys, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, poly = result[0]
    assert isinstance(poly, MultiPolygon)
    assert poly == geom
# End test_insert_multi_poly function


def test_insert_lines(setup_geopackage):
    """
    Test insert a line
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring)
    coords = [(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)]
    geom = LineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, LineString)
    assert line == geom
# End test_insert_lines function


def test_insert_multi_point(setup_geopackage):
    """
    Test insert a multi point
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.multi_point)
    multipoints = [(300000, 1), (300000, 4000000)]
    geom = MultiPoint(multipoints, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, MultiPoint)
    assert line == geom
# End test_insert_multi_point function


def test_insert_lines_z(setup_geopackage):
    """
    Test insert a line with Z
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True)
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringZ(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, LineStringZ)
    assert line == geom
# End test_insert_lines_z function


def test_insert_lines_m(setup_geopackage):
    """
    Test insert a line with M
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        m_enabled=True)
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, LineStringM)
    assert line == geom
# End test_insert_lines_m function


def test_insert_lines_zm(setup_geopackage):
    """
    Test insert a line with ZM
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True, m_enabled=True)
    coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
              (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, LineStringZM)
    assert line == geom
# End test_insert_lines_zm function


def test_insert_multi_lines(setup_geopackage):
    """
    Test insert multi lines
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields,
        shape_type=GeometryType.multi_linestring,
        z_enabled=True, m_enabled=True)
    coords = [[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)],
              [(600000, 100000), (600000, 3900000), (400000, 3900000),
               (400000, 100000)]]
    geom = MultiLineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, MultiLineString)
    assert line == geom
# End test_insert_multi_lines function


def test_insert_polygon_m(setup_geopackage):
    """
    Test insert polygon m
    """
    rings = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.polygon)
    geom = PolygonM(rings, srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc.escaped_name)
    assert len(result) == 1
    _, poly = result[0]
    assert isinstance(poly, PolygonM)
    assert poly == geom
# End test_insert_polygon_m function


@mark.parametrize('val, expected', [
    (b'1977-06-15 03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    (b'1977-06-15 03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    (b'2000-06-06 11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    (b'2000-06-06 11:43:37+01:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=1)))),
    (b'2000-06-06 11:43:37+02:30', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=2, minutes=30)))),
    (b'2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    (b'2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    (b'1977-06-15T03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    (b'1977-06-15T03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    (b'2000-06-06T11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    (b'2022-02-14T08:37:41.0Z', datetime(2022, 2, 14, 8, 37, 41, 0)),
])
def test_convert_datetime(val, expected):
    """
    Test the datetime converter
    """
    assert _convert_datetime(val) == expected
# End test_convert_datetime function


def test_custom_spatial_reference(tmp_path, fields):
    """
    Test custom spatial reference
    """
    path = tmp_path / 'fc'
    wkt = WGS_1984_UTM_Zone_23N.replace('1984', '1975')
    srs_id = 300001
    srs = SpatialReferenceSystem(
        name='Nineteen Seventy Five', organization='CUSTOM',
        org_coord_sys_id=0, definition=wkt, srs_id=srs_id)
    geo = GeoPackage.create(path)
    name = 'custom_srs_fc'
    fc = geo.create_feature_class(name, srs=srs, fields=fields)
    assert isinstance(fc, FeatureClass)
    assert fc.spatial_reference_system.srs_id == srs_id
    assert fc.spatial_reference_system.as_record() == srs.as_record()
# End test_custom_spatial_reference function


def test_escaped_columns(setup_geopackage):
    """
    Test ability to add fields that need escaping to be added
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'keyword_column_fc'
    select = Field('select', SQLFieldType.integer)
    union = Field('UnIoN', SQLFieldType.text, 20)
    all_ = Field('ALL', SQLFieldType.text, 50)
    example_dot = Field('why.do.this', SQLFieldType.text, 123)
    regular = Field('regular', SQLFieldType.integer)
    fields = select, union, all_, example_dot, regular
    assert repr(select) == '"select" INTEGER'
    assert repr(union) == '"UnIoN" TEXT20'
    assert repr(all_) == '"ALL" TEXT50'
    assert repr(example_dot) == '"why.do.this" TEXT123'
    assert repr(regular) == 'regular INTEGER'
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    expected_names = ['fid', SHAPE, select.name, union.name, all_.name,
                      example_dot.name, regular.name]
    assert fc.field_names == expected_names
    rows = [(Point(x=1, y=2), 1, 'asdf', 'lmnop', ';;::;;;'),
            (Point(x=3, y=4), 2, 'qwerty', 'xyz', '!!!!!')]
    with fc.geopackage.connection as conn:
        conn.executemany(
            f"""INSERT INTO {fc.name} (SHAPE, {select.escaped_name}, 
                            {union.escaped_name}, {all_.escaped_name}, 
                            {example_dot.escaped_name})
                VALUES (?, ?, ?, ?, ?)""", rows)
    cursor = conn.execute(
        f"""SELECT {select.escaped_name}, {union.escaped_name}, 
                    {all_.escaped_name}, {example_dot.escaped_name}
            FROM {fc.name}""")
    records = cursor.fetchall()
    assert len(records) == 2
    assert records[0] == (1, 'asdf', 'lmnop', ';;::;;;')
    assert records[1] == (2, 'qwerty', 'xyz', '!!!!!')
# End test_escaped_columns function


def test_escaped_table(setup_geopackage):
    """
    Test ability to add fields that need escaping to be added
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'SELECT'
    select = Field('a', SQLFieldType.integer)
    union = Field('b', SQLFieldType.text, 20)
    all_ = Field('c', SQLFieldType.text, 50)
    fields = select, union, all_
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    expected_names = ['fid', SHAPE, select.name, union.name, all_.name]
    assert fc.field_names == expected_names
    rows = [(Point(x=1, y=2), 1, 'asdf', 'lmnop'),
            (Point(x=3, y=4), 2, 'qwerty', 'xyz')]
    with fc.geopackage.connection as conn:
        conn.executemany(
            f"""INSERT INTO {fc.escaped_name} (SHAPE, {select.escaped_name}, 
                            {union.escaped_name}, {all_.escaped_name})
                VALUES (?, ?, ?, ?)""", rows)
    cursor = conn.execute(
        f"""SELECT {select.escaped_name}, {union.escaped_name}, 
                    {all_.escaped_name}
            FROM {fc.escaped_name}""")
    records = cursor.fetchall()
    assert len(records) == 2
    assert records[0] == (1, 'asdf', 'lmnop')
    assert records[1] == (2, 'qwerty', 'xyz')
# End test_escaped_table function


@mark.skipif(sys.platform != 'darwin', reason='will be different on windows')
def test_representation():
    """
    Test string representation
    """
    gpkg = GeoPackage('/some/path/to/geopackage.gpkg')
    assert repr(gpkg) == "GeoPackage(path=PosixPath('/some/path/to/geopackage.gpkg'))"
    fc = FeatureClass(gpkg, '/some/path/to/geopackage.gpkg')
    assert repr(fc) == "FeatureClass(geopackage=GeoPackage(path=PosixPath('/some/path/to/geopackage.gpkg')), name='/some/path/to/geopackage.gpkg')"
    tbl = Table(gpkg, '/some/path/to/geopackage.gpkg')
    assert repr(tbl) == "Table(geopackage=GeoPackage(path=PosixPath('/some/path/to/geopackage.gpkg')), name='/some/path/to/geopackage.gpkg')"
# End test_representation function


if __name__ == '__main__':
    pass
