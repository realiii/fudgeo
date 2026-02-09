# -*- coding: utf-8 -*-
"""
Test GeoPackage
"""


import sys
from datetime import datetime, timedelta
from math import isnan
from random import randint, choice
from sqlite3 import IntegrityError
from string import ascii_uppercase, digits

from pytest import mark, raises

from fudgeo.constant import FID, SHAPE
from fudgeo.enumeration import ShapeType, MetadataScope, FieldType
from fudgeo.extension.metadata import TableReference
from fudgeo.extension.schema import GlobConstraint
from fudgeo.geometry import (
    LineString, LineStringM, LineStringZ, LineStringZM, MultiLineString,
    MultiPoint, MultiPolygon, Point, Polygon, PolygonM)
from fudgeo.geopkg import (
    FeatureClass, Field, GeoPackage, SpatialReferenceSystem, Table)
from fudgeo.extension.ogr import add_ogr_contents, has_ogr_contents
from fudgeo.sql import SELECT_SRS
from tests.crs import WGS_1984_UTM_Zone_23N

# noinspection SqlNoDataSourceInspection
INSERT_POINTS = """
    INSERT INTO {} ({}, "int.fld", text_fld, test_fld_size, test_bool) 
    VALUES (?, ?, ?, ?, ?)
"""
# noinspection SqlNoDataSourceInspection
INSERT_ROWS = """
    INSERT INTO {} ("int.fld", text_fld, test_fld_size, test_bool) 
    VALUES (?, ?, ?, ?)
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
    assert table.primary_key_field.name == FID
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
    assert len(table) == 2
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
    assert tbl.exists
    assert tbl
    assert table.count == 0
    assert len(table) == 0
    # noinspection SqlNoDataSourceInspection
    sql = """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'"""
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == trigger_count
    tbl.drop()
    assert not geo._check_table_exists(name)
    assert not table.exists
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
    assert fc.primary_key_field.name == FID
    assert isinstance(fc, FeatureClass)
    with raises(ValueError):
        geo.create_feature_class(name, srs=srs, fields=fields)
    assert fc.count == 0
    fc = geo.create_feature_class('ANOTHER', srs=srs, spatial_index=False)
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


