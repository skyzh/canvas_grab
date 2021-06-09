import questionary
from ..configurable import Configurable, Interactable
from ..utils import find_choice
from ..snapshot import CanvasFileSnapshot, CanvasModuleSnapshot
from ..error import CanvasGrabCliError


class OrganizeMode(Configurable, Interactable):
    """OrganizeMode decides how data are stored on disk.

    Currently, there are four modes: module (with link) and
    as-is (with link).
    """

    def __init__(self):
        self.mode = 'module'
        self.delete_file = False

    def get_snapshots(self, course):
        if self.mode == 'module_link':
            canvas_snapshot_module = CanvasModuleSnapshot(
                course, True)
        else:
            canvas_snapshot_module = CanvasModuleSnapshot(
                course)

        if self.mode == 'file_link':
            canvas_snapshot_file = CanvasFileSnapshot(course, True)
        else:
            canvas_snapshot_file = CanvasFileSnapshot(course)

        if self.mode == 'module' or self.mode == 'module_link':
            canvas_snapshots = [canvas_snapshot_module, canvas_snapshot_file]
        elif self.mode == 'file' or self.mode == 'file_link':
            canvas_snapshots = [canvas_snapshot_file, canvas_snapshot_module]
        else:
            raise CanvasGrabCliError(f"Unsupported organize mode {self.mode}")

        return self.mode, canvas_snapshots

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
            questionary.Choice(
                'Organize by module, only download files', 'module'),
            questionary.Choice(
                'Organize by module, download files, links and pages', 'module_link'),
            questionary.Choice(
                'As-is in file list', 'file'),
            questionary.Choice(
                'As-is in file list, plus pages', 'file_link'),
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
