# -*- coding: utf-8 -*-
"""
Polygons
"""


from struct import pack
from typing import Any, ClassVar, TYPE_CHECKING

from fudgeo.constant import (
    COUNT_CODE, EMPTY, FOUR_D, THREE_D, TWO_D, WKB_MULTI_POLYGON_M_PRE,
    WKB_MULTI_POLYGON_PRE, WKB_MULTI_POLYGON_ZM_PRE, WKB_MULTI_POLYGON_Z_PRE,
    WKB_POLYGON_M_PRE, WKB_POLYGON_PRE, WKB_POLYGON_ZM_PRE, WKB_POLYGON_Z_PRE)
from fudgeo.enumeration import EnvelopeCode
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, ENV_COORD, ENV_GEOM, as_array, lazy_unpack,
    pack_coordinates, unpack_lines, unpack_polygons)


if TYPE_CHECKING:  # pragma: no cover
    from numpy import ndarray
    from fudgeo.geometry.util import Envelope


class BaseLinearRing(AbstractGeometry):
    """
    Base Linear Ring
    """
    __slots__ = 'coordinates',

    _class: ClassVar[Any] = object
    _env_code: ClassVar[int] = EnvelopeCode.empty

    def __init__(self, coordinates: list, srs_id: int) -> None:
        """
        Initialize the BaseLinearRing class
        """
        super().__init__(srs_id=srs_id)
        self.coordinates: 'ndarray' = as_array(coordinates)
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
    def is_empty(self) -> bool:
        """
        Is Empty
        """
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
        return pack_coordinates(ary, EMPTY, self.coordinates)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:  # pragma: nocover
        """
        From Geopackage, no-op for Linear Ring
        """
        pass
    # End from_gpkg method
# End BaseLinearRing class


class LinearRing(BaseLinearRing):
    """
    Linear Ring
    """
    __slots__ = 'coordinates',

    _class: ClassVar[Any] = Point
    _env_code: ClassVar[int] = EnvelopeCode.xy
# End LinearRing class


class LinearRingZ(BaseLinearRing):
    """
    Linear Ring Z
    """
    __slots__ = 'coordinates',

    _class: ClassVar[Any] = PointZ
    _env_code: ClassVar[int] = EnvelopeCode.xyz
# End LinearRingZ class


class LinearRingM(BaseLinearRing):
    """
    Linear Ring M
    """
    __slots__ = 'coordinates',

    _class: ClassVar[Any] = PointM
    _env_code: ClassVar[int] = EnvelopeCode.xym
# End LinearRingM class


class LinearRingZM(BaseLinearRing):
    """
    Linear Ring ZM
    """
    __slots__ = 'coordinates',

    _class: ClassVar[Any] = PointZM
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
# End LinearRingZM class