def test_spatial_reference_equal():
    """
    Test spatial references equal
    """
    srs1 = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    srs2 = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    srs3 = SpatialReferenceSystem(
        'Different_Name', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    assert id(srs1) != id(srs2)
    assert srs1 == srs1
    assert srs1 == srs2
    assert srs1 == srs3
# End test_spatial_reference_equal function


def test_spatial_references(setup_geopackage):
    """
    Test spatial references equal
    """
    _, gpkg, srs, _ = setup_geopackage
    references = gpkg.spatial_references
    assert len(references) == 2
    assert 4326 in references
    assert srs.srs_id in references
    assert srs == references[srs.srs_id]
# End test_spatial_references function


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
        assert fc.drop_spatial_index()
        assert not fc.has_spatial_index
        assert fc.add_spatial_index()
        assert fc.has_spatial_index
    assert isinstance(fc, FeatureClass)
    fc = geo.create_feature_class(name, srs=srs, fields=fields, overwrite=True, spatial_index=add_index)
    assert fc.exists
    assert fc
    assert fc.count == 0
    assert len(fc) == 0
    # noinspection SqlNoDataSourceInspection
    sql = """SELECT count(type) AS C FROM sqlite_master WHERE type = 'trigger'"""
    cursor = conn.execute(sql)
    count, = cursor.fetchone()
    assert count == trigger_count
    fc.drop()
    assert not geo._check_table_exists(name)
    assert not fc.exists
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
    with raises(KeyError):
        _ = geo.feature_classes['a']
    assert isinstance(geo['A'], FeatureClass)
    assert isinstance(geo['a'], FeatureClass)
    for c in 'DEF':
        geo.create_table(c, fields=fields)
    assert set(geo.tables) == set('DEF')
    assert isinstance(geo.tables['F'], Table)
    with raises(KeyError):
        _ = geo.tables['f']
    assert isinstance(geo['F'], Table)
    assert isinstance(geo['f'], Table)
    geo.connection.close()
    if path.exists():
        path.unlink()
# End test_tables_and_feature_classes function


@mark.parametrize('name, geom, has_z, has_m, type_', [
    ('test_points', ShapeType.point, False, False, 'Point'),
    ('test_points_z', ShapeType.point, True, False, 'PointZ'),
    ('test_points_m', ShapeType.point, False, True, 'PointM'),
    ('test_points_zm', ShapeType.point, True, True, 'PointZM'),
    ('test_lines', ShapeType.linestring, False, False, 'LineString'),
    ('test_lines_z', ShapeType.linestring, True, False, 'LineStringZ'),
    ('test_lines_m', ShapeType.linestring, False, True, 'LineStringM'),
    ('test_lines_zm', ShapeType.linestring, True, True, 'LineStringZM'),
    ('test_polygons', ShapeType.polygon, False, False, 'Polygon'),
    ('test_polygons_z', ShapeType.polygon, True, False, 'PolygonZ'),
    ('test_polygons_m', ShapeType.polygon, False, True, 'PolygonM'),
    ('test_polygons_zm', ShapeType.polygon, True, True, 'PolygonZM'),
])
def test_create_feature_class_options(setup_geopackage, name, geom, has_z, has_m, type_):
    """
    Test creating feature classes with different shape options
    """
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        name, shape_type=geom, srs=srs, fields=flds,
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
    _, gpkg, srs, flds = setup_geopackage
    name = 'SELECT'
    fc = gpkg.create_feature_class(
        name, shape_type=ShapeType.polygon, srs=srs, fields=flds)
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        name, srs, fields=flds, shape_type=ShapeType.point,
        spatial_index=add_index)
    assert fc.has_spatial_index is add_index
    assert isinstance(fc, FeatureClass)
    count = 10000
    rows = random_points_and_attrs(count, srs.srs_id)
    with gpkg.connection as conn:
        conn.executemany(INSERT_POINTS.format(fc.escaped_name, fc.geometry_column_name), rows)
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.polygon,
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
    assert not fc.is_empty
    fc.delete()
    assert fc.is_empty
# End test_insert_poly function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_multi_poly(setup_geopackage, add_index):
    """
    Test create a feature class with "multi polygons"
    """
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.multi_polygon,
        spatial_index=add_index)
    assert fc.is_multi_part
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
    assert poly.srs_id == srs.srs_id
    new_srs_id = 1234
    fc._update_srs_id([(poly, 'a', 'b')], srs_id=new_srs_id, parts=True)
    poly.srs_id = new_srs_id
    assert poly.srs_id == new_srs_id
    for g in poly:
        assert g.srs_id == new_srs_id
# End test_insert_multi_poly function


