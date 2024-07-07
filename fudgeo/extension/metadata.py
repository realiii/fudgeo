# -*- coding: utf-8 -*-
"""
Metadata Extension
"""


from abc import abstractmethod
from datetime import datetime
from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING

from fudgeo.alias import DATE, INT, REFERENCES, REFERENCE_RECORD, TABLE
from fudgeo.enumeration import MetadataReferenceScope, MetadataScope
from fudgeo.sql import (
    CREATE_METADATA, CREATE_METADATA_REFERENCE, HAS_METADATA, INSERT_EXTENSION,
    INSERT_METADATA, INSERT_METADATA_REFERENCE, METADATA_RECORDS,
    SELECT_METADATA_ID)
from fudgeo.util import now


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection
    from fudgeo.geopkg import GeoPackage


class AbstractReference:
    """
    Abstract Reference
    """
    def __init__(self, scope: str, file_id: int, parent_id: INT = None,
                 timestamp: DATE = None) -> None:
        """
        Initialize the AbstractReference class
        """
        super().__init__()
        self._scope: str = scope
        self._file_id: int = file_id
        self._parent_id: INT = parent_id
        self._timestamp: datetime = timestamp or now()
    # End init built-in

    @abstractmethod
    def as_record(self) -> REFERENCE_RECORD:  # pragma: no cover
        """
        As Record
        """
        pass
    # End as_record method

    @abstractmethod
    def validate(self, geopackage: 'GeoPackage') -> None:  # pragma: no cover
        """
        Validate
        """
        pass
    # End validate method
# End AbstractReference class


class AbstractTableReference(AbstractReference):
    """
    Abstract Table Reference
    """
    def __init__(self, scope: str, table_name: str, file_id: int,
                 parent_id: INT = None, timestamp: DATE = None) -> None:
        """
        Initialize the AbstractTableReference class
        """
        super().__init__(
            scope=scope, file_id=file_id, parent_id=parent_id,
            timestamp=timestamp)
        self._table_name: str = table_name
    # End init built-in

    @abstractmethod
    def as_record(self) -> REFERENCE_RECORD:  # pragma: no cover
        """
        As Record
        """
        pass
    # End as_record method

    def _validate_table_name(self, geopackage: 'GeoPackage') -> TABLE:
        """
        Validate Table Name
        """
        table_name = self._table_name
        table = geopackage.feature_classes.get(
            table_name, geopackage.tables.get(table_name))
        if not table:
            raise ValueError(
                f'table name "{table_name}" not found in {geopackage!r}')
        return table
    # End _validate_table_name method

    @staticmethod
    def _validate_column_name(name: str, table: TABLE) -> None:
        """
        Validate Column Name
        """
        if name not in table.field_names:
            raise ValueError(
                f'column name "{name}" not found in table "{table.name}"')
    # End _validate_column_name method

    @staticmethod
    def _validate_row_id(row_id: int, table: TABLE) -> None:
        """
        Validate Row ID
        """
        # noinspection SqlNoDataSourceInspection
        cursor = table.geopackage.connection.execute(f"""
            SELECT COUNT(1) AS C 
            FROM {table.escaped_name} 
            WHERE ROWID = {row_id}
        """)
        count, = cursor.fetchone()
        if not count:
            raise ValueError(
                f'row id {row_id} does not exist in table "{table.name}"')
    # End _validate_row_id method

    def validate(self, geopackage: 'GeoPackage') -> None:
        """
        Validate
        """
        self._validate_table_name(geopackage)
    # End validate method
# End AbstractTableReference class


class AbstractColumnReference(AbstractTableReference):
    """
    Abstract Column Reference
    """
    def __init__(self, scope: str, table_name: str, column_name: str,
                 file_id: int, parent_id: INT = None,
                 timestamp: DATE = None) -> None:
        """
        Initialize the AbstractTableReference class
        """
        super().__init__(
            scope=scope, table_name=table_name, file_id=file_id,
            parent_id=parent_id, timestamp=timestamp)
        self._column_name: str = column_name
    # End init built-in

    @abstractmethod
    def as_record(self) -> REFERENCE_RECORD:  # pragma: no cover
        """
        As Record
        """
        pass
    # End as_record method

    def validate(self, geopackage: 'GeoPackage') -> None:
        """
        Validate
        """
        self._validate_column_name(
            self._column_name, self._validate_table_name(geopackage))
    # End validate method
# End AbstractColumnReference class


class GeoPackageReference(AbstractReference):
    """
    GeoPackage Reference
    """
    def __init__(self, file_id: int, parent_id: INT = None,
                 timestamp: DATE = None) -> None:
        """
        Initialize the GeoPackageReference class
        """
        super().__init__(
            scope=MetadataReferenceScope.geopackage, file_id=file_id,
            parent_id=parent_id, timestamp=timestamp)
    # End init built-in

    def as_record(self) -> REFERENCE_RECORD:
        """
        As Record
        """
        return (self._scope, None, None, None, self._timestamp,
                self._file_id, self._parent_id)
    # End as_record method

    def validate(self, geopackage: 'GeoPackage') -> None:
        """
        Validate, just pass for Geopackage
        """
        pass
    # End validate method
# End GeoPackageReference class