class BasePolygon(AbstractGeometry):
    """
    Base Polygon
    """
    __slots__ = '_rings',

    _class: ClassVar[Any] = object
    _dimension: ClassVar[int] = 0
    _env_code: ClassVar[int] = EnvelopeCode.empty
    _wkb_prefix: ClassVar[bytes] = EMPTY

    def __init__(self, coordinates: list[list], srs_id: int) -> None:
        """
        Initialize the BasePolygon class
        """
        super().__init__(srs_id=srs_id)
        self._rings: list = self._make_rings(coordinates)
    # End init built-in

    def __eq__(self, other: Any) -> bool:
        """
        Equals
        """
        if not isinstance(other, self.__class__):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.rings == other.rings
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict:
        """
        Geo Interface
        """
        # NOTE return 4 values when ZM present even though GeoJSON spec
        #  suggests no more than 3
        #  https://stevage.github.io/geojson-spec/#section-3.1.1
        return {'type': 'Polygon',
                'bbox': self.envelope.bounding_box,
                'coordinates': tuple(
                    tuple(tuple(coords) for coords in ring.coordinates)
                    for ring in self.rings)}
    # End geo_interface property

    def _make_rings(self, coordinates: list[list]) -> list:
        """
        Make Rings
        """
        srs_id = self.srs_id
        cls = self._class
        return [cls(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def rings(self) -> list:
        """
        Rings
        """
        if self._args:
            # noinspection PyTypeChecker
            self._rings = self._make_rings(
                unpack_lines(*self._args, is_ring=True))
            self._args = None
        return self._rings
    # End rings property

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        if self._is_empty is not None:
            return self._is_empty
        return not (bool(self._args) or bool(self.rings))
    # End is_empty property

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = ENV_GEOM[self._env_code](self.rings)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, ary: bytearray) -> bytearray:
        """
        To WKB
        """
        geoms = self.rings
        ary.extend(self._wkb_prefix + pack(COUNT_CODE, len(geoms)))
        return self._join_geometries(ary, geoms)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:
        """
        From Geopackage
        """
        return lazy_unpack(cls=cls, value=value, dimension=cls._dimension)
    # End from_gpkg method
# End BasePolygon class


class Polygon(BasePolygon):
    """
    Polygon
    """
    __slots__ = '_rings',

    _class: ClassVar[Any] = LinearRing
    _dimension: ClassVar[int] = TWO_D
    _env_code: ClassVar[int] = EnvelopeCode.xy
    _wkb_prefix: ClassVar[bytes] = WKB_POLYGON_PRE
# End Polygon class


class PolygonZ(BasePolygon):
    """
    Polygon Z
    """
    __slots__ = '_rings',

    _class: ClassVar[Any] = LinearRingZ
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xyz
    _wkb_prefix: ClassVar[bytes] = WKB_POLYGON_Z_PRE
# End PolygonZ class


class PolygonM(BasePolygon):
    """
    Polygon M
    """
    __slots__ = '_rings',

    _class: ClassVar[Any] = LinearRingM
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xym
    _wkb_prefix: ClassVar[bytes] = WKB_POLYGON_M_PRE
# End PolygonM class


class PolygonZM(BasePolygon):
    """
    Polygon ZM
    """
    __slots__ = '_rings',

    _class: ClassVar[Any] = LinearRingZM
    _dimension: ClassVar[int] = FOUR_D
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
    _wkb_prefix: ClassVar[bytes] = WKB_POLYGON_ZM_PRE
# End PolygonZM class


class BaseMultiPolygon(AbstractGeometry):
    """
    Base Multi Polygon
    """
    __slots__ = '_polygons',

    _class: ClassVar[Any] = object
    _dimension: ClassVar[int] = 0
    _env_code: ClassVar[int] = EnvelopeCode.empty
    _wkb_prefix: ClassVar[bytes] = EMPTY

    def __init__(self, coordinates: list[list[list]],
                 srs_id: int) -> None:
        """
        Initialize the BaseMultiPolygon class
        """
        super().__init__(srs_id=srs_id)
        self._polygons: list = self._make_polygons(coordinates)
    # End init built-in

    def __eq__(self, other: Any) -> bool:
        """
        Equals
        """
        if not isinstance(other, self.__class__):  # pragma: nocover
            return NotImplemented
        if self.srs_id != other.srs_id:
            return False
        return self.polygons == other.polygons
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict:
        """
        Geo Interface
        """
        # NOTE return 4 values when ZM present even though GeoJSON spec
        #  suggests no more than 3
        #  https://stevage.github.io/geojson-spec/#section-3.1.1
        return {'type': 'MultiPolygon',
                'bbox': self.envelope.bounding_box,
                'coordinates': tuple(tuple(tuple(
                    tuple(coords) for coords in ring.coordinates)
                    for ring in poly.rings) for poly in self.polygons)}
    # End geo_interface property

    def _make_polygons(self, coordinates: list[list[list]]) -> list:
        """
        Make Polygons
        """
        srs_id = self.srs_id
        cls = self._class
        return [cls(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_polygons method

    @property
    def polygons(self) -> list:
        """
        Polygons
        """
        if self._args:
            # noinspection PyTypeChecker
            self._polygons = self._make_polygons(unpack_polygons(*self._args))
            self._args = None
        return self._polygons
    # End polygons property

    @property
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        if self._is_empty is not None:
            return self._is_empty
        return not (bool(self._args) or bool(self.polygons))
    # End is_empty property

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = ENV_GEOM[self._env_code](self.polygons)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, ary: bytearray) -> bytearray:
        """
        To WKB
        """
        geoms = self.polygons
        ary.extend(self._wkb_prefix + pack(COUNT_CODE, len(geoms)))
        return self._join_geometries(ary, geoms)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:
        """
        From Geopackage
        """
        return lazy_unpack(cls=cls, value=value, dimension=cls._dimension)
    # End from_gpkg method
# End BaseMultiPolygon class


class MultiPolygon(BaseMultiPolygon):
    """
    Multi Polygon
    """
    __slots__ = '_polygons',

    _class: ClassVar[Any] = Polygon
    _dimension: ClassVar[int] = TWO_D
    _env_code: ClassVar[int] = EnvelopeCode.xy
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POLYGON_PRE
# End MultiPolygon class


class MultiPolygonZ(BaseMultiPolygon):
    """
    Multi Polygon Z
    """
    __slots__ = '_polygons',

    _class: ClassVar[Any] = PolygonZ
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xyz
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POLYGON_Z_PRE
# End MultiPolygonZ class


class MultiPolygonM(BaseMultiPolygon):
    """
    Multi Polygon M
    """
    __slots__ = '_polygons',

    _class: ClassVar[Any] = PolygonM
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xym
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POLYGON_M_PRE
# End MultiPolygonM class


class MultiPolygonZM(BaseMultiPolygon):
    """
    Multi Polygon ZM
    """
    __slots__ = '_polygons',

    _class: ClassVar[Any] = PolygonZM
    _dimension: ClassVar[int] = FOUR_D
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POLYGON_ZM_PRE
# End MultiPolygonZM class


if __name__ == '__main__':  # pragma: no cover
    pass