@mark.parametrize('add_index', [
    False, True
])
def test_insert_lines(setup_geopackage, add_index):
    """
    Test insert a line
    """
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.multi_point,
        spatial_index=add_index)
    assert fc.is_multi_part
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    tbl = 'SELECT'
    kwargs = dict(
        name=tbl, srs=srs, fields=flds,
        shape_type=ShapeType.linestring,
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds,
        shape_type=ShapeType.multi_linestring,
        z_enabled=False, m_enabled=False, spatial_index=add_index)
    assert fc.is_multi_part
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
    _, gpkg, srs, flds = setup_geopackage
    fc = gpkg.create_feature_class(
        'SELECT', srs, fields=flds, shape_type=ShapeType.polygon,
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
    select = Field('select', data_type=FieldType.integer, is_nullable=False)
    union = Field('UnIoN', data_type=FieldType.text, size=20, is_nullable=False)
    all_ = Field('ALL', data_type=FieldType.text, size=50)
    example_dot = Field('why.do.this', data_type=FieldType.text,
                        size=123, is_nullable=False, default='.......')
    regular = Field('regular', data_type=FieldType.integer)
    fields = select, union, all_, example_dot, regular
    assert repr(select) == '"select" INTEGER NOT NULL'
    assert repr(union) == '"UnIoN" TEXT(20) NOT NULL'
    assert repr(all_) == '"ALL" TEXT(50)'
    assert repr(example_dot) == """"why.do.this" TEXT(123) default '.......' NOT NULL"""
    assert repr(regular) == 'regular INTEGER'
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    expected_names = [FID, SHAPE, select.name, union.name, all_.name,
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

    (_, _, select_field, union_field,
     all_field, dot_field, regular_field) = fc.fields

    assert select_field == select
    assert union_field == union
    assert all_field == all_
    assert dot_field == example_dot
    assert regular_field == regular
# End test_escaped_columns function


def test_escaped_table(setup_geopackage):
    """
    Test ability to add fields that need escaping to be added
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'SELECT'
    select = Field('a', FieldType.integer)
    union = Field('b', FieldType.text, 20)
    all_ = Field('c', FieldType.text, 50)
    fields = select, union, all_
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=fields)
    assert fc.is_empty
    expected_names = [FID, SHAPE, select.name, union.name, all_.name]
    assert fc.field_names == expected_names
    rows = [(Point(x=1, y=2, srs_id=srs.srs_id), 1, 'asdf', 'lmnop'),
            (Point(x=3, y=4, srs_id=srs.srs_id), 2, 'qwerty', 'xyz')]
    with fc.geopackage.connection as conn:
        # noinspection SqlNoDataSourceInspection
        conn.executemany(
            f"""INSERT INTO {fc.escaped_name} ({fc.geometry_column_name}, {select.escaped_name}, 
                            {union.escaped_name}, {all_.escaped_name})
                VALUES (?, ?, ?, ?)""", rows)
    assert not fc.is_empty
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
    a = Field('a', FieldType.integer)
    b = Field('b', FieldType.text, 20)
    c = Field('c', FieldType.text, 50)
    flds = a, b, c
    fc = gpkg.create_feature_class(name=name, srs=srs, fields=flds)
    expected_names = [FID, SHAPE, a.name, b.name, c.name]
    assert fc.field_names == expected_names
    flds = fc._validate_fields(fields=expected_names)
    assert [f.name for f in flds] == [a.name, b.name, c.name]
    flds = fc._validate_fields(fields=[n.upper() for n in expected_names])
    assert [f.name for f in flds] == [a.name, b.name, c.name]
    assert not fc._validate_fields(fields='d')
    assert not fc._validate_fields(fields=1234)
    assert not fc._validate_fields(fields=())
    assert not fc._validate_fields(fields=(None, Ellipsis, 1234, object))
# End test_validate_fields_feature_class function


@mark.parametrize('names, include_primary, include_geometry, where_clause, expected', [
    (('a', 'b', 'c'), False, True, '', ('', 'a', 'b', 'c')),
    (('a', 'b', 'c'), True, True, '', ('', FID, 'a', 'b', 'c')),
    ((), False, True, '', ('',)),
    ((), True, True, '', ('', FID)),
    (('a', 'b', 'c'), False, True, 'a = 10', ('', 'a', 'b', 'c')),
    (('a', 'b', 'c'), True, True, "a = 20 AND c = 'asdf'", ('', FID, 'a', 'b', 'c')),
    (('a', 'b', 'c'), False, False, '', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, False, '', (FID, 'a', 'b', 'c')),
    ((), False, False, '', (FID,)),
    ((), True, False, '', (FID,)),
    (('a', 'b', 'c'), False, False, 'a = 10', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, False, "a = 20 AND c = 'asdf'", (FID, 'a', 'b', 'c')),
])
def test_select_feature_class(setup_geopackage, names, include_primary, include_geometry, where_clause, expected):
    """
    Test select method on feature class
    """
    _, gpkg, srs, _ = setup_geopackage
    name = 'SELECT_FC'
    a = Field('a', FieldType.integer)
    b = Field('b', FieldType.text, 20)
    c = Field('c', FieldType.text, 50)
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
    a = Field('a', FieldType.integer)
    b = Field('b', FieldType.text, 20)
    c = Field('c', FieldType.text, 50)
    tbl = gpkg.create_table(name=name, fields=(a, b, c))
    expected_names = [FID, a.name, b.name, c.name]
    assert tbl.field_names == expected_names
    flds = tbl._validate_fields(fields=expected_names)
    assert [f.name for f in flds] == [a.name, b.name, c.name]
    flds = tbl._validate_fields(fields=[n.upper() for n in expected_names])
    assert [f.name for f in flds] == [a.name, b.name, c.name]
    assert not tbl._validate_fields(fields='d')
    assert not tbl._validate_fields(fields=1234)
    assert not tbl._validate_fields(fields=())
    assert not tbl._validate_fields(fields=(None, Ellipsis, 1234, object))
# End test_validate_fields_table function


@mark.parametrize('names, include, where_clause, expected', [
    (('a', 'b', 'c'), False, '', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, '', (FID, 'a', 'b', 'c')),
    ((), False, '', (FID,)),
    ((), True, '', (FID,)),
    (('a', 'b', 'c'), False, 'a = 10', ('a', 'b', 'c')),
    (('a', 'b', 'c'), True, "a = 20 AND c = 'asdf'", (FID, 'a', 'b', 'c')),
])
def test_select_table(setup_geopackage, names, include, where_clause, expected):
    """
    Test select method on table class
    """
    _, gpkg, _, _ = setup_geopackage
    name = 'SELECT_TABLE'
    a = Field('a', FieldType.integer)
    b = Field('b', FieldType.text, 20)
    c = Field('c', FieldType.text, 50)
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


@mark.parametrize('name, data_type, size, is_nullable, default, expected', [
    ('a', FieldType.integer, None, True, None, 'a INTEGER'),
    ('a', FieldType.integer, None, False, 1234, 'a INTEGER default 1234 NOT NULL'),
    ('a', FieldType.integer, None, True, 1234, 'a INTEGER default 1234'),
    ('b', FieldType.text, 256, True, None, 'b TEXT(256)'),
    ('b', FieldType.text, 256, False, None, 'b TEXT(256) NOT NULL'),
    ('b', FieldType.text, 256, False, 'asdf', "b TEXT(256) default 'asdf' NOT NULL"),
    ('SELECT', FieldType.integer, 256, False, None, '"SELECT" INTEGER NOT NULL'),
    ('SELECT', FieldType.text, 256, False, 'asdf', """"SELECT" TEXT(256) default 'asdf' NOT NULL"""),
])
def test_field_repr(name, data_type, size, is_nullable, default, expected):
    """
    Test Field Representation
    """
    field = Field(name=name, data_type=data_type, size=size,
                  is_nullable=is_nullable, default=default)
    assert repr(field) == expected
# End test_field_repr function


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
    assert not tbl.exists

    tbl = geo.create_table(name, fields)
    assert tbl.exists
# End test_exists function


def test_copy_table(setup_geopackage):
    """
    Test copy method for Table
    """
    _, gpkg, _, flds = setup_geopackage
    another_name = 'another_table'
    gpkg.create_table(another_name, fields=flds)
    name = 'source_tbl'
    tbl = gpkg.create_table(name, fields=flds)
    assert isinstance(tbl, Table)
    count = 1000
    rows = random_points_and_attrs(count, 4326)
    rows = [row[1:] for row in rows]
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS.format(tbl.escaped_name), rows)
    assert tbl.count == count

    with raises(ValueError):
        tbl.copy(another_name)
    with raises(ValueError):
        tbl.copy(name)

    result = tbl.copy(another_name, overwrite=True)
    assert isinstance(result, Table)
    assert result.count == count

    desc = 'The quick brown fox'
    sql = f'{tbl.primary_key_field.escaped_name} > 500'
    result = tbl.copy(another_name, description=desc, where_clause=sql, overwrite=True)
    assert isinstance(result, Table)
    assert result.exists
    assert result.description == desc
    assert result.count == 500
# End test_copy_table function


@mark.parametrize('name, count, sql, sub_count', [
    ('areacode_a', 325, """STATE = 'TX'""", 27),
    ('detail_l', 14_640, """Type = 1""", 12_633),
    ('places_p', 2176, """ST = 'TN'""", 427),
])
def test_copy_feature_class(setup_geopackage, data_path, name, count, sql, sub_count):
    """
    Test copy method for Feature Class
    """
    _, target_gpkg, _, _ = setup_geopackage
    path = data_path / 'copy.gpkg'
    assert path.is_file()
    source_gpkg = GeoPackage(path)

    fc = FeatureClass(geopackage=source_gpkg, name=name)
    assert fc.exists
    assert fc.count == count

    with raises(ValueError):
        fc.copy(name)

    desc = 'The quick brown fox'
    result = fc.copy(
        name=f'{name}_copy', geopackage=target_gpkg, description=desc,
        geom_name=SHAPE)
    assert isinstance(result, FeatureClass)
    assert result.exists
    assert result.count == count
    assert result.geometry_column_name == SHAPE

    desc = 'The quick brown fox'
    result = fc.copy(
        name=f'{name}_copy', geopackage=target_gpkg, description=desc,
        geom_name=SHAPE, where_clause=sql, overwrite=True)
    assert isinstance(result, FeatureClass)
    assert result.exists
    assert result.count == sub_count
    assert result.geometry_column_name == SHAPE
# End test_copy_feature_class function


def test_copy_feature_class_narrow(setup_geopackage, data_path):
    """
    Test copy method for narrow Feature Class (only has fid and geometry)
    """
    count = 325
    _, target_gpkg, _, _ = setup_geopackage
    path = data_path / 'copy.gpkg'
    assert path.is_file()
    source_gpkg = GeoPackage(path)

    fc = FeatureClass(geopackage=source_gpkg, name='areacode_narrow_a')
    assert fc.exists
    assert fc.count == count

    result = fc.copy(name=fc.name, geopackage=target_gpkg, geom_name=SHAPE)
    assert isinstance(result, FeatureClass)
    assert result.exists
    assert result.count == count
    assert result.geometry_column_name == SHAPE

    sql = f"""{fc.primary_key_field.escaped_name} <= 100"""
    result = fc.copy(name=fc.name, where_clause=sql,
                     geopackage=target_gpkg, geom_name=SHAPE, overwrite=True)
    assert isinstance(result, FeatureClass)
    assert result.exists
    assert result.count == 100
    assert result.geometry_column_name == SHAPE
# End test_copy_feature_class_narrow function


@mark.parametrize('name, count, out_count', [
    ('areacode_a', 325, 4826),
    ('areacode_narrow_a', 325, 4826),
    ('detail_l', 14_640, 14_640),
    ('places_p', 2176, 2176),
])
def test_explode_feature_class(setup_geopackage, data_path, name, count, out_count):
    """
    Test explode method for Feature Class
    """
    _, target_gpkg, _, _ = setup_geopackage
    path = data_path / 'copy.gpkg'
    assert path.is_file()
    source_gpkg = GeoPackage(path)

    fc = FeatureClass(geopackage=source_gpkg, name=name)
    assert fc.exists
    assert fc.count == count

    with raises(ValueError):
        fc.explode(name)

    result = fc.explode(name=f'{name}_single', geopackage=target_gpkg)
    assert isinstance(result, FeatureClass)
    assert result.exists
    assert result.count == out_count
# End test_explode_feature_class function


@mark.parametrize('is_unique, is_ascending', [
    (True, True), (True, False), (False, True), (False, False)
])
def test_add_remove_index(data_path, mem_gpkg, is_unique, is_ascending):
    """
    Test add / remove index on a Feature Class
    """
    path = data_path / 'copy.gpkg'
    assert path.is_file()
    gpkg = GeoPackage(path)
    name = 'detail_l'
    fc = gpkg[name].copy(name=name, geopackage=mem_gpkg, where_clause='FID <= 500')
    assert fc.exists
    assert fc.count == 252
    index_name = 'detail_l_idx'
    assert not fc._check_index_exists(index_name)

    if is_unique:
        with raises(IntegrityError):
            fc.add_attribute_index(
                index_name, fields=('Type', 'Type_Desc'),
                is_unique=is_unique, is_ascending=is_ascending)
    else:
        assert fc.add_attribute_index(
            index_name, fields=('Type', 'Type_Desc'),
            is_unique=is_unique, is_ascending=is_ascending)
        assert fc._check_index_exists(index_name)
        assert fc.drop_attribute_index(index_name)
        assert not fc._check_index_exists(index_name)
# End test_add_remove_index function


def test_table_add_drop_fields(setup_geopackage):
    """
    Test add / drop fields on a Table
    """
    _, gpkg, _, flds = setup_geopackage
    name = 'source_tbl'
    tbl = gpkg.create_table(name, fields=flds)
    assert isinstance(tbl, Table)
    count = 1000
    rows = random_points_and_attrs(count, 4326)
    rows = [row[1:] for row in rows]
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS.format(tbl.escaped_name), rows)
    assert tbl.count == count
    assert not tbl.add_fields(fields=flds)

    fld = Field('a', FieldType.integer)
    assert tbl.add_fields(fields=fld)
    assert 'a' in tbl.field_names

    flds = fld, Field('b', FieldType.text, 20), Field('c', FieldType.real)
    assert len(set(flds)) == 3
    assert tbl.add_fields(fields=flds)
    assert 'b' in tbl.field_names
    assert 'c' in tbl.field_names

    fld = Field('d', FieldType.text, 20)
    assert not tbl.drop_fields(fields=fld)
    assert not tbl.drop_fields(fields=[fld])

    assert tbl.drop_fields(fields=flds)
    assert 'a' not in tbl.field_names
    assert 'b' not in tbl.field_names
    assert 'c' not in tbl.field_names

    assert not tbl.drop_fields(fields=tbl.primary_key_field)
# End test_table_add_drop_fields function


def test_setup_geo_file_based(setup_geopackage):
    """
    Test that conftest is left in file based state
    """
    _, gpkg, _, _ = setup_geopackage
    assert gpkg.path.is_file()
# End test_setup_geo_file_based function


@mark.parametrize('use_index, use_ogr, use_meta, use_schema', [
    (False, False, False, False),
    (True, False, False, False),
    (False, True, False, False),
    (False, False, True, False),
    (False, False, False, True),
    (True, True, True, True),
    (False, True, True, True),
    (True, False, True, True),
    (True, True, False, True),
    (True, True, True, False),
])
def test_rename_feature_class(setup_geopackage, use_index, use_ogr, use_meta, use_schema):
    """
    Test Rename Feature Class
    """
    _, gpkg, srs, flds = setup_geopackage
    name = 'asdf'
    fc = gpkg.create_feature_class(
        name=name, srs=srs, fields=flds, shape_type=ShapeType.point,
        spatial_index=use_index)
    if use_ogr:
        add_ogr_contents(gpkg.connection, name=fc.name, escaped_name=fc.escaped_name)
    assert fc.has_spatial_index is use_index
    assert isinstance(fc, FeatureClass)
    count = 100
    rows = random_points_and_attrs(count, srs.srs_id)
    with gpkg.connection as conn:
        conn.executemany(INSERT_POINTS.format(fc.escaped_name, fc.geometry_column_name), rows)
    if use_meta:
        gpkg.enable_metadata_extension()
        assert gpkg.is_metadata_enabled
        metadata = gpkg.metadata
        scopes = (MetadataScope.undefined, MetadataScope.undefined,
                  MetadataScope.undefined, MetadataScope.series)
        for scope in scopes:
            metadata.add_metadata(
                uri='https://schemas.opengis.net/iso/19139/',
                scope=scope)
        reference = TableReference(table_name=name, file_id=4, parent_id=1)
        metadata.add_references(reference)
    if use_schema:
        gpkg.enable_schema_extension()
        assert gpkg.is_schema_enabled
        schema = gpkg.schema
        constraint = GlobConstraint(name='numeric', pattern='[0-9]')
        schema.add_constraints(constraint)
        schema.add_column_definition(
            table_name=name, column_name=flds[0].name,
            constraint_name=constraint.name)

    assert fc.name == name
    new_name = f'{name}_renamed'
    fc.rename(new_name)
    assert fc.name == new_name
    assert fc.exists
    assert fc.count == count
    assert fc.has_spatial_index is use_index

    if use_ogr:
        with fc.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT feature_count 
                    FROM gpkg_ogr_contents 
                    WHERE table_name = '{new_name}'""")
            ogr_count, = cursor.fetchone()
            assert ogr_count == count
    if use_meta:
        with fc.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT COUNT(1) AS CNT 
                    FROM gpkg_metadata_reference 
                    WHERE table_name = '{new_name}'""")
            rec_count, = cursor.fetchone()
            assert rec_count == 1
    if use_schema:
        with fc.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT COUNT(1) AS CNT 
                    FROM gpkg_data_columns 
                    WHERE table_name = '{new_name}'""")
            rec_count, = cursor.fetchone()
            assert rec_count == 1

