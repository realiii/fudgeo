# -*- coding: utf-8 -*-
"""
Metadata Extension Tests
"""


from pytest import fixture, mark, raises

from crs import WGS_1984_UTM_Zone_23N
from fudgeo.enumeration import GeometryType, MetadataScope, SQLFieldType
from fudgeo.extension.metadata import (
    ColumnReference, GeoPackageReference, Metadata, RowColumnReference,
    RowReference, TableReference)
from fudgeo.geometry import LineString, Point
from fudgeo.geopkg import Field, GeoPackage, SpatialReferenceSystem


@mark.parametrize('on_create, post_create', [
    (True, False),
    (False, False),
    (False, True),
    (True, True),
])
def test_create_geopackage(tmp_path, on_create, post_create):
    """
    Test create geopackage
    """
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_metadata=on_create)
    assert pkg.is_metadata_enabled is on_create
    if not on_create:
        assert pkg.metadata is None
    else:
        assert isinstance(pkg.metadata, Metadata)
    if post_create:
        assert pkg.enable_metadata_extension() is True
        assert pkg.is_metadata_enabled is True
        assert isinstance(pkg.metadata, Metadata)
    pkg.connection.close()
    if path.exists():
        path.unlink()
# End test_create_geopackage function


@fixture(scope='function')
def example1(tmp_path, random_utm_coordinates) -> GeoPackage:
    """
    Geopackage for Example 1
    """
    scopes = (MetadataScope.undefined, MetadataScope.undefined,
              MetadataScope.undefined, MetadataScope.series,
              MetadataScope.dataset, MetadataScope.feature_type,
              MetadataScope.feature, MetadataScope.attribute_type,
              MetadataScope.attribute)
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_metadata=True)
    srs = SpatialReferenceSystem(
        name='WGS_1984_UTM_Zone_23N', organization='EPSG',
        org_coord_sys_id=32623, definition=WGS_1984_UTM_Zone_23N)
    fields = Field(name='overhead_clearance', data_type=SQLFieldType.double),
    roads = pkg.create_feature_class(
        name='roads', srs=srs, shape_type=GeometryType.linestring,
        fields=fields)
    bridge = pkg.create_feature_class(
        name='bridge', srs=srs, shape_type=GeometryType.linestring,
        fields=fields)
    eastings, northings = random_utm_coordinates
    records = []
    for begin_east, end_east, begin_north, end_north in zip(
            eastings[:1000], eastings[1000:2000],
            northings[:1000], northings[1000:2000]):
        line = LineString([(begin_east, begin_north), (end_east, end_north)],
                          srs_id=srs.srs_id)
        records.append((line, 12.3))
    with pkg.connection as conn:
        conn.executemany(f"""
            INSERT INTO {roads.name} (SHAPE, overhead_clearance) 
            VALUES (?, ?)""", records)
        conn.executemany(f"""
            INSERT INTO {bridge.name} (SHAPE, overhead_clearance) 
            VALUES (?, ?)""", records)
    metadata = pkg.metadata
    uri = 'https://www.isotc211.org/2005/gmd'
    for scope in scopes:
        metadata.add_metadata(uri=uri, scope=scope)
    return pkg
# End example1 function


