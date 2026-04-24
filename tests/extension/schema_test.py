# -*- coding: utf-8 -*-
"""
Schema Extension Tests
"""


from pytest import mark, raises

from fudgeo.enumeration import ConstraintType, FieldType
from fudgeo.extension.schema import (
    EnumerationConstraint, GlobConstraint, RangeConstraint, Schema)
from fudgeo.geopkg import Field, GeoPackage


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
    pkg = GeoPackage.create(path, enable_schema=on_create)
    fields = [Field(name='some_field_name', data_type=FieldType.double),
              Field(name='bobloblaw', data_type=FieldType.blob)]
    tbl = pkg.create_table(name='the_table', fields=fields)
    assert pkg.is_schema_enabled is on_create
    if not on_create:
        assert pkg.metadata is None
    else:
        assert isinstance(pkg.schema, Schema)
    if post_create:
        assert pkg.enable_schema_extension() is True
        assert pkg.is_schema_enabled is True
        assert isinstance(pkg.schema, Schema)
    tbl.drop()
    pkg.connection.close()
    if path.exists():
        try:
            path.unlink()
        except PermissionError:
            pass
# End test_create_geopackage function


def test_add_constraints(tmp_path):
    """
    Add Constraints
    """
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_schema=True)
    constraint = RangeConstraint(name='sampleRange', min_value=1, max_value=10)
    constraints = [
        EnumerationConstraint(name='sampleEnum', values=[1, 3, 5, 7, 9]),
        GlobConstraint(name='sampleGlob', pattern='[1-2][0-9][0-9][0-9]'),
    ]
    pkg.schema.add_constraints(constraint)
    pkg.schema.add_constraints(constraints)
    cursor = pkg.connection.execute(
        """SELECT COUNT(1) AS C FROM gpkg_data_column_constraints""")
    count, = cursor.fetchone()
    assert count == 7
# End test_add_constraints function


def test_add_enumeration(tmp_path):
    """
    Add Enumeration Constraints
    """
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_schema=True)
    constraints = (
        EnumerationConstraint(name='sampleEnum1', values=[7, 9, 11]),
        EnumerationConstraint(name='sampleEnum2', values=[1, 3, 5], descriptions=['one', 'three', 'five']),
        EnumerationConstraint(name='sampleEnum3', values=['A', 'B', 'C'], descriptions=['Ehh', 'Bee', 'See']),
    )
    pkg.schema.add_constraints(constraints)
    cursor = pkg.connection.execute(
        """SELECT constraint_name, constraint_type, value, description 
           FROM gpkg_data_column_constraints""")
    data = cursor.fetchall()
    assert len(data) == 9
    assert data == [
        ('sampleenum1', 'enum', '7', '7'),
        ('sampleenum1', 'enum', '9', '9'),
        ('sampleenum1', 'enum', '11', '11'),
        ('sampleenum2', 'enum', '1', 'one'),
        ('sampleenum2', 'enum', '3', 'three'),
        ('sampleenum2', 'enum', '5', 'five'),
        ('sampleenum3', 'enum', 'A', 'Ehh'),
        ('sampleenum3', 'enum', 'B', 'Bee'),
        ('sampleenum3', 'enum', 'C', 'See')]
    pkg.create_table(name='the_table', fields=[Field(name='the_field', data_type=FieldType.text)])
    pkg.schema.add_column_definition(
        table_name='the_table', column_name='the_field',
        constraint_name='sampleEnum2')
    pkg.schema.add_column_definition(
        table_name='the_table', column_name='the_field',
        constraint_name='sampleEnum3')
    cursor = pkg.connection.execute("""SELECT * FROM gpkg_data_columns""")
    assert cursor.fetchall() == [('the_table', 'the_field', None, None, None, None, 'sampleenum3')]
# End test_add_enumeration function


@mark.parametrize('table_name, column_name, name, title, description, mime_type, constraint_name, msg', [
    ('table_name', 'column_name', None, None, None, None, None, 'table name "table_name" not found'),
    ('the_table', 'column_name', None, None, None, None, None, 'column name "column_name" not found'),
    ('the_table', 'bobloblaw', None, None, None, None, None, 'expected mime_type value for blob column'),
    ('the_table', 'some_field_name', None, None, None, None, 'SELECT', 'constraint "SELECT" not found'),
])
def test_add_column_definition_validation(tmp_path, table_name, column_name, name,
                                          title, description, mime_type,
                                          constraint_name, msg):
    """
    Test add column definition validation steps
    """
    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_schema=True)
    fields = [Field(name='some_field_name', data_type=FieldType.double),
              Field(name='bobloblaw', data_type=FieldType.blob)]
    pkg.create_table(name='the_table', fields=fields)
    schema = pkg.schema
    if msg:
        with raises(ValueError) as context:
            schema.add_column_definition(
                table_name, column_name, name, title, description,
                mime_type, constraint_name)
        assert context.value.args[0].startswith(msg)
    if constraint_name:
        constraint = GlobConstraint(name=constraint_name, pattern='[0-9]')
        schema.add_constraints(constraint)
        cursor = pkg.connection.execute("""SELECT * FROM gpkg_data_column_constraints""")
        records = cursor.fetchall()
        assert len(records) == 1
        schema.add_column_definition(
            table_name, column_name, name, title, description,
            mime_type, constraint_name)