# End test_rename_feature_class function


@mark.parametrize('use_meta, use_schema', [
    (False, False),
    (False, True),
    (True, False),
    (True, True),
])
def test_rename_table(setup_geopackage, use_meta, use_schema):
    """
    Test Rename Table
    """
    _, gpkg, srs, flds = setup_geopackage
    name = 'asdf'
    tbl = gpkg.create_table(name=name, fields=flds)
    assert isinstance(tbl, Table)
    count = 100
    rows = random_points_and_attrs(count, srs.srs_id)
    rows = [row[1:] for row in rows]
    with gpkg.connection as conn:
        conn.executemany(INSERT_ROWS.format(tbl.escaped_name), rows)
    if use_meta:
        gpkg.enable_metadata_extension()
        assert gpkg.is_metadata_enabled
        metadata = gpkg.metadata
        scopes = (MetadataScope.undefined, MetadataScope.undefined,
                  MetadataScope.undefined, MetadataScope.series)
        for scope in scopes:
            metadata.add_metadata(
                uri='https://schemas.opengis.net/iso/19139/',
                scope=scope)
        reference = TableReference(table_name=name, file_id=4, parent_id=1)
        metadata.add_references(reference)
    if use_schema:
        gpkg.enable_schema_extension()
        assert gpkg.is_schema_enabled
        schema = gpkg.schema
        constraint = GlobConstraint(name='numeric', pattern='[0-9]')
        schema.add_constraints(constraint)
        schema.add_column_definition(
            table_name=name, column_name=flds[0].name,
            constraint_name=constraint.name)

    assert tbl.name == name
    new_name = f'{name}_renamed'
    tbl.rename(new_name)
    assert tbl.name == new_name
    assert tbl.exists
    assert tbl.count == count

    if use_meta:
        with tbl.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT COUNT(1) AS CNT 
                    FROM gpkg_metadata_reference 
                    WHERE table_name = '{new_name}'""")
            rec_count, = cursor.fetchone()
            assert rec_count == 1
    if use_schema:
        with tbl.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT COUNT(1) AS CNT 
                    FROM gpkg_data_columns 
                    WHERE table_name = '{new_name}'""")
            rec_count, = cursor.fetchone()
            assert rec_count == 1

    tbl.drop_fields(flds[0])

    if use_schema:
        with tbl.geopackage.connection as conn:
            cursor = conn.execute(
                f"""SELECT COUNT(1) AS CNT 
                    FROM gpkg_data_columns 
                    WHERE table_name = '{new_name}'""")
            rec_count, = cursor.fetchone()
            assert rec_count == 0
