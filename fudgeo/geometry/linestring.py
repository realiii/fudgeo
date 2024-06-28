# -*- coding: utf-8 -*-
"""
Line String
"""


from struct import pack
from typing import Any, ClassVar, TYPE_CHECKING

from fudgeo.constant import (
    COUNT_CODE, EMPTY, FOUR_D, THREE_D, TWO_D, WKB_LINESTRING_M_PRE,
    WKB_LINESTRING_PRE, WKB_LINESTRING_ZM_PRE, WKB_LINESTRING_Z_PRE,
    WKB_MULTI_LINESTRING_M_PRE, WKB_MULTI_LINESTRING_PRE,
    WKB_MULTI_LINESTRING_ZM_PRE, WKB_MULTI_LINESTRING_Z_PRE)
from fudgeo.enumeration import EnvelopeCode
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, ENV_COORD, ENV_GEOM, as_array, lazy_unpack,
    pack_coordinates, unpack_line, unpack_lines)


if TYPE_CHECKING:
    from numpy import ndarray
    from fudgeo.geometry.util import Envelope


class BaseLineString(AbstractGeometry):
    """
    Base Line String
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = object
    _dimension: ClassVar[int] = 0
    _env_code: ClassVar[int] = EnvelopeCode.empty
    _has_m: ClassVar[bool] = False
    _has_z: ClassVar[bool] = False
    _wkb_prefix: ClassVar[bytes] = EMPTY

    def __init__(self, coordinates: list, srs_id: int) -> None:
        """
        Initialize the BaseLineString class
        """
        super().__init__(srs_id=srs_id)
        self._coordinates: 'ndarray' = as_array(coordinates)
    # End init built-in

    def __eq__(self, other: Any) -> bool:
        """
        Equals
        """
        if not isinstance(other, self.__class__):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.points == other.points
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict:
        """
        Geo Interface
        """
        # NOTE return 4 values when ZM present even though GeoJSON spec
        #  suggests no more than 3
        #  https://stevage.github.io/geojson-spec/#section-3.1.1
        return {'type': 'LineString',
                'bbox': self.envelope.bounding_box,
                'coordinates': tuple(
                    tuple(coords) for coords in self.coordinates)}
    # End geo_interface property

    @property
    def coordinates(self) -> 'ndarray':
        """
        Coordinates
        """
        if self._args:
            self._coordinates = unpack_line(*self._args)
            self._args = None
        # noinspection PyTypeChecker
        return self._coordinates
    # End coordinates property

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        if self._is_empty is not None:
            return self._is_empty
        return not len(self.coordinates)
    # End is_empty property

    @property
    def points(self) -> list:
        """
        Points
        """
        srs_id = self.srs_id
        cls = self._class
        return [cls.from_tuple(coords, srs_id=srs_id)
                for coords in self.coordinates]
    # End points property

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = ENV_COORD[self._env_code](self.coordinates)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, ary: bytearray) -> bytearray:
        """
        To WKB
        """
        return pack_coordinates(ary, self._wkb_prefix, self.coordinates,
                                has_z=self._has_z, has_m=self._has_m)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:
        """
        From Geopackage
        """
        return lazy_unpack(cls=cls, value=value, dimension=cls._dimension)
    # End from_gpkg method
# End BaseLineString class


class LineString(BaseLineString):
    """
    Line String
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = Point
    _dimension: ClassVar[int] = TWO_D
    _env_code: ClassVar[int] = EnvelopeCode.xy
    _wkb_prefix: ClassVar[bytes] = WKB_LINESTRING_PRE
# End LineString class


class LineStringZ(BaseLineString):
    """
    Line String Z
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointZ
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xyz
    _has_z: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_LINESTRING_Z_PRE
# End LineStringZ class


class LineStringM(BaseLineString):
    """
    Line String M
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointM
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xym
    _has_m: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_LINESTRING_M_PRE
# End LineStringM class


