# -*- coding: utf-8 -*-
"""
Test Utility Functions
"""


from datetime import datetime, timedelta, timezone

from pytest import mark

from fudgeo.util import convert_datetime


@mark.parametrize('val, expected', [
    (b'1977-06-15 03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    (b'1977-06-15 03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    (b'2000-06-06 11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    (b'2000-06-06 11:43:37+01:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=1)))),
    (b'2000-06-06 11:43:37+02:30', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=2, minutes=30)))),
    (b'2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    (b'2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    (b'1977-06-15T03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    (b'1977-06-15T03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    (b'2000-06-06T11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    (b'2022-02-14T08:37:41.0Z', datetime(2022, 2, 14, 8, 37, 41, 0)),
])
def test_convert_datetime(val, expected):
    """
    Test the datetime converter
    """
    assert convert_datetime(val) == expected
# End test_convert_datetime function


if __name__ == '__main__':  # pragma: no cover
    pass
