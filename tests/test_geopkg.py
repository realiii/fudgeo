# -*- coding: utf-8 -*-
"""
Test GeoPackage
"""


import sys
from datetime import datetime, timedelta
from math import isnan
from random import randint, choice
from string import ascii_uppercase, digits

from pytest import mark, raises

from fudgeo.constant import SHAPE
from fudgeo.enumeration import GeometryType, SQLFieldType
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiPoint, MultiPolygon, Point, Polygon, PolygonM)
from fudgeo.geopkg import (
    FeatureClass, Field, GeoPackage, SpatialReferenceSystem, Table)
from fudgeo.extension.ogr import has_ogr_contents
from fudgeo.sql import SELECT_SRS
from tests.crs import WGS_1984_UTM_Zone_23N

# noinspection SqlNoDataSourceInspection
INSERT_ROWS = """
    INSERT INTO {} ({}, "int.fld", text_fld, test_fld_size, test_bool) 
    VALUES (?, ?, ?, ?, ?)
"""
# noinspection SqlNoDataSourceInspection
SELECT_ST_FUNCS = """SELECT ST_IsEmpty({0}), ST_MinX({0}), ST_MaxX({0}), ST_MinY({0}), ST_MaxY({0}) FROM {1}"""
# noinspection SqlNoDataSourceInspection,SqlResolve
SELECT_RTREE = """SELECT * FROM rtree_{0}_{1} ORDER BY 1"""
# noinspection SqlNoDataSourceInspection
INSERT_SHAPE = """INSERT INTO {} ({}) VALUES (?)"""


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


@mark.parametrize('name, ogr_contents, trigger_count', [
    ('SELECT', True, 4),
    ('SELECT', False, 0),
    ('SEL;ECT', True, 4),
    ('SEL;ECT', False, 0),
    ('SEL ECT', True, 4),
    ('SEL ECT', False, 0),
])
def test_create_table(tmp_path, fields, name, ogr_contents, trigger_count):
    """
    Create Table
    """
    path = tmp_path / 'tbl'
    geo = GeoPackage.create(path, ogr_contents=ogr_contents)
    table = geo.create_table(name, fields)
    field_names = ', '.join(f.escaped_name for f in fields)
    assert isinstance(table, Table)
    assert table.primary_key_field.name == 'fid'
    with raises(ValueError):
        geo.create_table(name, fields)
    conn = geo.connection
    assert table.count == 0
    now = datetime.now()
    eee_datetime = now + timedelta(days=1)
    fff_datetime = now + timedelta(days=2)
    records = [
        (1, 'asdf', 'longer than 10 characters', 123.456, eee_datetime, fff_datetime),
        (2, 'qwerty', 'not much longer than 10', 987.654, now + timedelta(days=100), now + timedelta(days=200))]
    # noinspection SqlNoDataSourceInspection,SqlInsertValues
    sql = f"""INSERT INTO {table.escaped_name} ({field_names}) 
              VALUES (?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, records)
    conn.commit()
    assert table.count == 2
    *_, eee, select = fields
    # noinspection SqlNoDataSourceInspection
    cursor = table.select(fields=eee)
    value, = cursor.fetchone()
    assert isinstance(value, datetime)
    assert value == eee_datetime
    # noinspection SqlNoDataSourceInspection
    cursor = table.select(fields=select)
    value, = cursor.fetchone()
    assert isinstance(value, datetime)
    assert value == fff_datetime
    table = geo.create_table('ANOTHER')
    assert isinstance(table, Table)
    # noinspection SqlNoDataSourceInspection
    cursor = conn.execute(
        """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'""")
    count, = cursor.fetchone()
    assert count == trigger_count
    conn.close()
    if path.exists():
        path.unlink()
# End test_create_table function


