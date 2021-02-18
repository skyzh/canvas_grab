from canvas_grab.configurable import Configurable
from PyInquirer import prompt


class OrganizeMode(Configurable):

    def __init__(self):
        self.mode = ''

    def to_config(self):
        return {
            'mode': self.mode
        }

    def from_config(self, config):
        self.mode = config['mode']

    def interact(self):
        questions = [
            {
                'type': 'list',
                'name': 'mode',
                'message': 'Select default file organization mode',
                'choices': [
                    {'name': 'By module (recommended)', 'value': 'module'},
                    {'name': 'As-is in file list', 'value': 'file'},
                    {'name': 'Custom',
                     'value': 'custom', 'disabled': 'not supported yet'},
                ]
            }
        ]
        answers = prompt(questions)
        self.from_config(answers)