class TableReference(AbstractTableReference):
    """
    Table Reference
    """
    def __init__(self, table_name: str, file_id: int, parent_id: INT = None,
                 timestamp: DATE = None) -> None:
        """
        Initialize the TableReference class
        """
        super().__init__(
            scope=MetadataReferenceScope.table, table_name=table_name,
            file_id=file_id, parent_id=parent_id, timestamp=timestamp)
    # End init built-in

    def as_record(self) -> REFERENCE_RECORD:
        """
        As Record
        """
        return (self._scope, self._table_name, None, None, self._timestamp,
                self._file_id, self._parent_id)
    # End as_record method
# End TableReference class


class ColumnReference(AbstractColumnReference):
    """
    Column Reference
    """
    def __init__(self, table_name: str, column_name: str, file_id: int,
                 parent_id: INT = None, timestamp: DATE = None) -> None:
        """
        Initialize the ColumnReference class
        """
        super().__init__(
            scope=MetadataReferenceScope.column, table_name=table_name,
            column_name=column_name, file_id=file_id, parent_id=parent_id,
            timestamp=timestamp)
    # End init built-in

    def as_record(self) -> REFERENCE_RECORD:
        """
        As Record
        """
        return (self._scope, self._table_name, self._column_name, None,
                self._timestamp, self._file_id, self._parent_id)
    # End as_record method
# End ColumnReference class


class RowReference(AbstractTableReference):
    """
    Row Reference
    """
    def __init__(self, table_name: str, row_id: int, file_id: int,
                 parent_id: INT = None, timestamp: DATE = None) -> None:
        """
        Initialize the RowReference class
        """
        super().__init__(
            scope=MetadataReferenceScope.row, table_name=table_name,
            file_id=file_id, parent_id=parent_id, timestamp=timestamp)
        self._row_id: int = row_id
    # End init built-in

    def as_record(self) -> REFERENCE_RECORD:
        """
        As Record
        """
        return (self._scope, self._table_name, None, self._row_id,
                self._timestamp, self._file_id, self._parent_id)
    # End as_record method

    def validate(self, geopackage: 'GeoPackage') -> None:
        """
        Validate
        """
        self._validate_row_id(
            self._row_id, self._validate_table_name(geopackage))
    # End validate method
# End RowReference class


class RowColumnReference(AbstractColumnReference):
    """
    Row/Column Reference
    """
    def __init__(self, table_name: str, column_name: str, row_id: int,
                 file_id: int, parent_id: INT = None,
                 timestamp: DATE = None) -> None:
        """
        Initialize the RowColumnReference class
        """
        super().__init__(scope=MetadataReferenceScope.row_col,
                         table_name=table_name, column_name=column_name,
                         file_id=file_id, parent_id=parent_id,
                         timestamp=timestamp)
        self._row_id: int = row_id
    # End init built-in

    def as_record(self) -> REFERENCE_RECORD:
        """
        As Record
        """
        return (self._scope, self._table_name, self._column_name, self._row_id,
                self._timestamp, self._file_id, self._parent_id)
    # End as_record method

    def validate(self, geopackage: 'GeoPackage') -> None:
        """
        Validate
        """
        table = self._validate_table_name(geopackage)
        self._validate_column_name(self._column_name, table)
        self._validate_row_id(self._row_id, table)
    # End validate method
# End RowColumnReference class


class Metadata:
    """
    Metadata
    """
    def __init__(self, geopackage: 'GeoPackage') -> None:
        """
        Initialize the Metadata class
        """
        super().__init__()
        self._geopackage: 'GeoPackage' = geopackage
    # End init built-in

    def add_metadata(self, uri: str, scope: str = MetadataScope.dataset,
                     metadata: str = '', mime_type: str = 'text/xml') -> INT:
        """
        Add Metadata to the Geopackage if the metadata extension enabled.
        """
        if not self._geopackage.is_metadata_enabled:
            return
        with self._geopackage.connection as conn:
            conn.execute(INSERT_METADATA, (scope, uri, mime_type, metadata))
        cursor = conn.execute(SELECT_METADATA_ID)
        id_, = cursor.fetchone()
        return id_
    # End add_metadata method

    def add_references(self, references: REFERENCES) -> None:
        """
        Add Metadata References if metadata extension enabled.
        """
        if not self._geopackage.is_metadata_enabled:
            return
        if isinstance(references, AbstractReference):
            references = references,
        records = []
        for reference in references:
            reference.validate(self._geopackage)
            records.append(reference.as_record())
        with self._geopackage.connection as conn:
            conn.executemany(INSERT_METADATA_REFERENCE, records)
    # End add_references method
# End Metadata class


def has_metadata_extension(conn: 'Connection') -> bool:
    """
    Has Metadata Extension Tables
    """
    try:
        cursor = conn.execute(HAS_METADATA)
    except (DatabaseError, OperationalError):
        return False
    return bool(cursor.fetchone())
# End has_metadata_extension function


def add_metadata_extension(conn: 'Connection') -> None:
    """
    Add Metadata Extension Tables and Entries
    """
    conn.executemany(INSERT_EXTENSION, METADATA_RECORDS)
    conn.execute(CREATE_METADATA)
    conn.execute(CREATE_METADATA_REFERENCE)
# End add_metadata_extension function


if __name__ == '__main__':  # pragma: no cover
    pass
