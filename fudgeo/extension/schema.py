# -*- coding: utf-8 -*-
"""
Schema Extension
"""


from abc import ABCMeta, abstractmethod
from numbers import Number
from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING, Union

from fudgeo.alias import CONSTRAINTS, GPKG, RECORDS, STRING, TABLE
from fudgeo.enumeration import ConstraintType, FieldType
from fudgeo.sql import (
    CREATE_DATA_COLUMNS, CREATE_DATA_COLUMN_CONSTRAINTS, HAS_SCHEMA,
    INSERT_COLUMN_CONSTRAINTS, INSERT_COLUMN_DEFINITION, INSERT_EXTENSION,
    SCHEMA_RECORDS, SELECT_CONSTRAINT_NAME, SELECT_CONSTRAINT_RECORD,
    SELECT_DATA_COLUMNS_BY_TABLE_NAME, SELECT_DISTINCT_CONSTRAINT_NAMES,
    SELECT_TABLE_SCHEMA)


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection


class AbstractConstraint(metaclass=ABCMeta):
    """
    Abstract Constraint
    """
    def __init__(self, type_: str, name: str,
                 description: STRING) -> None:
        """
        Initialize the AbstractConstraint class
        """
        super().__init__()
        self._type: str = type_
        self._name: str = name
        self._description: STRING = description
    # End init built-in

    @property
    def name(self) -> str:
        """
        Name
        """
        return self._name.casefold()
    # End name property

    def validate(self) -> None:
        """
        Validate
        """
        if not isinstance(self._name, str):
            raise TypeError('constraint name must be a string')
    # End validate method

    @abstractmethod
    def as_records(self) -> RECORDS:  # pragma: no cover
        """
        As Records
        """
        pass
    # End as_records method
# End AbstractConstraint class


class EnumerationConstraint(AbstractConstraint):
    """
    Enumeration Constraint
    """
    def __init__(self, name: str, values: Union[list, tuple],
                 description: STRING = None) -> None:
        """
        Initialize the EnumerationConstraint class
        """
        super().__init__(
            type_=ConstraintType.enum, name=name, description=description)
        self._values: list = sorted(set(values))
    # End init built-in

    def validate(self) -> None:
        """
        Validate
        """
        super().validate()
        if not self._values:
            raise ValueError(
                'one or more items required for enumeration values')
    # End validate method

    def as_records(self) -> RECORDS:
        """
        As Records
        """
        return [(self._type, self.name, value, None, None, None, None,
                 self._description) for value in self._values]
    # End as_records method
# End EnumerationConstraint class


class GlobConstraint(AbstractConstraint):
    """
    Glob Constraint
    """
    def __init__(self, name: str, pattern: str,
                 description: STRING = None) -> None:
        """
        Initialize the GlobConstraint class
        """
        super().__init__(
            type_=ConstraintType.glob, name=name, description=description)
        self._pattern: str = pattern
    # End init built-in

    def validate(self) -> None:
        """
        Validate
        """
        super().validate()
        if not isinstance(self._pattern, str):
            raise TypeError('glob pattern must be a string')
    # End validate method

    def as_records(self) -> RECORDS:
        """
        As Records
        """
        return [(self._type, self.name, self._pattern,
                 None, None, None, None, self._description)]
    # End as_records method
# End GlobConstraint class


class RangeConstraint(AbstractConstraint):
    """
    Range Constraint
    """
    def __init__(self, name: str, min_value: float, max_value: float,
                 min_inclusive: bool = True, max_inclusive: bool = True,
                 description: STRING = None) -> None:
        """
        Initialize the RangeConstraint class
        """
        super().__init__(
            type_=ConstraintType.range_, name=name, description=description)
        self._min_value: float = min_value
        self._min_inclusive: bool = min_inclusive
        self._max_value: float = max_value
        self._max_inclusive: bool = max_inclusive
    # End init built-in

    def validate(self) -> None:
        """
        Validate
        """
        super().validate()
        if (not isinstance(self._min_value, Number) or
                not isinstance(self._max_value, Number)):
            raise TypeError('min value and max value must be numbers')
        if self._min_value >= self._max_value:
            raise ValueError('min value must be smaller than max value')
    # End validate method

    def as_records(self) -> RECORDS:
        """
        As Records
        """
        return [(self._type, self.name, None,
                 self._min_value, int(self._min_inclusive),
                 self._max_value, int(self._max_inclusive), self._description)]
    # End as_records method
