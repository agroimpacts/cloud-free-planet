from rasterfoundry.api import API
import logging

class RFClient():
    def __init__(self, config):
        rf_config = config['rasterfoundry']
        self.api_key = rf_config['api_key']
        self.api_uri = rf_config['api_uri']
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.api = API(refresh_token = self.api_key, host = self.api_uri)

    def create_project(self, project_name):
        api = self.api
        # api.