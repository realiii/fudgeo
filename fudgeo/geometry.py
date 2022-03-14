# -*- coding: utf-8 -*-
"""
Geometry
"""


from abc import abstractmethod
from functools import lru_cache, reduce
from operator import add
from struct import pack, unpack
from typing import List, Tuple

from fudgeo.constant import (
    BYTE_UINT, COUNT_UNIT, DOUBLE, EMPTY, GP_MAGIC, QUADRUPLE, SRS_ID, TRIPLE,
    WGS84, WKB_LINESTRING_M_PRE, WKB_LINESTRING_PRE, WKB_LINESTRING_ZM_PRE,
    WKB_LINESTRING_Z_PRE, WKB_MULTI_LINESTRING_M_PRE, WKB_MULTI_LINESTRING_PRE,
    WKB_MULTI_LINESTRING_ZM_PRE, WKB_MULTI_LINESTRING_Z_PRE,
    WKB_MULTI_POINT_M_PRE, WKB_MULTI_POINT_PRE, WKB_MULTI_POINT_ZM_PRE,
    WKB_MULTI_POINT_Z_PRE, WKB_MULTI_POLYGON_PRE, WKB_MULTI_POLYGON_Z_PRE,
    WKB_POINT_M_PRE, WKB_POINT_PRE, WKB_POINT_ZM_PRE, WKB_POINT_Z_PRE,
    WKB_POLYGON_PRE, WKB_POLYGON_Z_PRE)


__all__ = ['Point', 'PointZ', 'PointM', 'PointZM', 'MultiPoint', 'MultiPointZ',
           'MultiPointM', 'MultiPointZM', 'LineString', 'LineStringZ',
           'LineStringM', 'LineStringZM', 'MultiLineString', 'MultiLineStringZ',
           'MultiLineStringM', 'MultiLineStringZM', 'Polygon', 'PolygonZ',
           'MultiPolygon', 'MultiPolygonZ']


def _unpack_line(value: bytes, dimension: int,
                 is_ring: bool = False) -> List[Tuple[float, ...]]:
    """
    Unpack Values for LineString
    """
    count, data = _get_count_and_data(value, is_ring=is_ring)
    total = dimension * count
    values: Tuple[float, ...] = unpack(f'<{total}d', data)
    return [values[i:i + dimension] for i in range(0, total, dimension)]
# End _unpack_line function


def _unpack_points(value: bytes, dimension: int) -> List[Tuple[float, ...]]:
    """
    Unpack Values for Multi Point
    """
    offset = 5
    size = (8 * dimension) + offset
    count, data = _get_count_and_data(value)
    total = dimension * count
    data = [data[i + offset:i + size] for i in range(0, len(data), size)]
    values: Tuple[float, ...] = unpack(f'<{total}d', reduce(add, data))
    return [values[i:i + dimension] for i in range(0, total, dimension)]
# End _unpack_points function


def _unpack_lines(value: bytes, dimension: int, is_ring: bool = False) \
        -> List[List[Tuple[float, ...]]]:
    """
    Unpack Values for Multi LineString and Polygons
    """
    size, last_end = 8 * dimension, 0
    offset, unit = (4, COUNT_UNIT) if is_ring else (9, '<BII')
    count, data = _get_count_and_data(value)
    lines = []
    for _ in range(count):
        *_, length = unpack(unit, data[last_end:last_end + offset])
        end = last_end + offset + (size * length)
        # noinspection PyTypeChecker
        points: List[Tuple[float, ...]] = _unpack_line(
            data[last_end:end], dimension, is_ring=is_ring)
        last_end = end
        lines.append(points)
    return lines
# End _unpack_lines function


def _unpack_polygons(value: bytes, dimension: int) \
        -> List[List[List[Tuple[float, ...]]]]:
    """
    Unpack Values for Multi Polygon Type Containing Polygons
    """
    size, last_end = 8 * dimension, 0
    count, data = _get_count_and_data(value)
    polygons = []
    for _ in range(0, count):
        points = _unpack_lines(data[last_end:], dimension, is_ring=True)
        point_count = sum(len(x) for x in points)
        last_end += (point_count * size) + (len(points) * 4) + 9
        polygons.append(points)
    return polygons