# End RangeConstraint class


class DataColumnRecord:
    """
    Data Column Record
    """
    def __init__(self, table_name: str, column_name: str, name: STRING = None,
                 title: STRING = None, description: STRING = None,
                 mime_type: STRING = None, constraint_name: STRING = None) -> None:
        """
        Initialize the DataColumnRecord class
        """
        super().__init__()
        self._table_name: str = table_name
        self._column_name: str = column_name
        self._name: STRING = name
        self._title: STRING = title
        self._description: STRING = description
        self._mime_type: STRING = mime_type
        self._constraint_name: STRING = constraint_name
    # End init built-in

    @property
    def table_name(self) -> str:
        """
        Table Name
        """
        return self._table_name

    @table_name.setter
    def table_name(self, value: str) -> None:
        self._table_name = value
    # End table_name property

    @property
    def name(self) -> STRING:
        """
        Alias Name / Short Name
        """
        return self._name

    @name.setter
    def name(self, value: STRING) -> None:
        self._name = value
    # End name property

    @property
    def description(self) -> STRING:
        """
        Description / Comment
        """
        return self._description

    @description.setter
    def description(self, value: STRING) -> None:
        self._description = value
    # End description property

    @property
    def constraint_name(self) -> STRING:
        """
        Constraint Name
        """
        return self._constraint_name

    @constraint_name.setter
    def constraint_name(self, value: STRING) -> None:
        self._constraint_name = value
    # End constraint_name property

    def as_record(self) -> tuple[str, str, STRING, STRING, STRING, STRING, STRING]:
        """
        As Record
        """
        return (self.table_name, self._column_name, self.name, self._title,
                self.description, self._mime_type, self.constraint_name)
    # End as_record method
# End DataColumnRecord class


class Schema:
    """
    Schema
    """
    def __init__(self, geopackage: GPKG) -> None:
        """
        Initialize the Schema class
        """
        super().__init__()
        self._geopackage: GPKG = geopackage
    # End init built-in

    def add_column_definition(self, table_name: str, column_name: str,
                              name: STRING = None, title: STRING = None,
                              description: STRING = None,
                              mime_type: STRING = None,
                              constraint_name: STRING = None) -> None:
        """
        Add Column Definition
        """
        if not self._geopackage.is_schema_enabled:
            return
        element = self._get_element(table_name)
        self._check_column_name(element, column_name)
        field = element.fields[element.field_names.index(column_name)]
        if field.data_type == FieldType.blob and not mime_type:
            raise ValueError(
                f'expected mime_type value for blob column {column_name}')
        constraint_name = self._check_constraint(constraint_name)
        with self._geopackage.connection as conn:
            record = (table_name, column_name, name, title,
                      description, mime_type, constraint_name)
            conn.execute(INSERT_COLUMN_DEFINITION, record)
    # End add_column_definition method

    def _check_constraint(self, constraint_name: STRING) -> STRING:
        """
        Check if a constraint exists, ensure the constraint name is lower case
        """
        if not constraint_name:
            return constraint_name
        cursor = self._geopackage.connection.execute(
            SELECT_CONSTRAINT_NAME, (constraint_name,))
        if cursor.fetchone():
            return constraint_name.casefold()
        raise ValueError(
            f'constraint "{constraint_name}" not found in {self._geopackage!r}')
    # End _check_constraint method

    @staticmethod
    def _check_column_name(element: TABLE, column_name: str) -> None:
        """
        Check Column Name
        """
        if column_name in element.field_names:
            return
        raise ValueError(
            f'column name "{column_name}" not found in table "{element.name}"')
    # End _check_column_name method

    def _get_element(self, name: str) -> TABLE:
        """
        Get Element based on name
        """
        if table := self._geopackage[name]:
            return table
        raise ValueError(
            f'table name "{name}" not found in {self._geopackage!r}')
    # End _get_element method

    def add_constraints(self, constraints: CONSTRAINTS) -> None:
        """
        Add Constraints
        """
        if not self._geopackage.is_schema_enabled:
            return
        if isinstance(constraints, AbstractConstraint):
            constraints = constraints,
        records = []
        for constraint in constraints:
            constraint.validate()
            records.extend(constraint.as_records())
        with self._geopackage.connection as conn:
            conn.executemany(INSERT_COLUMN_CONSTRAINTS, records)
    # End add_constraints method