@mark.parametrize('name, ogr_contents, has_table, trigger_count', [
    ('SELECT', True, True, 2),
    ('SELECT', False, False, 0),
    ('SEL;ECT', True, True, 2),
    ('SEL;ECT', False, False, 0),
    ('SEL ECT', True, True, 2),
    ('SEL ECT', False, False, 0),
])
def test_create_table_drop_table(tmp_path, fields, name, ogr_contents, has_table, trigger_count):
    """
    Create Table, overwrite Table, and Drop Table
    """
    path = tmp_path / 'tbl_drop'
    geo = GeoPackage.create(path, ogr_contents=ogr_contents)
    conn = geo.connection
    assert has_ogr_contents(conn) is has_table
    table = geo.create_table(name, fields)
    assert isinstance(table, Table)
    tbl = geo.create_table(name, fields, overwrite=True)
    assert tbl.exists()
    assert table.count == 0
    # noinspection SqlNoDataSourceInspection
    sql = """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'"""
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == trigger_count
    tbl.drop()
    assert not geo._check_table_exists(name)
    assert not table.exists()
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == 0
    conn.close()
    if path.exists():
        path.unlink()
# End test_create_table_drop_table function


@mark.parametrize('name, ogr_contents, trigger_count, add_index', [
    ('ASDF', True, 4, False),
    ('ASDF', False, 0, False),
    ('SELECT', True, 4, False),
    ('SELECT', False, 0, False),
    ('SEL;ECT', True, 4, False),
    ('SEL;ECT', False, 0, False),
    ('SEL ECT', True, 4, False),
    ('SEL ECT', False, 0, False),
    ('ASDF', True, 11, True),
    ('ASDF', False, 7, True),
    ('SELECT', True, 11, True),
    ('SELECT', False, 7, True),
    ('SEL;ECT', True, 11, True),
    ('SEL;ECT', False, 7, True),
    ('SEL ECT', True, 11, True),
    ('SEL ECT', False, 7, True),
])
def test_create_feature_class(tmp_path, fields, name, ogr_contents, trigger_count, add_index):
    """
    Create Feature Class
    """
    path = tmp_path / 'fc'
    geo = GeoPackage.create(path, ogr_contents=ogr_contents)
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    assert fc.primary_key_field.name == 'fid'
    assert isinstance(fc, FeatureClass)
    with raises(ValueError):
        geo.create_feature_class(name, srs=srs, fields=fields)
    assert fc.count == 0
    fc = geo.create_feature_class('ANOTHER', srs=srs)
    assert isinstance(fc, FeatureClass)
    # noinspection SqlNoDataSourceInspection
    cursor = geo.connection.execute(
        """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'""")
    count, = cursor.fetchone()
    assert count == trigger_count
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_create_feature_class function


@mark.parametrize('name, ogr_contents, has_table, trigger_count, add_index', [
    ('ASDF', True, True, 2, False),
    ('ASDF', False, False, 0, False),
    ('SELECT', True, True, 2, False),
    ('SELECT', False, False, 0, False),
    ('SEL;ECT', True, True, 2, False),
    ('SEL;ECT', False, False, 0, False),
    ('SEL ECT', True, True, 2, False),
    ('SEL ECT', False, False, 0, False),
    ('ASDF', True, True, 9, True),
    ('ASDF', False, False, 7, True),
    ('SELECT', True, True, 9, True),
    ('SELECT', False, False, 7, True),
    ('SEL;ECT', True, True, 9, True),
    ('SEL;ECT', False, False, 7, True),
    ('SEL ECT', True, True, 9, True),
    ('SEL ECT', False, False, 7, True),
])
def test_create_feature_drop_feature(tmp_path, fields, name, ogr_contents, has_table, trigger_count, add_index):
    """
    Create Feature Class, Overwrite it, and then Drop it
    """
    path = tmp_path / 'fc_drop'
    geo = GeoPackage.create(path, ogr_contents=ogr_contents)
    conn = geo.connection
    assert has_ogr_contents(conn) is has_table
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    if not add_index:
        assert fc.add_spatial_index()
        assert fc.has_spatial_index
    assert isinstance(fc, FeatureClass)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, overwrite=True, spatial_index=add_index)
    assert fc.exists()
    assert fc.count == 0
    # noinspection SqlNoDataSourceInspection
    sql = """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'"""
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == trigger_count
    fc.drop()
    assert not geo._check_table_exists(name)
    assert not fc.exists()
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == 0
    conn.close()
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
    assert fc.count == 0
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


