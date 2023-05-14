# -*- coding: utf-8 -*-
"""
Base Classes
"""


from abc import abstractmethod
from typing import List, Optional, Tuple

from fudgeo.geometry.util import EMPTY_ENVELOPE, Envelope, make_header


class AbstractGeometry:
    """
    Abstract Geometry
    """
    __slots__ = 'srs_id', '_env', '_args'

    def __init__(self, srs_id: int) -> None:
        """
        Initialize the AbstractGeometry class
        """
        super().__init__()
        self.srs_id: int = srs_id
        self._env: Envelope = EMPTY_ENVELOPE
        self._args: Optional[Tuple[memoryview, int]] = None
    # End init built-in

    @abstractmethod
    def _to_wkb(self) -> bytearray:  # pragma: nocover
        """
        To WKB
        """
        pass
    # End _to_wkb method

    @staticmethod
    def _join_geometries(prefix: bytes,
                         geoms: List['AbstractGeometry']) -> bytearray:
        """
        Join Geometries
        """
        ary = bytearray(prefix)
        for geom in geoms:
            ary.extend(geom._to_wkb())
        return ary
    # End _join_geometries method

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """
        Is Empty
        """
        pass
    # End is_empty property

    @property
    @abstractmethod
    def envelope(self) -> Envelope:
        """
        Envelope
        """
        pass
    # End envelope property

    def to_gpkg(self) -> bytes:
        """
        To Geopackage
        """
        env_code, env_wkb = self.envelope.to_wkb()
        return (make_header(srs_id=self.srs_id, is_empty=self.is_empty,
                            envelope_code=env_code) + env_wkb + self._to_wkb())
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


if __name__ == '__main__':  # pragma: no cover
    pass
