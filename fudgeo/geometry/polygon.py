# -*- coding: utf-8 -*-
"""
Polygons
"""


from struct import pack
from typing import List

from fudgeo.constant import (
    COUNT_CODE, DOUBLE, FOUR_D, HEADER_OFFSET, QUADRUPLE, THREE_D, TRIPLE,
    TWO_D, WGS84, WKB_MULTI_POLYGON_M_PRE, WKB_MULTI_POLYGON_PRE,
    WKB_MULTI_POLYGON_ZM_PRE, WKB_MULTI_POLYGON_Z_PRE, WKB_POLYGON_M_PRE,
    WKB_POLYGON_PRE, WKB_POLYGON_ZM_PRE, WKB_POLYGON_Z_PRE)
from fudgeo.geometry.base import AbstractGeometryExtent
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    pack_coordinates, unpack_header, unpack_line, unpack_lines, unpack_polygons)


MSG_LINEAR_RINGS: str = 'Linear Rings not supported for Geopackage'


class LinearRing(AbstractGeometryExtent):
    """
    Linear Ring
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[DOUBLE],
                 srs_id: int = WGS84) -> None:
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
        return [Point(x=x, y=y) for x, y in self.coordinates]
    # End points property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates)
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRing':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_line(wkb, dimension=TWO_D, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRing':
        """
        From Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End from_gpkg method
# End LinearRing class


class LinearRingZ(AbstractGeometryExtent):
    """
    Linear Ring Z
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
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
        return [PointZ(x=x, y=y, z=z) for x, y, z in self.coordinates]
    # End points property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_z=True)
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRingZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_line(wkb, dimension=THREE_D, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZ':
        """
        From Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End from_gpkg method
# End LinearRingZ class


class LinearRingM(AbstractGeometryExtent):
    """
    Linear Ring M
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int = WGS84) -> None:
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
        return [PointM(x=x, y=y, m=m) for x, y, m in self.coordinates]
    # End points property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_m=True)
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRingM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_line(wkb, dimension=THREE_D, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingM':
        """
        From Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End from_gpkg method
# End LinearRingM class


class LinearRingZM(AbstractGeometryExtent):
    """
    Linear Ring ZM
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[QUADRUPLE],
                 srs_id: int = WGS84) -> None:
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
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    @property
    def points(self) -> List[PointZM]:
        """
        Points
        """
        return [PointZM(x=x, y=y, z=z, m=m) for x, y, z, m in self.coordinates]
    # End points property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_z=True, has_m=True)
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'LinearRingZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_line(wkb, dimension=FOUR_D, is_ring=True))
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End to_gpkg method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZM':
        """
        From Geopackage
        """
        raise NotImplementedError(MSG_LINEAR_RINGS)
    # End from_gpkg method
# End LinearRingZM class


class Polygon(AbstractGeometryExtent):
    """
    Polygon
    """
    __slots__ = 'rings',

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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'Polygon':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_lines(wkb, dimension=TWO_D, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'Polygon':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=TWO_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End Polygon class


class PolygonZ(AbstractGeometryExtent):
    """
    Polygon Z
    """
    __slots__ = 'rings',

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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.rings)
    # End is_empty property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_Z_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PolygonZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_lines(wkb, dimension=THREE_D, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZ':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=THREE_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonZ class


class PolygonM(AbstractGeometryExtent):
    """
    Polygon M
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[TRIPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PolygonM class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingM] = [
            LinearRingM(coords) for coords in coordinates]
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

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_M_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PolygonM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_lines(wkb, dimension=THREE_D, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonM':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=THREE_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonM class


class PolygonZM(AbstractGeometryExtent):
    """
    Polygon ZM
    """
    __slots__ = 'rings',

    def __init__(self, coordinates: List[List[QUADRUPLE]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the PolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self.rings: List[LinearRingZM] = [
            LinearRingZM(coords) for coords in coordinates]
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

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.rings
        return (WKB_POLYGON_ZM_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'PolygonZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_lines(wkb, dimension=FOUR_D, is_ring=True))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'PolygonZM':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=FOUR_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonZM class


class MultiPolygon(AbstractGeometryExtent):
    """
    Multi Polygon
    """
    __slots__ = 'polygons',

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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygon':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_polygons(wkb, dimension=TWO_D))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygon':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=TWO_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygon class


class MultiPolygonZ(AbstractGeometryExtent):
    """
    Multi Polygon Z
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPolygonZ class
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.polygons)
    # End is_empty property

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_Z_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygonZ':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_polygons(wkb, dimension=THREE_D))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZ':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=THREE_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonZ class


class MultiPolygonM(AbstractGeometryExtent):
    """
    Multi Polygon M
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPolygonM class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonM] = [
            PolygonM(coords) for coords in coordinates]
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

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_M_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygonM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_polygons(wkb, dimension=THREE_D))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonM':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=THREE_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonM class


class MultiPolygonZM(AbstractGeometryExtent):
    """
    Multi Polygon M
    """
    __slots__ = 'polygons',

    def __init__(self, coordinates: List[List[List[QUADRUPLE]]],
                 srs_id: int = WGS84) -> None:
        """
        Initialize the MultiPolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self.polygons: List[PolygonZM] = [
            PolygonZM(coords) for coords in coordinates]
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

    def to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.polygons
        return (WKB_MULTI_POLYGON_ZM_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End to_wkb method

    @classmethod
    def from_wkb(cls, wkb: bytes) -> 'MultiPolygonZM':
        """
        From WKB
        """
        # noinspection PyTypeChecker
        return cls(unpack_polygons(wkb, dimension=FOUR_D))
    # End from_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiPolygonZM':
        """
        From Geopackage
        """
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=FOUR_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonZM class


if __name__ == '__main__':  # pragma: no cover
    pass
