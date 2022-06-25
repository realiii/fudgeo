# -*- coding: utf-8 -*-
"""
Test GeoPackage
"""
from datetime import datetime, timedelta, timezone
from math import isnan
from random import randint, choice
from string import ascii_uppercase, digits

from pytest import fixture, mark, raises

from fudgeo.enumeration import GeometryType, SQLFieldType
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiPoint, MultiPolygon, Point, Polygon)
from fudgeo.geopkg import (
    FeatureClass, Field, GeoPackage, SpatialReferenceSystem, Table,
    _convert_datetime)

WGS_1984_UTM_Zone_23N = (
    """PROJCS["WGS_1984_UTM_Zone_23N",
       GEOGCS["GCS_WGS_1984",
       DATUM["D_WGS_1984",
       SPHEROID["WGS_1984",6378137.0,298.257223563]],
       PRIMEM["Greenwich",0.0],
       UNIT["Degree",0.0174532925199433]],
       PROJECTION["Transverse_Mercator"],
       PARAMETER["False_Easting",500000.0],
       PARAMETER["False_Northing",0.0],
       PARAMETER["Central_Meridian",-45.0],
       PARAMETER["Scale_Factor",0.9996],
       PARAMETER["Latitude_Of_Origin",0.0],
       UNIT["Meter",1.0]];IsHighPrecision""")


INSERT_ROWS = """
    INSERT INTO test1 (SHAPE, int_fld, text_fld, test_fld_size, test_bool) 
    VALUES (?, ?, ?, ?, ?)
"""

INSERT_SHAPE = """INSERT INTO test1 (SHAPE) VALUES (?)"""
SELECT_FID_SHAPE = """SELECT fid, SHAPE "[{}]" FROM test1"""


@fixture
def setup_geopackage(tmp_path):
    """
    Setup Basics
    """
    path = tmp_path.joinpath('test.gpkg')
    gpkg = GeoPackage.create(path)
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fields = (
        Field('int_fld', SQLFieldType.integer),
        Field('text_fld', SQLFieldType.text),
        Field('test_fld_size', SQLFieldType.text, 100),
        Field('test_bool', SQLFieldType.boolean),
        Field('test_timestamp', SQLFieldType.timestamp))
    yield path, gpkg, srs, fields
    if path.exists():
        path.unlink()
# End setup_geopackage function


@fixture
def fields():
    """
    Fields
    """
    return [Field('AAA', SQLFieldType.integer),
            Field('BBB', SQLFieldType.text, size=10),
            Field('CCC', SQLFieldType.text),
            Field('DDD', SQLFieldType.double),
            Field('EEE', SQLFieldType.datetime),
            Field('FFF', SQLFieldType.timestamp)]
# End fields function


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
    name = 'TTT'
    table = geo.create_table(name, fields)
    field_names = ', '.join(f.name for f in fields)
    assert isinstance(table, Table)
    with raises(ValueError):
        geo.create_table(name, fields)
    conn = geo.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 0
    now = datetime.now()
    eee_datetime = now + timedelta(days=1)
    fff_datetime = now + timedelta(days=2)
    records = [
        (1, 'asdf', 'longer than 10 characters', 123.456, eee_datetime, fff_datetime),
        (2, 'qwerty', 'not much longer than 10', 987.654, now + timedelta(days=100), now + timedelta(days=200))]
    sql = f"""INSERT INTO {name}({field_names}) VALUES (?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, records)
    conn.commit()
    cursor = conn.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 2
    *_, eee, fff = fields
    cursor = conn.execute(f"""SELECT {eee.name} FROM {name}""")
    value, = cursor.fetchone()
    assert isinstance(value, datetime)
    assert value == eee_datetime
    cursor = conn.execute(f"""SELECT {fff.name} FROM {name}""")
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
    name = 'TTT_DDD'
    table = geo.create_table(name, fields)
    assert isinstance(table, Table)
    tbl = geo.create_table(name, fields, overwrite=True)
    conn = geo.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {name}""")
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
    name = 'FFF'
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    table = geo.create_feature_class(name, srs=srs, fields=fields)
    assert isinstance(table, FeatureClass)
    with raises(ValueError):
        geo.create_feature_class(name, srs=srs, fields=fields)
    cursor = geo.connection.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 0
    table = geo.create_feature_class('ANOTHER', srs=srs)
    assert isinstance(table, FeatureClass)
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
    name = 'FFF_DDD'
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    table = geo.create_feature_class(name, srs=srs, fields=fields)
    assert isinstance(table, FeatureClass)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, overwrite=True)
    cursor = geo.connection.execute(f"""SELECT count(fid) FROM {name}""")
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


