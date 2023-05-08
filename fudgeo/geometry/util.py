# -*- coding: utf-8 -*-
"""
Utility Functions
"""


from functools import lru_cache, reduce
from math import isfinite, nan
from operator import add
# noinspection PyPep8Naming
from struct import error as StructError, pack, unpack
from typing import List, TYPE_CHECKING, Tuple, Union

from fudgeo.constant import (
    COORDINATES, COUNT_CODE, DOUBLE, EMPTY, ENVELOPE_COUNT, ENVELOPE_OFFSET,
    GP_MAGIC, HEADER_CODE, HEADER_OFFSET, POINT_PREFIX, QUADRUPLE, TRIPLE,
    TWO_D)


if TYPE_CHECKING:  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from fudgeo.geometry.linestring import (
        LineString, LineStringZ, LineStringM, LineStringZM)
    # noinspection PyUnresolvedReferences
    from fudgeo.geometry.polygon import (
        LinearRing, LinearRingZ, LinearRingM, LinearRingZM,
        Polygon, PolygonZ, PolygonM, PolygonZM)


GEOMS = Union[List['LineString'], List['LinearRing'], List['Polygon']]
GEOMS_Z = Union[List['LineStringZ'], List['LinearRingZ'], List['PolygonZ']]
GEOMS_M = Union[List['LineStringM'], List['LinearRingM'], List['PolygonM']]
GEOMS_ZM = Union[List['LineStringZM'], List['LinearRingZM'], List['PolygonZM']]
VALUES = List[float]


class Envelope:
    """
    Envelope
    """
    __slots__ = ['_code', '_min_x', '_max_x', '_min_y', '_max_y',
                 '_min_z', '_max_z', '_min_m', '_max_m']

    def __init__(self, code: int, min_x: float, max_x: float,
                 min_y: float, max_y: float,
                 min_z: float = nan, max_z: float = nan,
                 min_m: float = nan, max_m: float = nan) -> None:
        """
        Initialize the Envelope class
        """
        super().__init__()
        self._code: int = code
        self._min_x: float = min_x
        self._max_x: float = max_x
        self._min_y: float = min_y
        self._max_y: float = max_y
        self._min_z: float = min_z
        self._max_z: float = max_z
        self._min_m: float = min_m
        self._max_m: float = max_m
    # End init built-in

    def __repr__(self) -> str:
        """
        String Representation
        """
        x = f'min_x={self.min_x}, max_x={self.max_x}'
        y = f'min_y={self.min_y}, max_y={self.max_y}'
        z = f'min_z={self.min_z}, max_z={self.max_z}'
        m = f'min_m={self.min_m}, max_m={self.max_m}'
        return f'Envelope(code={self.code}, {x}, {y}, {z}, {m})'
    # End repr built-in

    def __eq__(self, other: 'Envelope') -> bool:
        """
        Equality
        """
        if not isinstance(other, Envelope):
            return NotImplemented
        code = self.code
        if code != other.code:
            return False
        if not code:
            return True
        same_x = self.min_x == other.min_x and self.max_x == other.max_x
        same_y = self.min_y == other.min_y and self.max_y == other.max_y
        same_xy = same_x and same_y
        if not same_xy or code == 1:
            return same_xy
        same_z = self.min_z == other.min_z and self.max_z == other.max_z
        if code == 2:
            return same_z
        same_m = self.min_m == other.min_m and self.max_m == other.max_m
        if code == 3:
            return same_m
        return same_m and same_z
    # End eq built-in

    @property
    def code(self) -> int:
        """
        Envelope Code
        """
        return self._code
    # End code property

    @property
    def min_x(self) -> float:
        """
        Min X
        """
        return self._min_x
    # End min_x property

    @property
    def max_x(self) -> float:
        """
        Max X
        """
        return self._max_x
    # End max_x property

    @property
    def min_y(self) -> float:
        """
        Min Y
        """
        return self._min_y
    # End min_y property

    @property
    def max_y(self) -> float:
        """
        Max Y
        """
        return self._max_y
    # End max_y property

    @property
    def min_z(self) -> float:
        """
        Min Z
        """
        return self._min_z
    # End min_z property

    @property
    def max_z(self) -> float:
        """
        Max Z
        """
        return self._max_z
    # End max_z property

    @property
    def min_m(self) -> float:
        """
        Min M
        """
        return self._min_m
    # End min_m property

    @property
    def max_m(self) -> float:
        """
        Max M
        """
        return self._max_m
    # End max_m property
# End Envelope class


EMPTY_ENVELOPE = Envelope(code=0, min_x=nan, max_x=nan, min_y=nan, max_y=nan)


def unpack_line(value: bytes, dimension: int,
                is_ring: bool = False) -> List[Tuple[float, ...]]:
    """
    Unpack Values for LineString
    """
    count, data = get_count_and_data(value, is_ring=is_ring)
    total = dimension * count
    values: Tuple[float, ...] = unpack(f'<{total}d', data)
    return [values[i:i + dimension] for i in range(0, total, dimension)]
# End unpack_line function