# End Schema class


def copy_schema(source: TABLE, target: TABLE) -> None:
    """
    Copy Schema for a Table or Feature Class
    """
    if not source.geopackage.is_schema_enabled:
        return
    # noinspection PyProtectedMember
    is_same = source._check_same_geopackage(
        source.geopackage, target.geopackage)
    with source.geopackage.connection as conn:
        if not has_schema(conn, name=source.name):
            return
        constraints, records = fetch_schema(conn, name=source.name)
    target.geopackage.enable_schema_extension()
    for record in records:
        record.table_name = target.name
    if not is_same:
        names = {name for _, name, *_ in constraints}
        with target.geopackage.connection as conn:
            cursor = conn.execute(SELECT_DISTINCT_CONSTRAINT_NAMES)
            target_names = {name for name, in cursor.fetchall()}
            lut = {name: make_unique_name(name, target_names) for name in names}
            constraints = [(type_, lut[name], *data)
                           for type_, name, *data in constraints]
            conn.executemany(INSERT_COLUMN_CONSTRAINTS, constraints)
        for record in records:
            if record.constraint_name:
                record.constraint_name = lut[record.constraint_name]
    for record in records:
        target.geopackage.schema.add_column_definition(*record.as_record())
# End copy_schema function


def make_unique_name(name: str, names: set[str]) -> str:
    """
    Make Unique Name accounting for case sensitivity
    """
    if name.casefold() not in names:
        names.add(name.casefold())
        return name
    counter = 1
    new_name = f'{name}_{counter}'
    while new_name.casefold() in names:
        counter += 1
        new_name = f'{name}_{counter}'
    names.add(new_name.casefold())
    return new_name
# End make_unique_name function


def fetch_schema(conn: 'Connection', name: str) \
        -> tuple[CONSTRAINTS, list[DataColumnRecord]]:
    """
    Fetch Schema Records and Constraints
    """
    cursor = conn.execute(SELECT_DATA_COLUMNS_BY_TABLE_NAME, (name,))
    records = [DataColumnRecord(*record) for record in cursor.fetchall()]
    names = {rec.constraint_name for rec in records if rec.constraint_name}
    constraints = []
    for name in names:
        cursor = conn.execute(SELECT_CONSTRAINT_RECORD, (name,))
        constraints.extend(cursor.fetchall())
    return constraints, records
# End fetch_metadata function


def has_schema(conn: 'Connection', name: str) -> bool:
    """
    Has Schema entries for a Table or Feature Class
    """
    if not has_schema_extension(conn):
        return False
    cursor = conn.execute(SELECT_TABLE_SCHEMA, (name,))
    return bool(cursor.fetchall())
# End has_schema function


def has_schema_extension(conn: 'Connection') -> bool:
    """
    Has Schema Extension Tables
    """
    try:
        cursor = conn.execute(HAS_SCHEMA)
    except (DatabaseError, OperationalError):  # pragma: no cover
        return False
    return bool(cursor.fetchone())
# End has_schema_extension function


def add_schema_extension(conn: 'Connection') -> None:
    """
    Add Schema Extension Tables and Entries
    """
    conn.executemany(INSERT_EXTENSION, SCHEMA_RECORDS)
    conn.execute(CREATE_DATA_COLUMNS)
    conn.execute(CREATE_DATA_COLUMN_CONSTRAINTS)
# End add_schema_extension function


if __name__ == '__main__':  # pragma: no cover
    pass