@mark.parametrize('name, geom, has_z, has_m', [
    ('test_points', GeometryType.point, False, False),
    ('test_points_z', GeometryType.point, True, False),
    ('test_points_m', GeometryType.point, False, True),
    ('test_points_zm', GeometryType.point, True, True),
    ('test_lines', GeometryType.linestring, False, False),
    ('test_lines_z', GeometryType.linestring, True, False),
    ('test_lines_m', GeometryType.linestring, False, True),
    ('test_lines_zm', GeometryType.linestring, True, True),
    ('test_polygons', GeometryType.polygon, False, False),
    ('test_polygons_z', GeometryType.polygon, True, False),
])
def test_create_feature_class_options(setup_geopackage, name, geom, has_z, has_m):
    """
    Test creating feature classes with different shape options
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        name, srs=srs, fields=fields, m_enabled=has_m, z_enabled=has_z)
    assert isinstance(fc, FeatureClass)
    conn = gpkg.connection
    cursor = conn.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 0
    assert fc.spatial_reference_system.srs_id == 32623
    assert fc.has_z is has_z
    assert fc.has_m is has_m
# End test_create_feature_class_options function


def test_insert_point_rows(setup_geopackage):
    """
    Test Insert Point Rows
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.point)
    assert isinstance(fc, FeatureClass)
    count = 10000
    rows = random_points_and_attrs(count, srs.srs_id)
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS, rows)
        cursor = conn.execute("""SELECT count(fid) from test1""")
        row_count, = cursor.fetchone()
    assert row_count == count
    with gpkg.connection as conn:
        cursor = conn.execute("""SELECT SHAPE FROM test1 LIMIT 10""")
        points = [rec[0] for rec in cursor.fetchall()]
    assert all([isinstance(pt, Point) for pt in points])
    assert all(pt.srs_id == srs.srs_id for pt in points)
    assert all(isnan(v) for v in fc.extent)
    fc.extent = (300000, 1, 700000, 4000000)
    assert (300000, 1, 700000, 4000000) == fc.extent
# End test_insert_point_rows function


def _insert_shape_and_fetch(gpkg, geom):
    with gpkg.connection as conn:
        conn.execute(INSERT_SHAPE, (geom,))
        cursor = conn.execute(SELECT_FID_SHAPE.format(geom.__class__.__name__))
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.polygon)
    geom = Polygon(rings, srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.multi_polygon)
    polys = [[[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1),
               (300000, 1)]],
             [[(100000, 1000000), (100000, 2000000), (200000, 2000000),
               (200000, 1000000), (100000, 1000000)]]]
    geom = MultiPolygon(polys, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.linestring)
    coords = [(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)]
    geom = LineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.multi_point)
    multipoints = [(300000, 1), (300000, 4000000)]
    geom = MultiPoint(multipoints, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True)
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringZ(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.linestring,
        m_enabled=True)
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True, m_enabled=True)
    coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
              (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
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
    gpkg.create_feature_class(
        'test1', srs, fields=fields,
        shape_type=GeometryType.multi_linestring,
        z_enabled=True, m_enabled=True)
    coords = [[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)],
              [(600000, 100000), (600000, 3900000), (400000, 3900000),
               (400000, 100000)]]
    geom = MultiLineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom)
    assert len(result) == 1
    _, line = result[0]
    assert isinstance(line, MultiLineString)
    assert line == geom
# End test_insert_multi_lines function


@mark.parametrize('val, expected', [
    (b'1977-06-15 03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    (b'1977-06-15 03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    (b'2000-06-06 11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    (b'2000-06-06 11:43:37+01:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=1)))),
    (b'2000-06-06 11:43:37+02:30', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=2, minutes=30)))),
    (b'2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
])
def test_convert_datetime(val, expected):
    """
    Test the datetime converter
    """
    assert _convert_datetime(val) == expected
# End test_convert_datetime function


if __name__ == '__main__':
    pass