@mark.parametrize('name, add_index', [
    ('ASDF', True),
    ('ASDF', False),
    ('SELECT', True),
    ('SELECT', False),
    ('SEL;ECT', True),
    ('SEL;ECT', False),
    ('SEL ECT', True),
    ('SEL ECT', False),
])
def test_insert_point_rows(setup_geopackage, name, add_index):
    """
    Test Insert Point Rows
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        name, srs, fields=fields, shape_type=GeometryType.point,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    assert isinstance(fc, FeatureClass)
    count = 10000
    rows = random_points_and_attrs(count, srs.srs_id)
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS.format(fc.escaped_name, fc.geometry_column_name), rows)
    assert fc.count == count
    # noinspection SqlNoDataSourceInspection
    cursor = fc.select(limit=10)
    points = [rec[0] for rec in cursor.fetchall()]
    assert all([isinstance(pt, Point) for pt in points])
    assert all(pt.srs_id == srs.srs_id for pt in points)
    assert all(isnan(v) for v in fc.extent)
    fc.extent = (300000, 1, 700000, 4000000)
    assert (300000, 1, 700000, 4000000) == fc.extent
    if not add_index:
        assert fc.add_spatial_index()
    cursor = gpkg.connection.execute(f"""
        SELECT COUNT(1) AS C FROM "rtree_{name}_{fc.geometry_column_name}"
    """)
    assert cursor.fetchone() == (count,)
# End test_insert_point_rows function


def _insert_shape_and_fetch(gpkg, geom, fc):
    with gpkg.connection as conn:
        conn.execute(INSERT_SHAPE.format(fc.escaped_name, fc.geometry_column_name), (geom,))
        cursor = fc.select(include_primary=True)
        return cursor.fetchall()


@mark.parametrize('rings, add_index', [
    ([[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)]], False),
    ([[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)],
      [(400000, 100000), (600000, 100000), (600000, 3900000), (400000, 3900000), (400000, 100000)]], False),
    ([[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)]], True),
    ([[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)],
      [(400000, 100000), (600000, 100000), (600000, 3900000), (400000, 3900000), (400000, 100000)]], True),
])
def test_insert_poly(setup_geopackage, rings, add_index):
    """
    Test create a feature class and insert a polygon
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.polygon,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    geom = Polygon(rings, srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    poly, _ = result[0]
    assert isinstance(poly, Polygon)
    assert poly == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_poly function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_multi_poly(setup_geopackage, add_index):
    """
    Test create a feature class with "multi polygons"
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.multi_polygon,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    polys = [[[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1),
               (300000, 1)]],
             [[(100000, 1000000), (100000, 2000000), (200000, 2000000),
               (200000, 1000000), (100000, 1000000)]]]
    geom = MultiPolygon(polys, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    poly, _ = result[0]
    assert isinstance(poly, MultiPolygon)
    assert poly == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 100000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 100000, 700000, 1, 4000000)]
# End test_insert_multi_poly function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_lines(setup_geopackage, add_index):
    """
    Test insert a line
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)]
    geom = LineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, _ = result[0]
    assert isinstance(line, LineString)
    assert line == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_lines function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_multi_point(setup_geopackage, add_index):
    """
    Test insert a multi point
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.multi_point,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    multipoints = [(300000, 1), (700000, 4000000)]
    geom = MultiPoint(multipoints, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    pts, _ = result[0]
    assert isinstance(pts, MultiPoint)
    assert pts == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_multi_point function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_lines_z(setup_geopackage, add_index):
    """
    Test insert a line with Z
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringZ(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, _ = result[0]
    assert isinstance(line, LineStringZ)
    assert line == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_lines_z function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_lines_m(setup_geopackage, add_index):
    """
    Test insert a line with M
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        m_enabled=True, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [(300000, 1, 10), (300000, 4000000, 20), (700000, 4000000, 30),
              (700000, 1, 40)]
    geom = LineStringM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, _ = result[0]
    assert isinstance(line, LineStringM)
    assert line == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_lines_m function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_lines_zm(setup_geopackage, add_index):
    """
    Test insert a line with ZM
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True, m_enabled=True, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
              (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, _ = result[0]
    assert isinstance(line, LineStringZM)
    assert line == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_lines_zm function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_and_update_lines_zm(setup_geopackage, add_index):
    """
    Test insert a line with ZM an then update the geometry
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.linestring,
        z_enabled=True, m_enabled=True, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
              (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, primary = result[0]
    assert isinstance(line, LineStringZM)
    assert line == geom
    assert primary == 1

    coords = [(321000, 123, 101, 0), (321000, 4560000, 202, 1111),
              (789000, 4000000, 303, 2222), (789000, 1, 404, 3333)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    gpkg.connection.execute(f"""
        UPDATE {fc.escaped_name} 
        SET {fc.geometry_column_name} = ? 
        WHERE {fc.primary_key_field.escaped_name} = ?""", (geom, primary))

    cursor = fc.select(include_primary=True)
    result = cursor.fetchall()
    assert len(result) == 1
    line, primary = result[0]
    assert isinstance(line, LineStringZM)
    assert line == geom
    assert primary == 1
# End test_insert_and_update_lines_zm function


@mark.parametrize('geom_name, add_index, is_error', [
    ('geom', False, False),
    ('geom', True, False),
    ('GeOmEtRy', False, False),
    ('GeOmEtRy', True, False),
    ('aa bb', False, True),
    ('cc-dd', True, True),
])
def test_non_standard_geom_name(setup_geopackage, geom_name, add_index, is_error):
    """
    Test non-standard geometry column name
    """
    _, gpkg, srs, fields = setup_geopackage
    tbl = 'SELECT'
    kwargs = dict(
        name=tbl, srs=srs, fields=fields,
        shape_type=GeometryType.linestring,
        z_enabled=True, m_enabled=True, spatial_index=add_index,
        geom_name=geom_name)
    if is_error:
        with raises(ValueError):
            gpkg.create_feature_class(**kwargs)
        return
    fc = gpkg.create_feature_class(**kwargs)
    assert fc.has_spatial_index is add_index
    assert fc.geometry_column_name == geom_name
    if add_index:
        assert fc.spatial_index_name == f'rtree_{tbl}_{geom_name}'
    coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
              (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
    geom = LineStringZM(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    line, primary = result[0]
    assert isinstance(line, LineStringZM)
    assert line == geom
    assert primary == 1
# End test_non_standard_geom_name function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_multi_lines(setup_geopackage, add_index):
    """
    Test insert multi lines
    """
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields,
        shape_type=GeometryType.multi_linestring,
        z_enabled=False, m_enabled=False, spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    coords = [[(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1)],
              [(600000, 100000), (600000, 3900000), (400000, 3900000),
               (400000, 100000)]]
    geom = MultiLineString(coords, srs_id=srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    lines, _ = result[0]
    assert isinstance(lines, MultiLineString)
    assert lines == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 300000, 700000, 1, 4000000)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 300000, 700000, 1, 4000000)]
# End test_insert_multi_lines function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_polygon_m(setup_geopackage, add_index):
    """
    Test insert polygon m
    """
    rings = [[(0, 0, 0), (0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 0)],
              [(5, 5, 5), (5, 15, 10), (15, 15, 15), (15, 5, 20), (5, 5, 5)]]
    _, gpkg, srs, fields = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=fields, shape_type=GeometryType.polygon,
        spatial_index=add_index, m_enabled=True)
    assert fc.has_spatial_index is add_index
    geom = PolygonM(rings, srs.srs_id)
    result = _insert_shape_and_fetch(gpkg, geom, fc)
    assert len(result) == 1
    poly, _ = result[0]
    assert isinstance(poly, PolygonM)
    assert poly == geom
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 0, 15, 0, 15)]
    if add_index:
        cursor = gpkg.connection.execute(SELECT_RTREE.format(
            fc.name, fc.geometry_column_name))
        assert cursor.fetchall() == [(1, 0, 15, 0, 15)]
# End test_insert_polygon_m function


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
    rows = [(Point(x=1, y=2, srs_id=srs.srs_id), 1, 'asdf', 'lmnop', ';;::;;;'),
            (Point(x=3, y=4, srs_id=srs.srs_id), 2, 'qwerty', 'xyz', '!!!!!')]
    with fc.geopackage.connection as conn:
        # noinspection SqlNoDataSourceInspection
        conn.executemany(
            f"""INSERT INTO {fc.name} ({fc.geometry_column_name}, {select.escaped_name}, 
                            {union.escaped_name}, {all_.escaped_name}, 
                            {example_dot.escaped_name})
                VALUES (?, ?, ?, ?, ?)""", rows)
    # noinspection SqlNoDataSourceInspection
    cursor = fc.select(fields=(select, union, all_, example_dot), include_geometry=False)
    records = cursor.fetchall()
    assert len(records) == 2
    assert records[0] == (1, 'asdf', 'lmnop', ';;::;;;')
    assert records[1] == (2, 'qwerty', 'xyz', '!!!!!')
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 1.0, 1.0, 2.0, 2.0), (0, 3.0, 3.0, 4.0, 4.0)]
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
    rows = [(Point(x=1, y=2, srs_id=srs.srs_id), 1, 'asdf', 'lmnop'),
            (Point(x=3, y=4, srs_id=srs.srs_id), 2, 'qwerty', 'xyz')]
    with fc.geopackage.connection as conn:
        # noinspection SqlNoDataSourceInspection
        conn.executemany(
            f"""INSERT INTO {fc.escaped_name} ({fc.geometry_column_name}, {select.escaped_name}, 
                            {union.escaped_name}, {all_.escaped_name})
                VALUES (?, ?, ?, ?)""", rows)
    # noinspection SqlNoDataSourceInspection
    cursor = fc.select(fields=(select, union, all_), include_geometry=False)
    records = cursor.fetchall()
    assert len(records) == 2
    assert records[0] == (1, 'asdf', 'lmnop')
    assert records[1] == (2, 'qwerty', 'xyz')
    cursor = gpkg.connection.execute(
        SELECT_ST_FUNCS.format(fc.geometry_column_name, fc.escaped_name))
    assert cursor.fetchall() == [(0, 1, 1, 2, 2), (0, 3, 3, 4, 4)]
# End test_escaped_table function


def test_validate_fields_feature_class(setup_geopackage):
    """
    Test validate fields on feature class
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'VALIDATE_FIELDS_FC'
    a = Field('a', SQLFieldType.integer)
    b = Field('b', SQLFieldType.text, 20)
    c = Field('c', SQLFieldType.text, 50)
    fields = a, b, c
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    expected_names = ['fid', SHAPE, a.name, b.name, c.name]
    assert fc.field_names == expected_names
    fields = fc._validate_fields(fields=expected_names)
    assert [f.name for f in fields] == [a.name, b.name, c.name]
    fields = fc._validate_fields(fields=[n.upper() for n in expected_names])
    assert [f.name for f in fields] == [a.name, b.name, c.name]
    assert not fc._validate_fields(fields='d')
    assert not fc._validate_fields(fields=1234)
    assert not fc._validate_fields(fields=())
    assert not fc._validate_fields(fields=(None, Ellipsis, 1234, object))
# End test_validate_fields_feature_class function


@mark.parametrize('names, include_primary, include_geometry, where_clause, expected', [
    (('a', 'b', 'c'), False, True, '', ('', 'a', 'b', 'c')),
    (('a', 'b', 'c'), True, True, '', ('', 'fid', 'a', 'b', 'c')),
    ((), False, True, '', ('',)),
    ((), True, True, '', ('', 'fid')),
    (('a', 'b', 'c'), False, True, 'a = 10', ('', 'a', 'b', 'c')),
    (('a', 'b', 'c'), True, True, "a = 20 AND c = 'asdf'", ('', 'fid', 'a', 'b', 'c')),
    (('a', 'b', 'c'), False, False, '', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, False, '', ('fid', 'a', 'b', 'c')),
    ((), False, False, '', ('fid',)),
    ((), True, False, '', ('fid',)),
    (('a', 'b', 'c'), False, False, 'a = 10', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, False, "a = 20 AND c = 'asdf'", ('fid', 'a', 'b', 'c')),
])
def test_select_feature_class(setup_geopackage, names, include_primary, include_geometry, where_clause, expected):
    """
    Test select method on feature class
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'SELECT_FC'
    a = Field('a', SQLFieldType.integer)
    b = Field('b', SQLFieldType.text, 20)
    c = Field('c', SQLFieldType.text, 50)
    fields = a, b, c
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    cursor = fc.select(fields=names, include_primary=include_primary,
                       include_geometry=include_geometry, where_clause=where_clause)
    assert tuple(name for name, *_ in cursor.description) == expected
    assert not cursor.fetchall()
# End test_select_feature_class function


def test_validate_fields_table(setup_geopackage):
    """
    Test validate fields method on table class
    """
    _, gpkg, _, _ = setup_geopackage
    name = 'VALIDATE_FIELDS_TABLE'
    a = Field('a', SQLFieldType.integer)
    b = Field('b', SQLFieldType.text, 20)
    c = Field('c', SQLFieldType.text, 50)
    tbl = gpkg.create_table(name=name, fields=(a, b, c))
    expected_names = ['fid', a.name, b.name, c.name]
    assert tbl.field_names == expected_names
    fields = tbl._validate_fields(fields=expected_names)
    assert [f.name for f in fields] == [a.name, b.name, c.name]
    fields = tbl._validate_fields(fields=[n.upper() for n in expected_names])
    assert [f.name for f in fields] == [a.name, b.name, c.name]
    assert not tbl._validate_fields(fields='d')
    assert not tbl._validate_fields(fields=1234)
    assert not tbl._validate_fields(fields=())
    assert not tbl._validate_fields(fields=(None, Ellipsis, 1234, object))
# End test_validate_fields_table function


@mark.parametrize('names, include, where_clause, expected', [
    (('a', 'b', 'c'), False, '', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, '', ('fid', 'a', 'b', 'c')),
    ((), False, '', ('fid',)),
    ((), True, '', ('fid',)),
    (('a', 'b', 'c'), False, 'a = 10', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, "a = 20 AND c = 'asdf'", ('fid', 'a', 'b', 'c')),
])
def test_select_table(setup_geopackage, names, include, where_clause, expected):
    """
    Test select method on table class
    """
    _, gpkg, _, _ = setup_geopackage
    name = 'SELECT_TABLE'
    a = Field('a', SQLFieldType.integer)
    b = Field('b', SQLFieldType.text, 20)
    c = Field('c', SQLFieldType.text, 50)
    tbl = gpkg.create_table(name=name, fields=(a, b, c))
    cursor = tbl.select(fields=names, include_primary=include, where_clause=where_clause)
    assert tuple(name for name, *_ in cursor.description) == expected
    assert not cursor.fetchall()
# End test_select_table function


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


def test_exists(tmp_path, fields):
    """
    Test exists methods
    """
    name = 'example'
    path = tmp_path / 'tbl_exists'

    assert not GeoPackage(path).exists('asdf')

    geo = GeoPackage.create(path)
    assert not geo.exists(None)

    tbl = Table(geopackage=None, name=name)
    assert not tbl.exists()

    tbl = geo.create_table(name, fields)
    assert tbl.exists()
# End test_exists function


if __name__ == '__main__':
    pass
