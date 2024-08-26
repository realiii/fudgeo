# -*- coding: utf-8 -*-
"""
Utility Functions
"""


from functools import lru_cache
from math import nan
# noinspection PyPep8Naming
from struct import error as StructError, pack, unpack
from typing import Any, Callable, Union

from numpy import array, frombuffer, ndarray
from bottleneck import nanmax, nanmin

from fudgeo.alias import GEOMS, GEOMS_M, GEOMS_Z, GEOMS_ZM
from fudgeo.constant import (
    COUNT_CODE, EMPTY, ENVELOPE_COUNT, ENVELOPE_OFFSET, GP_MAGIC, HEADER_CODE,
    HEADER_OFFSET, POINT_PREFIX_ZM)
from fudgeo.enumeration import EnvelopeCode


def as_array(coordinates: Any) -> ndarray:
    """
    Convert input coordinates to an array
    """
    if not isinstance(coordinates, ndarray):
        coordinates = array(coordinates, dtype=float)
    return coordinates
# End as_array function


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
        if not isinstance(other, Envelope):  # pragma: no cover
            return NotImplemented
        code = self.code
        if code != other.code:
            return False
        if not code:
            return True
        same_x = self.min_x == other.min_x and self.max_x == other.max_x
        same_y = self.min_y == other.min_y and self.max_y == other.max_y
        same_xy = same_x and same_y
        if not same_xy or code == EnvelopeCode.xy:
            return same_xy
        same_z = self.min_z == other.min_z and self.max_z == other.max_z
        if code == EnvelopeCode.xyz:
            return same_z
        same_m = self.min_m == other.min_m and self.max_m == other.max_m
        if code == EnvelopeCode.xym:
            return same_m
        return same_m and same_z
    # End eq built-in

    @property
    def bounding_box(self) -> tuple[float, float, float, float]:
        """
        Bounding Box
        """
        return self.min_x, self.min_y, self.max_x, self.max_y
    # End bounding_box property

    def to_wkb(self) -> tuple[int, bytes]:
        """
        To WKB
        """
        code = self.code
        if code not in {EnvelopeCode.xy, EnvelopeCode.xyz,
                        EnvelopeCode.xym, EnvelopeCode.xyzm}:
            return EnvelopeCode.empty, EMPTY
        values = self.min_x, self.max_x, self.min_y, self.max_y
        if code == EnvelopeCode.xy:
            pass
        elif code == EnvelopeCode.xyz:
            values = *values, self.min_z, self.max_z
        elif code == EnvelopeCode.xym:
            values = *values, self.min_m, self.max_m
        elif code == EnvelopeCode.xyzm:
            values = *values, self.min_z, self.max_z, self.min_m, self.max_m
        return code, pack(f'<{ENVELOPE_COUNT[code]}d', *values)
    # End to_wkb method

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


def lazy_unpack(cls: Any, value: Union[bytes, bytearray],
                dimension: int) -> Any:
    """
    Unpack just the header and envelope, adding data to class for later use.
    """
    (srs_id, env_code, offset,
     is_empty) = unpack_header(bytes(value[:HEADER_OFFSET]))
    obj = cls([], srs_id=srs_id)
    obj._is_empty = is_empty
    if is_empty:
        return obj
    view = memoryview(value)
    obj._env = unpack_envelope(code=env_code, view=view[:offset])
    obj._args = view[offset:], dimension
    return obj
# End lazy_unpack function


def unpack_line(view: memoryview, dimension: int,
                is_ring: bool = False) -> ndarray:
    """
    Unpack Values for LineString
    """
    count, data = get_count_and_data(view, is_ring=is_ring)
    return frombuffer(
        data, dtype=float, count=dimension * count).reshape(-1, dimension)
# End unpack_line function


def unpack_points(view: memoryview, dimension: int) -> ndarray:
    """
    Unpack Values for Multi Point
    """
    offset = 5
    size = (8 * dimension) + offset
    count, data = get_count_and_data(view)
    if not count:
        return array([], dtype=float)
    ary = bytearray()
    for i in range(0, len(data), size):
        ary.extend(data[i + offset:i + size])
    return frombuffer(
        ary, dtype=float, count=dimension * count).reshape(-1, dimension)
# End unpack_points function


def pack_coordinates(ary: bytearray, prefix: bytes, coordinates: ndarray,
                     has_z: bool = False, has_m: bool = False,
                     use_point_prefix: bool = False) -> bytearray:
    """
    Pack Coordinates
    """
    count = len(coordinates)
    ary.extend(prefix + pack(COUNT_CODE, count))
    data = coordinates.tobytes()
    if not use_point_prefix or not count:
        ary.extend(data)
        return ary
    length = len(data)
    view = memoryview(data)
    step = length // count
    prefix = POINT_PREFIX_ZM.get((has_z, has_m))
    for i in range(0, length, step):
        ary.extend(prefix)
        ary.extend(view[i:i + step])
    return ary
