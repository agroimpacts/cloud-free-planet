import math
from rasterio.coords import BoundingBox

class GeoUtils():
    # returns extent by centroid and cellgrid resolution
    @classmethod
    def define_extent(self, x, y, buffer = 0.005 / 2):
        xmin = x - buffer
        xmax = x + buffer
        ymin = y - buffer
        ymax = y + buffer

        return {
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax
        }

    @classmethod
    def BoundingBox_to_extent(self, bbox):
        return {
            "xmin": bbox.left,
            "xmax": bbox.right,
            "ymin": bbox.bottom,
            "ymax": bbox.top
        }

    @classmethod
    def extent_to_BoundingBox(self, extent):
        return BoundingBox(extent['xmin'], extent['ymin'], extent['xmax'], extent['ymax'])

    @classmethod
    def define_BoundingBox(self, x, y, buffer = 0.005 / 2):
        return self.extent_to_BoundingBox(self.define_extent(x, y, buffer))

    @classmethod
    def polygon_to_extent(self, polygon):
        # (minx, miny, maxx, maxy)
        # geom.bounds
        return {
            "xmin": polygon.bounds[0],
            "xmax": polygon.bounds[2],
            "ymin": polygon.bounds[1],
            "ymax": polygon.bounds[3]
        }

    @classmethod
    def extent_intersection(self, ext1, ext2):
        xminNew = ext1['xmin']
        yminNew = ext1['ymin']
        xmaxNew = ext1['xmax']
        ymaxNew = ext1['ymax']
        if(ext1['xmin'] < ext2['xmin']): 
            xminNew = ext2['xmin']
        if(ext1['ymin'] < ext2['ymin']):
            yminNew = ext2['ymin']
        if(ext1['xmax'] > ext2['xmax']):
            xmaxNew = ext2['xmax']
        if(ext1['ymax'] > ext2['ymax']):
            ymaxNew = ext2['ymax']

        return {
            "xmin": xminNew,
            "xmax": xmaxNew,
            "ymin": yminNew,
            "ymax": ymaxNew
        }

    @classmethod
    def define_aoi(self, x, y, buffer = 0.005 / 2):
        extent = self.define_extent(x, y, buffer)
        xmin = extent['xmin']
        xmax = extent['xmax']
        ymin = extent['ymin']
        ymax = extent['ymax']

        aoi = {
            'type': 'Polygon',
            'coordinates': [
                    [
                        [
                            xmin,
                            ymin
                        ],
                        [
                            xmax,
                            ymin
                        ],
                        [
                            xmax,
                            ymax
                        ],
                        [
                            xmin,
                            ymax
                        ],
                        [
                            xmin,
                            ymin
                        ]
                    ]
            ]
        }
        return aoi
