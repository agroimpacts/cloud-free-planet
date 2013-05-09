## What is pprepair?

pprepair (planar partition repair) takes a set of polygons and ensures that they form a valid planar partition, made of valid polygons and having no gaps or overlaps. It can be used as a validator, telling of problems in individual polygons or in the planar partition, and also as an automatic repair tool, outputting a set of polygons that do form a valid planar partition. If you are only interested in repairing individual polygons, have a look at [prepair](https://github.com/tudelft-gist/prepair).

## What is a planar partition and why is it important to have valid planar partitions?

Planar partitions are subdivisions of the plane into polygons, and are frequently used in GIS to model various concepts like land use, geology, administrative subdivisions, natural features and cadastral parcels, among many others.

However, the polygons in a planar partition are often created separately, and thus cannot be expected to fit with each other exactly. Other times, these polygons are stored and modified separately, causing different errors and inconsistencies to be introduced. These come in the form of invalid polygons, gaps, overlaps and disconnected polygons.

When software that expects a planar partition received one that is not so, it can give erroneous results (in the best case), or fail to give a result at all, often without a clear explanation to the user.

## How does pprepair work?

In short, pprepair creates a constrained triangulation of the polygons, tags each triangle with the polygon that it belongs to, modifies the triangulation to ensure that only one tag is present in each, and reconstructs the polygons from the triangulation. Many more details are available in Ken Arroyo Ohori's MSc thesis [here](http://www.gdmc.nl/ken/files/10mscthesis.pdf).

## How do I use pprepair?

pprepair is a command-line program, which we provide as source code, together with makefiles for Mac and Linux. We plan on offering binaries (including for Windows) in the future.

To compile pprepair, you first need to install the free libraries [CGAL](http://www.cgal.org) and [OGR](http://www.gdal.org/ogr/). Afterwards run:

    $ make -f filename
    $ ./pprepair -i inputfile -o outputfile -fix

You can get all the options simply by running pprepair with no arguments
    $ ./pprepair

## Can I use pprepair in my organisation? What is the license of pprepair?

Following in CGAL's footsteps, pprepair is available under a dual license scheme, GPLv3 and commercial. If you choose to use pprepair under the free-of-charge GPLv3 license, you have to comply with its terms. If these are not suitable for you, you have to buy a commercial license.

The [GPLv3](http://www.gnu.org/copyleft/gpl.html) allows you to use, copy and modify the software freely. However, if you incorporate pprepair in your software, you must distribute the source code of your software, as well as any modifications made to pprepair, under the GPLv3 as well.

If you are interested in getting a commercial license for pprepair, please contact [Ken Arroyo Ohori](mailto:g.a.k.arroyoohori@tudelft.nl).

## Help! pprepair is crashing

This can be due to several reasons. 99% of the time it can be solved by:
  - If your data set has very large polygons, try passing the -bd flag
  - If your data set has points that are **very** close together, try uncommenting line 26 in definitions/CGALDefinitions.h (#define EXACT_CONSTRUCTIONS)

If your problem persists, please report it [here](https://github.com/tudelft-gist/pprepair/issues?state=open).
