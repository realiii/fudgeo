# -*- coding: utf-8 -*-
"""
Test Geometry
"""

from time import perf_counter
from sys import version_info

from pytest import mark

from fudgeo.geometry import LineString, Point, Polygon


@mark.skipif(version_info[:2] != (3, 11), reason='threshold based on 3.11')
@mark.parametrize('scale, geom_type, expected', [
    (1, Point, 0.025),
    (1, LineString, 0.0025),
    (1, Polygon, 0.0025),
])
def test_performance(random_utm_coordinates, scale, geom_type, expected):
    """
    Test Performance, garbage test of round trips,
    just used to check for accidental slowdown
    """
    srs_id = 32623
    end = start = perf_counter()
    eastings, northings = random_utm_coordinates
    pairs = zip(eastings * scale, northings * scale)
    if geom_type is Point:
        start = perf_counter()
        points1 = [Point(x=x, y=y, srs_id=srs_id) for x, y in pairs]
        points2 = [Point.from_gpkg(pt.to_gpkg()) for pt in points1]
        end = perf_counter()
        assert points1 == points2
        assert not hasattr(points1, 'envelope')
        assert not hasattr(points1, '_env')
    elif geom_type is LineString:
        start = perf_counter()
        line1 = LineString(list(pairs), srs_id=srs_id)
        line2 = LineString.from_gpkg(line1.to_gpkg())
        end = perf_counter()
        assert line1 == line2
        assert line1.envelope == line2.envelope
        assert line1.envelope.code == 1
    elif geom_type is Polygon:
        start = perf_counter()
        polygon1 = Polygon([list(pairs)], srs_id=srs_id)
        polygon2 = Polygon.from_gpkg(polygon1.to_gpkg())
        end = perf_counter()
        assert polygon1 == polygon2
        assert polygon1.envelope == polygon2.envelope
        assert polygon1.envelope.code == 1
    assert (end - start) <= expected
# End test_performance function


if __name__ == '__main__':
    pass
