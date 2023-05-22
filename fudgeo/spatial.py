# -*- coding: utf-8 -*-
"""
Spatial Type Functions
"""


from functools import lru_cache
# noinspection PyPep8Naming
from struct import error as StructError, unpack
from typing import Callable, Dict, Optional, TYPE_CHECKING, Tuple, Type, Union

from fudgeo.constant import (
    ENVELOPE_COUNT, ENVELOPE_OFFSET, HEADER_CODE, HEADER_OFFSET, POINT_PREFIXES,
    QUADRUPLE, WKB_LINESTRING_M_PRE, WKB_LINESTRING_PRE, WKB_LINESTRING_ZM_PRE,
    WKB_LINESTRING_Z_PRE, WKB_MULTI_LINESTRING_M_PRE, WKB_MULTI_LINESTRING_PRE,
    WKB_MULTI_LINESTRING_ZM_PRE, WKB_MULTI_LINESTRING_Z_PRE,
    WKB_MULTI_POINT_M_PRE, WKB_MULTI_POINT_PRE, WKB_MULTI_POINT_ZM_PRE,
    WKB_MULTI_POINT_Z_PRE, WKB_MULTI_POLYGON_M_PRE, WKB_MULTI_POLYGON_PRE,
    WKB_MULTI_POLYGON_ZM_PRE, WKB_MULTI_POLYGON_Z_PRE, WKB_POINT_M_PRE,
    WKB_POINT_PRE, WKB_POINT_ZM_PRE, WKB_POINT_Z_PRE, WKB_POLYGON_M_PRE,
    WKB_POLYGON_PRE, WKB_POLYGON_ZM_PRE, WKB_POLYGON_Z_PRE)
from fudgeo.geometry.linestring import (
    LineString, LineStringZ, LineStringM, LineStringZM,
    MultiLineString, MultiLineStringZ, MultiLineStringM, MultiLineStringZM)
from fudgeo.geometry.point import (
    Point, PointZ, PointM, PointZM,
    MultiPoint, MultiPointZ, MultiPointM, MultiPointZM)
from fudgeo.geometry.polygon import (
    Polygon, PolygonZ, PolygonM, PolygonZM,
    MultiPolygon, MultiPolygonZ, MultiPolygonM, MultiPolygonZM)


if TYPE_CHECKING:
    from fudgeo.geometry.base import AbstractGeometry


NONES = Tuple[None, None, None, None]


@lru_cache()
def _find_bounds(geometry: bytes) -> Union[QUADRUPLE, NONES]:
    """
    Find Bounds from Geometry, use envelope first, fail over to coordinates.
    Cache the results to avoid doing all the unpacking work in each function.
    """
    view = memoryview(geometry)
    _, _, flags, _ = unpack(HEADER_CODE, view[:HEADER_OFFSET])
    code = (flags & (0x07 << 1)) >> 1
    try:
        offset = ENVELOPE_OFFSET[code]
    except KeyError:
        return None, None, None, None
    if code:
        try:
            # noinspection PyTypeChecker
            return unpack(
                f'<{ENVELOPE_COUNT[code]}d', view[HEADER_OFFSET:offset])[:4]
        except (StructError, IndexError):
            pass
    prefix = view[offset: offset + 5]
    try:
        # noinspection PyTypeChecker
        geom_type = PREFIX_GEOM_TYPE[prefix]
    except KeyError:
        return None, None, None, None
    if prefix in POINT_PREFIXES:
        # noinspection PyProtectedMember
        x, y, *_ = geom_type._unpack(view[offset:])
        return x, x, y, y
    else:
        envelope = geom_type.from_gpkg(view).envelope
        return envelope.min_x, envelope.max_x, envelope.min_y, envelope.max_y
# End _find_bounds function


def _st_is_empty(geometry: bytes) -> Optional[int]:
    """
    Is Empty
    """
    if geometry is None:
        return
    _, _, flags, _ = unpack(HEADER_CODE, geometry[:HEADER_OFFSET])
    return (flags & (0x01 << 4)) >> 4
# End _st_is_empty function


def _st_min_x(geometry: bytes) -> Optional[float]:
    """
    Min X
    """
    return _find_bounds(geometry)[0]
# End _st_min_x function


def _st_max_x(geometry: bytes) -> Optional[float]:
    """
    Max X
    """
    return _find_bounds(geometry)[1]
# End _st_max_x function


def _st_min_y(geometry: bytes) -> Optional[float]:
    """
    Min Y
    """
    return _find_bounds(geometry)[2]
# End _st_min_y function


def _st_max_y(geometry: bytes) -> Optional[float]:
    """
    Max Y
    """
    return _find_bounds(geometry)[3]
# End _st_max_y function


ST_FUNCS: Dict[str, Callable] = {
    'ST_IsEmpty': _st_is_empty,
    'ST_MinX': _st_min_x,
    'ST_MaxX': _st_max_x,
    'ST_MinY': _st_min_y,
    'ST_MaxY': _st_max_y
}


PREFIX_GEOM_TYPE: Dict[bytes, Type['AbstractGeometry']] = {
    WKB_POINT_PRE: Point,
    WKB_POINT_Z_PRE: PointZ,
    WKB_POINT_M_PRE: PointM,
    WKB_POINT_ZM_PRE: PointZM,

    WKB_LINESTRING_PRE: LineString,
    WKB_LINESTRING_Z_PRE: LineStringZ,
    WKB_LINESTRING_M_PRE: LineStringM,
    WKB_LINESTRING_ZM_PRE: LineStringZM,

    WKB_POLYGON_PRE: Polygon,
    WKB_POLYGON_Z_PRE: PolygonZ,
    WKB_POLYGON_M_PRE: PolygonM,
    WKB_POLYGON_ZM_PRE: PolygonZM,

    WKB_MULTI_POINT_PRE: MultiPoint,
    WKB_MULTI_POINT_Z_PRE: MultiPointZ,
    WKB_MULTI_POINT_M_PRE: MultiPointM,
    WKB_MULTI_POINT_ZM_PRE: MultiPointZM,

    WKB_MULTI_LINESTRING_PRE: MultiLineString,
    WKB_MULTI_LINESTRING_Z_PRE: MultiLineStringZ,
    WKB_MULTI_LINESTRING_M_PRE: MultiLineStringM,
    WKB_MULTI_LINESTRING_ZM_PRE: MultiLineStringZM,

    WKB_MULTI_POLYGON_PRE: MultiPolygon,
    WKB_MULTI_POLYGON_Z_PRE: MultiPolygonZ,
    WKB_MULTI_POLYGON_M_PRE: MultiPolygonM,
    WKB_MULTI_POLYGON_ZM_PRE: MultiPolygonZM,
}


if __name__ == '__main__':  # pragma: no cover
    pass
