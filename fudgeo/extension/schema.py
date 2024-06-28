# -*- coding: utf-8 -*-
"""
Schema Extension
"""


from abc import abstractmethod
from numbers import Number
from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING, Union

from fudgeo.alias import CONSTRAINTS, RECORDS, STRING
from fudgeo.enumeration import ConstraintType, SQLFieldType
from fudgeo.sql import (
    CREATE_DATA_COLUMNS, CREATE_DATA_COLUMN_CONSTRAINTS, HAS_SCHEMA,
    INSERT_COLUMN_CONSTRAINTS, INSERT_COLUMN_DEFINITION, INSERT_EXTENSION,
    SCHEMA_RECORDS, SELECT_CONSTRAINT_NAME)


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection
    from fudgeo.geopkg import GeoPackage


class AbstractConstraint:
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
        return [(self._type, self._name, value, None, None, None, None,
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
        return [(self._type, self._name, self._pattern,
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
        return [(self._type, self._name, None,
                 self._min_value, int(self._min_inclusive),
                 self._max_value, int(self._max_inclusive), self._description)]
    # End as_records method
# End RangeConstraint class


class Schema:
    """
    Schema
    """
    def __init__(self, geopackage: 'GeoPackage') -> None:
        """
        Initialize the Schema class
        """
        super().__init__()
        self._geopackage: 'GeoPackage' = geopackage
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
        table = self._geopackage.feature_classes.get(
            table_name, self._geopackage.tables.get(table_name))
        if not table:
            raise ValueError(
                f'table name "{table_name}" not found in {self._geopackage!r}')
        if column_name not in table.field_names:
            raise ValueError(f'column name "{column_name}" '
                             f'not found in table "{table.name}"')
        field = table.fields[table.field_names.index(column_name)]
        if field.data_type == SQLFieldType.blob and not mime_type:
            raise ValueError(
                f'expected mime_type value for blob column {column_name}')
        if constraint_name:
            cursor = self._geopackage.connection.execute(
                SELECT_CONSTRAINT_NAME, (constraint_name,))
            if not cursor.fetchall():
                raise ValueError(
                    f'constraint name "{constraint_name}" '
                    f'not found in {self._geopackage!r}')
        with self._geopackage.connection as conn:
            record = (table_name, column_name, name, title,
                      description, mime_type, constraint_name)
            conn.execute(INSERT_COLUMN_DEFINITION, record)
    # End add_column_definition method

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


def has_schema_extension(conn: 'Connection') -> bool:
    """
    Has Schema Extension Tables
    """
    try:
        cursor = conn.execute(HAS_SCHEMA)
    except (DatabaseError, OperationalError):
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
