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
    __slots__ = 'srs_id',

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractGeometry class
        """
        super().__init__()
        self.srs_id: int = srs_id
    # End init built-in

    @staticmethod
    def _join_geometries(geoms: List['AbstractGeometry']) -> bytes:
        """
        Join Geometries
        """
        return reduce(add, [geom.to_wkb() for geom in geoms], EMPTY)
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
    def to_wkb(self, use_prefix: bool = True) -> bytes:  # pragma: nocover
        """
        To WKB
        """
        pass
    # End to_wkb method

    @classmethod
    @abstractmethod
    def from_wkb(cls, wkb: bytes) -> 'AbstractGeometry':  # pragma: nocover
        """
        From WKB
        """
        pass
    # End from_wkb method

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        return (
            make_header(srs_id=self.srs_id, is_empty=self.is_empty) +
            self.to_wkb())
    # End to_gpkg method

    @classmethod
    @abstractmethod
    def from_gpkg(cls, value: bytes) -> 'AbstractGeometry':  # pragma: nocover
        """
        From Geopackage
        """
        pass
    # End from_gpkg method
# End AbstractGeometry class


class AbstractGeometryExtent(AbstractGeometry):
    """
    Abstract Geometry with Extent
    """
    __slots__ = '_extent',

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractGeometryExtent class
        """
        super().__init__(srs_id=srs_id)
        self._extent: Tuple[float, ...] = ()
    # End init built-in
# End AbstractGeometryExtent class


if __name__ == '__main__':  # pragma: no cover
    pass
