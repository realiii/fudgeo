# -*- coding: utf-8 -*-
"""
Test Utility Functions
"""


from datetime import date, datetime, timedelta, timezone

from pytest import mark

from fudgeo.util import (
    adapt_date, adapt_datetime, convert_date, convert_datetime)


@mark.parametrize('val, expected', [
    (b'1977-06-15', datetime(1977, 6, 15)),
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
    (b'2022-02-14T08:37:41.0Z', datetime(2022, 2, 14, 8, 37, 41, 0, tzinfo=timezone.utc)),
    (b'2025-12-25T18:34:56.978Z', datetime(2025, 12, 25, 18, 34, 56, 978000, tzinfo=timezone.utc)),
    (b'2026-01-01T06:00:00Z', datetime(2026, 1, 1, 6, 0, 0, 0, tzinfo=timezone.utc)),
    (b'2025-02-14T17:22:33.161Z', datetime(2025, 2, 14, 17, 22, 33, 161000, tzinfo=timezone.utc)),
    (b'2026-04-01T05:00:00.099Z', datetime(2026, 4, 1, 5, 0, 0, 99000, tzinfo=timezone.utc)),
    (b'2025-12-25T18:34:56.978Z', datetime(2025, 12, 25, 18, 34, 56, 978000, tzinfo=timezone.utc)),
])
def test_convert_datetime(val, expected):
    """
    Test the datetime converter
    """
    assert convert_datetime(val) == expected
# End test_convert_datetime function


@mark.parametrize('expected, val', [
    ('1977-06-15 00:00:00', datetime(1977, 6, 15)),
    ('1977-06-15 03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    ('1977-06-15 03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    ('2000-06-06 11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    ('2000-06-06 11:43:37+01:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=1)))),
    ('2000-06-06 11:43:37+02:30', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(hours=2, minutes=30)))),
    ('2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    ('2000-06-06 11:43:37-05:15', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone(timedelta(seconds=-18900)))),
    ('1977-06-15 03:18:54', datetime(1977, 6, 15, 3, 18, 54, 0)),
    ('1977-06-15 03:18:54.123456', datetime(1977, 6, 15, 3, 18, 54, 123456)),
    ('2000-06-06 11:43:37+00:00', datetime(2000, 6, 6, 11, 43, 37, 0, tzinfo=timezone.utc)),
    ('2022-02-14 08:37:41+00:00', datetime(2022, 2, 14, 8, 37, 41, 0, tzinfo=timezone.utc)),
    ('2025-12-25 18:34:56.978000+00:00', datetime(2025, 12, 25, 18, 34, 56, 978000, tzinfo=timezone.utc)),
    ('2026-01-01 06:00:00+00:00', datetime(2026, 1, 1, 6, 0, 0, 0, tzinfo=timezone.utc)),
    ('2025-02-14 17:22:33.161000+00:00', datetime(2025, 2, 14, 17, 22, 33, 161000, tzinfo=timezone.utc)),
    ('2026-04-01 05:00:00.099000+00:00', datetime(2026, 4, 1, 5, 0, 0, 99000, tzinfo=timezone.utc)),
    ('2025-12-25 18:34:56.978000+00:00', datetime(2025, 12, 25, 18, 34, 56, 978000, tzinfo=timezone.utc)),
])
def test_adapt_datetime(expected, val):
    """
    Test the datetime adapter
    """
    assert adapt_datetime(val) == expected
# End test_adapt_datetime function


@mark.parametrize('val, expected', [
    (b'1977-06-15 00:00:00', date(1977, 6, 15)),
    (b'1977-06-15 03:18:54', date(1977, 6, 15)),
    (b'1977-06-15 03:18:54.123456', date(1977, 6, 15)),
    (b'2000-06-06 11:43:37+00:00', date(2000, 6, 6)),
    (b'2000-06-06 11:43:37+01:00', date(2000, 6, 6)),
    (b'2000-06-06 11:43:37+02:30', date(2000, 6, 6)),
    (b'2000-06-06 11:43:37-05:15', date(2000, 6, 6)),
    (b'2000-06-06 11:43:37-05:15', date(2000, 6, 6)),
    (b'1977-06-15T03:18:54', date(1977, 6, 15)),
    (b'1977-06-15T03:18:54.123456', date(1977, 6, 15)),
    (b'2000-06-06T11:43:37+00:00', date(2000, 6, 6)),
    (b'2022-02-14T08:37:41.0Z', date(2022, 2, 14)),
    (b'2025-12-25T18:34:56.978Z', date(2025, 12, 25)),
    (b'2026-01-01T06:00:00Z', date(2026, 1, 1)),
    (b'2025-02-14T17:22:33.161Z', date(2025, 2, 14)),
    (b'2026-04-01T05:00:00.099Z', date(2026, 4, 1)),
    (b'2025-12-25T18:34:56.978Z', date(2025, 12, 25)),
])
def test_convert_date(val, expected):
    """
    Test the date converter
    """
    assert convert_date(val) == expected
# End test_convert_date function


@mark.parametrize('expected, val', [
    ('1977-06-15', datetime(1977, 6, 15, 1, 2, 3)),
    ('1977-06-15', date(1977, 6, 15)),
    ('2000-06-06', datetime(2000, 6, 6, 11, 43, 37)),
    ('2000-06-06', date(2000, 6, 6)),
    ('1977-06-15', datetime(1977, 6, 15, 11, 12, 13)),
    ('1977-06-15', date(1977, 6, 15)),
])
def test_adapt_date(expected, val):
    """
    Test the date adapter
    """
    assert adapt_date(val) == expected
# End test_adapt_date function


if __name__ == '__main__':  # pragma: no cover
    pass
