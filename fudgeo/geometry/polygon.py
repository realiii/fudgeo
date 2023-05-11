# -*- coding: utf-8 -*-
"""
Polygons
"""


from struct import pack
from typing import List

from fudgeo.constant import (
    COUNT_CODE, DOUBLE, FOUR_D, QUADRUPLE, THREE_D, TRIPLE, TWO_D,
    WKB_MULTI_POLYGON_M_PRE, WKB_MULTI_POLYGON_PRE, WKB_MULTI_POLYGON_ZM_PRE,
    WKB_MULTI_POLYGON_Z_PRE, WKB_POLYGON_M_PRE, WKB_POLYGON_PRE,
    WKB_POLYGON_ZM_PRE, WKB_POLYGON_Z_PRE)
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.point import Point, PointM, PointZ, PointZM
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, Envelope, envelope_from_coordinates,
    envelope_from_coordinates_m, envelope_from_coordinates_z,
    envelope_from_coordinates_zm, envelope_from_geometries,
    envelope_from_geometries_m, envelope_from_geometries_z,
    envelope_from_geometries_zm, lazy_unpack, pack_coordinates, unpack_lines,
    unpack_polygons)


class LinearRing(AbstractGeometry):
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

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_coordinates(self.coordinates)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRing':  # pragma: nocover
        """
        From Geopackage, no-op for Linear Ring
        """
        pass
    # End from_gpkg method
# End LinearRing class


class LinearRingZ(AbstractGeometry):
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

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_coordinates_z(self.coordinates)
        self._env = env
        return env
    # End envelope property

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZ':  # pragma: nocover
        """
        From Geopackage, no-op for Linear Ring
        """
        pass
    # End from_gpkg method
# End LinearRingZ class


class LinearRingM(AbstractGeometry):
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

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_coordinates_m(self.coordinates)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_m=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingM':  # pragma: nocover
        """
        From Geopackage, no-op for Linear Ring
        """
        pass
    # End from_gpkg method
# End LinearRingM class


