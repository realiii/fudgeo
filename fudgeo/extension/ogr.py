# -*- coding: utf-8 -*-
"""
OGR Extension (unofficial) for tracking row counts
"""


from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING

from fudgeo.sql import (
    GPKG_OGR_CONTENTS_DELETE_TRIGGER, GPKG_OGR_CONTENTS_INSERT_TRIGGER,
    HAS_OGR_CONTENTS, INSERT_GPKG_OGR_CONTENTS)


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection


def has_ogr_contents(conn: 'Connection') -> bool:
    """
    Has gpkg_ogr_contents table
    """
    try:
        cursor = conn.execute(HAS_OGR_CONTENTS)
    except (DatabaseError, OperationalError):
        return False
    return bool(cursor.fetchone())
# End has_ogr_contents function


def add_ogr_contents(conn: 'Connection', name: str, escaped_name: str) -> None:
    """
    Add OGR Contents Table Entry and Triggers
    """
    conn.execute(INSERT_GPKG_OGR_CONTENTS, (name, 0))
    conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.format(name, escaped_name))
    conn.execute(GPKG_OGR_CONTENTS_DELETE_TRIGGER.format(name, escaped_name))
# End add_ogr_contents function


if __name__ == '__main__':  # pragma: no cover
    pass
