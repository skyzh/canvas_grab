import questionary
from canvas_grab.configurable import Configurable
from canvas_grab.utils import find_choice


class OrganizeMode(Configurable):

    def __init__(self):
        self.mode = 'module'
        self.delete_file = False

    def to_config(self):
        return {
            'mode': self.mode,
            'delete_file': self.delete_file
        }

    def from_config(self, config):
        self.mode = config['mode']
        self.delete_file = config['delete_file']

    def interact(self):
        choices = [
            questionary.Choice('By module (recommended)', 'module'),
            questionary.Choice('As-is in file list', 'file'),
            questionary.Choice('Custom', 'custom',
                               disabled='not supported yet')
        ]
        self.mode = questionary.select(
            'Select default file organization mode',
            choices,
            default=find_choice(choices, self.mode)
        ).unsafe_ask()
        choices = [
            questionary.Choice(
                "Delete local files if they disappears on Canvas", True),
            questionary.Choice("Always keep local files", False)
        ]
        self.delete_file = questionary.select(
            'How to handle deleted files on Canvas',
            choices,
            default=find_choice(choices, self.delete_file)
        ).unsafe_ask()
