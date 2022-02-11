# -*- coding: utf-8 -*-
"""
SQL Constants
"""


INSERT_GPKG_CONTENTS_SHORT = """
    INSERT INTO gpkg_contents (
        table_name, data_type, identifier, description, last_change, srs_id) 
    VALUES (?, ?, ?, ?, ?, ?)
"""


INSERT_GPKG_OGR_CONTENTS = """
    INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES (?, ?)
"""


GPKG_OGR_CONTENTS_INSERT_TRIGGER = """
    CREATE TRIGGER trigger_insert_feature_count_{0}
    AFTER INSERT ON {0}
    BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 
          WHERE lower(table_name) = lower('{0}'); END;
"""


GPKG_OGR_CONTENTS_DELETE_TRIGGER = """
    CREATE TRIGGER trigger_delete_feature_count_{0}
    AFTER DELETE ON {0}
    BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 
          WHERE lower(table_name) = lower('{0}'); END;
"""


INSERT_GPKG_GEOM_COL = """
    INSERT INTO gpkg_geometry_columns (
        table_name, column_name, geometry_type_name, srs_id, z, m) 
    VALUES (?, ?, ?, ?, ?, ?)
"""


CREATE_FEATURE_TABLE = """
    CREATE TABLE {name} (
        fid INTEGER not null primary key autoincrement, 
        SHAPE {feature_type}{other_fields})
"""


CREATE_TABLE = """
    CREATE TABLE {name} (
        fid INTEGER not null 
        primary key autoincrement  
        {other_fields})
"""


INSERT_GPKG_SRS = """
    INSERT INTO gpkg_spatial_ref_sys (
        srs_name, srs_id, organization, organization_coordsys_id, 
        definition, description)  
    VALUES (?, ?, ?, ?, ?, ?)
"""


TABLE_EXISTS = """
    SELECT name FROM sqlite_master 
    WHERE type = 'table' AND name= ?
"""


CHECK_SRS_EXISTS = """
    SELECT srs_id FROM gpkg_spatial_ref_sys 
    WHERE srs_id = ?
"""


SELECT_SRS = """
    SELECT gpkg_spatial_ref_sys.srs_name,
           gpkg_spatial_ref_sys.organization,
           gpkg_spatial_ref_sys.organization_coordsys_id,
           gpkg_spatial_ref_sys.definition,
           gpkg_spatial_ref_sys.description
    FROM gpkg_contents LEFT JOIN gpkg_spatial_ref_sys ON 
            gpkg_contents.srs_id = gpkg_spatial_ref_sys.srs_id
    WHERE gpkg_contents.table_name = ?
"""


SELECT_HAS_ZM = """
    SELECT gpkg_geometry_columns.z,gpkg_geometry_columns.m
    FROM gpkg_contents LEFT JOIN gpkg_geometry_columns ON 
            gpkg_contents.table_name = gpkg_geometry_columns.table_name
    WHERE gpkg_contents.table_name = ?
"""


UPDATE_EXTENT = """    
    UPDATE gpkg_contents 
    SET min_x=?, min_y=?, max_x=?, max_y=? 
    WHERE table_name = ?
"""


SELECT_EXTENT = """
    SELECT min_x, min_y, max_x, max_y
    FROM gpkg_contents
    WHERE table_name = ?
"""


SELECT_TABLES_BY_TYPE = (
    """SELECT table_name FROM gpkg_contents WHERE data_type = ?""")


DEFAULT_SRS_RECS = (
    ('Undefined Cartesian SRS', -1, 'NONE', -1, 'undefined',
     'undefined cartesian coordinate reference system'),
    ('Undefined Geographic SRS', 0, 'NONE', 0, 'undefined',
     'undefined geographic coordinate reference system'))

EPSG_4326 = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]"""
ESRI_4326 = """GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]"""

DEFAULT_EPSG_RECS = DEFAULT_SRS_RECS + (
    ('WGS 84', 4326, 'EPSG', 4326, EPSG_4326, ''),)
DEFAULT_ESRI_RECS = DEFAULT_SRS_RECS + (
    ('GCS_WGS_1984', 4326, 'EPSG', 4326, ESRI_4326, ''),)


if __name__ == '__main__':
    pass