def unpack_points(value: bytes, dimension: int) -> List[Tuple[float, ...]]:
    """
    Unpack Values for Multi Point
    """
    offset = 5
    size = (8 * dimension) + offset
    count, data = get_count_and_data(value)
    if not count:
        return []
    total = dimension * count
    data = [data[i + offset:i + size] for i in range(0, len(data), size)]
    values: Tuple[float, ...] = unpack(f'<{total}d', reduce(add, data))
    return [values[i:i + dimension] for i in range(0, total, dimension)]
# End unpack_points function


def pack_coordinates(coordinates: COORDINATES, has_z: bool = False,
                     has_m: bool = False, use_prefix: bool = False) -> bytes:
    """
    Pack Coordinates
    """
    flat = []
    for coords in coordinates:
        flat.extend(coords)
    count = len(coordinates)
    total = count * sum((TWO_D, has_z, has_m))
    data = pack(f'<{total}d', *flat)
    if not use_prefix:
        return pack(COUNT_CODE, count) + data
    length = len(data)
    step = length // count
    prefix = POINT_PREFIX.get((has_z, has_m))
    parts = [prefix + data[i:i + step] for i in range(0, length, step)]
    return pack(COUNT_CODE, count) + EMPTY.join(parts)
# End pack_coordinates function


def unpack_lines(value: bytes, dimension: int, is_ring: bool = False) \
        -> List[List[Tuple[float, ...]]]:
    """
    Unpack Values for Multi LineString and Polygons
    """
    size, last_end = 8 * dimension, 0
    offset, unit = (4, COUNT_CODE) if is_ring else (9, '<BII')
    count, data = get_count_and_data(value)
    lines = []
    for _ in range(count):
        *_, length = unpack(unit, data[last_end:last_end + offset])
        end = last_end + offset + (size * length)
        # noinspection PyTypeChecker
        points: List[Tuple[float, ...]] = unpack_line(
            data[last_end:end], dimension, is_ring=is_ring)
        last_end = end
        lines.append(points)
    return lines
# End unpack_lines function


def unpack_polygons(value: bytes, dimension: int) \
        -> List[List[List[Tuple[float, ...]]]]:
    """
    Unpack Values for Multi Polygon Type Containing Polygons
    """
    size, last_end = 8 * dimension, 0
    count, data = get_count_and_data(value)
    polygons = []
    for _ in range(0, count):
        points = unpack_lines(data[last_end:], dimension, is_ring=True)
        point_count = sum(len(x) for x in points)
        last_end += (point_count * size) + (len(points) * 4) + 9
        polygons.append(points)
    return polygons
# End unpack_polygons method


def get_count_and_data(value: bytes, is_ring: bool = False) \
        -> Tuple[int, bytes]:
    """
    Get Count from header and return the value portion of the stream
    """
    first, second = (0, 4) if is_ring else (5, 9)
    header, data = value[first: second], value[second:]
    count, = unpack(COUNT_CODE, header)
    return count, data
# End get_count_and_data function


@lru_cache(maxsize=None)
def make_header(srs_id: int, is_empty: bool) -> bytes:
    """
    Cached Creation of a GeoPackage Geometry Header
    """
    flags = 1
    if is_empty:
        flags |= (1 << 4)
    return pack(HEADER_CODE, GP_MAGIC, 0, flags, srs_id)
# End make_header function


@lru_cache(maxsize=None)
def unpack_header(value: bytes) -> Tuple[int, int, int, bool]:
    """
    Cached Unpacking of a GeoPackage Geometry Header
    """
    _, _, flags, srs_id = unpack(HEADER_CODE, value)
    envelope_code = (flags & (0x07 << 1)) >> 1
    is_empty = bool((flags & (0x01 << 4)) >> 4)
    return srs_id, envelope_code, ENVELOPE_OFFSET[envelope_code], is_empty
# End unpack_header function


def unpack_envelope(code: int, value: bytes) -> Envelope:
    """
    Unpack Envelope

    From Geopackage spec (v1.3.1)
    0: no envelope (space saving slower indexing option), 0 bytes
    1: envelope is [minx, maxx, miny, maxy], 32 bytes
    2: envelope is [minx, maxx, miny, maxy, minz, maxz], 48 bytes
    3: envelope is [minx, maxx, miny, maxy, minm, maxm], 48 bytes
    4: envelope is [minx, maxx, miny, maxy, minz, maxz, minm, maxm], 64 bytes
    """
    if not code:
        return EMPTY_ENVELOPE
    if code not in ENVELOPE_COUNT:
        return EMPTY_ENVELOPE
    try:
        values = unpack(f'<{ENVELOPE_COUNT[code]}d', value[HEADER_OFFSET:])
    except StructError:
        return EMPTY_ENVELOPE
    min_x = max_x = min_y = max_y = min_z = max_z = min_m = max_m = nan
    if code == 1:
        min_x, max_x, min_y, max_y = values
    elif code == 2:
        min_x, max_x, min_y, max_y, min_z, max_z = values
    elif code == 3:
        min_x, max_x, min_y, max_y, min_m, max_m = values
    elif code == 4:
        min_x, max_x, min_y, max_y, min_z, max_z, min_m, max_m = values
    return Envelope(
        code=code, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
        min_z=min_z, max_z=max_z, min_m=min_m, max_m=max_m)