# End pack_coordinates function


def unpack_lines(view: memoryview, dimension: int, is_ring: bool = False) \
        -> list[ndarray]:
    """
    Unpack Values for Multi LineString and Polygons
    """
    size, last_end = 8 * dimension, 0
    offset, unit = (4, COUNT_CODE) if is_ring else (9, '<BII')
    count, data = get_count_and_data(view)
    lines = []
    for _ in range(count):
        *_, length = unpack(unit, data[last_end:last_end + offset])
        end = last_end + offset + (size * length)
        points = unpack_line(data[last_end:end], dimension, is_ring=is_ring)
        last_end = end
        lines.append(points)
    return lines
# End unpack_lines function


def unpack_polygons(view: memoryview, dimension: int) \
        -> list[list[ndarray]]:
    """
    Unpack Values for Multi Polygon Type Containing Polygons
    """
    size, last_end = 8 * dimension, 0
    count, data = get_count_and_data(view)
    polygons = []
    for _ in range(0, count):
        points = unpack_lines(data[last_end:], dimension, is_ring=True)
        point_count = sum(len(x) for x in points)
        last_end += (point_count * size) + (len(points) * 4) + 9
        polygons.append(points)
    return polygons
# End unpack_polygons method


def get_count_and_data(view: memoryview, is_ring: bool = False) \
        -> tuple[int, memoryview]:
    """
    Get Count from header and return the value portion of the stream
    """
    first, second = (0, 4) if is_ring else (5, 9)
    count, = unpack(COUNT_CODE, view[first: second])
    return count, view[second:]
# End get_count_and_data function


@lru_cache(maxsize=None)
def make_header(srs_id: int, is_empty: bool, envelope_code: int = 0) -> bytes:
    """
    Cached Creation of a GeoPackage Geometry Header
    """
    flags = 1
    if is_empty:
        flags |= (1 << 4)
        envelope_code = 0
    flags |= (envelope_code << 1)
    return pack(HEADER_CODE, GP_MAGIC, 0, flags, srs_id)
# End make_header function


@lru_cache(maxsize=None)
def unpack_header(view: Union[bytes, memoryview]) -> tuple[int, int, int, bool]:
    """
    Cached Unpacking of a GeoPackage Geometry Header
    """
    _, _, flags, srs_id = unpack(HEADER_CODE, view)
    envelope_code = (flags & (0x07 << 1)) >> 1
    is_empty = bool((flags & (0x01 << 4)) >> 4)
    return srs_id, envelope_code, ENVELOPE_OFFSET[envelope_code], is_empty
# End unpack_header function


def unpack_envelope(code: int, view: memoryview) -> Envelope:
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
    if code not in ENVELOPE_COUNT:  # pragma: no cover
        return EMPTY_ENVELOPE
    try:
        values = unpack(f'<{ENVELOPE_COUNT[code]}d', view[HEADER_OFFSET:])
    except StructError:  # pragma: no cover
        return EMPTY_ENVELOPE
    min_x = max_x = min_y = max_y = min_z = max_z = min_m = max_m = nan
    if code == EnvelopeCode.xy:
        min_x, max_x, min_y, max_y = values
    elif code == EnvelopeCode.xyz:
        min_x, max_x, min_y, max_y, min_z, max_z = values
    elif code == EnvelopeCode.xym:
        min_x, max_x, min_y, max_y, min_m, max_m = values
    elif code == EnvelopeCode.xyzm:
        min_x, max_x, min_y, max_y, min_z, max_z, min_m, max_m = values
    return Envelope(
        code=code, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
        min_z=min_z, max_z=max_z, min_m=min_m, max_m=max_m)
# End unpack_envelope function


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
    return _envelope_xy(xs=array(xs, dtype=float), ys=array(ys, dtype=float))
# End envelope_from_geometries function


