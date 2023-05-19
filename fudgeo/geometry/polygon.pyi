# -*- coding: utf-8 -*-
"""
Polygons
"""


from typing import Any, ClassVar, List

from numpy import ndarray

from fudgeo.constant import (
    DOUBLE, QUADRUPLE, TRIPLE)
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import Envelope


class BaseLinearRing(AbstractGeometry):
    """
    Base Linear Ring
    """
    _class: ClassVar[Any]
    _env_code: ClassVar[int]
    coordinates: ndarray

    def __init__(self, coordinates: List, srs_id: int) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> Any: ...
# End BaseLinearRing class


class LinearRing(BaseLinearRing):
    """
    Linear Ring
    """
    def __init__(self, coordinates: List[DOUBLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'LinearRing') -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[Point]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRing': ...
# End LinearRing class


class LinearRingZ(BaseLinearRing):
    """
    Linear Ring Z
    """
    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'LinearRingZ') -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointZ]: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @property
    def envelope(self) -> Envelope: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZ': ...
# End LinearRingZ class


class LinearRingM(BaseLinearRing):
    """
    Linear Ring M
    """
    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'LinearRingM') -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointM]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingM': ...
# End LinearRingM class


class LinearRingZM(BaseLinearRing):
    """
    Linear Ring ZM
    """
    def __init__(self, coordinates: List[QUADRUPLE], srs_id: int) -> None: ...
    def __eq__(self, other: 'LinearRingZM') -> bool: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def points(self) -> List[PointZM]: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> None: ...
# End LinearRingZM class


class BasePolygon(AbstractGeometry):
    """
    Base Polygon
    """
    _class: ClassVar[Any]
    _dimension: ClassVar[int]
    _env_code: ClassVar[int]
    _wkb_prefix: ClassVar[bytes]
    _rings: List

    def __init__(self, coordinates: List[List], srs_id: int) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    def _make_rings(self, coordinates: List[List]) -> List: ...
    @property
    def rings(self) -> List: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> Any: ...
# End BasePolygon class


class Polygon(BasePolygon):
    """
    Polygon
    """
    def __init__(self, coordinates: List[List[DOUBLE]], srs_id: int) -> None: ...
    def __eq__(self, other: 'Polygon') -> bool: ...
    def _make_rings(self, coordinates: List[List[DOUBLE]]) -> List[LinearRing]: ...
    @property
    def rings(self) -> List[LinearRing]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Polygon': ...
# End Polygon class


class PolygonZ(BasePolygon):
    """
    Polygon Z
    """
    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None: ...
    def __eq__(self, other: 'PolygonZ') -> bool: ...
    def _make_rings(self, coordinates: List[List[TRIPLE]]) -> List[LinearRingZ]: ...
    @property
    def rings(self) -> List[LinearRingZ]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZ': ...
# End PolygonZ class


class PolygonM(BasePolygon):
    """
    Polygon M
    """
    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None: ...
    def __eq__(self, other: 'PolygonM') -> bool: ...
    def _make_rings(self, coordinates: List[List[TRIPLE]]) -> List[LinearRingM]: ...
    @property
    def rings(self) -> List[LinearRingM]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonM': ...
# End PolygonM class


class PolygonZM(BasePolygon):
    """
    Polygon ZM
    """
    def __init__(self, coordinates: List[List[QUADRUPLE]], srs_id: int) -> None: ...
    def __eq__(self, other: 'PolygonZM') -> bool: ...
    def _make_rings(self, coordinates: List[List[QUADRUPLE]]) -> List[LinearRingZM]: ...
    @property
    def rings(self) -> List[LinearRingZM]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZM': ...
# End PolygonZM class


class BaseMultiPolygon(AbstractGeometry):
    """
    Base Multi Polygon
    """
    _class: ClassVar[Any]
    _dimension: ClassVar[int]
    _env_code: ClassVar[int]
    _wkb_prefix: ClassVar[bytes]
    _polygons: List

    def __init__(self, coordinates: List[List[List]], srs_id: int) -> None: ...
    def __eq__(self, other: Any) -> bool: ...
    def _make_polygons(self, coordinates: List[List[List]]) -> List: ...
    @property
    def polygons(self) -> List: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> Any: ...
# End BaseMultiPolygon class


class MultiPolygon(BaseMultiPolygon):
    """
    Multi Polygon
    """
    def __init__(self, coordinates: List[List[List[DOUBLE]]], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPolygon') -> bool: ...
    def _make_polygons(self, coordinates: List[List[List[DOUBLE]]]) -> List[Polygon]: ...
    @property
    def polygons(self) -> List[Polygon]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygon': ...
# End MultiPolygon class


class MultiPolygonZ(BaseMultiPolygon):
    def __init__(self, coordinates: List[List[List[TRIPLE]]], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPolygonZ') -> bool: ...
    def _make_polygons(self, coordinates: List[List[List[TRIPLE]]]) -> List[PolygonZ]: ...
    @property
    def polygons(self) -> List[PolygonZ]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZ': ...
# End MultiPolygonZ class


class MultiPolygonM(BaseMultiPolygon):
    """
    Multi Polygon M
    """
    def __init__(self, coordinates: List[List[List[TRIPLE]]], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPolygonM') -> bool: ...
    def _make_polygons(self, coordinates: List[List[List[TRIPLE]]]) -> List[PolygonM]: ...
    @property
    def polygons(self) -> List[PolygonM]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonM': ...
# End MultiPolygonM class


class MultiPolygonZM(BaseMultiPolygon):
    """
    Multi Polygon ZM
    """
    def __init__(self, coordinates: List[List[List[QUADRUPLE]]], srs_id: int) -> None: ...
    def __eq__(self, other: 'MultiPolygonZM') -> bool: ...
    def _make_polygons(self, coordinates: List[List[List[QUADRUPLE]]]) -> List[PolygonZM]: ...
    @property
    def polygons(self) -> List[PolygonZM]: ...
    @property
    def is_empty(self) -> bool: ...
    @property
    def envelope(self) -> Envelope: ...
    def _to_wkb(self, ary: bytearray) -> bytearray: ...
    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZM': ...
# End MultiPolygonZM class


if __name__ == '__main__':  # pragma: no cover
    pass