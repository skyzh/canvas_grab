from canvas_grab.configurable import Configurable
from PyInquirer import prompt
from canvasapi import Canvas


class Endpoint(Configurable):

    def __init__(self):
        self.endpoint = ''
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
        questions = [
            {
                'type': 'input',
                'name': 'endpoint',
                'message': 'Canvas API endpoint',
                'default': 'https://oc.sjtu.edu.cn'
            },
            {
                'type': 'input',
                'name': 'api_key',
                'message': 'API Key'
            }
        ]
        answers = prompt(questions)
        self.from_config(answers)

    def login(self):
        return Canvas(self.endpoint, self.api_key)
