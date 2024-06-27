PRAGMA application_id=0x47504B47;
PRAGMA user_version=10400;

-- TABLES

CREATE TABLE gpkg_spatial_ref_sys (
    srs_name                 TEXT    NOT NULL,
    srs_id                   INTEGER NOT NULL PRIMARY KEY,
    organization             TEXT    NOT NULL,
    organization_coordsys_id INTEGER NOT NULL,
    definition               TEXT    NOT NULL,
    description              TEXT
);


CREATE TABLE gpkg_contents (
    table_name  TEXT     NOT NULL PRIMARY KEY,
    data_type   TEXT     NOT NULL,
    identifier  TEXT UNIQUE,
    description TEXT              DEFAULT '',
    last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S.%fZ', 'now')),
    min_x       DOUBLE,
    min_y       DOUBLE,
    max_x       DOUBLE,
    max_y       DOUBLE,
    srs_id      INTEGER,
    CONSTRAINT fk_gc_r_srs_id
        FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys (srs_id)
);


CREATE TABLE gpkg_geometry_columns (
    table_name         TEXT    NOT NULL,
    column_name        TEXT    NOT NULL,
    geometry_type_name TEXT    NOT NULL,
    srs_id             INTEGER NOT NULL,
    z                  TINYINT NOT NULL,
    m                  TINYINT NOT NULL,
    CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
    CONSTRAINT uk_gc_table_name UNIQUE (table_name),
    CONSTRAINT fk_gc_tn FOREIGN KEY (table_name)
        REFERENCES gpkg_contents (table_name),
    CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id)
        REFERENCES gpkg_spatial_ref_sys (srs_id)
);


CREATE TABLE gpkg_tile_matrix_set (
    table_name TEXT    NOT NULL PRIMARY KEY,
    srs_id     INTEGER NOT NULL,
    min_x      DOUBLE  NOT NULL,
    min_y      DOUBLE  NOT NULL,
    max_x      DOUBLE  NOT NULL,
    max_y      DOUBLE  NOT NULL,
    CONSTRAINT fk_gtms_table_name FOREIGN KEY (table_name)
        REFERENCES gpkg_contents (table_name),
    CONSTRAINT fk_gtms_srs FOREIGN KEY (srs_id)
        REFERENCES gpkg_spatial_ref_sys (srs_id)
);


CREATE TABLE gpkg_tile_matrix (
    table_name    TEXT    NOT NULL,
    zoom_level    INTEGER NOT NULL,
    matrix_width  INTEGER NOT NULL,
    matrix_height INTEGER NOT NULL,
    tile_width    INTEGER NOT NULL,
    tile_height   INTEGER NOT NULL,
    pixel_x_size  DOUBLE  NOT NULL,
    pixel_y_size  DOUBLE  NOT NULL,
    CONSTRAINT pk_ttm PRIMARY KEY (table_name, zoom_level),
    CONSTRAINT fk_tmm_table_name FOREIGN KEY (table_name)
        REFERENCES gpkg_contents (table_name)
);


CREATE TABLE gpkg_extensions (
    table_name     TEXT,
    column_name    TEXT,
    extension_name TEXT NOT NULL,
    definition     TEXT NOT NULL,
    scope          TEXT NOT NULL,
    CONSTRAINT ge_tce UNIQUE (table_name, column_name, extension_name)
);

-- VIEWS

CREATE VIEW st_spatial_ref_sys AS
SELECT srs_name,
       srs_id,
       organization,
       organization_coordsys_id,
       definition,
       description
FROM gpkg_spatial_ref_sys;


CREATE VIEW spatial_ref_sys AS
SELECT srs_id                   AS srid,
       organization             AS auth_name,
       organization_coordsys_id AS auth_srid,
       definition               AS srtext
FROM gpkg_spatial_ref_sys;


CREATE VIEW st_geometry_columns AS
SELECT table_name,
       column_name,
       'ST_' || geometry_type_name AS geometry_type_name,
       g.srs_id,
       srs_name
FROM gpkg_geometry_columns as g
         JOIN gpkg_spatial_ref_sys AS s
WHERE g.srs_id = s.srs_id;


CREATE VIEW geometry_columns AS
SELECT table_name                                      AS f_table_name,
       column_name                                     AS f_geometry_column,
       case geometry_type_name
           WHEN 'POINT' THEN 1
           WHEN 'LINESTRING' THEN 2
           WHEN 'POLYGON' THEN 3
           WHEN 'MULTIPOINT' THEN 4
           WHEN 'MULTILINESTRING' THEN 5
           WHEN 'MULTIPOLYGON' THEN 6
           ELSE 0 END                                  AS geometry_type,
       2 + (CASE z WHEN 1 THEN 1 WHEN 2 THEN 1 ELSE 0 END) +
       (CASE m WHEN 1 THEN 1 WHEN 2 THEN 1 ELSE 0 END) AS coord_dimension,
       srs_id                                          AS srid
FROM gpkg_geometry_columns;
