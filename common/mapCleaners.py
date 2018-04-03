# functions for cleaning mapping polygons
import os, re, subprocess, glob
from osgeo import ogr
from osgeo import gdal  # gdal2 change
from datetime import datetime
from MappingCommon import MappingCommon

def polyPrepair(mapc, shape_name, table):
    """Runs prepair on individual polygons extracted from data.base and writes
    them to shape file"""
    shape_name_out = shape_name + ".shp"
    #print shape_name, shape_name_out, os.getcwd()
    # driver = ogr.GetDriverByName('ESRI Shapefile')
    driver = gdal.GetDriverByName('ESRI Shapefile')  # gdal 2 change
    if os.path.exists(shape_name_out):
        driver.Delete(shape_name_out)   # gdal 2 change
        
    ds = driver.Create(shape_name_out, 0, 0, 0)  # gdal2 change
    layer = ds.CreateLayer(shape_name, geom_type = ogr.wkbPolygon)
    layer_defn = layer.GetLayerDefn()
    # fd = ogr.FieldDefn('name', ogr.OFTString)
    fd = gdal.FieldDefn('name', gdal.OFTString)
    layer.CreateField(fd)

    for i in range(0, len(table)):
        name = table[i][0]
        wkt = re.sub("^SRID=*.*;", "", table[i][1])
        wktfix = wktPrepair(mapc, wkt)
        # geom = ogr.CreateGeometryFromWkt(wktfix)
        geom = gdal.CreateGeometryFromWkt(wktfix)
        featureIndex = i
        # feature = ogr.Feature(layer_defn)
        feature = gdal.Feature(layer_defn)
        feature.SetGeometry(geom)
        feature.SetFID(featureIndex)
        feature.SetField('name', name)
        layer.CreateFeature(feature)
        feature.Destroy()
    
    ds = None  # gdal2 change

def wktPrepair(mapc, wkt):
    wktfix = subprocess.Popen([mapc.projectRoot + "/prepair/prepair", "--wkt", 
                               wkt, "--minarea", "0.00000000000000000001"],
                              stdout = subprocess.PIPE).communicate()[0]
    return(wktfix)

def polyPPrepair(mapc, shape_name_in, shape_name_out):
    shape_in = shape_name_in + ".shp"
    shape_out = shape_name_out + ".shp"
    polyfix = subprocess.Popen([mapc.projectRoot + "/pprepair/pprepair", "-i",
                                shape_in, "-o", shape_out, "-fix"], 
                               stdout = subprocess.PIPE).communicate()[0]

def shapeReader(mapc, shape_name_in):
    """Reads shape file into polygon hash table"""
    logFilePath = mapc.projectRoot + "/log"
    shape_in = shape_name_in + ".shp"
    now = str(datetime.today())
    # polys = ogr.Open(shape_in)
    polys = gdal.Open(shape_in)
    if polys is None:
        k = open(logFilePath + "/miscellaneous.log", "a")
        k.write("mapFix: OGR couldn't open '%s' at '%s'\n" % (shape_in, now))
        k.close()
        raise Exception("OGR can't open '%s'!" % shape_in)
    elements = polys.GetLayer()
    outHash = {}

    for element in elements:
        name = element.GetField("name")
        geom = element.GetGeometryRef()
        area = geom.GetArea()
        wkt = geom.ExportToWkt()
        if name not in outHash:
            outHash[name] = [wkt]
        else: 
            outHash[name].append(wkt)
    return(outHash)

def shapeWriter(mapc, poly_hash, shape_name_out):
    """Writes out a polygon hash table to a shapefile"""
    shape_name = shape_name_out + ".shp"
    driver = gdal.GetDriverByName('ESRI Shapefile')  # gdal2 change
    if os.path.exists(shape_name):
        driver.Delete(shape_name)  # gdal2 change

    # ds = driver.Create(shape_name)
    ds = driver.Create(shape_name, 0, 0, 0)  # gdal2 change
    layer = ds.CreateLayer(shape_name, geom_type = ogr.wkbPolygon)
    layer_defn = layer.GetLayerDefn()
    # fd = ogr.FieldDefn('name', ogr.OFTString)
    fd = gdal.FieldDefn('name', gdal.OFTString)
    layer.CreateField(fd)
    fids = 0
    for name in poly_hash:
        fids += 1
        geom = gdal.CreateGeometryFromWkt(poly_hash[name][0])
        featureIndex = fids
        feature = gdal.Feature(layer_defn)
        feature.SetGeometry(geom)
        feature.SetFID(featureIndex)
        feature.SetField('name', name)
        layer.CreateFeature(feature)
        feature.Destroy()

    ds = None  # gdal2 change

def cleanPolyHash(mapc, poly_hash):
    """Creates a clean polygon hash table, unioning any polygons having the 
    same name."""
    cleanHash = {} 
    for name in poly_hash:
        if len(poly_hash[name]) == 1:  # if only 1 polygon of the name 
            wktfix = wktPrepair(mapc, poly_hash[name][0])
            cleanHash[name] = [wktfix]
        else:  # if >1 polygon w/that name (b/c split earlier by prepair)
            poly1 = ogr.CreateGeometryFromWkt(poly_hash[name][0])
            for polygon in poly_hash[name][1:]:
                geom = gdal.CreateGeometryFromWkt(polygon)
                union = poly1.Union(geom)                
            unionwkt = union.ExportToWkt()
            unionwkt_fix = wktPrepair(mapc, unionwkt)
            cleanHash[name] = [unionwkt_fix] 
            
    return(cleanHash)

def tempShapeDel(mapc, path, nameroot):
    """Deletes temporary shapes having given common name root."""
    tempfilelist = glob.glob(path + "*" + nameroot + "*")
    try:
        for f in tempfilelist:
            #print(f)
            os.remove(f)
    except Exception, e:
        print e


