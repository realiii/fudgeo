# -*- coding: utf-8 -*-
"""
Polygons
"""


from struct import pack
from typing import Any, List, Type, Union

from fudgeo.constant import (
    COUNT_CODE, DOUBLE, FOUR_D, HEADER_OFFSET, QUADRUPLE, THREE_D, TRIPLE,
    TWO_D, WKB_MULTI_POLYGON_M_PRE, WKB_MULTI_POLYGON_PRE,
    WKB_MULTI_POLYGON_ZM_PRE, WKB_MULTI_POLYGON_Z_PRE, WKB_POLYGON_M_PRE,
    WKB_POLYGON_PRE, WKB_POLYGON_ZM_PRE, WKB_POLYGON_Z_PRE)
from fudgeo.geometry.base import (
    AbstractGeopackageGeometryEnvelope, AbstractSpatialGeometryEnvelope)
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    pack_coordinates, unpack_envelope, unpack_header, unpack_lines,
    unpack_polygons)


POLYGON_TYPES = Union[Type['Polygon'], Type['PolygonZ'],
                      Type['PolygonM'], Type['PolygonZM']]
MULTI_POLYGON_TYPES = Union[Type['MultiPolygon'], Type['MultiPolygonZ'],
                            Type['MultiPolygonM'], Type['MultiPolygonZM']]


def _unpack_polygon(cls: POLYGON_TYPES, value: bytes, dimension: int) -> Any:
    """
    Unpack Linear Rings into Polygon
    """
    srs_id, env_code, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
    if is_empty:
        return cls([], srs_id=srs_id)
    # noinspection PyTypeChecker
    obj = cls(unpack_lines(value[offset:], dimension=dimension, is_ring=True),
              srs_id=srs_id)
    obj._envelope = unpack_envelope(code=env_code, value=value[:offset])
    return obj
# End _unpack_polygon function


def _unpack_multi_polygon(cls: MULTI_POLYGON_TYPES, value: bytes,
                          dimension: int) -> Any:
    """
    Unpack Polygons into MultiPolygon
    """
    srs_id, env_code, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
    if is_empty:
        return cls([], srs_id=srs_id)
    # noinspection PyTypeChecker
    obj = cls(unpack_polygons(value[offset:], dimension=dimension),
              srs_id=srs_id)
    obj._envelope = unpack_envelope(code=env_code, value=value[:offset])
    return obj
# End _unpack_multi_polygon function


class LinearRing(AbstractSpatialGeometryEnvelope):
    """
    Linear Ring
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[DOUBLE], srs_id: int) -> None:
        """
        Initialize the LinearRing class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[DOUBLE] = coordinates
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

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates)
    # End _to_wkb method
# End LinearRing class


class LinearRingZ(AbstractSpatialGeometryEnvelope):
    """
    Linear Ring Z
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the LinearRingZ class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
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

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_z=True)
    # End _to_wkb method
# End LinearRingZ class


class LinearRingM(AbstractSpatialGeometryEnvelope):
    """
    Linear Ring M
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the LinearRingM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
    # End init built-in

    def __eq__(self, other: 'LinearRingM') -> bool:
        """
        Equals
        """
        if not isinstance(other, LinearRingM):  # pragma: nocover
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

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_m=True)
    # End _to_wkb method
# End LinearRingM class


class LinearRingZM(AbstractSpatialGeometryEnvelope):
    """
    Linear Ring ZM
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[QUADRUPLE], srs_id: int) -> None:
        """
        Initialize the LinearRingZM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[QUADRUPLE] = coordinates
    # End init built-in

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.coordinates)
    # End is_empty property

    def __eq__(self, other: 'LinearRingZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, LinearRingZM):  # pragma: nocover
            return NotImplemented
        return self.points == other.points
    # End eq built-in

    @property
    def points(self) -> List[PointZM]:
        """
        Points
        """
        srs_id = self.srs_id
        return [PointZM(x=x, y=y, z=z, m=m, srs_id=srs_id)
                for x, y, z, m in self.coordinates]
    # End points property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_z=True, has_m=True)
    # End _to_wkb method
# End LinearRingZM class


class Polygon(AbstractGeopackageGeometryEnvelope):
    """
    Polygon
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[DOUBLE]], srs_id: int) -> None:
        """
        Initialize the Polygon class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRing] = [
            LinearRing(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Polygon':
        """
        From Geopackage
        """
        return _unpack_polygon(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End Polygon class


class PolygonZ(AbstractGeopackageGeometryEnvelope):
    """
    Polygon Z
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonZ class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingZ] = [
            LinearRingZ(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_Z_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZ':
        """
        From Geopackage
        """
        return _unpack_polygon(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End PolygonZ class


class PolygonM(AbstractGeopackageGeometryEnvelope):
    """
    Polygon M
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonM class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingM] = [
            LinearRingM(coords, srs_id=srs_id) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'PolygonM') -> bool:
        """
        Equals
        """
        if not isinstance(other, PolygonM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.rings == other.rings
    # End eq built-in

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_M_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonM':
        """
        From Geopackage
        """
        return _unpack_polygon(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End PolygonM class


class PolygonZM(AbstractGeopackageGeometryEnvelope):
    """
    Polygon ZM
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[QUADRUPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingZM] = [
            LinearRingZM(coords, srs_id=srs_id) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'PolygonZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, PolygonZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.rings == other.rings
    # End eq built-in

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_ZM_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZM':
        """
        From Geopackage
        """
        return _unpack_polygon(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End PolygonZM class


class MultiPolygon(AbstractGeopackageGeometryEnvelope):
    """
    Multi Polygon
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[DOUBLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygon class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[Polygon] = [
            Polygon(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygon':
        """
        From Geopackage
        """
        return _unpack_multi_polygon(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End MultiPolygon class


class MultiPolygonZ(AbstractGeopackageGeometryEnvelope):
    """
    Multi Polygon Z
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonZ class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonZ] = [
            PolygonZ(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_Z_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZ':
        """
        From Geopackage
        """
        return _unpack_multi_polygon(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPolygonZ class


class MultiPolygonM(AbstractGeopackageGeometryEnvelope):
    """
    Multi Polygon M
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonM class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonM] = [
            PolygonM(coords, srs_id=srs_id) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPolygonM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPolygonM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.polygons == other.polygons
    # End eq built-in

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_M_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonM':
        """
        From Geopackage
        """
        return _unpack_multi_polygon(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPolygonM class


class MultiPolygonZM(AbstractGeopackageGeometryEnvelope):
    """
    Multi Polygon M
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[QUADRUPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonZM] = [
            PolygonZM(coords, srs_id=srs_id) for coords in coordinates]
    # End init built-in

    def __eq__(self, other: 'MultiPolygonZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, MultiPolygonZM):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.polygons == other.polygons
    # End eq built-in

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_ZM_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZM':
        """
        From Geopackage
        """
        return _unpack_multi_polygon(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End MultiPolygonZM class


if __name__ == '__main__':  # pragma: no cover
    pass
