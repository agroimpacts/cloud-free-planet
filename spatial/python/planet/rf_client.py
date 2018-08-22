from rasterfoundry.api import API
from rasterfoundry.models import Project

import logging
import configparser
import ssl
import jwt
import uuid
import json

# https://docs.rasterfoundry.com/#/
class RFClient():
    def __init__(self, config):
        rf_config = config['rasterfoundry']
        imagery_config = config['imagery']
        self.api_key = rf_config['api_key']
        self.api_uri = rf_config['api_uri']
        # it's enabled only in s3 mode and with explicit enabled flag
        self.enabled = json.loads(rf_config['enabled'].lower()) and json.loads(imagery_config['local_mode'].lower())
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if self.enabled:
            self.api = API(refresh_token = self.api_key, host = self.api_uri)
            self.api_token_decoded = jwt.decode(self.api.api_token, algorithms = ['RS256'], verify = False)
            self.owner = self.api_token_decoded['sub']
        else:
            self.api = None
            self.api_token_decoded = None
            self.owner = None
        self.datasource = {"id": "e4d1b0a0-99ee-493d-8548-53df8e20d2aa"} # 4-band PlanetScope
        # https://assets.planet.com/docs/Planet_Combined_Imagery_Product_Specs_letter_screen.pdf
        self.bands = [
                {
                    "number": 0,
                    "name": "Blue",
                    "wavelength": [455, 515]
                },
                {
                    "number": 1,
                    "name": "Green",
                    "wavelength": [500, 590]
                },
                {
                    "number": 2,
                    "name": "Red",
                    "wavelength": [690, 670]
                },
                {
                    "number": 3,
                    "name": "Near Infrared",
                    "wavelength": [780, 860]
                }
        ]

    def create_project(self, project_name, visibility = 'PRIVATE', tileVisibility = 'PRIVATE'):
        return self.api.client.Imagery.post_projects(
            project = {
                "name": project_name,
                "description": "mapperAL generated project for TMS view",
                "visibility": visibility,
                "tileVisibility": tileVisibility,
                "owner": self.owner,
                "tags": ["Planet Scene mapperAL project"]
            }
        ).result()

    def create_scene(self, scene_name, uri, visibility = 'PRIVATE'):
        scene_uuid = str(uuid.uuid4())
        return self.api.client.Imagery.post_scenes(
            scene = {
                "id": scene_uuid,
                "owner": self.owner,
                "name": scene_name,
                "ingestLocation": uri,
                "visibility": visibility,
                "images": [{
                    "rawDataBytes": 0,
                    "visibility": visibility,
                    "filename": uri,
                    "sourceUri": uri,
                    "scene": scene_uuid,
                    "imageMetadata": {},
                    "resolutionMeters": 0,
                    "metadataFiles": [],
                    "bands": self.bands
                }],
                "thumbnails": [],
                "sceneMetadata": {},
                "metadataFiles": [],
                "sceneType": "COG",
                "filterFields": {},
                "tags": [
                    "Planet Scenes",
                    "GeoTIFF"
                ],
                "statusFields": {
                    "thumbnailStatus": "SUCCESS",
                    "boundaryStatus": "SUCCESS",
                    "ingestStatus": "INGESTED"
                },
                "datasource": self.datasource
            }
        ).result()

    def add_scenes_to_project(self, scenes, project):
        return self.api.client.Imagery.post_projects_uuid_scenes(
            uuid = project.id, 
            scenes = [scene.id for scene in scenes]
        ).future.result()

    def create_scene_project(self, scene_id, scene_uri):
        if self.enabled:
            new_project = self.create_project("Project {}".format(scene_id))
            new_scene = self.create_scene(scene_id, scene_uri)
            result = self.add_scenes_to_project([new_scene], new_project)
            return new_scene, Project(new_project, self.api)

    def create_tms_uri(self, scene_id, scene_uri):
        tms_uri = ''
        if self.enabled:
            try:
                new_scene, new_project = self.create_scene_project(scene_id, scene_uri)
                tms_uri = new_project.tms()
            except:
                self.logger.info("An error happend during RF TMS URI creation, scene_id: {}, scene_uri: {}".format(scene_id, scene_uri))
        return tms_uri

# example main function        
def main():
    # disable ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # read config
    config = configparser.ConfigParser()
    config.read('cfg/config.ini')

    rfclient = RFClient(config)
    
    scene_uri = "s3://activemapper/planet/analytic_sr/GS/20161011_073242_0e0e.tif"
    scene_id = "20161011_073242_0e0e"

    tms_uri = rfclient.create_tms_uri(scene_id, scene_uri)

    print(tms_uri)

if __name__ == "__main__":
    main()
