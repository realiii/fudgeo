# -*- coding: utf-8 -*-
"""
Package Initialization
"""


from fudgeo.geopkg import (
    GeoPackage, MemoryGeoPackage, Table, FeatureClass,
    SpatialReferenceSystem, Field)


__version__ = '1.1.0'


__all__ = ['GeoPackage', 'MemoryGeoPackage', 'Table', 'FeatureClass',
           'SpatialReferenceSystem', 'Field']


if __name__ == '__main__':  # pragma: no cover
    pass