def envelope_from_geometries_z(geoms: GEOMS_Z) -> Envelope:
    """
    Envelope from Geometries with Z
    """
    if not geoms:  # pragma: no cover
        return EMPTY_ENVELOPE
    xs, ys, zs = [], [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
        zs.extend((env.min_z, env.max_z))
    return _envelope_xyz(
        xs=array(xs, dtype=float), ys=array(ys, dtype=float),
        zs=array(zs, dtype=float))
# End envelope_from_geometries_z function


def envelope_from_geometries_m(geoms: GEOMS_M) -> Envelope:
    """
    Envelope from Geometries with M
    """
    if not geoms:  # pragma: no cover
        return EMPTY_ENVELOPE
    xs, ys, ms = [], [], []
    for geom in geoms:
        env = geom.envelope
        xs.extend((env.min_x, env.max_x))
        ys.extend((env.min_y, env.max_y))
        ms.extend((env.min_m, env.max_m))
    return _envelope_xym(
        xs=array(xs, dtype=float), ys=array(ys, dtype=float),
        ms=array(ms, dtype=float))
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
    return _envelope_xyzm(
        xs=array(xs, dtype=float), ys=array(ys, dtype=float),
        zs=array(zs, dtype=float), ms=array(ms, dtype=float))
# End envelope_from_geometries_zm function


def envelope_from_coordinates(coordinates: ndarray) -> Envelope:
    """
    Envelope from Coordinates
    """
    if not len(coordinates):
        return EMPTY_ENVELOPE
    return _envelope_xy(xs=coordinates[:, 0], ys=coordinates[:, 1])
# End envelope_from_coordinates function


def envelope_from_coordinates_z(coordinates: ndarray) -> Envelope:
    """
    Envelope from Coordinates with Z
    """
    if not len(coordinates):
        return EMPTY_ENVELOPE
    return _envelope_xyz(
        xs=coordinates[:, 0], ys=coordinates[:, 1], zs=coordinates[:, 2])
# End envelope_from_coordinates_z function


def envelope_from_coordinates_m(coordinates: ndarray) -> Envelope:
    """
    Envelope from Coordinates with M
    """
    if not len(coordinates):
        return EMPTY_ENVELOPE
    return _envelope_xym(
        xs=coordinates[:, 0], ys=coordinates[:, 1], ms=coordinates[:, 2])
# End envelope_from_coordinates_m function


def envelope_from_coordinates_zm(coordinates: ndarray) -> Envelope:
    """
    Envelope from Coordinates with ZM
    """
    if not len(coordinates):
        return EMPTY_ENVELOPE
    return _envelope_xyzm(
        xs=coordinates[:, 0], ys=coordinates[:, 1],
        zs=coordinates[:, 2], ms=coordinates[:, 3])
# End envelope_from_coordinates_zm function


def _envelope_xy(xs: ndarray, ys: ndarray) -> Envelope:
    """
    Envelope XY
    """
    min_x, max_x = nanmin(xs), nanmax(xs)
    min_y, max_y = nanmin(ys), nanmax(ys)
    return Envelope(code=EnvelopeCode.xy,
                    min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)
# End _envelope_xy function


def _envelope_xyz(xs: ndarray, ys: ndarray, zs: ndarray) -> Envelope:
    """
    Envelope XYZ
    """
    min_x, max_x = nanmin(xs), nanmax(xs)
    min_y, max_y = nanmin(ys), nanmax(ys)
    min_z, max_z = nanmin(zs), nanmax(zs)
    return Envelope(code=EnvelopeCode.xyz,
                    min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
                    min_z=min_z, max_z=max_z)
# End _envelope_xyz function


def _envelope_xym(xs: ndarray, ys: ndarray, ms: ndarray) -> Envelope:
    """
    Envelope XYM
    """
    min_x, max_x = nanmin(xs), nanmax(xs)
    min_y, max_y = nanmin(ys), nanmax(ys)
    min_m, max_m = nanmin(ms), nanmax(ms)
    return Envelope(code=EnvelopeCode.xym,
                    min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
                    min_m=min_m, max_m=max_m)
# End _envelope_xym function


def _envelope_xyzm(xs: ndarray, ys: ndarray,
                   zs: ndarray, ms: ndarray) -> Envelope:
    """
    Envelope XYZM
    """
    min_x, max_x = nanmin(xs), nanmax(xs)
    min_y, max_y = nanmin(ys), nanmax(ys)
    min_z, max_z = nanmin(zs), nanmax(zs)
    min_m, max_m = nanmin(ms), nanmax(ms)
    return Envelope(code=EnvelopeCode.xyzm,
                    min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y,
                    min_z=min_z, max_z=max_z, min_m=min_m, max_m=max_m)
# End _envelope_xyzm function


ENV_GEOM: dict[int, Callable[[Union[GEOMS, GEOMS_Z, GEOMS_M, GEOMS_ZM]], Envelope]] = {
    EnvelopeCode.empty: lambda _: EMPTY_ENVELOPE,
    EnvelopeCode.xy: envelope_from_geometries,
    EnvelopeCode.xyz: envelope_from_geometries_z,
    EnvelopeCode.xym: envelope_from_geometries_m,
    EnvelopeCode.xyzm: envelope_from_geometries_zm,
}


ENV_COORD: dict[int, Callable[[ndarray], Envelope]] = {
    EnvelopeCode.empty: lambda _: EMPTY_ENVELOPE,
    EnvelopeCode.xy: envelope_from_coordinates,
    EnvelopeCode.xyz: envelope_from_coordinates_z,
    EnvelopeCode.xym: envelope_from_coordinates_m,
    EnvelopeCode.xyzm: envelope_from_coordinates_zm,
}


if __name__ == '__main__':  # pragma: no cover
    pass
