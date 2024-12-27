# fudgeo

`fudgeo` removes the *fear uncertainty doubt* from using GeoPackages with 
`Python`. `fudgeo` is a lightweight package for creating OGC GeoPackages, Feature 
Classes, and Tables.  Easily read and write geometries and attributes to
Feature Classes and Tables using regular `Python` objects and `SQLite` syntax.

For details on OGC GeoPackages, please see the [OGC web page](http://www.geopackage.org/).


## Installation

`fudgeo` is available from the [Python Package Index](https://pypi.org/project/fudgeo/).


## Python Compatibility

The `fudgeo` library is compatible with Python 3.9 to 3.13.  Developed and 
tested on **macOS** and **Windows**, should be fine on **Linux** too.


## Usage

`fudgeo` can be used to: 
* Create a new empty `GeoPackage` or open an existing `GeoPackage`
* Create new `FeatureClass` or `Table` with optional overwrite
* Create `SpatialReferenceSystem` for a `FeatureClass`
* Build geometry objects from lists of coordinate values
* Work with data in `Table` or `FeatureClass` in a normal `SQLite` manner (e.g. `SELECT`, `INSERT`, `UPDATE`, `DELETE`)
* Retrieve fields from a `FeatureClass` or `Table`
* Access primary key field of `FeatureClass` or `Table` 
* Access geometry column name and geometry type for `FeatureClass`
* Add spatial index on `FeatureClass`
* Drop `FeatureClass` or `Table`
* Add metadata and schema details


### Create an Empty GeoPackage / Open GeoPackage

```python
from fudgeo.geopkg import GeoPackage

# Creates an empty geopackage
gpkg: GeoPackage = GeoPackage.create('../data/example.gpkg')

# Opens an existing Geopackage (no validation)
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')
```

`GeoPackage`s are created with *three* default Spatial References defined
automatically, a pair of Spatial References to handle **undefined** cases,
and a **WGS 84** entry. 

The definition of the WGS84 entry is flexible - meaning that the 
*WKT for WGS84* can be setup per the users liking. As an example, 
use with Esri's ArcGIS means either using the *EPSG WKT* or the *ESRI WKT*. By
default, the *ESRI WKT* is used - However, if *EPSG WKT* is desired, you
may provide a ``flavor`` parameter to the create method specifying EPSG.

```python
from fudgeo.geopkg import GeoPackage

# Creates an empty geopackage using EPSG definitions
gpkg: GeoPackage = GeoPackage.create('../temp/test.gpkg', flavor='EPSG')
```

### Create a Feature Class

Use the `create_feature_class` method of a GeoPackage to make
a new feature class.  Feature classes require a name and a Spatial 
Reference, the name must follow SQLite naming requirements.  Each
feature class is defined with `fid` and `SHAPE` fields, additional
fields can be defined during creation.  `SHAPE` is the default geometry
column name however it can be specified during feature class creation.

A Feature Class can be created with *Z* or *M* (or both) enabled. If 
either of these options are enabled, the geometry inserted into the 
Feature Class **must** include a value for the option specified.

```python
from fudgeo.enumeration import GeometryType, SQLFieldType
from fudgeo.geopkg import FeatureClass, Field, GeoPackage, SpatialReferenceSystem

SRS_WKT: str = (
    'PROJCS["WGS_1984_UTM_Zone_23N",'
    'GEOGCS["GCS_WGS_1984",'
    'DATUM["D_WGS_1984",'
    'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PRIMEM["Greenwich",0.0],'
    'UNIT["Degree",0.0174532925199433]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["False_Easting",500000.0],'
    'PARAMETER["False_Northing",0.0],'
    'PARAMETER["Central_Meridian",-45.0],'
    'PARAMETER["Scale_Factor",0.9996],'
    'PARAMETER["Latitude_Of_Origin",0.0],'
    'UNIT["Meter",1.0]]')

SRS: SpatialReferenceSystem = SpatialReferenceSystem(
    name='WGS_1984_UTM_Zone_23N', organization='EPSG',
    org_coord_sys_id=32623, definition=SRS_WKT)
fields: tuple[Field, ...] = (
    Field('road_id', SQLFieldType.integer),
    Field('name', SQLFieldType.text, size=100),
    Field('begin_easting', SQLFieldType.double),
    Field('begin_northing', SQLFieldType.double),
    Field('end_easting', SQLFieldType.double),
    Field('end_northing', SQLFieldType.double),
    Field('begin_longitude', SQLFieldType.double),
    Field('begin_latitude', SQLFieldType.double),
    Field('end_longitude', SQLFieldType.double),
    Field('end_latitude', SQLFieldType.double),
    Field('is_one_way', SQLFieldType.boolean))

gpkg: GeoPackage = GeoPackage.create('../temp/test.gpkg')
fc: FeatureClass = gpkg.create_feature_class(
    'road_l', srs=SRS, fields=fields, shape_type=GeometryType.linestring,
    m_enabled=True, overwrite=True, spatial_index=True)
```

### About Spatial References For GeoPackages

Spatial References in GeoPackages can use any definition from any 
authority - be that `EPSG`, `ESRI`, or another authority. `fudgeo` imposes no 
restriction and performs no checks on the definitions provided. Take care 
to ensure that the definitions are compatible with the platform / software 
you intend to utilize with the `GeoPackage`.

### Insert Features into a Feature Class (SQL)

Features can be inserted into a Feature Class using SQL.

This example shows the creation of a random point Feature Class and
builds upon the code from previous examples. Note that the create Feature Class
portion of the code is omitted...

```python
from random import choice, randint
from string import ascii_uppercase, digits

from fudgeo.geometry import LineStringM
from fudgeo.geopkg import GeoPackage

# Generate some random points and attributes
rows: list[tuple[LineStringM, int, str, float, float, float, float, bool]] = []
for i in range(10000):
    name = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
    road_id = randint(0, 1000)
    eastings = [randint(300000, 600000) for _ in range(20)]
    northings = [randint(1, 100000) for _ in range(20)]
    coords = [(x, y, m) for m, (x, y) in enumerate(zip(eastings, northings))]
    road = LineStringM(coords, srs_id=32623)
    rows.append((road, road_id, name, eastings[0], northings[0],
                 eastings[-1], northings[-1], False))

# NOTE Builds from previous examples
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')   
with gpkg.connection as conn:
    conn.executemany("""
        INSERT INTO road_l (SHAPE, road_id, name, begin_easting, begin_northing, 
                            end_easting, end_northing, is_one_way) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", rows)
```

### Geometry Examples

Review the tests for `fudgeo` for a comprehensive look into 
creating geometries, below are some examples showing the simplicity
of this package.


```python
from fudgeo.geometry import LineStringZM, Point, Polygon

# Point in WGS 84
pt: Point = Point(x=-119, y=34)

# Line with ZM Values for use with UTM Zone 23N (WGS 84)
coords: list[tuple[float, float, float, float]] = [
    (300000, 1, 10, 0), (300000, 4000000, 20, 1000),
    (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
line: LineStringZM = LineStringZM(coords, srs_id=32623)

# list of rings where a ring is simply the list of points it contains.
rings: list[list[tuple[float, float]]] = [
    [(300000, 1), (300000, 4000000), (700000, 4000000), (700000, 1), (300000, 1)]]
poly: Polygon = Polygon(rings, srs_id=32623)
```

### Select Features from GeoPackage

When selecting features from a GeoPackage feature class use SQL or use the
helper method `select`.  

For simple geometries (e.g. those without *Z* or *M*) this can be done via a 
basic `SELECT` statement or the `select` method.

```python
from fudgeo.geometry import Point
from fudgeo.geopkg import FeatureClass, GeoPackage

gpkg = GeoPackage(...)

# NOTE for fudgeo version v0.8.0 and above use helper method
fc = FeatureClass(geopackage=gpkg, name='point_fc')
cursor = fc.select(fields=('example_id',), include_geometry=True)
features: list[tuple[Point, int]] = cursor.fetchall()

# NOTE for fudgeo prior to v0.8.0
cursor = gpkg.connection.execute("""SELECT SHAPE, example_id FROM point_fc""")
features: list[tuple[Point, int]] = cursor.fetchall()
```

When using SQL with extended geometry types (e.g. those with *Z* and/or *M*) 
then ensure `SQLite` knows how to convert the geopackage stored geometry to a 
`fudgeo` geometry by including the converter, this is done like so:


```python
from fudgeo.geometry import LineStringM
from fudgeo.geopkg import FeatureClass, GeoPackage

gpkg = GeoPackage('../data/example.gpkg')
# NOTE for fudgeo version v0.8.0 and above use helper method
fc = FeatureClass(geopackage=gpkg, name='test')
cursor = fc.select(fields=('road_id',), include_geometry=True)
features: list[tuple[LineStringM, int]] = cursor.fetchall()

# NOTE for fudgeo prior to v0.8.0
cursor = gpkg.connection.execute(
    """SELECT SHAPE "[LineStringM]", road_id FROM test""")
features: list[tuple[LineStringM, int]] = cursor.fetchall()
```


## Extensions
### Spatial Index Extension
Spatial Index Extension implementation based on section [F.3. RTree Spatial Indexes](http://www.geopackage.org/spec131/index.html#extension_rtree)
of the **GeoPackage Encoding Standard**.

Spatial Indexes apply to individual feature classes.  A spatial index can be
added at create time or added on an existing feature class.

```python
from fudgeo.enumeration import SQLFieldType
from fudgeo.geopkg import FeatureClass, Field, GeoPackage, SpatialReferenceSystem


SRS_WKT: str = (
    'PROJCS["WGS_1984_UTM_Zone_23N",'
    'GEOGCS["GCS_WGS_1984",'
    'DATUM["D_WGS_1984",'
    'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    'PRIMEM["Greenwich",0.0],'
    'UNIT["Degree",0.0174532925199433]],'
    'PROJECTION["Transverse_Mercator"],'
    'PARAMETER["False_Easting",500000.0],'
    'PARAMETER["False_Northing",0.0],'
    'PARAMETER["Central_Meridian",-45.0],'
    'PARAMETER["Scale_Factor",0.9996],'
    'PARAMETER["Latitude_Of_Origin",0.0],'
    'UNIT["Meter",1.0]]')
SRS: SpatialReferenceSystem = SpatialReferenceSystem(
    name='WGS_1984_UTM_Zone_23N', organization='EPSG',
    org_coord_sys_id=32623, definition=SRS_WKT)
fields: tuple[Field, ...] = (
    Field('id', SQLFieldType.integer),
    Field('name', SQLFieldType.text, size=100))

gpkg: GeoPackage = GeoPackage.create('../temp/spatial_index.gpkg')
# add spatial index at create time
event: FeatureClass = gpkg.create_feature_class(
    'event_p', srs=SRS, fields=fields, spatial_index=True)
assert event.has_spatial_index is True

# add spatial index on an existing feature class / post create
signs: FeatureClass = gpkg.create_feature_class(
    'signs_p', srs=SRS, fields=fields)
# no spatial index
assert signs.has_spatial_index is False
signs.add_spatial_index()
# spatial index now present
assert signs.has_spatial_index is True
```

Refer to **SQLite** [documentation](https://www.sqlite.org/rtree.html#using_r_trees_effectively) 
on how to use these indexes for faster filtering / querying.  Also note
how to handle [round off error](https://www.sqlite.org/rtree.html#roundoff_error) 
when querying.


### Metadata Extension
Metadata Extension implementation based on [F.8. Metadata](http://www.geopackage.org/spec131/index.html#extension_metadata)
of the **GeoPackage Encoding Standard**.

The metadata extension is enabled at the GeoPackage level applying to all
tables and feature classes.  That said, not every table and feature class is 
required to have metadata.  

Metadata extension can be enabled at create time for a GeoPackage or 
can be enabled on an existing GeoPackage.

```python
from fudgeo.geopkg import GeoPackage

# enable metadata at create time
gpkg: GeoPackage = GeoPackage.create('../data/metadata.gpkg', enable_metadata=True)
assert gpkg.is_metadata_enabled is True

# enable metadata on an existing GeoPackage
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')
assert gpkg.is_metadata_enabled is False
gpkg.enable_metadata_extension()
assert gpkg.is_metadata_enabled is True
```

```python
from fudgeo.enumeration import MetadataScope
from fudgeo.extension.metadata import TableReference
from fudgeo.geopkg import GeoPackage

# open GeoPackage with metadata extension enabled
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')

# open a metadata xml file and add it to the GeoPackage
with open(...) as fin:
    id_ = gpkg.metadata.add_metadata(
        uri='https://www.isotc211.org/2005/gmd',
        scope=MetadataScope.dataset, metadata=fin.read()
    )
# apply the metadata to a feature class
reference = TableReference(table_name='road_l', file_id=id_)
gpkg.metadata.add_references(reference)
```

Support provided for the following reference types:
* `GeoPackageReference` -- used for `GeoPackage` level metadata
* `TableReference` -- used for `Table` and `FeatureClass` level metadata
* `ColumnReference` -- used for a **column** in a `Table` or `FeatureClass`
* `RowReference` -- used for a **row** in a `Table` or `FeatureClass`
* `RowColumnReference` -- used for **row / column** combination in a `Table` or `FeatureClass`


### Schema Extension
Schema Extension implementation based on [F.9. Schema](http://www.geopackage.org/spec131/index.html#extension_schema)
of the **GeoPackage Encoding Standard**.

The schema extension is enabled at the GeoPackage level and allows for extended
definitions on column names (e.g. name, title, description) and for constraints
to be defined for columns.  Constraints definitions are intended for 
applications usage and, while similar, are not the same as database constraints.

Schema extension can be enabled at create time for a GeoPackage or 
can be enabled on an existing GeoPackage.


```python
from fudgeo.geopkg import GeoPackage

# enable schema at create time
gpkg: GeoPackage = GeoPackage.create('../data/schema.gpkg', enable_schema=True)
assert gpkg.is_schema_enabled is True

# enable schema on an existing GeoPackage
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')
assert gpkg.is_schema_enabled is False
gpkg.enable_schema_extension()
assert gpkg.is_schema_enabled is True
```

```python
from fudgeo.extension.schema import (
    EnumerationConstraint, GlobConstraint, RangeConstraint)
from fudgeo.geopkg import GeoPackage

# open GeoPackage with schema extension enabled
gpkg: GeoPackage = GeoPackage('../data/example.gpkg')

# add constraints for use with column definitions
constraints = [
    EnumerationConstraint(name='odds', values=[1, 3, 5, 7, 9]),
    EnumerationConstraint(name='colors', values=['red', 'yellow', 'blue']),
    GlobConstraint(name='pin', pattern='[0-9][0-9][0-9][0-9]'),
    RangeConstraint(name='exertion', min_value=6, max_value=20),
    RangeConstraint(name='longitude', min_value=-180, max_value=180),
    RangeConstraint(name='latitude', min_value=90, max_value=90),
]
gpkg.schema.add_constraints(constraints)

# use constrains and set some additional details for column name
gpkg.schema.add_column_definition(
    table_name='road_l', column_name='begin_longitude', 
    name='Beginning Longitude for Road', title='Begin Longitude', 
    constraint_name='longitude')
gpkg.schema.add_column_definition(
    table_name='road_l', column_name='begin_latitude', 
    name='Beginning Latitude for Road', title='Begin Latitude', 
    constraint_name='latitude')
gpkg.schema.add_column_definition(
    table_name='road_l', column_name='end_longitude', 
    name='Ending Longitude for Road', title='End Longitude', 
    constraint_name='longitude')
gpkg.schema.add_column_definition(
    table_name='road_l', column_name='end_latitude', 
    name='Ending Latitude for Road', title='End Latitude', 
    constraint_name='latitude')
```

Support provided for the following constraint types:
* `EnumerationConstraint` -- restrict to one or more values
* `GlobConstraint` -- pattern match based constraint
* `RangeConstraint` -- value constrained within a range, optionally including the bounds


## License

[MIT](https://raw.githubusercontent.com/realiii/fudgeo/refs/heads/develop/LICENSE)

## Release History

### v0.8.2
* documentation edits
* copyright bump

### v0.8.1
* add support for creating feature classes with a geometry column name other than `SHAPE`
* ensure support for Python 3.13 and update documentation / configuration

### v0.8.0
* drop support for Python 3.7 and 3.8
* modernize type hinting
* add `select` method to `FeatureClass` and `Table` objects

### v0.7.2
* bump `user_version` to reflect adopted version 1.4.0 of OGC GeoPackage
* updated r-tree triggers based on changes made in 1.4.0

### v0.7.1
* ensure support for Python 3.12 and update documentation / configuration

### v0.7.0
* add support for **schema** extension
* add support for **metadata** extension
* add `__geo_interface__` to geometry classes
* introduce `bounding_box` property on `Envelope` class
* introduce `as_tuple` method on `Point` classes
* add `extension` sub-package, move `spatial` module into `extension`
* add `spatial_index_name` property on `FeatureClass`, returns the index table name
* enable enforcement of foreign key constraints
* reorganize code to handle OGR contents like an extension
* move protected functions from `geopkg` module into `util` module and rename
* add type hinting to `enumerations` module
* move `EnvelopeCode` into `enumerations`

### v0.6.0
* change `ogr_contents` default value to `False` (breaking change)
* add `spatial_index` option to `FeatureClass` creation, default to `False`
* add `add_spatial_index` method to `FeatureClass` for adding spatial index post creation
* add `has_spatial_index` property to `FeatureClass`
* add `count` property to `Table` and `FeatureClass`
* add `primary_key_field` property to `Table` and `FeatureClass`
* small speed-up to `Point` unpacking
* update `is_empty` to rely on internal attribute data type
* improvements to SQL statements to handle names that must be escaped
* bump `user_version` to reflect adopted version 1.3.1 of OGC GeoPackage
* add optional views for geometry columns and spatial references

### v0.5.2
* store empty state on the instance during geometry read
* introduce base classes for common capability and parametrize via class attributes
* add stub files to provide type hinting specialization 

### v0.5.1
* small performance improvements by reducing `bytes` concatenation and building up `bytearray`

### v0.5.0
* performance improvements for geometry reading (especially for geometries with large numbers of points / parts)
* performance improvements for geometry writing
* incorporated `numpy` and `bottleneck` as dependencies

### v0.4.2
* only unpack header and delay unpacking coordinates until needed
* write envelope to geometry header

### v0.4.1
* unpack envelope from header (when available)
* add `envelope` property to 2D, 3D, and 4D geometry
* derive envelope from underlying coordinates / geometries if not set from header

### v0.4.0
* add string representations to `GeoPackage`, `Table`, and `FeatureClass`
* allow optional creation of the `gpkg_ogr_contents`, defaults to True (create)
* split `geometry` module into a sub-package

### v0.3.10
* add `escaped_name` property to `BaseTable`, applies to `Table` and `FeatureClass`
* escape the name of input table / feature class during `create`

### v0.3.9
* quote reversal, doubles inside of singles for `escaped_name`

### v0.3.8
* add `fields` property to `BaseTable`, applies to `Table` and `FeatureClass`
* add `field_names` property to `BaseTable`, applies to `Table` and `FeatureClass`
* add `escaped_name` property to `Field` to return name valid for use in queries
* add type hinting to embedded sql statements and supporting values

### v0.3.7
* add `is_empty` property to geometries, improved handling for empty geometries
* update `user_version` to `10300`
* add handling for geometry headers with envelopes (skipping content)
* add type hinting to constants

### v0.3.6
* add `srs_id` (optional) to `SpatialReferenceSystem` instantiation, default to `org_coord_sys_id` if not specified

### v0.3.5
* store `coordinates` in attribute on 2D, 3D, and 4D geometry
* avoid creating points on instantiation of geometry
* expose `points` property to return point objects for 2D, 3D, and 4D geometry

### v0.3.4
* add `from_tuple` class methods to `Point`, `PointZ`, `PointM`, and `PointZM`

### v0.3.3
* catch possible exception when parsing microseconds from time
* add converter for `timestamp` to use same converter as `datetime`
* use lower case table names in queries

### v0.3.2
* include `PolygonM`, `PolygonZM`, `MultiPolygonM`, and `MultiPolygonZM` in geometry registration

### v0.3.1
* delay opening a `GeoPackage` connection until `connection` property is accessed 

### v0.3.0
* add support for `PolygonM`, `PolygonZM`, `MultiPolygonM`, and `MultiPolygonZM`
* add `geometry_column_name` and `geometry_type` properties to `FeatureClass`
* simplify query used by `has_z` and `has_m`

### v0.2.1
* improve `_convert_datetime` to handle different formats for timestamp (contributed by [@alexeygribko](https://github.com/alexeygribko))

### v0.2.0
* improve `_convert_datetime` to handle timezone
* add `DATETIME` tp `SQLFieldType`

### v0.1.2
* add option to overwrite feature classes and tables in `create_feature_class` and `create_table` methods 
* add option to overwrite in `create` method on `FeatureClass` and `Table` classes
* add `drop` method on `FeatureClass` and `Table` classes

### v0.1.1
* make compatible with Python 3.7 and up (update type hints, remove walrus)
* add support for OGR contents table (`gpkg_ogr_contents`) and triggers
* add `tables` and `feature_classes` properties to `GeoPackage` class
* include `application_id` and `user_version` in SQL definition
* fix timestamp format (was missing seconds)

### v0.1.0
* initial release, basic port of legacy `pygeopkg` package
