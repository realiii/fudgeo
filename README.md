# fudgeo

`fudgeo` removes the *fear uncertainty doubt* from using GeoPackages with 
`Python`. `fudgeo` is a lightweight package for creating OGC GeoPackages, Feature 
Classes, and Tables.  Easily read and write geometries and attributes to
Feature Classes and Tables using regular `Python` objects and `SQLite` syntax.

For details on OGC GeoPackages, please see the [OGC web page](http://www.geopackage.org/).


## Installation

`fudgeo` is available from the [Python Package Index](https://pypi.org/project/fudgeo/).


## Python Compatibility

The `fudgeo` library is compatible with Python 3.7 to 3.11.


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


### Create an Empty GeoPackage / Open GeoPackage

```python
from fudgeo.geopkg import GeoPackage

# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\data\example.gpkg')

# Opens an existing Geopackage (no validation)
gpkg = GeoPackage(r'c:\data\example.gpkg')
```

`GeoPackage`s are created with *three* default Spatial References defined
automatically, a pair of Spatial References to handle **undefined** cases,
and a **WGS 84** entry. 

The definition of the WGS84 entry is flexible - meaning that the 
*WKT for WGS84* can be setup per the users liking. As an example, 
use with Esri's ArcGIS means either using the *EPSG WKT* or the *ESRI WKT*. By
default the *ESRI WKT* is used - However, if *EPSG WKT* is desired, you
may provide a ``flavor`` parameter to the create method specifying EPSG.

```python
# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\temp\test.gpkg', flavor='EPSG')
```

### Create a Feature Class

Use the `create_feature_class` method of a GeoPackage to make
a new feature class.  Feature classes require a name and a Spatial 
Reference, the name must follow SQLite naming requirements.  Each
feature class is defined with `fid` and `SHAPE` fields, additional
fields can be defined during creation.

A Feature Class can be created with *Z* or *M* (or both) enabled. If 
either of these options are enabled, the geometry inserted into the 
Feature Class **must** include a value for the option specified.

```python
from typing import Tuple

from fudgeo.geopkg import FeatureClass, Field, GeoPackage, SpatialReferenceSystem
from fudgeo.enumeration import GeometryType, SQLFieldType

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
fields: Tuple[Field, ...] = (
    Field('road_id', SQLFieldType.integer),
    Field('name', SQLFieldType.text, size=100),
    Field('begin_easting', SQLFieldType.double),
    Field('begin_northing', SQLFieldType.double),
    Field('end_easting', SQLFieldType.double),
    Field('end_northing', SQLFieldType.double),
    Field('is_one_way', SQLFieldType.boolean))

gpkg: GeoPackage = GeoPackage.create(r'c:\temp\test.gpkg')
fc: FeatureClass = gpkg.create_feature_class(
    'road_l', srs=SRS, fields=fields, shape_type=GeometryType.linestring,
    z_enabled=False, m_enabled=True, overwrite=True, spatial_index=True)
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
from typing import List, Tuple

from fudgeo.geometry import LineStringM
from fudgeo.geopkg import GeoPackage

# Generate some random points and attributes
rows: List[Tuple[LineStringM, int, str, float, float, float, float, bool]] = []
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
gpkg: GeoPackage = GeoPackage(r'c:\data\example.gpkg')   
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
from fudgeo.geometry import Point, LineStringZM, Polygon

# Point in WGS 84
pt = Point(x=-119, y=34)

# Line with ZM Values for use with UTM Zone 23N (WGS 84)
coords = [(300000, 1, 10, 0), (300000, 4000000, 20, 1000),
          (700000, 4000000, 30, 2000), (700000, 1, 40, 3000)]
line = LineStringZM(coords, srs_id=32623)

# list of rings where a ring is simply the list of points it contains.
rings = [[(300000, 1), (300000, 4000000), (700000, 4000000),
          (700000, 1), (300000, 1)]]
poly = Polygon(rings, srs_id=32623)
```

### Select Features from GeoPackage (SQL)

When selecting features from a GeoPackage feature class use SQL.  For 
the most part (mainly simple geometries e.g. those without *Z* or *M*) this 
can be done via a basic `SELECT` statement like:

```python
gpkg = GeoPackage(...)
cursor = gpkg.connection.execute("""SELECT SHAPE, example_id FROM point_fc""")
features = cursor.fetchall()
```

This will return a list of tuples where each tuple contains a `Point`
object and an integer for `example_id` field.

When working with extended geometry types (those with *Z* and/or *M*) 
then the approach is to ensure `SQLite` knows how to convert the 
geopackage stored geometry to a `fudgeo` geometry, this is done like so:

```python
gpkg = GeoPackage(r'c:\data\example.gpkg')
cursor = gpkg.connection.execute(
    """SELECT SHAPE "[LineStringM]", road_id FROM test""")
features = cursor.fetchall()
```

or a little more general, accounting for extended geometry types and
possibility of the geometry column being something other tha `SHAPE`:

```python
from fudgeo.geopkg import FeatureClass

gpkg = GeoPackage(r'c:\data\example.gpkg')
fc = FeatureClass(geopackage=gpkg, name='road_l')
cursor = gpkg.connection.execute(f"""
    SELECT {fc.geometry_column_name} "[{fc.geometry_type}]", road_id 
    FROM {fc.escaped_name}""")
features = cursor.fetchall()
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Release History

### next release
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
