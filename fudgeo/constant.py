# -*- coding: utf-8 -*-
"""
Constants
"""


from struct import pack
from typing import Dict, List, Tuple, Union


DOUBLE = Tuple[float, float]
TRIPLE = Tuple[float, float, float]
QUADRUPLE = Tuple[float, float, float, float]
COORDINATES = Union[List[DOUBLE], List[TRIPLE], List[QUADRUPLE]]


WGS84: int = 4326

GP_MAGIC: bytes = b'GP'
EMPTY: bytes = b''
BYTE_CODE: str = '<BI'
COUNT_CODE: str = '<I'
HEADER_CODE: str = '<2s2bi'

TWO_D: int = 2
THREE_D: int = 3
FOUR_D: int = 4

TWO_D_PACK_CODE: str = f'<{TWO_D}d'
THREE_D_PACK_CODE: str = f'<{THREE_D}d'
FOUR_D_PACK_CODE: str = f'<{FOUR_D}d'
TWO_D_UNPACK_CODE: str = f'{BYTE_CODE}{TWO_D}d'
THREE_D_UNPACK_CODE: str = f'{BYTE_CODE}{THREE_D}d'
FOUR_D_UNPACK_CODE: str = f'{BYTE_CODE}{FOUR_D}d'

WKB_POINT_PRE: bytes = pack(BYTE_CODE, 1, 1)
WKB_POINT_Z_PRE: bytes = pack(BYTE_CODE, 1, 1001)
WKB_POINT_M_PRE: bytes = pack(BYTE_CODE, 1, 2001)
WKB_POINT_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3001)

WKB_LINESTRING_PRE: bytes = pack(BYTE_CODE, 1, 2)
WKB_LINESTRING_Z_PRE: bytes = pack(BYTE_CODE, 1, 1002)
WKB_LINESTRING_M_PRE: bytes = pack(BYTE_CODE, 1, 2002)
WKB_LINESTRING_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3002)

WKB_POLYGON_PRE: bytes = pack(BYTE_CODE, 1, 3)
WKB_POLYGON_Z_PRE: bytes = pack(BYTE_CODE, 1, 1003)
WKB_POLYGON_M_PRE: bytes = pack(BYTE_CODE, 1, 2003)
WKB_POLYGON_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3003)

WKB_MULTI_POINT_PRE: bytes = pack(BYTE_CODE, 1, 4)
WKB_MULTI_POINT_Z_PRE: bytes = pack(BYTE_CODE, 1, 1004)
WKB_MULTI_POINT_M_PRE: bytes = pack(BYTE_CODE, 1, 2004)
WKB_MULTI_POINT_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3004)

WKB_MULTI_LINESTRING_PRE: bytes = pack(BYTE_CODE, 1, 5)
WKB_MULTI_LINESTRING_Z_PRE: bytes = pack(BYTE_CODE, 1, 1005)
WKB_MULTI_LINESTRING_M_PRE: bytes = pack(BYTE_CODE, 1, 2005)
WKB_MULTI_LINESTRING_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3005)

WKB_MULTI_POLYGON_PRE: bytes = pack(BYTE_CODE, 1, 6)
WKB_MULTI_POLYGON_Z_PRE: bytes = pack(BYTE_CODE, 1, 1006)
WKB_MULTI_POLYGON_M_PRE: bytes = pack(BYTE_CODE, 1, 2006)
WKB_MULTI_POLYGON_ZM_PRE: bytes = pack(BYTE_CODE, 1, 3006)


POINT_PREFIX: Dict[Tuple[bool, bool], bytes] = {
    (False, False): WKB_POINT_PRE,
    (True, False): WKB_POINT_Z_PRE,
    (False, True): WKB_POINT_M_PRE,
    (True, True): WKB_POINT_ZM_PRE,
}


HEADER_OFFSET: int = 8
ENVELOPE_LENGTH: Dict[int, int] = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
ENVELOPE_COUNT: Dict[int, int] = {k: v // 8 for k, v in ENVELOPE_LENGTH.items()}
ENVELOPE_OFFSET = {k: v + HEADER_OFFSET for k, v in ENVELOPE_LENGTH.items()}


if __name__ == '__main__':
    pass
