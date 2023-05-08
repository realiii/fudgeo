# -*- coding: utf-8 -*-
"""
Points
"""


from math import isnan, nan
from struct import pack, unpack
from typing import Any, List, Type, Union

from fudgeo.constant import (
    DOUBLE, EMPTY, FOUR_D, FOUR_D_PACK_CODE, FOUR_D_UNPACK_CODE, HEADER_OFFSET,
    QUADRUPLE, THREE_D, THREE_D_PACK_CODE, THREE_D_UNPACK_CODE, TRIPLE, TWO_D,
    TWO_D_PACK_CODE, TWO_D_UNPACK_CODE, WKB_MULTI_POINT_M_PRE,
    WKB_MULTI_POINT_PRE, WKB_MULTI_POINT_ZM_PRE, WKB_MULTI_POINT_Z_PRE,
    WKB_POINT_M_PRE, WKB_POINT_PRE, WKB_POINT_ZM_PRE, WKB_POINT_Z_PRE)
from fudgeo.geometry.base import (
    AbstractGeopackageGeometry, AbstractGeopackageGeometryEnvelope)
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, Envelope, envelope_from_coordinates,
    envelope_from_coordinates_m, envelope_from_coordinates_z,
    envelope_from_coordinates_zm, pack_coordinates, unpack_envelope,
    unpack_header, unpack_points)


MULTI_POINT_TYPES = Union[Type['MultiPoint'], Type['MultiPointZ'],
                          Type['MultiPointM'], Type['MultiPointZM']]


def _unpack_multi_point(cls: MULTI_POINT_TYPES, value: bytes,
                        dimension: int) -> Any:
    """
    Unpack Points into MultiPoint
    """
    srs_id, env_code, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
    if is_empty:
        return cls([], srs_id=srs_id)
    # noinspection PyTypeChecker
    obj = cls(unpack_points(value[offset:], dimension=dimension), srs_id=srs_id)
    obj._envelope = unpack_envelope(code=env_code, value=value[:offset])
    return obj
# End _unpack_multi_point function


class Point(AbstractGeopackageGeometry):
    """
    Point
    """
    __slots__ = 'x', 'y'

    def __init__(self, *, x: float, y: float, srs_id: int) -> None:
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return isnan(self.x) and isnan(self.y)
    # End is_empty property

    @staticmethod
    def _unpack(value: bytes) -> DOUBLE:
        """
        Unpack Values
        """
        *_, x, y = unpack(TWO_D_UNPACK_CODE, value)
        return x, y
    # End _unpack method

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_PRE if use_prefix else EMPTY
        return pre + pack(TWO_D_PACK_CODE, self.x, self.y)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Point':
        """
        From Geopackage
        """
        srs_id, _, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls.empty(srs_id)
        x, y = cls._unpack(value[offset:])
        return cls(x=x, y=y, srs_id=srs_id)
    # End from_gpkg method

    @classmethod
    def from_tuple(cls, xy: DOUBLE, srs_id: int) -> 'Point':
        """
        From Tuple
        """
        x, y = xy
        return cls(x=x, y=y, srs_id=srs_id)
    # End from_tuple method

    @classmethod
    def empty(cls, srs_id: int) -> 'Point':
        """
        Empty Point
        """
        return cls(x=nan, y=nan, srs_id=srs_id)
    # End empty method
# End Point class


class PointZ(AbstractGeopackageGeometry):
    """
    Point Z
    """
    __slots__ = 'x', 'y', 'z'

    def __init__(self, *, x: float, y: float, z: float, srs_id: int) -> None:
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return isnan(self.x) and isnan(self.y) and isnan(self.z)
    # End is_empty property

    @staticmethod
    def _unpack(value: bytes) -> TRIPLE:
        """
        Unpack Values
        """
        *_, x, y, z = unpack(THREE_D_UNPACK_CODE, value)
        return x, y, z
    # End _unpack method

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_Z_PRE if use_prefix else EMPTY
        return pre + pack(THREE_D_PACK_CODE, self.x, self.y, self.z)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZ':
        """
        From Geopackage
        """
        srs_id, _, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls.empty(srs_id)
        x, y, z = cls._unpack(value[offset:])
        return cls(x=x, y=y, z=z, srs_id=srs_id)
    # End from_gpkg method

    @classmethod
    def from_tuple(cls, xyz: TRIPLE, srs_id: int) -> 'PointZ':
        """
        From Tuple
        """
        x, y, z = xyz
        return cls(x=x, y=y, z=z, srs_id=srs_id)
    # End from_tuple method

    @classmethod
    def empty(cls, srs_id: int) -> 'PointZ':
        """
        Empty PointZ
        """
        return cls(x=nan, y=nan, z=nan, srs_id=srs_id)
    # End empty method
# End PointZ class


class PointM(AbstractGeopackageGeometry):
    """
    Point M
    """
    __slots__ = 'x', 'y', 'm'

    def __init__(self, *, x: float, y: float, m: float, srs_id: int) -> None:
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return isnan(self.x) and isnan(self.y) and isnan(self.m)
    # End is_empty property

    @staticmethod
    def _unpack(value: bytes) -> TRIPLE:
        """
        Unpack Values
        """
        *_, x, y, m = unpack(THREE_D_UNPACK_CODE, value)
        return x, y, m
    # End _unpack method

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_M_PRE if use_prefix else EMPTY
        return pre + pack(THREE_D_PACK_CODE, self.x, self.y, self.m)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointM':
        """
        From Geopackage
        """
        srs_id, _, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls.empty(srs_id)
        x, y, m = cls._unpack(value[offset:])
        return cls(x=x, y=y, m=m, srs_id=srs_id)
    # End from_gpkg method

    @classmethod
    def from_tuple(cls, xym: TRIPLE, srs_id: int) -> 'PointM':
        """
        From Tuple
        """
        x, y, m = xym
        return cls(x=x, y=y, m=m, srs_id=srs_id)
    # End from_tuple method

    @classmethod
    def empty(cls, srs_id: int) -> 'PointM':
        """
        Empty PointM
        """
        return cls(x=nan, y=nan, m=nan, srs_id=srs_id)
    # End empty method
