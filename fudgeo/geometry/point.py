# -*- coding: utf-8 -*-
"""
Points
"""


from math import isnan, nan
from struct import pack, unpack
from typing import Any, ClassVar, TYPE_CHECKING, Union

from fudgeo.alias import BYTE_ARRAY, DOUBLE, QUADRUPLE, TRIPLE
from fudgeo.constant import (
    EMPTY, FOUR_D, FOUR_D_PACK_CODE, FOUR_D_UNPACK_CODE, HEADER_OFFSET, THREE_D,
    THREE_D_PACK_CODE, THREE_D_UNPACK_CODE, TWO_D, TWO_D_PACK_CODE,
    TWO_D_UNPACK_CODE, WKB_MULTI_POINT_M_PRE, WKB_MULTI_POINT_PRE,
    WKB_MULTI_POINT_ZM_PRE, WKB_MULTI_POINT_Z_PRE, WKB_POINT_M_PRE,
    WKB_POINT_PRE, WKB_POINT_ZM_PRE, WKB_POINT_Z_PRE)
from fudgeo.enumeration import EnvelopeCode
from fudgeo.geometry.base import AbstractGeometry
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, ENV_COORD, as_array, lazy_unpack, make_header,
    pack_coordinates, unpack_header, unpack_points)


if TYPE_CHECKING:  # pragma: no cover
    from numpy import ndarray
    from fudgeo.geometry.util import Envelope


class Point(AbstractGeometry):
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
        return self.as_tuple() == other.as_tuple()
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict[str, Union[str, DOUBLE]]:
        """
        Geo Interface
        """
        return {'type': 'Point', 'coordinates': self.as_tuple()}
    # End geo_interface property

    def as_tuple(self) -> DOUBLE:
        """
        As Tuple
        """
        return self.x, self.y
    # End as_tuple method

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

    def _to_wkb(self, ary: BYTE_ARRAY = None) -> bytes:
        """
        To WKB
        """
        return WKB_POINT_PRE + pack(TWO_D_PACK_CODE, *self.as_tuple())
    # End _to_wkb method

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        return EMPTY_ENVELOPE
    # End envelope property

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return (make_header(srs_id=self.srs_id,
                            is_empty=self.is_empty) + self._to_wkb())
    # End to_gpkg method

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


class PointZ(AbstractGeometry):
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
        return self.as_tuple() == other.as_tuple()
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict[str, Union[str, TRIPLE]]:
        """
        Geo Interface
        """
        return {'type': 'Point', 'coordinates': self.as_tuple()}

    # End geo_interface property

    def as_tuple(self) -> TRIPLE:
        """
        As Tuple
        """
        return self.x, self.y, self.z
    # End as_tuple method

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

    def _to_wkb(self, ary: BYTE_ARRAY = None) -> bytes:
        """
        To WKB
        """
        return WKB_POINT_Z_PRE + pack(THREE_D_PACK_CODE, *self.as_tuple())
    # End _to_wkb method

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        return EMPTY_ENVELOPE
    # End envelope property

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return (make_header(srs_id=self.srs_id,
                            is_empty=self.is_empty) + self._to_wkb())
    # End to_gpkg method

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


class PointM(AbstractGeometry):
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
        return self.as_tuple() == other.as_tuple()
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict[str, Union[str, TRIPLE]]:
        """
        Geo Interface
        """
        return {'type': 'Point', 'coordinates': self.as_tuple()}
    # End geo_interface property

    def as_tuple(self) -> TRIPLE:
        """
        As Tuple
        """
        return self.x, self.y, self.m
    # End as_tuple method

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

    def _to_wkb(self, ary: BYTE_ARRAY = None) -> bytes:
        """
        To WKB
        """
        return WKB_POINT_M_PRE + pack(THREE_D_PACK_CODE, *self.as_tuple())
    # End _to_wkb method

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        return EMPTY_ENVELOPE
    # End envelope property

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return (make_header(srs_id=self.srs_id,
                            is_empty=self.is_empty) + self._to_wkb())
    # End to_gpkg method

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


class PointZM(AbstractGeometry):
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
        return self.as_tuple() == other.as_tuple()
    # End eq built-in

    @property
    def __geo_interface__(self) -> dict[str, Union[str, QUADRUPLE]]:
        """
        Geo Interface
        """
        # NOTE return 4 values when ZM present even though GeoJSON spec
        #  suggests no more than 3
        #  https://stevage.github.io/geojson-spec/#section-3.1.1
        return {'type': 'Point', 'coordinates': self.as_tuple()}
    # End geo_interface property

    def as_tuple(self) -> QUADRUPLE:
        """
        As Tuple
        """
        return self.x, self.y, self.z, self.m
    # End as_tuple method

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

    def _to_wkb(self, ary: BYTE_ARRAY = None) -> bytes:
        """
        To WKB
        """
        return WKB_POINT_ZM_PRE + pack(FOUR_D_PACK_CODE, *self.as_tuple())
    # End _to_wkb method

    @property
    def envelope(self) -> 'Envelope':
        """
        Envelope
        """
        return EMPTY_ENVELOPE
    # End envelope property

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        # noinspection PyArgumentEqualDefault
        return (make_header(srs_id=self.srs_id,
                            is_empty=self.is_empty) + self._to_wkb(None))
    # End to_gpkg method

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


class BaseMultiPoint(AbstractGeometry):
    """
    Base Multi Point
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
        Initialize the BaseMultiPoint class
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
        return {'type': 'MultiPoint',
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
            self._coordinates = unpack_points(*self._args)
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
        return pack_coordinates(
            ary, self._wkb_prefix, self.coordinates,
            has_z=self._has_z, has_m=self._has_m,
            use_point_prefix=True)
    # End _to_wkb method

    @classmethod
    def from_gpkg(cls, value: bytes) -> Any:
        """
        From Geopackage
        """
        return lazy_unpack(cls=cls, value=value, dimension=cls._dimension)
    # End from_gpkg method
# End BaseMultiPoint class


class MultiPoint(BaseMultiPoint):
    """
    Multi Point
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = Point
    _dimension: ClassVar[int] = TWO_D
    _env_code: ClassVar[int] = EnvelopeCode.xy
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POINT_PRE
# End MultiPoint class


class MultiPointZ(BaseMultiPoint):
    """
    Multi Point Z
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointZ
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xyz
    _has_z: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POINT_Z_PRE
# End MultiPointZ class


class MultiPointM(BaseMultiPoint):
    """
    Multi Point M
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointM
    _dimension: ClassVar[int] = THREE_D
    _env_code: ClassVar[int] = EnvelopeCode.xym
    _has_m: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POINT_M_PRE
# End MultiPointM class


class MultiPointZM(BaseMultiPoint):
    """
    Multi Point ZM
    """
    __slots__ = '_coordinates',

    _class: ClassVar[Any] = PointZM
    _dimension: ClassVar[int] = FOUR_D
    _env_code: ClassVar[int] = EnvelopeCode.xyzm
    _has_m: ClassVar[bool] = True
    _has_z: ClassVar[bool] = True
    _wkb_prefix: ClassVar[bytes] = WKB_MULTI_POINT_ZM_PRE
# End MultiPointZM class


if __name__ == '__main__':  # pragma: no cover
    pass
