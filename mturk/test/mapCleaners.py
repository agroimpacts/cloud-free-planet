# functions for cleaning mapping polygons
import os, re, subprocess, glob
from osgeo import ogr
from MTurkMappingAfrica import MTurkMappingAfrica

def polyPrepair(shape_name, table):
    #mtma = MTurkMappingAfrica()
    shape_name_out = shape_name + ".shp"
    #print shape_name, shape_name_out, os.getcwd()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(shape_name_out):
        driver.DeleteDataSource(shape_name_out)
        
    ds = driver.CreateDataSource(shape_name_out)
    layer = ds.CreateLayer(shape_name, geom_type=ogr.wkbPolygon)
    layer_defn = layer.GetLayerDefn()
    fd = ogr.FieldDefn('name', ogr.OFTString)
    layer.CreateField(fd)

    for i in range(0, len(table)):
        name = table[i][0]
        wkt = re.sub("^SRID=*.*;", "", table[i][1])
        #wktfix = subprocess.Popen([mtma.projectRoot + "/prepair/prepair", "--wkt", wkt, "--minarea", "0.000000001"],
        #    stdout=subprocess.PIPE).communicate()[0]
        wktfix = wktPrepair(wkt)
        geom = ogr.CreateGeometryFromWkt(wktfix)
        featureIndex = i
        feature = ogr.Feature(layer_defn)
        feature.SetGeometry(geom)
        feature.SetFID(featureIndex)
        feature.SetField('name', name)
        layer.CreateFeature(feature)

    feature.Destroy()
    ds.Destroy()

def wktPrepair(wkt):
    mtma = MTurkMappingAfrica()
    wktfix = subprocess.Popen([mtma.projectRoot + "/prepair/prepair", "--wkt", wkt, "--minarea", "0.000000001"],
        stdout=subprocess.PIPE).communicate()[0]
    return(wktfix)

def polyPPrepair(shape_name_in, shape_name_out):
    mtma = MTurkMappingAfrica()
    shape_in = shape_name_in + ".shp"
    shape_out = shape_name_out + ".shp"
    polyfix = subprocess.Popen([mtma.projectRoot + "/pprepair/pprepair", "-i", shape_in, "-o", shape_out, "-fix"], 
        stdout=subprocess.PIPE).communicate()

def shapeReader(shape_name_in):
    shape_in = shape_name_in + ".shp"
    polys = ogr.Open(shape_in)
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

def shapeWriter(poly_hash, shape_name_out):
    shape_name = shape_name_out + ".shp"
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(shape_name):
        driver.DeleteDataSource(shape_name)

    ds = driver.CreateDataSource(shape_name)
    layer = ds.CreateLayer(shape_name, geom_type=ogr.wkbPolygon)
    layer_defn = layer.GetLayerDefn()
    fd = ogr.FieldDefn('name', ogr.OFTString)
    layer.CreateField(fd)
    fids = 0
    for name in poly_hash:
        fids += 1
        geom = ogr.CreateGeometryFromWkt(poly_hash[name][0])
        featureIndex = fids
        feature = ogr.Feature(layer_defn)
        feature.SetGeometry(geom)
        feature.SetFID(featureIndex)
        feature.SetField('name', name)
        layer.CreateFeature(feature)

    feature.Destroy()
    ds.Destroy()

def cleanPolyHash(poly_hash):
    cleanHash = {} 
    for name in poly_hash:
        if len(poly_hash[name]) == 1:
            wktfix = wktPrepair(poly_hash[name][0])
            cleanHash[name] = [wktfix]
        else:
            poly1 = ogr.CreateGeometryFromWkt(poly_hash[name][0])
            for polygon in poly_hash[name][1:]:
                geom = ogr.CreateGeometryFromWkt(polygon)
                union = poly1.Union(geom)                
            unionwkt = union.ExportToWkt()
            unionwkt_fix = wktPrepair(unionwkt)
            cleanHash[name] = [unionwkt_fix] 
            
    return(cleanHash)

def tempShapeDel(assignment_id):
    tempfilelist = glob.glob("*" + assignment_id + "*")
    try:
        for f in tempfilelist:
            print(f)
            os.remove(f)
    except Exception,e:
        print e