@fixture(scope='function')
def example2(tmp_path, random_utm_coordinates) -> GeoPackage:
    """
    Geopackage for Example 2
    """
    scopes = (MetadataScope.field_session, MetadataScope.undefined,
              MetadataScope.undefined, MetadataScope.undefined,
              MetadataScope.undefined, MetadataScope.undefined,
              MetadataScope.undefined, MetadataScope.undefined,
              MetadataScope.undefined, MetadataScope.feature_type,
              MetadataScope.feature, MetadataScope.attribute,
              MetadataScope.attribute, MetadataScope.feature,
              MetadataScope.attribute, MetadataScope.attribute,
              MetadataScope.feature, MetadataScope.attribute,
              MetadataScope.attribute)
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_metadata=True)
    srs = SpatialReferenceSystem(
        name='WGS_1984_UTM_Zone_23N', organization='EPSG',
        org_coord_sys_id=32623, definition=WGS_1984_UTM_Zone_23N)
    fields = [Field(name='category', data_type=SQLFieldType.integer),
              Field(name='point', data_type=SQLFieldType.integer)]
    poi = pkg.create_feature_class(name='poi', srs=srs, fields=fields)
    eastings, northings = random_utm_coordinates
    records = []
    for i, (easting, northing) in enumerate(zip(eastings, northings)):
        records.append((Point(x=easting, y=northing, srs_id=srs.srs_id),
                        i // 100, easting + northing))
    with pkg.connection as conn:
        conn.executemany(f"""
            INSERT INTO {poi.name} (SHAPE, category, point)
            VALUES (?, ?, ?)""", records)
    metadata = pkg.metadata
    uri = 'https://schemas.opengis.net/iso/19139/'
    for scope in scopes:
        metadata.add_metadata(uri=uri, scope=scope)
    return pkg
# End example2 function


def test_add_metadata_hierarchical_example1(example1):
    """
    Test add metadata using Hierarchical Metadata Example
    """
    pkg = example1
    metadata = pkg.metadata
    connection = metadata._geopackage.connection
    cursor = connection.execute("""SELECT COUNT(1) AS C FROM gpkg_metadata""")
    count, = cursor.fetchone()
    assert count == 9
    cursor = connection.execute("""SELECT id FROM gpkg_metadata""")
    assert [i for i, in cursor.fetchall()] == list(range(1, 10))
    reference = TableReference(table_name='roads', file_id=4, parent_id=1)
    references = [
        TableReference(table_name='roads', file_id=5, parent_id=4),
        TableReference(table_name='roads', file_id=6, parent_id=5),
        ColumnReference(table_name='roads', column_name='overhead_clearance',
                        file_id=8, parent_id=5),
        RowReference(table_name='bridge', row_id=987, file_id=7, parent_id=5),
        RowColumnReference(
            table_name='bridge', column_name='overhead_clearance',
            row_id=987, file_id=7, parent_id=5)
    ]
    metadata.add_references(reference)
    metadata.add_references(references)
    cursor = connection.execute(
        """SELECT COUNT(1) AS C FROM gpkg_metadata_reference""")
    count, = cursor.fetchone()
    assert count == 6
# End test_add_metadata_hierarchical_example1 function


def test_add_metadata_hierarchical_example2(example2):
    """
    Test add metadata using Hierarchical Metadata Example
    """
    pkg = example2
    metadata = pkg.metadata
    connection = metadata._geopackage.connection
    cursor = connection.execute("""SELECT COUNT(1) AS C FROM gpkg_metadata""")
    count, = cursor.fetchone()
    assert count == 19
    cursor = connection.execute("""SELECT id FROM gpkg_metadata""")
    assert [i for i, in cursor.fetchall()] == list(range(1, 20))
    table_name = 'poi'
    references = [
        GeoPackageReference(file_id=1),
        TableReference(table_name=table_name, file_id=1),
        TableReference(table_name=table_name, file_id=10, parent_id=1),
        RowReference(table_name=table_name, row_id=1, file_id=11, parent_id=1),
        RowReference(table_name=table_name, row_id=2, file_id=14, parent_id=1),
        RowReference(table_name=table_name, row_id=3, file_id=17, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='point', row_id=1, file_id=12, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='point', row_id=1, file_id=15, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='point', row_id=1, file_id=18, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='category', row_id=1, file_id=13, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='category', row_id=1, file_id=16, parent_id=1),
        RowColumnReference(table_name=table_name, column_name='category', row_id=1, file_id=19, parent_id=1)
    ]
    metadata.add_references(references)
    cursor = connection.execute(
        """SELECT COUNT(1) AS C FROM gpkg_metadata_reference""")
    count, = cursor.fetchone()
    assert count == 12
    table = pkg.feature_classes[table_name]
    table.drop()
    cursor = connection.execute(
        """SELECT COUNT(1) AS C FROM gpkg_metadata_reference""")
    count, = cursor.fetchone()
    assert count == 1
# End test_add_metadata_hierarchical_example2 function


@mark.parametrize('reference', [
    TableReference(table_name='road', file_id=5, parent_id=4),
    ColumnReference(table_name='road', column_name='asdf', file_id=5, parent_id=4),
    RowReference(table_name='road', row_id=10_000, file_id=5, parent_id=4),
    RowColumnReference(table_name='road', row_id=10_000, column_name='asdf', file_id=5, parent_id=4),
])
def test_table_name_validation(example1, reference):
    """
    Test Table Name Validation in Reference Objects
    """
    with raises(ValueError) as context:
        example1.metadata.add_references(reference)
    assert context.value.args[0].startswith('table name "road" not found in GeoPackage(path=')
# End test_table_name_validation function


@mark.parametrize('reference', [
    ColumnReference(table_name='roads', column_name='asdf', file_id=5, parent_id=4),
    RowColumnReference(table_name='roads', row_id=10_000, column_name='asdf', file_id=5, parent_id=4),
])
def test_column_name_validation(example1, reference):
    """
    Test Column Name Validation in Reference Objects
    """
    with raises(ValueError) as context:
        example1.metadata.add_references(reference)
    assert context.value.args[0].startswith('column name "asdf" not found in table "roads"')
# End test_column_name_validation function


@mark.parametrize('reference', [
    RowReference(table_name='roads', row_id=10_000, file_id=5, parent_id=4),
    RowColumnReference(table_name='roads', row_id=10_000, column_name='overhead_clearance', file_id=5, parent_id=4),
])
def test_row_id_validation(example1, reference):
    """
    Test Row ID Validation in Reference Objects
    """
    with raises(ValueError) as context:
        example1.metadata.add_references(reference)
    assert context.value.args[0].startswith('row id 10000 does not exist in table "roads"')
# End test_row_id_validation function


if __name__ == '__main__':  # pragma: no cover
    pass
