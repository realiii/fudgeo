# -*- coding: utf-8 -*-
"""
SQL Constants
"""


from typing import Set, Tuple

# NOTE from https://sqlite.org/lang_keywords.html
KEYWORDS: Set[str] = {
    'ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ALWAYS', 'ANALYZE',
    'AND', 'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN',
    'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT',
    'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE',
    'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT', 'DEFERRABLE',
    'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DO', 'DROP', 'EACH',
    'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUDE', 'EXCLUSIVE', 'EXISTS',
    'EXPLAIN', 'FAIL', 'FILTER', 'FIRST', 'FOLLOWING', 'FOR', 'FOREIGN', 'FROM',
    'FULL', 'GENERATED', 'GLOB', 'GROUP', 'GROUPS', 'HAVING', 'IF', 'IGNORE',
    'IMMEDIATE', 'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT',
    'INSTEAD', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LAST',
    'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'MATERIALIZED', 'NATURAL', 'NO', 'NOT',
    'NOTHING', 'NOTNULL', 'NULL', 'NULLS', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER',
    'OTHERS', 'OUTER', 'OVER', 'PARTITION', 'PLAN', 'PRAGMA', 'PRECEDING',
    'PRIMARY', 'QUERY', 'RAISE', 'RANGE', 'RECURSIVE', 'REFERENCES', 'REGEXP',
    'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RETURNING', 'RIGHT',
    'ROLLBACK', 'ROW', 'ROWS', 'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP',
    'TEMPORARY', 'THEN', 'TIES', 'TO', 'TRANSACTION', 'TRIGGER', 'UNBOUNDED',
    'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL',
    'WHEN', 'WHERE', 'WINDOW', 'WITH', 'WITHOUT'
}

INSERT_GPKG_CONTENTS_SHORT: str = """
    INSERT INTO gpkg_contents (
        table_name, data_type, identifier, description, last_change, srs_id) 
    VALUES (?, ?, ?, ?, ?, ?)
"""


INSERT_GPKG_OGR_CONTENTS: str = """
    INSERT INTO gpkg_ogr_contents (table_name, feature_count) VALUES (?, ?)
"""


CREATE_OGR_CONTENTS: str = """
    CREATE TABLE gpkg_ogr_contents (
        table_name    TEXT NOT NULL PRIMARY KEY,
        feature_count INTEGER DEFAULT NULL
    );
"""


HAS_OGR_CONTENTS: str = """
    SELECT name FROM sqlite_master 
    WHERE type = 'table' AND name = 'gpkg_ogr_contents'
"""


DELETE_OGR_CONTENTS: str = """
    DELETE FROM gpkg_ogr_contents WHERE lower(table_name) = lower('{0}');
"""


# NOTE 0 - table name, 1 - escaped name, 2 - geometry column name
REMOVE_FEATURE_CLASS: str = """
    DELETE FROM gpkg_contents WHERE lower(table_name) = lower('{0}');
    DELETE FROM gpkg_geometry_columns WHERE lower(table_name) = lower('{0}');
    DELETE FROM gpkg_extensions 
    WHERE lower(table_name) = lower('{0}') AND 
          lower(extension_name) = 'gpkg_rtree_index';
    DROP TRIGGER IF EXISTS "trigger_insert_feature_count_{0}";
    DROP TRIGGER IF EXISTS "trigger_delete_feature_count_{0}";
    DROP TRIGGER IF EXISTS "rtree_{0}_{2}_insert";
    DROP TRIGGER IF EXISTS "rtree_{0}_{2}_update1";
    DROP TRIGGER IF EXISTS "rtree_{0}_{2}_update2";
    DROP TRIGGER IF EXISTS "rtree_{0}_{2}_update3";
    DROP TRIGGER IF EXISTS "rtree_{0}_{2}_update4";
    DROP TABLE IF EXISTS {1};
    DROP TABLE IF EXISTS "rtree_{0}_{2}";
"""


# NOTE 0 - name, 1 - escaped name
REMOVE_TABLE: str = """
    DELETE FROM gpkg_contents WHERE lower(table_name) = lower('{0}');
    DROP TRIGGER IF EXISTS "trigger_insert_feature_count_{0}";
    DROP TRIGGER IF EXISTS "trigger_delete_feature_count_{0}";
    DROP TABLE IF EXISTS {1};
"""


# NOTE 0 - name, 1 - escaped name
GPKG_OGR_CONTENTS_INSERT_TRIGGER: str = """
    CREATE TRIGGER "trigger_insert_feature_count_{0}"
    AFTER INSERT ON {1}
    BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count + 1 
          WHERE lower(table_name) = lower('{0}'); END;
"""


# NOTE 0 - name, 1 - escaped name
GPKG_OGR_CONTENTS_DELETE_TRIGGER: str = """
    CREATE TRIGGER "trigger_delete_feature_count_{0}"
    AFTER DELETE ON {1}
    BEGIN UPDATE gpkg_ogr_contents SET feature_count = feature_count - 1 
          WHERE lower(table_name) = lower('{0}'); END;
"""


