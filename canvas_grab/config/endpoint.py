from ..configurable import Configurable, Interactable
from canvasapi import Canvas
import questionary


class Endpoint(Configurable, Interactable):
    """Endpoint stores Canvas LMS endpoint and API key.
    """

    def __init__(self):
        self.endpoint = 'https://oc.sjtu.edu.cn'
        self.api_key = ''

    def to_config(self):
        return {
            'endpoint': self.endpoint,
            'api_key': self.api_key
        }

    def from_config(self, config):
        self.endpoint = config['endpoint']
        self.api_key = config['api_key']

    def interact(self):
        self.endpoint = questionary.text(
            'Canvas API endpoint', default=self.endpoint).unsafe_ask()
        self.api_key = questionary.text(
            'API Key', default=self.api_key, instruction="Please visit profile page of Canvas LMS to generate an access token").unsafe_ask()

    def login(self):
        return Canvas(self.endpoint, self.api_key)
