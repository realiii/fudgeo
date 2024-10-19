# -*- coding: utf-8 -*-
"""
Utility Functions
"""


from datetime import datetime, timedelta, timezone
from re import IGNORECASE, compile as recompile
from typing import Callable, Match, Optional

from fudgeo.sql import KEYWORDS


NAME_MATCHER: Callable[[str], Optional[Match[str]]] = (
    recompile(r'^[A-Z]\w*$', IGNORECASE).match)


def escape_name(name: str) -> str:
    """
    Escape Name
    """
    if _is_invalid_name(name):
        name = f'"{name}"'
    return name
# End escape_name function


def _is_invalid_name(name: str) -> bool:
    """
    Is invalid name
    """
    return name.upper() in KEYWORDS or not NAME_MATCHER(name)
# End _is_invalid_name function


def check_geometry_name(name: str) -> str:
    """
    Check geometry name
    """
    if _is_invalid_name(name):
        raise ValueError(f'Invalid field name for geometry column: {name}')
    return name
# End check_geometry_name function


def now() -> str:
    """
    Formatted Now
    """
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
# End now method


def convert_datetime(val: bytes) -> datetime:
    """
    Heavily Influenced by convert_timestamp from ../sqlite3/dbapi2.py,
    Added in support for timezone handling although the practice should
    be to resolve to UTC.
    """
    colon = b':'
    dash = b'-'
    # NOTE To split timestamps like that b'2022-09-06T13:50:33'
    for separator in (b' ', b'T'):
        try:
            dt, tm = val.split(separator)
            break
        except ValueError:
            pass
    else:  # pragma: no cover
        raise Exception(f"Could not split datetime: '{val}'")
    year, month, day = map(int, dt.split(dash))
    tm, *micro = tm.split(b'.')
    tz = []
    factor = 0
    for token, scale in zip((b'+', dash), (1, -1)):
        if token in tm:
            tm, *tz = tm.split(token)
            factor = scale
            break
    hours, minutes, seconds = map(int, tm.split(colon))
    try:
        micro = int('{:0<6.6}'.format(micro[0].decode())) if micro else 0
    except (ValueError, TypeError):
        micro = 0
    if tz:
        tz_hr, *tz_min = map(int, tz[0].split(colon))
        tz_min = tz_min[0] if tz_min else 0
        tzinfo = timezone(timedelta(
            hours=factor * tz_hr, minutes=factor * tz_min))
    else:
        tzinfo = None
    return datetime(year, month, day, hours, minutes, seconds,
                    micro, tzinfo=tzinfo)
# End convert_datetime function


if __name__ == '__main__':  # pragma: no cover
    pass
