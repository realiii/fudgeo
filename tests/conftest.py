# -*- coding: utf-8 -*-
"""
Fixtures
"""


from pathlib import Path
from random import randint
from typing import Generator

from pytest import fixture

from fudgeo.enumeration import FieldType
from fudgeo.geopkg import (
    Field, GeoPackage, MemoryGeoPackage, SpatialReferenceSystem)
from tests.geo import make_gpkg_geom_header
from tests.crs import WGS_1984_UTM_Zone_23N


@fixture(scope='session')
def header():
    """
    Header for Envelope Code 0
    """
    return lambda env_code: make_gpkg_geom_header(4326, env_code=env_code)
# End header function


@fixture
def setup_geopackage(tmp_path):
    """
    Setup Basics
    """
    path = tmp_path.joinpath('test.gpkg')
    # NOTE toggle for testing using memory
    pkg = GeoPackage.create(path)
    # pkg = MemoryGeoPackage.create(path)
    srs = SpatialReferenceSystem(
        'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, WGS_1984_UTM_Zone_23N)
    pkg.add_spatial_reference(srs)
    fields = (
        Field('int.fld', FieldType.integer),
        Field('text_fld', FieldType.text),
        Field('test_fld_size', FieldType.text, 100),
        Field('test_bool', FieldType.boolean),
        Field('test_timestamp', FieldType.timestamp))
    yield path, pkg, srs, fields
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            pass
# End setup_geopackage function


@fixture
def fields():
    """
    Fields
    """
    return [Field('AAA', FieldType.integer),
            Field('BBB', FieldType.text, size=10),
            Field('CCC', FieldType.text),
            Field('DDD', FieldType.double),
            Field('EEE', FieldType.datetime),
            Field('SELECT', FieldType.timestamp)]
# End fields function


@fixture
def fields_extended():
    """
    Fields extended with aliases and comments
    """
    return [Field('AAA', FieldType.integer, alias='An Alias for AAA', comment='This is a comment for AAA'),
            Field('BBB', FieldType.text, size=10, alias=' the bees knees'),
            Field('CCC', FieldType.text, alias='', comment='the quick brown fox jumps over the lazy dog'),
            Field('DDD', FieldType.double),
            Field('EEE', FieldType.datetime),
            Field('SELECT', FieldType.timestamp, alias='The SELECT Field', comment='This is the SELECT Field')
            ]
# End fields_extended function


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


@fixture(scope='session')
def data_path() -> Path:
    """
    Data Path
    """
    return Path(__file__).parent.parent.joinpath('data')
# End data_path function


@fixture(scope='function')
def mem_gpkg(tmp_path) -> Generator[MemoryGeoPackage, None, None]:
    """
    Fresh MemoryGeoPackage
    """
    gpkg = MemoryGeoPackage.create()
    yield gpkg
    gpkg.connection.close()
# End mem_gpkg function


if __name__ == '__main__':  # pragma: no cover
    pass
