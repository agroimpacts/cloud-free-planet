## What is prepair?

prepair -- pronounce 'pee-repair' as in 'polygon repair' -- permits us to easily repair "broken" GIS polygons, and that according to the international standards ISO 19107 (Geographic information -- Spatial schema). In brief, given a polygon, it *automatically* repairs it and returns back a valid polygon (actually a MultiPolygon if the input represents more than one polygon). Note that this project is only concerned with single polygons, if you're interested in validating how different polygons interact with each others (to be precise: to check if they form a planar partition) have a look at our other project [pprepair](https://github.com/tudelft-gist/pprepair).

Automated repair methods can be considered as interpreting ambiguous or ill-defined polygons and giving a coherent and clearly defined output. Examples of errors are: polygon has a dangling edge; polygon is not closed; polygon self-intersects; an inner ring of the polygon is located outside the outer ring; etc.

prepair performs more or less the same as the new PostGIS 2.0's function [ST_MakeValid()](http://***REMOVED***.org/documentation/manual-svn/ST_MakeValid.html), but is faster, scales better to massive polygons, and predicting its behaviour is simple (so one can guess how her polygons will be repaired).
We have implemented two repair paradigms: an extension of the [odd-even algorithm](https://en.wikipedia.org/wiki/Even-odd_rule) to handle GIS polygons containing inner rings and degeneracies; and one where we follow a *set difference* rule for the rings.

prepair is based on a constrained triangulation ([CGAL](http://www.cgal.org) is used) and [OGR](http://www.gdal.org/ogr/) is used to read/write WKT.

It is available under a dual license scheme: [GPLv3](http://www.gnu.org/copyleft/gpl.html) and commercial. If you are interested in a commercial license, please contact [Ken Arroyo Ohori](mailto:g.a.k.arroyoohori@tudelft.nl).

## Details
Details of how we automatically repair broken polygons, and what results you can expect, are available in our Agile 2012 [paper](http://www.gdmc.nl/ledoux/pdfs/_12agile.pdf) and the accompanying [slides](http://homepage.tudelft.nl/23t4p/pdfs/_12agile_pres.pdf).

## How to compile?

prepair is provided as source code, which is very easy to compile it on Linux and Mac. We plan on offering binaries (including for Windows) in the future.

To compile it, you first need to install the following three (free) libraries:

1. [CGAL](http://www.cgal.org)
2. [OGR](http://www.gdal.org/ogr/)
3. [CMake](http://www.cmake.org) 

Afterwards run:

    $ cmake .
    $ make

## It's a command-line program only

A [WKT](http://en.wikipedia.org/wiki/Well-known_text) or an OGR dataset (shapefile, geojson or GML for instance) is read as input, and a WKT or a shapefile (a MultiPolygon) is given as output:

    $ ./prepair --wkt 'POLYGON((0 0, 0 10, 10 0, 10 10, 0 0))'  
    MULTIPOLYGON (((0 10,0 0,5 5,0 10)),((5 5,10 0,10 10,5 5)))  
    
    $ ./prepair --ogr myfile.shp
    MULTIPOLYGON (((0 10,0 0,5 5,0 10)),((5 5,10 0,10 10,5 5)))

    $ ./prepair --shpOut --ogr data/CLC2006_180927.geojson 
    Creating out.shp
    
[Snap rounding](http://www.cgal.org/Manual/latest/doc_html/cgal_manual/Snap_rounding_2/Chapter_main.html) of the input segments can be performed:

    $ /prepair --isr 2 --wkt "POLYGON((0 0, 10 0, 15 5, 10 0, 10 10, 0 10, 0 0))"
    MULTIPOLYGON (((11 1,11 11,1 11,1 1,11 1)))
    
It's possible to remove small (sliver) polygons in the output by giving the smallest area allowed:

    $ ./prepair --wkt 'POLYGON((0 0, 10 0, 10 11, 11 10, 0 10))' 
    MULTIPOLYGON (((10 0,10 10,0 10,0 0,10 0)),((11 10,10 11,10 10,11 10)))

    $ ./prepair --wkt 'POLYGON((0 0, 10 0, 10 11, 11 10, 0 10))' --minarea 1
    Removing polygons smaller than 1 unit^2.
    MULTIPOLYGON (((10 0,10 10,0 10,0 0,10 0)))

## Examples of invalid input you can try

The folder 'data' contains examples of relatively big invalid polygons. These are from the [Corine Land Cover 2006 dataset.](http://sia.eionet.europa.eu/CLC2006)

A 'bowtie' polygon: 
    
    POLYGON((0 0, 0 10, 10 0, 10 10, 0 0))

Square with wrong orientation: 
    
    POLYGON((0 0, 0 10, 10 10, 10 0, 0 0))

Inner ring with one edge sharing part of an edge of the outer ring:

    POLYGON((0 0, 10 0, 10 10, 0 10, 0 0),(5 2,5 7,10 7, 10 2, 5 2))

Dangling edge:

    POLYGON((0 0, 10 0, 15 5, 10 0, 10 10, 0 10, 0 0))

Outer ring not closed:

    POLYGON((0 0, 10 0, 10 10, 0 10))

Two adjacent inner rings:

    POLYGON((0 0, 10 0, 10 10, 0 10, 0 0), (1 1, 1 8, 3 8, 3 1, 1 1), (3 1, 3 8, 5 8, 5 1, 3 1))

Polygon with an inner ring inside another inner ring:

    POLYGON((0 0, 10 0, 10 10, 0 10, 0 0), (2 8, 5 8, 5 2, 2 2, 2 8), (3 3, 4 3, 3 4, 3 3))