class LineStringZM(BaseLineString):
    """
    Line String ZM
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointZM
    _dimension: ClassVar[int] = FOUR_D
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
    _has_m: ClassVar[bool] = True
    _has_z: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_LINESTRING_ZM_PRE
# End LineStringZM class


class BaseMultiLineString(AbstractGeometry):
    """
    Base Multi Line String
    """
    __slots__ = '_lines',

    _class: ClassVar[Any] = object
    _dimension: ClassVar[int] = 0
    _env_code: ClassVar[int] = EnvelopeCode.empty
    _wkb_prefix: ClassVar[bytes] = EMPTY

    def __init__(self, coordinates: list[list], srs_id: int) -> None:
        """
        Initialize the MultiLineString class
        """
        super().__init__(srs_id=srs_id)
        self._lines: list[LineString] = self._make_lines(coordinates)
    # End init built-in

    def __eq__(self, other: Any) -> bool:
        """
        Equals
        """
        if not isinstance(other, self.__class__):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.lines == other.lines
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict:
        """
        Geo Interface
        """
        # NOTE return 4 values when ZM present even though GeoJSON spec
        #  suggests no more than 3
        #  https://stevage.github.io/geojson-spec/#section-3.1.1
        return {'type': 'MultiLineString',
                'bbox': self.envelope.bounding_box,
                'coordinates': tuple(
                    tuple(tuple(coords) for coords in line.coordinates)
                    for line in self.lines)}
    # End geo_interface property

    def _make_lines(self, coordinates: list[list]) -> list:
        """
        Make Lines
        """
        srs_id = self.srs_id
        cls = self._class
        # noinspection PyArgumentList
        return [cls(coords, srs_id=srs_id) for coords in coordinates]
    # End init built-in

    @property
    def lines(self) -> list:
        """
        Lines
        """
        if self._args:
            # noinspection PyTypeChecker
            self._lines = self._make_lines(unpack_lines(*self._args))
            self._args = None
        return self._lines
    # End lines property

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        if self._is_empty is not None:
            return self._is_empty
        return not (bool(self._args) or bool(self.lines))
    # End is_empty property

    def _to_wkb(self, ary: bytearray) -> bytearray:
        """
        To WKB
        """
        geoms = self.lines
        ary.extend(self._wkb_prefix + pack(COUNT_CODE, len(geoms)))
        return self._join_geometries(ary, geoms)
    # End _to_wkb method

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = ENV_GEOM[self._env_code](self.lines)
        self._env = env
        return env
    # End envelope property

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:
        """
        From Geopackage
        """
        return lazy_unpack(cls=cls, value=value, dimension=cls._dimension)
    # End from_gpkg method
# End BaseMultiLineString class


class MultiLineString(BaseMultiLineString):
    """
    Multi Line String
    """
    __slots__ = '_lines',

    _class: ClassVar[Any] = LineString
    _dimension: ClassVar[int] = TWO_D
    _env_code: ClassVar[int] = EnvelopeCode.xy
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_LINESTRING_PRE
# End MultiLineString class


class MultiLineStringZ(BaseMultiLineString):
    """
    Multi Line String Z
    """
    __slots__ = '_lines',

    _class: ClassVar[Any] = LineStringZ
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xyz
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_LINESTRING_Z_PRE
# End MultiLineStringZ class


class MultiLineStringM(BaseMultiLineString):
    """
    Multi Line String M
    """
    __slots__ = '_lines',

    _class: ClassVar[Any] = LineStringM
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xym
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_LINESTRING_M_PRE
# End MultiLineStringM class


class MultiLineStringZM(BaseMultiLineString):
    """
    Multi Line String ZM
    """
    __slots__ = '_lines',

    _class: ClassVar[Any] = LineStringZM
    _dimension: ClassVar[int] = FOUR_D
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_LINESTRING_ZM_PRE
# End MultiLineStringZM class


if __name__ == '__main__':  # pragma: no cover
    pass
