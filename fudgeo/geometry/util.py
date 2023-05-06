# -*- coding: utf-8 -*-
"""
Utility Functions
"""


from functools import lru_cache, reduce
from operator import add
from struct import pack, unpack
from typing import List, Tuple

from fudgeo.constant import (
    COORDINATES, COUNT_CODE, EMPTY, ENVELOPE_OFFSET, GP_MAGIC, HEADER_CODE,
    POINT_PREFIX, TWO_D)


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
def unpack_header(value: bytes) -> Tuple[int, int, bool]:
    """
    Cached Unpacking of a GeoPackage Geometry Header
    """
    _, _, flags, srs_id = unpack(HEADER_CODE, value)
    envelope_code = (flags & (0x07 << 1)) >> 1
    is_empty = bool((flags & (0x01 << 4)) >> 4)
    return srs_id, ENVELOPE_OFFSET[envelope_code], is_empty
# End unpack_header function


if __name__ == '__main__':  # pragma: no cover
    pass