# End _unpack_polygons method


def _get_count_and_data(value: bytes, is_ring: bool = False) \
        -> Tuple[int, bytes]:
    """
    Get Count from header and return the value portion of the stream
    """
    first, second = (0, 4) if is_ring else (5, 9)
    header, data = value[first: second], value[second:]
    count, = unpack(COUNT_UNIT, header)
    return count, data
# End _get_count_and_data function


@lru_cache(maxsize=None)
def _make_header_with_srs_id(srs_id: int) -> bytes:
    """
    Cached Header Creation
    """
    return pack('<2s2bi', GP_MAGIC, 0, 1, srs_id)
# End _make_header_with_srs_id function


class AbstractGeometry:
    """
    Abstract Geometry
    """
    __slots__ = [SRS_ID]

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the Point class
        """
        super().__init__()
        self.srs_id: int = srs_id
    # End init built-in

    @staticmethod
    def _joiner(*args) -> bytes:
        """
        Joiner
        """
        return EMPTY.join(args)
    # End _joiner method

    @staticmethod
    def _unpack_srs_id(value: bytes) -> int:
        """
        Unpack SRS ID
        """
        _, _, _, srs_id = unpack('<2s2bi', value[:8])
        return srs_id
    # End  method

    def _make_header(self) -> bytes:
        """
        Make Header
        """
        return _make_header_with_srs_id(self.srs_id)
    # End _make_header method

    @abstractmethod
    def to_wkb(self, use_prefix: bool = True) -> bytes:  # pragma: nocover
        """
        To WKB
        """
        pass
    # End to_wkb method

    @classmethod
    @abstractmethod
    def from_wkb(cls, wkb: bytes) -> 'AbstractGeometry':  # pragma: nocover
        """
        From WKB
        """
        pass
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return self._joiner(self._make_header(), self.to_wkb())
    # End to_gpkg method

    @classmethod
    @abstractmethod
    def from_gpkg(cls, value: bytes) -> 'AbstractGeometry':  # pragma: nocover
        """
        From Geopackage
        """
        pass
    # End from_gpkg method
# End AbstractGeometry class


class Point(AbstractGeometry):
    """
    Point
    """
    __slots__ = ['x', 'y']

    def __init__(self, *, x: float, y: float, srs_id: int = WGS84) -> None:
        """
        Initialize the Point class
        """
        super().__init__(srs_id=srs_id)
        self.x: float = x
        self.y: float = y
    # End init built-in

    def __eq__(self, other: 'Point') -> bool:
        """
        Equals
        """
        if not isinstance(other, Point):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return (self.x, self.y) == (other.x, other.y)
    # End eq built-in

    @staticmethod
    def _unpack(value: bytes) -> DOUBLE:
        """
        Unpack Values
        """
        *_, x, y = unpack(f'{BYTE_UINT}2d', value)
        return x, y
    # End _unpack method

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_PRE if use_prefix else EMPTY
        return self._joiner(pre, pack('<2d', self.x, self.y))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'Point':
        """
        From WKB
        """
        x, y = cls._unpack(wkb)
        return cls(x=x, y=y)
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Point':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        x, y = cls._unpack(value[8:])
        return cls(x=x, y=y, srs_id=srs_id)
    # End from_gpkg method
# End Point class


class PointZ(AbstractGeometry):
    """
    Point Z
    """
    __slots__ = ['x', 'y', 'z']

    def __init__(self, *, x: float, y: float, z: float,
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PointZ class
        """
        super().__init__(srs_id=srs_id)
        self.x: float = x
        self.y: float = y
        self.z: float = z
    # End init built-in

    def __eq__(self, other: 'PointZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, PointZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)
    # End eq built-in

    @staticmethod
    def _unpack(value: bytes) -> TRIPLE:
        """
        Unpack Values
        """
        *_, x, y, z = unpack(f'{BYTE_UINT}3d', value)
        return x, y, z
    # End _unpack method

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_Z_PRE if use_prefix else EMPTY
        return self._joiner(pre, pack('<3d', self.x, self.y, self.z))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PointZ':
        """
        From WKB
        """
        x, y, z = cls._unpack(wkb)
        return cls(x=x, y=y, z=z)
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        x, y, z = cls._unpack(value[8:])
        return cls(x=x, y=y, z=z, srs_id=srs_id)
    # End from_gpkg method
# End PointZ class


class PointM(AbstractGeometry):
    """
    Point M
    """
    __slots__ = ['x', 'y', 'm']

    def __init__(self, *, x: float, y: float, m: float,
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PointM class
        """
        super().__init__(srs_id=srs_id)
        self.x: float = x
        self.y: float = y
        self.m: float = m
    # End init built-in

    def __eq__(self, other: 'PointM') -> bool:
        """
        Equals
        """
        if not isinstance(other, PointM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return (self.x, self.y, self.m) == (other.x, other.y, other.m)
    # End eq built-in

    @staticmethod
    def _unpack(value: bytes) -> TRIPLE:
        """
        Unpack Values
        """
        *_, x, y, m = unpack(f'{BYTE_UINT}3d', value)
        return x, y, m
    # End _unpack method

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_M_PRE if use_prefix else EMPTY
        return self._joiner(pre, pack('<3d', self.x, self.y, self.m))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PointM':
        """
        From WKB
        """
        x, y, m = cls._unpack(wkb)
        return cls(x=x, y=y, m=m)
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        x, y, m = cls._unpack(value[8:])
        return cls(x=x, y=y, m=m, srs_id=srs_id)
    # End from_gpkg method
# End PointM class


class PointZM(AbstractGeometry):
    """
    Point ZM
    """
    __slots__ = ['x', 'y', 'z', 'm']

    def __init__(self, *, x: float, y: float, z: float, m: float,
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PointZM class
        """
        super().__init__(srs_id=srs_id)
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.m: float = m
    # End init built-in

    def __eq__(self, other: 'PointZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, PointZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return (self.x, self.y, self.z, self.m) == (
            other.x, other.y, other.z, other.m)
    # End eq built-in

    @staticmethod
    def _unpack(value: bytes) -> QUADRUPLE:
        """
        Unpack Values
        """
        *_, x, y, z, m = unpack(f'{BYTE_UINT}4d', value)
        return x, y, z, m
    # End _unpack method

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_ZM_PRE if use_prefix else EMPTY
        return self._joiner(pre, pack('<4d', self.x, self.y, self.z, self.m))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PointZM':
        """
        From WKB
        """
        x, y, z, m = cls._unpack(wkb)
        return cls(x=x, y=y, z=z, m=m)
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        x, y, z, m = cls._unpack(value[8:])
        return cls(x=x, y=y, z=z, m=m, srs_id=srs_id)
    # End from_gpkg method
# End PointZM class


class MultiPoint(AbstractGeometry):
    """
    MultiPoint
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[DOUBLE], srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPoint class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[Point] = [Point(x=x, y=y) for x, y in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPoint') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPoint):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POINT_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb() for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPoint':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_points(wkb, dimension=2))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPoint':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_points(value[8:], dimension=2), srs_id=srs_id)
    # End from_gpkg method
# End MultiPoint class


class MultiPointZ(AbstractGeometry):
    """
    MultiPointZ
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPointZ class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointZ] = [
            PointZ(x=x, y=y, z=z) for x, y, z in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPointZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPointZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POINT_Z_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb() for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPointZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_points(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_points(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End MultiPointZ class


class MultiPointM(AbstractGeometry):
    """
    MultiPointM
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPointM class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointM] = [
            PointM(x=x, y=y, m=m) for x, y, m in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPointM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPointM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POINT_M_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb() for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPointM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_points(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_points(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End MultiPointM class


class MultiPointZM(AbstractGeometry):
    """
    MultiPointZM
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[QUADRUPLE],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPointZM class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointZM] = [
            PointZM(x=x, y=y, z=z, m=m) for x, y, z, m in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPointZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPointZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POINT_ZM_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb() for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPointZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_points(wkb, dimension=4))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_points(value[8:], dimension=4), srs_id=srs_id)
    # End from_gpkg method
# End MultiPointZM class


class LineString(AbstractGeometry):
    """
    LineString
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[DOUBLE], srs_id: int = WGS84) -> None:
        """
        Initialize the LineString class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[Point] = [Point(x=x, y=y) for x, y in coordinates]
    # End init built-in

    def __eq__(self, other: 'LineString') -> bool:
        """
        Equals
        """
        if not isinstance(other, LineString):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_LINESTRING_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LineString':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=2))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineString':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_line(value[8:], dimension=2), srs_id=srs_id)
    # End from_gpkg method
# End LineString class


class LineStringZ(AbstractGeometry):
    """
    LineStringZ
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
        """
        Initialize the LineStringZ class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointZ] = [
            PointZ(x=x, y=y, z=z) for x, y, z in coordinates]
    # End init built-in

    def __eq__(self, other: 'LineStringZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, LineStringZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_LINESTRING_Z_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LineStringZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_line(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End LineStringZ class


class LineStringM(AbstractGeometry):
    """
    LineStringM
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
        """
        Initialize the LineStringM class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointM] = [
            PointM(x=x, y=y, m=m) for x, y, m in coordinates]
    # End init built-in

    def __eq__(self, other: 'LineStringM') -> bool:
        """
        Equals
        """
        if not isinstance(other, LineStringM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_LINESTRING_M_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LineStringM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_line(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End LineStringM class


class LineStringZM(AbstractGeometry):
    """
    LineStringZM
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[QUADRUPLE],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the LineStringZM class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointZM] = [
            PointZM(x=x, y=y, z=z, m=m) for x, y, z, m in coordinates]
    # End init built-in

    def __eq__(self, other: 'LineStringZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, LineStringZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_LINESTRING_ZM_PRE, pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LineStringZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=4))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringZM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_line(value[8:], dimension=4), srs_id=srs_id)
    # End from_gpkg method
# End LineStringZM class


class MultiLineString(AbstractGeometry):
    """
    Multi LineString
    """
    __slots__ = 'lines'

    def __init__(self, coordinates: List[List[DOUBLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiLineString class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineString] = [
            LineString(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiLineString') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiLineString):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.lines == other.lines
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_LINESTRING_PRE, pack(COUNT_UNIT, len(self.lines)),
            self._joiner(*[line.to_wkb() for line in self.lines]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiLineString':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=2))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineString':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(value[8:], dimension=2), srs_id=srs_id)
    # End from_gpkg method
# End MultiLineString class


class MultiLineStringZ(AbstractGeometry):
    """
    Multi LineString Z
    """
    __slots__ = 'lines'

    def __init__(self, coordinates: List[List[TRIPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiLineStringZ class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringZ] = [
            LineStringZ(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiLineStringZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiLineStringZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.lines == other.lines
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_LINESTRING_Z_PRE, pack(COUNT_UNIT, len(self.lines)),
            self._joiner(*[line.to_wkb() for line in self.lines]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiLineStringZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End MultiLineStringZ class


class MultiLineStringM(AbstractGeometry):
    """
    Multi LineString M
    """
    __slots__ = 'lines'

    def __init__(self, coordinates: List[List[TRIPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiLineStringM class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringM] = [
            LineStringM(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiLineStringM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiLineStringM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.lines == other.lines
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_LINESTRING_M_PRE, pack(COUNT_UNIT, len(self.lines)),
            self._joiner(*[line.to_wkb() for line in self.lines]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiLineStringM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End MultiLineStringM class


class MultiLineStringZM(AbstractGeometry):
    """
    Multi LineString ZM
    """
    __slots__ = 'lines'

    def __init__(self, coordinates: List[List[QUADRUPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiLineStringZM class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringZM] = [
            LineStringZM(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiLineStringZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiLineStringZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.lines == other.lines
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_LINESTRING_ZM_PRE, pack(COUNT_UNIT, len(self.lines)),
            self._joiner(*[line.to_wkb() for line in self.lines]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiLineStringZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=4))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringZM':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(value[8:], dimension=4), srs_id=srs_id)
    # End from_gpkg method
# End MultiLineStringZM class


class LinearRing(AbstractGeometry):
    """
    LinearRing
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[DOUBLE],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the LinearRing class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[Point] = [Point(x=x, y=y) for x, y in coordinates]
    # End init built-in

    def __eq__(self, other: 'LinearRing') -> bool:
        """
        Equals
        """
        if not isinstance(other, LinearRing):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRing':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=2, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError('Linear Rings not supported for Geopackage')
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRing':
        """
        From Geopackage
        """
        raise NotImplementedError('Linear Rings not supported for Geopackage')
    # End from_gpkg method
# End LinearRing class


class LinearRingZ(AbstractGeometry):
    """
    LinearRingZ
    """
    __slots__ = 'points'

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
        """
        Initialize the LinearRing class
        """
        super().__init__(srs_id=srs_id)
        self.points: List[PointZ] = [
            PointZ(x=x, y=y, z=z) for x, y, z in coordinates]
    # End init built-in

    def __eq__(self, other: 'LinearRingZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, LinearRingZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            pack(COUNT_UNIT, len(self.points)),
            self._joiner(*[pt.to_wkb(False) for pt in self.points]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRingZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_line(wkb, dimension=3, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError('Linear Rings not supported for Geopackage')
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZ':
        """
        From Geopackage
        """
        raise NotImplementedError('Linear Rings not supported for Geopackage')
    # End from_gpkg method
# End LinearRingZ class


class Polygon(AbstractGeometry):
    """
    Polygon
    """
    __slots__ = 'rings'

    def __init__(self, coordinates: List[List[DOUBLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the Polygon class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRing] = [
            LinearRing(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'Polygon') -> bool:
        """
        Equals
        """
        if not isinstance(other, Polygon):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.rings == other.rings
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_POLYGON_PRE, pack(COUNT_UNIT, len(self.rings)),
            self._joiner(*[ring.to_wkb() for ring in self.rings]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'Polygon':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=2, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Polygon':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(
            value[8:], dimension=2, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End Polygon class


class PolygonZ(AbstractGeometry):
    """
    PolygonZ
    """
    __slots__ = 'rings'

    def __init__(self, coordinates: List[List[TRIPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PolygonZ class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingZ] = [
            LinearRingZ(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'PolygonZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, PolygonZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.rings == other.rings
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_POLYGON_Z_PRE, pack(COUNT_UNIT, len(self.rings)),
            self._joiner(*[ring.to_wkb() for ring in self.rings]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PolygonZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_lines(wkb, dimension=3, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_lines(
            value[8:], dimension=3, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonZ class


class MultiPolygon(AbstractGeometry):
    """
    MultiPolygon
    """
    __slots__ = 'polygons'

    def __init__(self, coordinates: List[List[List[DOUBLE]]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPolygon class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[Polygon] = [
            Polygon(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPolygon') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPolygon):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.polygons == other.polygons
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POLYGON_PRE, pack(COUNT_UNIT, len(self.polygons)),
            self._joiner(*[polygon.to_wkb() for polygon in self.polygons]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygon':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_polygons(wkb, dimension=2))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygon':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_polygons(value[8:], dimension=2), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygon class


class MultiPolygonZ(AbstractGeometry):
    """
    MultiPolygonZ
    """
    __slots__ = 'polygons'

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPolygon class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonZ] = [
            PolygonZ(coords) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPolygonZ') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPolygonZ):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.polygons == other.polygons
    # End eq built-in

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return self._joiner(
            WKB_MULTI_POLYGON_Z_PRE, pack(COUNT_UNIT, len(self.polygons)),
            self._joiner(*[polygon.to_wkb() for polygon in self.polygons]))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygonZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(_unpack_polygons(wkb, dimension=3))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZ':
        """
        From Geopackage
        """
        srs_id = cls._unpack_srs_id(value)
        # noinspection PyTypeChecker
        return cls(_unpack_polygons(value[8:], dimension=3), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonZ class


if __name__ == '__main__':
    pass