INSERT_GPKG_GEOM_COL: str = """
    INSERT INTO gpkg_geometry_columns (
        table_name, column_name, geometry_type_name, srs_id, z, m) 
    VALUES (?, ?, ?, ?, ?, ?)
"""


CREATE_FEATURE_TABLE: str = """
    CREATE TABLE {name} (
        fid INTEGER not null primary key autoincrement, 
        SHAPE {feature_type}{other_fields})
"""


CREATE_TABLE: str = """
    CREATE TABLE {name} (
        fid INTEGER not null 
        primary key autoincrement  
        {other_fields})
"""


INSERT_GPKG_SRS: str = """
    INSERT INTO gpkg_spatial_ref_sys (
        srs_name, srs_id, organization, organization_coordsys_id, 
        definition, description)  
    VALUES (?, ?, ?, ?, ?, ?)
"""


TABLE_EXISTS: str = """
    SELECT name FROM sqlite_master 
    WHERE type = 'table' AND lower(name) = lower(?)
"""


CHECK_SRS_EXISTS: str = """
    SELECT srs_id 
    FROM gpkg_spatial_ref_sys 
    WHERE srs_id = ?
"""


SELECT_SRS: str = """
    SELECT gpkg_spatial_ref_sys.srs_name,
           gpkg_spatial_ref_sys.organization,
           gpkg_spatial_ref_sys.organization_coordsys_id,
           gpkg_spatial_ref_sys.definition,
           gpkg_spatial_ref_sys.description,
           gpkg_spatial_ref_sys.srs_id
    FROM gpkg_contents LEFT JOIN gpkg_spatial_ref_sys ON 
            gpkg_contents.srs_id = gpkg_spatial_ref_sys.srs_id
    WHERE lower(gpkg_contents.table_name) = lower(?)
"""


SELECT_HAS_ZM: str = """
    SELECT z, m
    FROM gpkg_geometry_columns
    WHERE lower(table_name) = lower(?)
"""


SELECT_GEOMETRY_COLUMN: str = """
    SELECT column_name
    FROM gpkg_geometry_columns
    WHERE lower(table_name) = lower(?)
"""


SELECT_GEOMETRY_TYPE: str = """
    SELECT GEOM || Z || M AS GT
    FROM (SELECT CASE
                     WHEN geometry_type_name == 'POINT'
                         THEN 'Point'
                     WHEN geometry_type_name == 'LINESTRING'
                         THEN 'LineString'
                     WHEN geometry_type_name == 'POLYGON'
                         THEN 'Polygon'
                     WHEN geometry_type_name == 'MULTIPOINT'
                         THEN 'MultiPoint'
                     WHEN geometry_type_name == 'MULTILINESTRING'
                         THEN 'MultiLineString'
                     WHEN geometry_type_name == 'MULTIPOLYGON'
                         THEN 'MultiPolygon'
                     ELSE ''
                     END AS GEOM,
                 CASE
                     WHEN z == 1
                         THEN 'Z'
                     ELSE ''
                     END AS Z,
                 CASE
                     WHEN m == 1
                         THEN 'M'
                     ELSE ''
                     END AS M
          FROM gpkg_geometry_columns
          WHERE lower(table_name) = lower(?)
  )
"""


UPDATE_EXTENT: str = """    
    UPDATE gpkg_contents 
    SET min_x = ?, min_y = ?, max_x = ?, max_y = ? 
    WHERE lower(table_name) = lower(?)
"""


SELECT_EXTENT: str = """
    SELECT min_x, min_y, max_x, max_y
    FROM gpkg_contents
    WHERE lower(table_name) = lower(?)
"""


SELECT_TABLES_BY_TYPE: str = """
    SELECT table_name 
    FROM gpkg_contents 
    WHERE data_type = ?
"""


DEFAULT_SRS_RECS: Tuple[Tuple[str, int, str, int, str, str], ...] = (
    ('Undefined Cartesian SRS', -1, 'NONE', -1, 'undefined',
     'undefined cartesian coordinate reference system'),
    ('Undefined Geographic SRS', 0, 'NONE', 0, 'undefined',
     'undefined geographic coordinate reference system'))


EPSG_4326: str = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]"""
ESRI_4326: str = """GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]"""


DEFAULT_EPSG_RECS: Tuple[Tuple[str, int, str, int, str, str], ...] = (
        DEFAULT_SRS_RECS + (('WGS 84', 4326, 'EPSG', 4326, EPSG_4326, ''),))
DEFAULT_ESRI_RECS: Tuple[Tuple[str, int, str, int, str, str], ...] = (
        DEFAULT_SRS_RECS + (('GCS_WGS_1984', 4326, 'EPSG', 4326, ESRI_4326, ''),))


# NOTE 0 - table name, 1 - geometry column name, 2 - primary key column name
SPATIAL_INDEX_CREATE_TABLE: str = """
    CREATE VIRTUAL TABLE "rtree_{0}_{1}" 
    USING rtree(id, minx, maxx, miny, maxy)
