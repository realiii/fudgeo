# -*- coding: utf-8 -*-
"""
Test Geometry
"""

from time import perf_counter

from pytest import mark

from fudgeo.geometry import LineString, Point, Polygon


@mark.parametrize('scale, geom_type, expected', [
    (1, Point, 0.045),
    (1, LineString, 0.03),
    (1, Polygon, 0.025),
])
def test_performance(random_utm_coordinates, scale, geom_type, expected):
    """
    Test Performance, garbage test of round trips,
    just used to check for accidental slowdown
    """
    start = perf_counter()
    srs_id = 32623
    eastings, northings = random_utm_coordinates
    pairs = zip(eastings * scale, northings * scale)
    if geom_type is Point:
        start = perf_counter()
        points1 = [Point(x=x, y=y, srs_id=srs_id) for x, y in pairs]
        points2 = [Point.from_gpkg(pt.to_gpkg()) for pt in points1]
        assert points1 == points2
    elif geom_type is LineString:
        start = perf_counter()
        line1 = LineString(list(pairs), srs_id=srs_id)
        line2 = LineString.from_gpkg(line1.to_gpkg())
        assert line1 == line2
    elif geom_type is Polygon:
        start = perf_counter()
        polygon1 = Polygon([list(pairs)], srs_id=srs_id)
        polygon2 = Polygon.from_gpkg(polygon1.to_gpkg())
        assert polygon1 == polygon2
    assert (perf_counter() - start) <= expected
# End test_performance function


if __name__ == '__main__':
    pass
