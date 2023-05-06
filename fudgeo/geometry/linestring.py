# -*- coding: utf-8 -*-
"""
Line String
"""


from struct import pack
from typing import Any, List, Type, Union

from fudgeo.constant import (
    COUNT_CODE, DOUBLE, FOUR_D, HEADER_OFFSET, QUADRUPLE, THREE_D, TRIPLE,
    TWO_D, WKB_LINESTRING_M_PRE, WKB_LINESTRING_PRE, WKB_LINESTRING_ZM_PRE,
    WKB_LINESTRING_Z_PRE, WKB_MULTI_LINESTRING_M_PRE, WKB_MULTI_LINESTRING_PRE,
    WKB_MULTI_LINESTRING_ZM_PRE, WKB_MULTI_LINESTRING_Z_PRE)
from fudgeo.geometry.base import AbstractGeopackageGeometryExtent
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    pack_coordinates, unpack_header, unpack_line, unpack_lines)


LINE_STRING_TYPES = Union[Type['LineString'], Type['LineStringZ'],
                          Type['LineStringM'], Type['LineStringZM']]
MULTI_LINE_STRING_TYPES = Union[
    Type['MultiLineString'], Type['MultiLineStringZ'],
    Type['MultiLineStringM'], Type['MultiLineStringZM']]


def _unpack_linestring(cls: LINE_STRING_TYPES, value: bytes,
                       dimension: int) -> Any:
    """
    Unpack LineString
    """
    srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
    if is_empty:
        return cls([], srs_id=srs_id)
    # noinspection PyTypeChecker
    return cls(unpack_line(value[offset:], dimension=dimension), srs_id=srs_id)
# End _unpack_linestring function


def _unpack_multi_linestring(cls: MULTI_LINE_STRING_TYPES, value: bytes,
                             dimension: int) -> Any:
    """
    Unpack LineStrings into MultiLineString
    """
    srs_id, offset, is_empty = unpack_header(value[:HEADER_OFFSET])
    if is_empty:
        return cls([], srs_id=srs_id)
    # noinspection PyTypeChecker
    return cls(unpack_lines(value[offset:], dimension=dimension), srs_id=srs_id)
# End _unpack_multi_linestring function


class LineString(AbstractGeopackageGeometryExtent):
    """
    LineString
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[DOUBLE], srs_id: int) -> None:
        """
        Initialize the LineString class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[DOUBLE] = coordinates
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
        return WKB_LINESTRING_PRE + pack_coordinates(self.coordinates)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineString':
        """
        From Geopackage
        """
        return _unpack_linestring(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End LineString class


class LineStringZ(AbstractGeopackageGeometryExtent):
    """
    LineStringZ
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the LineStringZ class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
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
        return WKB_LINESTRING_Z_PRE + pack_coordinates(
            self.coordinates, has_z=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringZ':
        """
        From Geopackage
        """
        return _unpack_linestring(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End LineStringZ class


class LineStringM(AbstractGeopackageGeometryExtent):
    """
    LineStringM
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[TRIPLE], srs_id: int) -> None:
        """
        Initialize the LineStringM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[TRIPLE] = coordinates
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
        return WKB_LINESTRING_M_PRE + pack_coordinates(
            self.coordinates, has_m=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringM':
        """
        From Geopackage
        """
        return _unpack_linestring(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End LineStringM class


class LineStringZM(AbstractGeopackageGeometryExtent):
    """
    LineStringZM
    """
    __slots__ = 'coordinates',

    def __init__(self, coordinates: List[QUADRUPLE], srs_id: int) -> None:
        """
        Initialize the LineStringZM class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: List[QUADRUPLE] = coordinates
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

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return WKB_LINESTRING_ZM_PRE + pack_coordinates(
            self.coordinates, has_z=True, has_m=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LineStringZM':
        """
        From Geopackage
        """
        return _unpack_linestring(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End LineStringZM class


class MultiLineString(AbstractGeopackageGeometryExtent):
    """
    Multi LineString
    """
    __slots__ = 'lines',

    def __init__(self, coordinates: List[List[DOUBLE]], srs_id: int) -> None:
        """
        Initialize the MultiLineString class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineString] = [
            LineString(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.lines)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.lines
        return (WKB_MULTI_LINESTRING_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineString':
        """
        From Geopackage
        """
        return _unpack_multi_linestring(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End MultiLineString class


class MultiLineStringZ(AbstractGeopackageGeometryExtent):
    """
    Multi LineString Z
    """
    __slots__ = 'lines',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the MultiLineStringZ class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringZ] = [
            LineStringZ(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.lines)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.lines
        return (WKB_MULTI_LINESTRING_Z_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringZ':
        """
        From Geopackage
        """
        return _unpack_multi_linestring(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiLineStringZ class


class MultiLineStringM(AbstractGeopackageGeometryExtent):
    """
    Multi LineString M
    """
    __slots__ = 'lines',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the MultiLineStringM class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringM] = [
            LineStringM(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.lines)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.lines
        return (WKB_MULTI_LINESTRING_M_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringM':
        """
        From Geopackage
        """
        return _unpack_multi_linestring(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiLineStringM class


class MultiLineStringZM(AbstractGeopackageGeometryExtent):
    """
    Multi LineString ZM
    """
    __slots__ = 'lines',

    def __init__(self, coordinates: List[List[QUADRUPLE]], srs_id: int) -> None:
        """
        Initialize the MultiLineStringZM class
        """
        super().__init__(srs_id=srs_id)
        self.lines: List[LineStringZM] = [
            LineStringZM(coords, srs_id=srs_id) for coords in coordinates]
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

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        return not len(self.lines)
    # End is_empty property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        geoms = self.lines
        return (WKB_MULTI_LINESTRING_ZM_PRE + pack(COUNT_CODE, len(geoms)) +
                self._join_geometries(geoms))
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'MultiLineStringZM':
        """
        From Geopackage
        """
        return _unpack_multi_linestring(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End MultiLineStringZM class


if __name__ == '__main__':  # pragma: no cover
    pass