# End unpack_envelope function


def _min_max(values: Union[VALUES, Tuple[float, ...]]) \
        -> Tuple[float, float]:
    """
    Min and Max values, returns nan's if empty list or no finite values.
    """
    if not values:
        return nan, nan
    values = [v for v in values if isfinite(v)]
    if not values:
        return nan, nan
    return min(values), max(values)
# End _min_max function


def envelope_from_geometries(geoms: GEOMS) -> Envelope:
    """
    Envelope from Geometries
    """
    if not geoms:
        return EMPTY_ENVELOPE
    xs, ys = [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
    return _envelope_xy(xs=xs, ys=ys)
# End envelope_from_geometries function


def envelope_from_geometries_z(geoms: GEOMS_Z) -> Envelope:
    """
    Envelope from Geometries with Z
    """
    if not geoms:
        return EMPTY_ENVELOPE
    xs, ys, zs = [], [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
        zs.extend((env.min_z, env.max_z))
    return _envelope_xyz(xs=xs, ys=ys, zs=zs)
# End envelope_from_geometries_z function


def envelope_from_geometries_m(geoms: GEOMS_M) -> Envelope:
    """
    Envelope from Geometries with M
    """
    if not geoms:
        return EMPTY_ENVELOPE
    xs, ys, ms = [], [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
        ms.extend((env.min_m, env.max_m))
    return _envelope_xym(xs=xs, ys=ys, ms=ms)
# End envelope_from_geometries_m function


def envelope_from_geometries_zm(geoms: GEOMS_ZM) -> Envelope:
    """
    Envelope from Geometries with ZM
    """
    if not geoms:
        return EMPTY_ENVELOPE
    xs, ys, zs, ms = [], [], [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
        zs.extend((env.min_z, env.max_z))
        ms.extend((env.min_m, env.max_m))
    return _envelope_xyzm(xs=xs, ys=ys, zs=zs, ms=ms)
# End envelope_from_geometries_zm function


def envelope_from_coordinates(coordinates: List[DOUBLE]) -> Envelope:
    """
    Envelope from Coordinates
    """
    if not coordinates:
        return EMPTY_ENVELOPE
    return _envelope_xy(*zip(*coordinates))
# End envelope_from_coordinates function


def envelope_from_coordinates_z(coordinates: List[TRIPLE]) -> Envelope:
    """
    Envelope from Coordinates with Z
    """
    if not coordinates:
        return EMPTY_ENVELOPE
    return _envelope_xyz(*zip(*coordinates))
# End envelope_from_coordinates_z function


def envelope_from_coordinates_m(coordinates: List[TRIPLE]) -> Envelope:
    """
    Envelope from Coordinates with M
    """
    if not coordinates:
        return EMPTY_ENVELOPE
    return _envelope_xym(*zip(*coordinates))
# End envelope_from_coordinates_m function


def envelope_from_coordinates_zm(coordinates: List[QUADRUPLE]) -> Envelope:
    """
    Envelope from Coordinates with ZM
    """
    if not coordinates:
        return EMPTY_ENVELOPE
    return _envelope_xyzm(*zip(*coordinates))
# End envelope_from_coordinates_zm function


def _envelope_xy(xs: VALUES, ys: VALUES) -> Envelope:
    """
    Envelope XY
    """
    min_x, max_x = _min_max(xs)
    min_y, max_y = _min_max(ys)
    return Envelope(code=1, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)
# End _envelope_xy function


def _envelope_xyz(xs: VALUES, ys: VALUES, zs: VALUES) -> Envelope:
    """
    Envelope XYZ
    """
    min_x, max_x = _min_max(xs)
    min_y, max_y = _min_max(ys)
    min_z, max_z = _min_max(zs)
    return Envelope(code=2, min_x=min_x, max_x=max_x,
                    min_y=min_y, max_y=max_y,
                    min_z=min_z, max_z=max_z)
# End _envelope_xyz function


def _envelope_xym(xs: VALUES, ys: VALUES, ms: VALUES) -> Envelope:
    """
    Envelope XYM
    """
    min_x, max_x = _min_max(xs)
    min_y, max_y = _min_max(ys)
    min_m, max_m = _min_max(ms)
    return Envelope(code=3, min_x=min_x, max_x=max_x,
                    min_y=min_y, max_y=max_y,
                    min_m=min_m, max_m=max_m)
# End _envelope_xym function


def _envelope_xyzm(xs: VALUES, ys: VALUES, zs: VALUES, ms: VALUES) -> Envelope:
    """
    Envelope XYZM
    """
    min_x, max_x = _min_max(xs)
    min_y, max_y = _min_max(ys)
    min_z, max_z = _min_max(zs)
    min_m, max_m = _min_max(ms)
    return Envelope(
        code=4, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
        min_z=min_z, max_z=max_z, min_m=min_m, max_m=max_m)
# End _envelope_xyzm function


if __name__ == '__main__':  # pragma: no cover
    pass
