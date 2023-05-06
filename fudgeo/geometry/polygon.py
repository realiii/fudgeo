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
from fudgeo.geometry.base import (
    AbstractGeopackageGeometryExtent, AbstractSpatialGeometryExtent)
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    pack_coordinates, unpack_header, unpack_line, unpack_lines, unpack_polygons)


class LinearRing(AbstractSpatialGeometryExtent):
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


class LinearRingZ(AbstractSpatialGeometryExtent):
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


class LinearRingM(AbstractSpatialGeometryExtent):
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


class LinearRingZM(AbstractSpatialGeometryExtent):
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


class Polygon(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=TWO_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End Polygon class


class PolygonZ(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=THREE_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonZ class


class PolygonM(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=THREE_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonM class


class PolygonZM(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_lines(
            value[offset:], dimension=FOUR_D, is_ring=True), srs_id=srs_id)
    # End from_gpkg method
# End PolygonZM class


class MultiPolygon(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=TWO_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygon class


class MultiPolygonZ(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=THREE_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonZ class


class MultiPolygonM(AbstractGeopackageGeometryExtent):
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
        srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
        if is_empty:
            return cls([], srs_id=srs_id)
        # noinspection PyTypeChecker
        return cls(unpack_polygons(
            value[offset:], dimension=THREE_D), srs_id=srs_id)
    # End from_gpkg method
# End MultiPolygonM class


class MultiPolygonZM(AbstractGeopackageGeometryExtent):
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