# End test_add_column_definition_validation function


def test_copy_testing(tmp_path, mem_gpkg):
    """
    Test copy schema testing
    """
    table_name = 'the_table'
    constraint_name = 'sample_glob'
    column_name = 'some_field_name'
    name = 'Some Field Name'
    title = 'The title for Some Field Name'
    description = 'The description for Some Field Name'

    path = tmp_path / 'test.gpkg'
    pkg = GeoPackage.create(path, enable_schema=True)
    fields = [Field(name=column_name, data_type=FieldType.double),
              Field(name='bobloblaw', data_type=FieldType.blob)]
    tbl = pkg.create_table(name=table_name, fields=fields)
    schema = pkg.schema

    constraint = GlobConstraint(name=constraint_name, pattern='[0-9]')
    schema.add_constraints(constraint)
    sql_constraints = """
        SELECT COUNT(1) AS CNT
        FROM gpkg_data_column_constraints"""
    sql = """
        SELECT COUNT(1) AS CNT
        FROM gpkg_data_columns"""

    cursor = pkg.connection.execute(sql_constraints)
    count,  = cursor.fetchone()
    assert count == 1

    schema.add_column_definition(
        table_name, column_name=column_name, name=name, title=title,
        description=description, constraint_name=constraint_name)

    cursor = pkg.connection.execute(sql)
    count,  = cursor.fetchone()
    assert count == 1

    tbl.copy('the_copy')

    cursor = pkg.connection.execute(sql_constraints)
    count,  = cursor.fetchone()
    assert count == 1
    cursor = pkg.connection.execute(sql)
    count,  = cursor.fetchone()
    assert count == 2

    tbl.copy('outside', geopackage=mem_gpkg)
    cursor = mem_gpkg.connection.execute(sql_constraints)
    count,  = cursor.fetchone()
    assert count == 1
    cursor = mem_gpkg.connection.execute(sql)
    count,  = cursor.fetchone()
    assert count == 1

    tbl = tbl.copy('outside2', geopackage=mem_gpkg)
    cursor = mem_gpkg.connection.execute(sql_constraints)
    count,  = cursor.fetchone()
    assert count == 2
    cursor = mem_gpkg.connection.execute(sql)
    count,  = cursor.fetchone()
    assert count == 2

    tbl.copy('outside3', geopackage=mem_gpkg)
    cursor = mem_gpkg.connection.execute(sql_constraints)
    count,  = cursor.fetchone()
    assert count == 2
    cursor = mem_gpkg.connection.execute(sql)
    count,  = cursor.fetchone()
    assert count == 3
# End test_add_column_definition_validation function


@mark.parametrize('name, values, description, count, exception', [
    ('a', [1, 2, 3], 'asdf', 3, None),
    ('b', (1, 2, 3), 'asdf', 3, None),
    ('c', (1, 2, 3, 3), 'asdf', 3, None),
    ('d', [], 'asdf', -1, ValueError),
    ('e', (), 'asdf', -1, ValueError),
    (None, (), 'asdf', -1, TypeError),
])
def test_enumeration_constraint(name, values, description, count, exception):
    """
    Test enumeration constraint
    """
    constraint = EnumerationConstraint(name, values, description)
    if exception:
        with raises(exception):
            constraint.validate()
    else:
        assert len(constraint.as_records()) == count
# End test_enumeration_constraint function


@mark.parametrize('name, pattern, description, exception', [
    ('a', '[0-9]', 'asdf', None),
    ('b', None, 'asdf', TypeError),
    ('c', 123, 'asdf', TypeError),
    ('d', Ellipsis, 'asdf', TypeError),
])
def test_glob_constraint(name, pattern, description, exception):
    """
    Test glob constraint
    """
    constraint = GlobConstraint(name, pattern, description)
    if exception:
        with raises(exception):
            constraint.validate()
    else:
        expected = [
            (ConstraintType.glob, name, pattern, None, None,
             None, None, description)]
        assert constraint.as_records() == expected
# End test_glob_constraint function


@mark.parametrize('name, min_value, max_value, min_inclusive, max_inclusive, description, exception', [
    ('a', 10, 100, True, True, 'asdf', None),
    ('b', 100, 10, True, True, 'asdf', ValueError),
    ('c', 100, 100, True, True, 'asdf', ValueError),
    ('d', None, 100, True, True, 'asdf', TypeError),
    ('e', 100, None, True, True, 'asdf', TypeError),
])
def test_range_constraint(name, min_value, max_value, min_inclusive, max_inclusive, description, exception):
    """
    Test range constraint
    """
    constraint = RangeConstraint(
        name, min_value, max_value, min_inclusive, max_inclusive, description)
    if exception:
        with raises(exception):
            constraint.validate()
    else:
        expected = [(ConstraintType.range_, name, None,
                     min_value, int(min_inclusive),
                     max_value, int(max_inclusive), description)]
        assert constraint.as_records() == expected
# End test_range_constraint function


if __name__ == '__main__':  # pragma: no cover
    pass
