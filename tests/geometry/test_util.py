# -*- coding: utf-8 -*-
"""
Test Utilities
"""

from struct import unpack

from numpy import arange, array
from pytest import approx, mark

from fudgeo.constant import HEADER_OFFSET
from fudgeo.geometry import (
    MultiPolygon, MultiPolygonM, MultiPolygonZ, MultiPolygonZM)
from fudgeo.geometry.util import (
    EMPTY_ENVELOPE, Envelope, _envelope_xy, _envelope_xym, _envelope_xyz,
    _envelope_xyzm, envelope_from_coordinates, envelope_from_coordinates_m,
    envelope_from_coordinates_z, envelope_from_coordinates_zm, unpack_envelope,
    unpack_header)


@mark.parametrize('cls, srs_id, offset, code, envelope, data', [
    (MultiPolygon, 4617, 8, 0, (), b"GP\x00\x01\t\x12\x00\x00\x01\x06\x00\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@"),
    (MultiPolygonZ, 4617, 8, 0, (), b"GP\x00\x01\t\x12\x00\x00\x01\xee\x03\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\x80\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@"),
    (MultiPolygonM, 4617, 8, 0, (), b"GP\x00\x01\t\x12\x00\x00\x01\xd6\x07\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00@\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygonZM, 4617, 8, 0, (), b"GP\x00\x01\t\x12\x00\x00\x01\xbe\x0b\x00\x00\x01\x00\x00\x00\x01\x03\x00\x00\xc0\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygon, 4617, 40, 1, (-111.38173159999997, -111.37039079999994, 49.85905440000005, 49.87050880000004), b'GP\x00\x03\t\x12\x00\x00`v`Jn\xd8[\xc0L/\x9d{\xb4\xd7[\xc0\x18\xbe\x9c~\xf5\xedH@\xb0p\x15\xd5l\xefH@\x01\x06\x00\x00\x00\x03\x00\x00\x00\x01\x03\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00L/\x9d{\xb4\xd7[\xc0xom\x97\xec\xeeH@\xe4\x12\xa2\xd7\xfa\xd7[\xc0X\x00\xd6\xf4\xea\xeeH@L\x98\xe6\x0c\xfb\xd7[\xc0@1\x90\x0c\xde\xeeH@<\x1aN\x99\x1b\xd8[\xc0\xd0aA\xab\xdd\xeeH@\xf0\xad\xb41\x1b\xd8[\xc0\xa0\x97\xa1\x96\x8b\xeeH@@\x08#QC\xd8[\xc0\x18\xabP\xee\x88\xeeH@\x8c/\xa1\x82C\xd8[\xc0\x10)\x9abi\xeeH@<\x85\xc8\x8e2\xd8[\xc0\xd0\xc4\xbe\xaep\xeeH@\xd0I\xb6\xba\x1c\xd8[\xc0H\x82\x98:~\xeeH@L~\x8bN\x16\xd8[\xc0p\xa1\xae\xff\x84\xeeH@\xd0`\x1a\x86\x0f\xd8[\xc0x\x11s\xa4\x8e\xeeH@\xb0)\xb21\n\xd8[\xc0\x10|\xd9\xd1\x93\xeeH@\xbc\xe9L\x90\xc7\xd7[\xc0@0\x80\xf0\xa1\xeeH@ XU/\xbf\xd7[\xc0\x90q\xa3m\xa1\xeeH@H\xb4\xe4\xf1\xb4\xd7[\xc0p\x1d\xfa\x93\x9d\xeeH@L/\x9d{\xb4\xd7[\xc0xom\x97\xec\xeeH@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\xc8\x027\x9cC\xd8[\xc0\x10\x15\xd2\xd0\xf5\xedH@LW\x1csC\xd8[\xc0@\xffe\xadW\xeeH@\x1c\xd6\n\x89j\xd8[\xc0x\xa2\x96\xe6V\xeeH@\xb0\xd7`\x86k\xd8[\xc0  vK\x17\xeeH@\xcc8\x1e}]\xd8[\xc0\xd0\xec=\xa6\xff\xedH@tXM|Z\xd8[\xc0h:\xbe\x07\xf9\xedH@`"\xeffW\xd8[\xc0\x18\xbe\x9c~\xf5\xedH@\xc8\x027\x9cC\xd8[\xc0\x10\x15\xd2\xd0\xf5\xedH@\x01\x03\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x008\xa4\x18 Q\xd8[\xc0H\x92\xfe\x03Q\xefH@D\xc5\xff\x1dQ\xd8[\xc0\xb0p\x15\xd5l\xefH@\x04\x80*n\\\xd8[\xc0 \x88\x1b\xa6l\xefH@8\xf7\xb2Hn\xd8[\xc0\xd0\xd1w\x12l\xefH@`v`Jn\xd8[\xc0h\xf3`AP\xefH@8\xa4\x18 Q\xd8[\xc0H\x92\xfe\x03Q\xefH@'),
    (MultiPolygonZ, 4617, 56, 2, (-113.56226129999999, -113.55962689999996, 50.71791630000007, 50.72021170000005, 123.45600000000559, 123.45600000000559), b"GP\x00\x05\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\xc0\x9f\x1a/\xdd^@\x01\xee\x03\x00\x00\x01\x00\x00\x00\x01\xeb\x03\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@x\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@"),
    (MultiPolygonM, 4617, 40, 1, (-113.56226129999999, -113.55962689999996, 50.71791630000007, 50.72021170000005), b"GP\x00\x03\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x01\xd6\x07\x00\x00\x01\x00\x00\x00\x01\xd3\x07\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
    (MultiPolygonZM, 4617, 56, 2, (-113.56226129999999, -113.55962689999996, 50.71791630000007, 50.72021170000005, 123.45600000000559, 123.45600000000559), b"GP\x00\x05\t\x12\x00\x00\x9c\xd3\xd1\x16\xfcc\\\xc0\x8c]X\xed\xd0c\\\xc0\x00\xe2j\xae\xe4[I@0\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\xc0\x9f\x1a/\xdd^@\x01\xbe\x0b\x00\x00\x01\x00\x00\x00\x01\xbb\x0b\x00\x00\x01\x00\x00\x00\r\x00\x00\x004Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x8c]X\xed\xd0c\\\xc00'\x90\xc8-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f(V\r\xc2\xdcc\\\xc0\x90\xa5\x92K-\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xd8\xf1\x15\x93\xedc\\\xc0\xd0\xa3\x9eO.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xbc\xd9\xe6\xc6\xf4c\\\xc00\xd9\xa0\xe5/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc4\x8c\x01#\xf9c\\\xc0\xd8\xa7D\xc8/\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x18\xfb\xedF\xfac\\\xc0\xf8UMk.\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xc0S\xc8\x95\xfac\\\xc0Hm\x9e4\x1e\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7fx\xbe\x0b\x00\xfac\\\xc0p\x8d\xe6m\x11\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\xe8\x17\x91\xcd\xfac\\\xc0\x98\x87\x19u\x08\\I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f$\x8cfe\xfbc\\\xc0\xa0I\xc3\xdf\xe5[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f\x9c\xd3\xd1\x16\xfcc\\\xc0\x00\xe2j\xae\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f4Z\x0e\xf4\xd0c\\\xc0\xb8\x1b\x00\xbb\xe4[I@\x00\xc0\x9f\x1a/\xdd^@\x00\x00\x00\x00\x00\x00\xf8\x7f"),
])
def test_geometry_header(cls, srs_id, offset, code, envelope, data):
    """
    Test geometry header + envelope
    """
    data = memoryview(data)
    sid, env_code, off, is_empty = unpack_header(data[:HEADER_OFFSET])
    assert not is_empty
    assert sid == srs_id
    assert off == offset
    assert env_code == code
    count = (off - HEADER_OFFSET) // 8
    values = unpack(f'<{count}d', data[HEADER_OFFSET:off])
    tolerance = 10 ** -6
    assert approx(values, abs=tolerance) == envelope
    env = unpack_envelope(code=env_code, view=data[:offset])
    if code:
        assert approx(env.min_x, abs=tolerance) == envelope[0]
        assert approx(env.max_x, abs=tolerance) == envelope[1]
        assert approx(env.min_y, abs=tolerance) == envelope[2]
        assert approx(env.max_y, abs=tolerance) == envelope[3]
    if code == 2:
        assert approx(env.min_z, abs=tolerance) == envelope[4]
        assert approx(env.max_z, abs=tolerance) == envelope[5]
    if not code:
        assert env is EMPTY_ENVELOPE
    geom = cls.from_gpkg(data)
    assert isinstance(geom, cls)
# End test_geometry_header function


def test_envelope_internal_and_coordinates():
    """
    Test _envelope_xy(zm) functions and related coordinate functions
    """
    xs = arange(0, 5)
    ys = arange(5, 10)
    zs = arange(10, 15)
    ms = arange(15, 20)
    env = Envelope(code=1, min_x=0, max_x=4, min_y=5, max_y=9)
    assert _envelope_xy(xs=xs, ys=ys) == env
    assert envelope_from_coordinates(array(list(zip(xs, ys)), dtype=float)) == env
    assert envelope_from_coordinates(array([], dtype=float)) is EMPTY_ENVELOPE
    env = Envelope(code=2, min_x=0, max_x=4, min_y=5, max_y=9,
                   min_z=10, max_z=14)
    assert _envelope_xyz(xs=xs, ys=ys, zs=zs) == env
    assert envelope_from_coordinates_z(array(list(zip(xs, ys, zs)), dtype=float)) == env
    assert envelope_from_coordinates_z(array([], dtype=float)) is EMPTY_ENVELOPE
    env = Envelope(code=3, min_x=0, max_x=4, min_y=5, max_y=9,
                   min_m=15, max_m=19)
    assert _envelope_xym(xs=xs, ys=ys, ms=ms) == env
    assert envelope_from_coordinates_m(array(list(zip(xs, ys, ms)), dtype=float)) == env
    assert envelope_from_coordinates_m(array([], dtype=float)) is EMPTY_ENVELOPE
    env = Envelope(code=4, min_x=0, max_x=4, min_y=5, max_y=9,
                   min_z=10, max_z=14, min_m=15, max_m=19)
    assert _envelope_xyzm(xs=xs, ys=ys, zs=zs, ms=ms) == env
    assert envelope_from_coordinates_zm(array(list(zip(xs, ys, zs, ms)), dtype=float)) == env
    assert envelope_from_coordinates_zm(array([], dtype=float)) is EMPTY_ENVELOPE
# End test_envelope_internal_and_coordinates function


def test_envelope():
    """
    Test Envelope
    """
    env1 = Envelope(code=1, min_x=0, min_y=0, max_x=1, max_y=1)
    assert not (env1 == EMPTY_ENVELOPE)
    assert EMPTY_ENVELOPE == EMPTY_ENVELOPE
    assert str(env1) == 'Envelope(code=1, min_x=0, max_x=1, min_y=0, max_y=1, min_z=nan, max_z=nan, min_m=nan, max_m=nan)'
# End test_envelope function


if __name__ == '__main__':  # pragma: no cover
    pass
