# fudgeo

`fudgeo` removes the *fear uncertainty doubt* from using GeoPackages with 
Python. `fudgeo` is a simple package for creating GeoPackages, Feature 
Classes, Tables, and geometries (read and write).

Inspired by elements of [**pygeopkg**](https://github.com/realiii/pygeopkg).

For more details on OGC GeoPackages, please see the [OGC web page](http://www.geopackage.org/).


## Installation

`fudgeo` is available from the [Python Package Index](https://pypi.org/project/fudgeo/).


### Python Compatibility

The `fudgeo` library is compatible with Python 3.9.


## Usage

`fudgeo` can be used to: 
* Create a new empty GeoPackage or Open an existing GeoPackage.
* Create new Feature Classes and Tables
* Insert feature (geometry and attributes) into a Feature Class.
* Insert rows into a Table (in the normal SQLite way)


### Create an Empty GeoPackage / Open GeoPackage

```python
from fudgeo.geopkg import GeoPackage

# Creates an empty geopackage
gpkg = GeoPackage.create(r'c:\data\example.gpkg')

# Opens an existing Geopackage (no validation)
gpkg = GeoPackage(r'c:\data\example.gpkg')
```

Geopackages are created with *three* default Spatial References defined
automatically, a pair of Spatial References to handle undefined cases,
and a WGS 84 entry. 

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
from fudgeo.geopkg import GeoPackage, SpatialReferenceSystem, Field
from fudgeo.enumeration import GeometryType, SQLFieldType

gpkg = GeoPackage.create(r'c:\temp\test.gpkg')

srs_wkt = (
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

srs = SpatialReferenceSystem(
    'WGS_1984_UTM_Zone_23N', 'EPSG', 32623, srs_wkt)
fields = (
    Field('heart_rate', SQLFieldType.integer),
    Field('power', SQLFieldType.double),
    Field('comment', SQLFieldType.text, 100),
    Field('is_valid', SQLFieldType.boolean))

fc = gpkg.create_feature_class(
    'test', srs, fields=fields, shape_type=GeometryType.point)
```

Read more about spatial references in GeoPackages [here](https://github.com/realiii/pygeopkg/blob/master/README.md#about-spatial-references-for-geopackages)


### Insert Features into a Feature Class (SQL)

Features can be inserted into a Feature Class using SQL.

This example shows the creation of a random point Feature Class and
builds upon the code from previous examples. Note that the create Feature Class
portion of the code is omitted...

```python
from random import choice, randint
from string import ascii_uppercase, digits
from fudgeo.geometry import Point
from fudgeo.geopkg import GeoPackage

# NOTE Builds from previous examples 
gpkg = GeoPackage(r'c:\data\example.gpkg')

# Generate some random points and attributes
rows = []
for i in range(10000):
    rand_str = ''.join(choice(ascii_uppercase + digits) for _ in range(10))
    rand_int = randint(0, 1000)
    rand_x = randint(300000, 600000)
    rand_y = randint(1, 100000)
    rows.append((Point(x=rand_x, y=rand_y, srs_id=32623), rand_int, rand_str))

with gpkg.connection as conn:
    conn.executemany(
        """INSERT INTO test (SHAPE, heart_rate, comment) 
           VALUES (?, ?, ?)""", rows)
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
the most part (mainly simple geometries) this can be done via a basic
select statement like:

```python
gpkg = GeoPackage(r'c:\data\example.gpkg')
cursor = gpkg.connection.execute(
    """SELECT SHAPE, heart_rate FROM test""")
features = cursor.fetchall()
```

This will return a list of tuples where each tuple contains a `Point`
object and an integer (heart rate).

When working with extended geometry types (those with *Z* and/or *M*) 
then the approach is to ensure SQLite knows how to convert the 
geopackage stored geometry to a `fudgeo` geometry, this is done like
so (pretending here that we created `test` table as a point geometry
with z enabled):

```python
gpkg = GeoPackage(r'c:\data\example.gpkg')
cursor = gpkg.connection.execute(
    """SELECT SHAPE "[PointZ]", heart_rate FROM test""")
features = cursor.fetchall()
```


## License

[MIT](https://choosealicense.com/licenses/mit/)

