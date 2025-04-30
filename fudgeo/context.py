# -*- coding: utf-8 -*-
"""
Context Managers
"""


from sqlite3 import OperationalError
from typing import TYPE_CHECKING

from fudgeo.alias import TABLE
from fudgeo.extension.ogr import OGR_CONTENTS, has_ogr_contents
from fudgeo.sql import GPKG_OGR_CONTENTS_INSERT_TRIGGER


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection


class ExecuteMany:
    """
    Execute Many
    """
    def __init__(self, connection: 'Connection', table: TABLE) -> None:
        """
        Initialize the ExecuteMany class
        """
        super().__init__()
        self._conn: 'Connection' = connection
        self._tbl: TABLE = table
        self._has_ogr: bool = has_ogr_contents(conn=connection)
    # End init built-in

    def __call__(self, sql: str, data: list) -> None:
        """
        Make Class Callable
        """
        self._conn.executemany(sql, data)
    # End call built-in

    def __enter__(self) -> 'ExecuteMany':
        """
        Context Manager Enter
        """
        if self._has_ogr:
            try:
                self._conn.execute(f"""
                    DROP TRIGGER IF EXISTS
                    trigger_insert_feature_count_{self._tbl.name}""")
            except OperationalError:
                pass
        return self
    # End enter built-in

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Context Manager Exit
        """
        if self._has_ogr:
            try:
                # noinspection SqlNoDataSourceInspection,SqlResolve
                self._conn.execute(f"""
                    UPDATE {OGR_CONTENTS}
                    SET feature_count = (SELECT count(1) AS C FROM {self._tbl.escaped_name})
                    WHERE lower(table_name) = lower('{self._tbl.name}')""")
            except OperationalError:
                pass
            try:
                stub = 'CREATE TRIGGER '
                self._conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.replace(
                    stub, f'{stub}IF NOT EXISTS ').format(
                    self._tbl.name, self._tbl.escaped_name))
            except OperationalError:
                pass
        return False
    # End exit built-in
# End ExecuteMany class


class ForeignKeys:
    """
    Foreign Keys
    """
    def __init__(self, connection: 'Connection') -> None:
        """
        Initialize the ForeignKeys class
        """
        super().__init__()
        self._conn: 'Connection' = connection
    # End init built-in

    def __enter__(self) -> 'ForeignKeys':
        """
        Context Manager Enter
        """
        self._conn.execute("""PRAGMA foreign_keys = false""")
        return self
    # End enter built-in

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """
        Context Manager Exit
        """
        self._conn.execute("""PRAGMA foreign_keys = true""")
        return False
    # End exit built-in
# End ForeignKeys class


if __name__ == '__main__':  # pragma: no cover
    pass
