# -*- coding: utf-8 -*-
"""
OGR Extension (unofficial) for tracking row counts
"""


from sqlite3 import DatabaseError, OperationalError
from typing import TYPE_CHECKING

from fudgeo.sql import (
    CREATE_OGR_CONTENTS, GPKG_OGR_CONTENTS_DELETE_TRIGGER,
    GPKG_OGR_CONTENTS_INSERT_TRIGGER, HAS_OGR_CONTENTS,
    INSERT_GPKG_OGR_CONTENTS)


if TYPE_CHECKING:  # pragma: no cover
    from sqlite3 import Connection


OGR_CONTENTS: str = 'gpkg_ogr_contents'


def has_ogr_contents(conn: 'Connection') -> bool:
    """
    Has gpkg_ogr_contents table
    """
    try:
        cursor = conn.execute(HAS_OGR_CONTENTS)
    except (DatabaseError, OperationalError):  # pragma: no cover
        return False
    return bool(cursor.fetchone())
# End has_ogr_contents function


def add_ogr_contents(conn: 'Connection', name: str, escaped_name: str) -> None:
    """
    Add OGR Contents Table Entry and Triggers, adds the table if it was not
    created during GeoPackage creation.
    """
    if not has_ogr_contents(conn):
        conn.execute(CREATE_OGR_CONTENTS)
    conn.execute(INSERT_GPKG_OGR_CONTENTS, (name, 0))
    conn.execute(GPKG_OGR_CONTENTS_INSERT_TRIGGER.format(name, escaped_name))
    conn.execute(GPKG_OGR_CONTENTS_DELETE_TRIGGER.format(name, escaped_name))
# End add_ogr_contents function


if __name__ == '__main__':  # pragma: no cover
    pass
