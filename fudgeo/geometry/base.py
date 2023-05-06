# -*- coding: utf-8 -*-
"""
Base Classes
"""


from abc import abstractmethod
from functools import reduce
from operator import add
from typing import List, Tuple

from fudgeo.constant import EMPTY
from fudgeo.geometry.util import make_header


class AbstractGeometry:
    """
    Abstract Geometry
    """
    __slots__ = []

    @staticmethod
    def _join_geometries(geoms: List['AbstractGeometry']) -> bytes:
        """
        Join Geometries
        """
        return reduce(add, [geom._to_wkb() for geom in geoms], EMPTY)
    # End _join_geometries method

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        pass
    # End is_empty property

    @abstractmethod
    def _to_wkb(self, use_prefix: bool = True) -> bytes:  # pragma: nocover
        """
        To WKB
        """
        pass
    # End _to_wkb method
# End AbstractGeometry class


# noinspection PyAbstractClass
class AbstractSpatialGeometry(AbstractGeometry):
    """
    Abstract Spatial Geometry
    """
    __slots__ = 'srs_id',

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractSpatialGeometry class
        """
        super().__init__()
        self.srs_id: int = srs_id
    # End init built-in
# End AbstractSpatialGeometry class


# noinspection PyAbstractClass
class AbstractSpatialGeometryExtent(AbstractSpatialGeometry):
    """
    Abstract Spatial Geometry with Extent
    """
    __slots__ = '_extent',

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractSpatialGeometryExtent class
        """
        super().__init__(srs_id=srs_id)
        self._extent: Tuple[float, ...] = ()
    # End init built-in
# End AbstractSpatialGeometryExtent class


class AbstractGeopackageGeometry(AbstractSpatialGeometry):
    """
    Abstract Geopackage Geometry
    """
    __slots__ = 'srs_id',

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return (make_header(srs_id=self.srs_id, is_empty=self.is_empty) +
                self._to_wkb())
    # End to_gpkg method

    @classmethod
    @abstractmethod
    def from_gpkg(cls, value: bytes) -> 'AbstractGeometry':  # pragma: nocover
        """
        From Geopackage
        """
        pass
    # End from_gpkg method
# End AbstractGeopackageGeometry class


# noinspection PyAbstractClass
class AbstractGeopackageGeometryExtent(AbstractGeopackageGeometry):
    """
    Abstract Spatial Geometry with Extent
    """
    __slots__ = '_extent',

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractSpatialGeometryExtent class
        """
        super().__init__(srs_id=srs_id)
        self._extent: Tuple[float, ...] = ()
    # End init built-in
# End AbstractGeopackageGeometryExtent class


if __name__ == '__main__':  # pragma: no cover
    pass