# End test_rename_table function


@mark.parametrize('pk_name', [
    FID, 'id', 'OBJECTID',
])
def test_create_elements_pk_name(tmp_path, fields, pk_name):
    """
    Create Table and Feature Class using specified primary key name
    """
    name = 'asdf'
    path = tmp_path / 'tbl'
    geo = GeoPackage.create(path)
    table = geo.create_table(f'{name}_table', fields=fields, pk_name=pk_name)
    assert isinstance(table, Table)
    assert table.primary_key_field.name == pk_name

    table2 = Table.create(
        geopackage=geo, name=f'{name}_table2', fields=fields, pk_name=pk_name)
    assert isinstance(table2, Table)
    assert table2.primary_key_field.name == pk_name

    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    fc = geo.create_feature_class(
        f'{name}_fc', srs=srs, fields=fields, pk_name=pk_name)
    assert isinstance(fc, FeatureClass)
    assert fc.primary_key_field.name == pk_name

    fc2 = FeatureClass.create(
        geopackage=geo, name=f'{name}_fc2', srs=srs, fields=fields,
        pk_name=pk_name, shape_type=ShapeType.point)
    assert isinstance(fc2, FeatureClass)
    assert fc2.primary_key_field.name == pk_name

    if path.exists():
        path.unlink()
# End test_create_elements_pk_name function


if __name__ == '__main__':  # pragma: no cover
    pass
