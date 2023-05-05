# -*- coding: utf-8 -*-
"""
Fixtures
"""


from random import randint

from pytest import fixture

from fudgeo.enumeration import SQLFieldType
from fudgeo.geopkg import Field, GeoPackage, SpatialReferenceSystem
from tests.conversion.geo import make_gpkg_geom_header
from tests.crs import WGS_1984_UTM_Zone_23N


@fixture(scope='session')
def header():
    """
    Header
    """
    return make_gpkg_geom_header(4326)
# End header function


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
        Field('int.fld', SQLFieldType.integer),
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
            Field('SELECT', SQLFieldType.timestamp)]
# End fields function


@fixture(scope='session')
def random_utm_coordinates():
    """
    Random UTM Coordinates
    """
    count = 10_000
    eastings = [randint(300000, 700000) for _ in range(count)]
    northings = [randint(0, 4000000) for _ in range(count)]
    return eastings, northings
# End random_utm_coordinates function


if __name__ == '__main__':  # pragma: no cover
    pass