"""


# NOTE 0 - table name, 1 - geometry column name, 2 - primary key column name
SPATIAL_INDEX_INSERT: str = """
    INSERT OR REPLACE INTO "rtree_{0}_{1}"
        SELECT {2}, ST_MinX("{1}"), ST_MaxX("{1}"), ST_MinY("{1}"), ST_MaxY("{1}") 
        FROM "{0}" WHERE "{1}" NOT NULL AND NOT ST_IsEmpty("{1}");
"""


# NOTE 0 - table name, 1 - geometry column name, 2 - primary key column name
SPATIAL_INDEX_TRIGGERS: str = """
    /* Conditions: Insertion of non-empty geometry
       Actions   : Insert record into rtree */
    CREATE TRIGGER "rtree_{0}_{1}_insert" AFTER INSERT ON "{0}"
      WHEN (NEW."{1}" NOT NULL AND NOT ST_IsEmpty(NEW."{1}"))
    BEGIN
      INSERT OR REPLACE INTO "rtree_{0}_{1}" VALUES (
        NEW."{2}",
        ST_MinX(NEW."{1}"), ST_MaxX(NEW."{1}"),
        ST_MinY(NEW."{1}"), ST_MaxY(NEW."{1}")
      );
    END;
    
    /* Conditions: Update of geometry column to non-empty geometry
                   No row ID change
       Actions   : Update record in rtree */
    CREATE TRIGGER "rtree_{0}_{1}_update1" AFTER UPDATE OF "{1}" ON "{0}"
      WHEN OLD."{2}" = NEW."{2}" AND
           (NEW."{1}" NOTNULL AND NOT ST_IsEmpty(NEW."{1}"))
    BEGIN
      INSERT OR REPLACE INTO "rtree_{0}_{1}" VALUES (
        NEW."{2}",
        ST_MinX(NEW."{1}"), ST_MaxX(NEW."{1}"),
        ST_MinY(NEW."{1}"), ST_MaxY(NEW."{1}")
      );
    END;
    
    /* Conditions: Update of geometry column to empty geometry
                   No row ID change
       Actions   : Remove record from rtree */
    CREATE TRIGGER "rtree_{0}_{1}_update2" AFTER UPDATE OF "{1}" ON "{0}"
      WHEN OLD."{2}" = NEW."{2}" AND
           (NEW."{1}" ISNULL OR ST_IsEmpty(NEW."{1}"))
    BEGIN
      DELETE FROM "rtree_{0}_{1}" WHERE id = OLD."{2}";
    END;
    
    /* Conditions: Update of any column
                   Row ID change
                   Non-empty geometry
       Actions   : Remove record from rtree for old identifier
                   Insert record into rtree for new identifier */
    CREATE TRIGGER "rtree_{0}_{1}_update3" AFTER UPDATE ON "{0}"
      WHEN OLD."{2}" != NEW."{2}" AND
           (NEW."{1}" NOTNULL AND NOT ST_IsEmpty(NEW."{1}"))
    BEGIN
      DELETE FROM "rtree_{0}_{1}" WHERE id = OLD."{2}";
      INSERT OR REPLACE INTO "rtree_{0}_{1}" VALUES (
        NEW."{2}",
        ST_MinX(NEW."{1}"), ST_MaxX(NEW."{1}"),
        ST_MinY(NEW."{1}"), ST_MaxY(NEW."{1}")
      );
    END;
    
    /* Conditions: Update of any column
                   Row ID change
                   Empty geometry
       Actions   : Remove record from rtree for old and new identifier */
    CREATE TRIGGER "rtree_{0}_{1}_update4" AFTER UPDATE ON "{0}"
      WHEN OLD."{2}" != NEW."{2}" AND
           (NEW."{1}" ISNULL OR ST_IsEmpty(NEW."{1}"))
    BEGIN
      DELETE FROM "rtree_{0}_{1}" WHERE id IN (OLD."{2}", NEW."{2}");
    END;
    
    /* Conditions: Row deleted
       Actions   : Remove record from rtree for old identifier */
    CREATE TRIGGER "rtree_{0}_{1}_delete" AFTER DELETE ON "{0}"
      WHEN OLD."{1}" NOT NULL
    BEGIN
      DELETE FROM "rtree_{0}_{1}" WHERE id = OLD."{2}";
    END;
"""


SPATIAL_INDEX_EXTENSION: str = """
    INSERT INTO gpkg_extensions (table_name, column_name, extension_name, 
                                 definition, scope) VALUES (?, ?, ?, ?, ?)
"""


SPATIAL_INDEX_RECORD: Tuple[str, str, str] = (
    'gpkg_rtree_index', 'https://www.geopackage.org/spec131/#extension_rtree',
    'write-only')


if __name__ == '__main__':
    pass
