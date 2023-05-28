# -*- coding: utf-8 -*-
"""
Points
"""

from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

from numpy import ndarray

from fudgeo.constant import DOUBLE, QUADRUPLE, TRIPLE
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.util import Envelope



class Point(AbstractGeometry):
    """
    Point
    """
    x: float
    y: float

    def __init__(self, *, x: float, y: float, srs_id: int) -> None: ...
    def __eq__(self, other: 'Point') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Union[str, DOUBLE]]: ...
    def as_tuple(self) -> DOUBLE: ...
    @property
    def is_empty(self) -> bool: ...
    @staticmethod
    def _unpack(value: bytes) -> DOUBLE: ...
    def _to_wkb(self, ary: Optional[bytearray] = None) -> bytes: ...
    @property
    def envelope(self) -> Envelope: ...
    def to_gpkg(self) -> bytes: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Point': ...
    @classmethod
    def from_tuple(cls, xy: DOUBLE, srs_id: int) -> 'Point': ...
    @classmethod
    def empty(cls, srs_id: int) -> 'Point': ...
# End Point class


class PointZ(AbstractGeometry):
    """
    Point Z
    """
    x: float
    y: float
    z: float

    def __init__(self, *, x: float, y: float, z: float, srs_id: int) -> None: ...
    def __eq__(self, other: 'PointZ') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Union[str, TRIPLE]]: ...
    def as_tuple(self) -> TRIPLE: ...
    @property
    def is_empty(self) -> bool: ...
    @staticmethod
    def _unpack(value: bytes) -> TRIPLE: ...
    def _to_wkb(self, ary: Optional[bytearray] = None) -> bytes: ...
    @property
    def envelope(self) -> Envelope: ...
    def to_gpkg(self) -> bytes: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZ': ...
    @classmethod
    def from_tuple(cls, xyz: TRIPLE, srs_id: int) -> 'PointZ': ...
    @classmethod
    def empty(cls, srs_id: int) -> 'PointZ': ...
# End PointZ class


class PointM(AbstractGeometry):
    """
    Point M
    """
    x: float
    y: float
    m: float

    def __init__(self, *, x: float, y: float, m: float, srs_id: int) -> None: ...
    def __eq__(self, other: 'PointM') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Union[str, TRIPLE]]: ...
    def as_tuple(self) -> TRIPLE: ...
    @property
    def is_empty(self) -> bool: ...
    @staticmethod
    def _unpack(value: bytes) -> TRIPLE: ...
    def _to_wkb(self, ary: Optional[bytearray] = None) -> bytes: ...
    @property
    def envelope(self) -> Envelope: ...
    def to_gpkg(self) -> bytes: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointM': ...
    @classmethod
    def from_tuple(cls, xym: TRIPLE, srs_id: int) -> 'PointM': ...
    @classmethod
    def empty(cls, srs_id: int) -> 'PointM': ...
# End PointM class


class PointZM(AbstractGeometry):
    """
    Point ZM
    """
    x: float
    y: float
    z: float
    m: float

    def __init__(self, *, x: float, y: float, z: float, m: float, srs_id: int) -> None: ...
    def __eq__(self, other: 'PointZM') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Union[str, QUADRUPLE]]: ...
    def as_tuple(self) -> QUADRUPLE: ...
    @property
    def is_empty(self) -> bool: ...
    @staticmethod
    def _unpack(value: bytes) -> QUADRUPLE: ...
    def _to_wkb(self, ary: Optional[bytearray] = None) -> bytes: ...
    @property
    def envelope(self) -> Envelope: ...
    def to_gpkg(self) -> bytes: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PointZM': ...
    @classmethod
    def from_tuple(cls, xyzm: QUADRUPLE, srs_id: int) -> 'PointZM': ...
    @classmethod
    def empty(cls, srs_id: int) -> 'PointZM': ...
# End PointZM class


class BaseMultiPoint(AbstractGeometry):
    """
    Base Multi Point
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any]
    _dimension: ClassVar[int]
    _env_code: ClassVar[int]
    _has_m: ClassVar[bool]
    _has_z: ClassVar[bool]
    _wkb_prefix: ClassVar[bytes]
    _coordinates: ndarray

    def __init__(self, coordinates: List, srs_id: int) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    @property
    def __geo_interface__(self) -> Dict: ...
    @property
    def coordinates(self) -> 'ndarray': ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> Any: ...
# End BaseMultiPoint class


class MultiPoint(BaseMultiPoint):
    """
    Multi Point
    """
    def __init__(self, coordinates: List[DOUBLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPoint') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Tuple[DOUBLE]]: ...
    @property
    def coordinates(self) -> 'ndarray': ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[Point]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPoint': ...
# End MultiPoint class


class MultiPointZ(BaseMultiPoint):
    """
    Multi Point Z
    """
    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPointZ') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Tuple[TRIPLE]]: ...
    @property
    def coordinates(self) -> 'ndarray': ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointZ]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZ': ...
# End MultiPointZ class


class MultiPointM(BaseMultiPoint):
    """
    Multi Point M
    """
    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPointM') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Tuple[TRIPLE]]: ...
    @property
    def coordinates(self) -> 'ndarray': ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointM]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointM': ...
# End MultiPointM class


class MultiPointZM(BaseMultiPoint):
    """
    Multi Point ZM
    """
    def __init__(self, coordinates: List[QUADRUPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPointZM') -> bool: ...
    @property
    def __geo_interface__(self) -> Dict[str, Tuple[QUADRUPLE]]: ...
    @property
    def coordinates(self) -> 'ndarray': ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointZM]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPointZM': ...
# End MultiPointZM class


if __name__ == '__main__':  # pragma: no cover
    pass