# End PointM class


class PointZM(AbstractGeopackageGeometry):
    """
    Point ZM
    """
    __slots__ = 'x', 'y', 'z', 'm'

    def __init__(self, *, x: float, y: float, z: float, m: float,
                 srs_id: int) -> None:
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return (isnan(self.x) and isnan(self.y) and
                isnan(self.z) and isnan(self.m))
    # End is_empty property

    @staticmethod
    def _unpack(value: bytes) -> QUADRUPLE:
        """
        Unpack Values
        """
        *_, x, y, z, m = unpack(FOUR_D_UNPACK_CODE, value)
        return x, y, z, m
    # End _unpack method

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        pre = WKB_POINT_ZM_PRE if use_prefix else EMPTY
        return pre + pack(FOUR_D_PACK_CODE, self.x, self.y, self.z, self.m)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZM':
        """
        From Geopackage
        """
        srs_id, _, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls.empty(srs_id)
        x, y, z, m = cls._unpack(value[offset:])
        return cls(x=x, y=y, z=z, m=m, srs_id=srs_id)
    # End from_gpkg method

    @classmethod
    def from_tuple(cls, xyzm: QUADRUPLE, srs_id: int) -> 'PointZM':
        """
        From Tuple
        """
        x, y, z, m = xyzm
        return cls(x=x, y=y, z=z, m=m, srs_id=srs_id)
    # End from_tuple method

    @classmethod
    def empty(cls, srs_id: int) -> 'PointZM':
        """
        Empty Point
        """
        return cls(x=nan, y=nan, z=nan, m=nan, srs_id=srs_id)
    # End empty method
# End PointZM class


class MultiPoint(AbstractGeopackageGeometryEnvelope):
    """
    Multi Point
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[DOUBLE], srs_id: int) -> None:
        """
        Initialize the MultiPoint class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[DOUBLE] = coordinates
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.coordinates)
    # End is_empty property

    @property
    def points(self) -> List[Point]:
        """
        Points
        """
        srs_id = self.srs_id
        return [Point(x=x, y=y, srs_id=srs_id) for x, y in self.coordinates]
    # End points property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._envelope is not EMPTY_ENVELOPE:
            return self._envelope
        env = envelope_from_coordinates(self.coordinates)
        self._envelope = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return WKB_MULTI_POINT_PRE + pack_coordinates(
            self.coordinates, use_prefix=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPoint':
        """
        From Geopackage
        """
        return _unpack_multi_point(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End MultiPoint class


class MultiPointZ(AbstractGeopackageGeometryEnvelope):
    """
    Multi Point Z
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the MultiPointZ class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.coordinates)
    # End is_empty property

    @property
    def points(self) -> List[PointZ]:
        """
        Points
        """
        srs_id = self.srs_id
        return [PointZ(x=x, y=y, z=z, srs_id=srs_id)
                for x, y, z in self.coordinates]
    # End points property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._envelope is not EMPTY_ENVELOPE:
            return self._envelope
        env = envelope_from_coordinates_z(self.coordinates)
        self._envelope = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return WKB_MULTI_POINT_Z_PRE + pack_coordinates(
            self.coordinates, has_z=True, use_prefix=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZ':
        """
        From Geopackage
        """
        return _unpack_multi_point(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPointZ class


class MultiPointM(AbstractGeopackageGeometryEnvelope):
    """
    Multi Point M
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the MultiPointM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.coordinates)
    # End is_empty property

    @property
    def points(self) -> List[PointM]:
        """
        Points
        """
        srs_id = self.srs_id
        return [PointM(x=x, y=y, m=m, srs_id=srs_id)
                for x, y, m in self.coordinates]
    # End points property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._envelope is not EMPTY_ENVELOPE:
            return self._envelope
        env = envelope_from_coordinates_m(self.coordinates)
        self._envelope = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return WKB_MULTI_POINT_M_PRE + pack_coordinates(
            self.coordinates, has_m=True, use_prefix=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointM':
        """
        From Geopackage
        """
        return _unpack_multi_point(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPointM class


class MultiPointZM(AbstractGeopackageGeometryEnvelope):
    """
    Multi Point ZM
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[QUADRUPLE], srs_id: int) -> None:
        """
        Initialize the MultiPointZM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[QUADRUPLE] = coordinates
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.coordinates)
    # End is_empty property

    @property
    def points(self) -> List[PointZM]:
        """
        Points
        """
        srs_id = self.srs_id
        return [PointZM(x=x, y=y, z=z, m=m, srs_id=srs_id)
                for x, y, z, m in self.coordinates]
    # End points property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._envelope is not EMPTY_ENVELOPE:
            return self._envelope
        env = envelope_from_coordinates_zm(self.coordinates)
        self._envelope = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return WKB_MULTI_POINT_ZM_PRE + pack_coordinates(
            self.coordinates, has_z=True, has_m=True, use_prefix=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZM':
        """
        From Geopackage
        """
        return _unpack_multi_point(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End MultiPointZM class


if __name__ == '__main__':  # pragma: no cover
    pass
