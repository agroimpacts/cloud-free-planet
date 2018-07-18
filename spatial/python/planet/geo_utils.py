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
