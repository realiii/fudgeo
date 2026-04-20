# -*- coding: utf-8 -*-
"""
Utility Functions
"""


from functools import lru_cache
from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING

from fudgeo.sql import CREATE_EXTENSIONS_TABLE, HAS_EXTENSIONS

if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection


@lru_cache()
def has_extensions(conn: 'Connection') -> bool:
    """
    Has gpkg_extensions table
    """
    return has_table_checker(conn, HAS_EXTENSIONS)
# End has_extensions function


def add_extensions(conn: 'Connection') -> None:
    """
    Add Extensions
    """
    if has_extensions(conn):
        return
    conn.execute(CREATE_EXTENSIONS_TABLE)
    has_extensions.cache_clear()
# End add_extensions function


def has_table_checker(conn: 'Connection', sql: str) -> bool:
    """
    Has Table Checker
    """
    try:
        cursor = conn.execute(sql)
    except (DatabaseError, OperationalError):  # pragma: no cover
        return False
    return bool(cursor.fetchone())
# End has_table_checker function


if __name__ == '__main__':  # pragma: no cover
    pass