class LinearRingZM(AbstractGeometry):
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

    def __eq__(self, other: 'LinearRingZM') -> bool:
        """
        Equals
        """
        if not isinstance(other, LinearRingZM):  # pragma: nocover
            return NotImplemented
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
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_coordinates_zm(self.coordinates)
        self._env = env
        return env
    # End envelope property

    def _to_wkb(self, use_prefix: bool = True) -> bytes:
        """
        To WKB
        """
        return pack_coordinates(self.coordinates, has_z=True, has_m=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> 'LinearRingZM':  # pragma: nocover
        """
        From Geopackage, no-op for Linear Ring
        """
        pass
    # End from_gpkg method
# End LinearRingZM class


class Polygon(AbstractGeometry):
    """
    Polygon
    """
    __slots__ = '_rings',

    def __init__(self, coordinates: List[List[DOUBLE]], srs_id: int) -> None:
        """
        Initialize the Polygon class
        """
        super().__init__(srs_id=srs_id)
        self._rings: List[LinearRing] = self._make_rings(coordinates)
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

    def _make_rings(self, coordinates: List[List[DOUBLE]]) -> List[LinearRing]:
        """
        Make Rings
        """
        srs_id = self.srs_id
        return [LinearRing(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def rings(self) -> List[LinearRing]:
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
        return not (bool(self._args) or bool(self.rings))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries(self.rings)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End Polygon class


class PolygonZ(AbstractGeometry):
    """
    Polygon Z
    """
    __slots__ = '_rings',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonZ class
        """
        super().__init__(srs_id=srs_id)
        self._rings: List[LinearRingZ] = self._make_rings(coordinates)
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

    def _make_rings(self, coordinates: List[List[TRIPLE]]) -> List[LinearRingZ]:
        """
        Make Rings
        """
        srs_id = self.srs_id
        return [LinearRingZ(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def rings(self) -> List[LinearRingZ]:
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
        return not (bool(self._args) or bool(self.rings))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_z(self.rings)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End PolygonZ class


class PolygonM(AbstractGeometry):
    """
    Polygon M
    """
    __slots__ = '_rings',

    def __init__(self, coordinates: List[List[TRIPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonM class
        """
        super().__init__(srs_id=srs_id)
        self._rings: List[LinearRingM] = self._make_rings(coordinates)
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

    def _make_rings(self, coordinates: List[List[TRIPLE]]) -> List[LinearRingM]:
        """
        Make Rings
        """
        srs_id = self.srs_id
        return [LinearRingM(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def rings(self) -> List[LinearRingM]:
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
        return not (bool(self._args) or bool(self.rings))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_m(self.rings)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End PolygonM class


class PolygonZM(AbstractGeometry):
    """
    Polygon ZM
    """
    __slots__ = '_rings',

    def __init__(self, coordinates: List[List[QUADRUPLE]], srs_id: int) -> None:
        """
        Initialize the PolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self._rings: List[LinearRingZM] = self._make_rings(coordinates)
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

    def _make_rings(self, coordinates: List[List[QUADRUPLE]]) \
            -> List[LinearRingZM]:
        """
        Make Rings
        """
        srs_id = self.srs_id
        return [LinearRingZM(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def rings(self) -> List[LinearRingZM]:
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
        return not (bool(self._args) or bool(self.rings))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_zm(self.rings)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End PolygonZM class


class MultiPolygon(AbstractGeometry):
    """
    Multi Polygon
    """
    __slots__ = '_polygons',

    def __init__(self, coordinates: List[List[List[DOUBLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygon class
        """
        super().__init__(srs_id=srs_id)
        self._polygons: List[Polygon] = self._make_polygons(coordinates)
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

    def _make_polygons(self, coordinates: List[List[List[DOUBLE]]]) \
            -> List[Polygon]:
        """
        Make Polygons
        """
        srs_id = self.srs_id
        return [Polygon(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_polygons method

    @property
    def polygons(self) -> List[Polygon]:
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
        return not (bool(self._args) or bool(self.polygons))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries(self.polygons)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=TWO_D)
    # End from_gpkg method
# End MultiPolygon class


class MultiPolygonZ(AbstractGeometry):
    """
    Multi Polygon Z
    """
    __slots__ = '_polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonZ class
        """
        super().__init__(srs_id=srs_id)
        self._polygons: List[PolygonZ] = self._make_polygons(coordinates)
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

    def _make_polygons(self, coordinates: List[List[List[TRIPLE]]]) \
            -> List[PolygonZ]:
        """
        Make Polygons
        """
        srs_id = self.srs_id
        return [PolygonZ(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_polygons method

    @property
    def polygons(self) -> List[PolygonZ]:
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
        return not (bool(self._args) or bool(self.polygons))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_z(self.polygons)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPolygonZ class


class MultiPolygonM(AbstractGeometry):
    """
    Multi Polygon M
    """
    __slots__ = '_polygons',

    def __init__(self, coordinates: List[List[List[TRIPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonM class
        """
        super().__init__(srs_id=srs_id)
        self._polygons: List[PolygonM] = self._make_polygons(coordinates)
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

    def _make_polygons(self, coordinates: List[List[List[TRIPLE]]]) \
            -> List[PolygonM]:
        """
        Make Polygons
        """
        srs_id = self.srs_id
        return [PolygonM(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_polygons method

    @property
    def polygons(self) -> List[PolygonM]:
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
        return not (bool(self._args) or bool(self.polygons))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_m(self.polygons)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=THREE_D)
    # End from_gpkg method
# End MultiPolygonM class


class MultiPolygonZM(AbstractGeometry):
    """
    Multi Polygon M
    """
    __slots__ = '_polygons',

    def __init__(self, coordinates: List[List[List[QUADRUPLE]]],
                 srs_id: int) -> None:
        """
        Initialize the MultiPolygonZM class
        """
        super().__init__(srs_id=srs_id)
        self._polygons: List[PolygonZM] = self._make_polygons(coordinates)
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

    def _make_polygons(self, coordinates: List[List[List[QUADRUPLE]]]) \
            -> List[PolygonZM]:
        """
        Make Polygons
        """
        srs_id = self.srs_id
        return [PolygonZM(coords, srs_id=srs_id) for coords in coordinates]
    # End _make_rings method

    @property
    def polygons(self) -> List[PolygonZM]:
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
        return not (bool(self._args) or bool(self.polygons))
    # End is_empty property

    @property
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        if self._env is not EMPTY_ENVELOPE:
            return self._env
        env = envelope_from_geometries_zm(self.polygons)
        self._env = env
        return env
    # End envelope property

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
        return lazy_unpack(cls=cls, value=value, dimension=FOUR_D)
    # End from_gpkg method
# End MultiPolygonZM class


if __name__ == '__main__':  # pragma: no cover
    pass
