# -*- coding: utf-8 -*-
"""
Test GeoPackage
"""

from pytest import raises

from fudgeo.enumeration import SQLFieldType
from fudgeo.geopkg import (
    FeatureClass, Field, GeoPackage,
    SpatialReferenceSystem, Table)


WGS_1984_UTM_Zone_23N = (
    """PROJCS["WGS_1984_UTM_Zone_23N","""
    """GEOGCS["GCS_WGS_1984","""
    """DATUM["D_WGS_1984","""
    """SPHEROID["WGS_1984",6378137.0,298.257223563]],"""
    """PRIMEM["Greenwich",0.0],"""
    """UNIT["Degree",0.0174532925199433]],"""
    """PROJECTION["Transverse_Mercator"],"""
    """PARAMETER["False_Easting",500000.0],"""
    """PARAMETER["False_Northing",0.0],"""
    """PARAMETER["Central_Meridian",-45.0],"""
    """PARAMETER["Scale_Factor",0.9996],"""
    """PARAMETER["Latitude_Of_Origin",0.0],"""
    """UNIT["Meter",1.0]];IsHighPrecision""")

#
# @fixture
# def setup_geopackage(tmpdir):
#     """
#     Setup Basics
#     """
#     target_path = tmpdir.join('test.gpkg')
#     gpkg = GeoPackage.create(target_path)
#     srs = SRS('WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
#     fields = (
#         Field('int_fld', SQLFieldTypes.integer),
#         Field('text_fld', SQLFieldTypes.text),
#         Field('test_fld_size', SQLFieldTypes.text, 100),
#         Field('test_bool', SQLFieldTypes.boolean))
#     yield target_path, gpkg, srs, fields
#     remove(target_path)
# # End setup_geopackage function


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
# End test_create_geopackage function


def test_create_table(tmp_path):
    """
    Create Table
    """
    path = tmp_path / 'tbl'
    geo = GeoPackage.create(path)
    fields = [Field('AAA', SQLFieldType.integer),
              Field('BBB', SQLFieldType.text, size=10),
              Field('CCC', SQLFieldType.text),
              Field('DDD', SQLFieldType.double)]
    name = 'TTT'
    table = geo.create_table(name, fields)
    assert isinstance(table, Table)
    with raises(ValueError):
        geo.create_table(name, fields)
    cursor = geo.connection.execute(f"""SELECT count(fid) FROM {name}""")
    count, = cursor.fetchone()
    assert count == 0
    table = geo.create_table('ANOTHER')
    assert isinstance(table, Table)
# End test_create_table function


def test_create_feature_class(tmp_path):
    """
    Create Feature Class
    """
    path = tmp_path / 'fc'
    geo = GeoPackage.create(path)
    fields = [Field('AAA', SQLFieldType.integer),
              Field('BBB', SQLFieldType.text, size=10),
              Field('CCC', SQLFieldType.text),
              Field('DDD', SQLFieldType.double)]
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
# End test_create_feature_class function


if __name__ == '__main__':
    pass
