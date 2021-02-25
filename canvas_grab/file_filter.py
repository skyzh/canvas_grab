import questionary
from canvas_grab.configurable import Configurable
from canvas_grab.utils import find_choice

FILE_GROUP = {
    'Video': [".mp4", ".avi", ".mkv"],
    'Audio': [".mp3", ".wav", ".aac", ".flac"],
    'Image': [".bmp", ".jpg", ".jpeg", ".png", ".gif"],
    'Document': [".ppt", ".pptx", ".doc", ".docx",
                 ".xls", ".xlsx", ".pdf", ".epub", ".caj"]
}


class FileFilter(Configurable):

    def __init__(self):
        self.allowed_group = ['Image', 'Document']
        self.allowed_extra = []

    def allowed_extensions(self):
        exts = []
        for group in self.allowed_group:
            exts.extend(FILE_GROUP[group])
        exts.extend(self.allowed_extra)
        return exts

    def filter_files(self, snapshot):
        if 'All' in self.allowed_group:
            return snapshot
        allowed = self.allowed_extensions()
        return {k: v for k, v in snapshot.items() if any(map(lambda ext: k.endswith(ext), allowed))}

    def to_config(self):
        return {
            'allowed_group': self.allowed_group,
            'allowed_extra': self.allowed_extra
        }

    def from_config(self, config):
        self.allowed_group = config['allowed_group']
        self.allowed_extra = config['allowed_extra']

    def interact(self):
        choices = []
        for key, group in FILE_GROUP.items():
            choices.append(questionary.Choice(
                f'{key} ({", ".join(group)})',
                key,
                checked=key in self.allowed_group
            ))
        choices.append(questionary.Choice(
            f'Allow all',
            'All',
            checked='All' in self.allowed_group
        ))
        choices.append(questionary.Choice(
            f'Custom',
            'custom',
            disabled='Please set extra allowed extensions in `allowed_extra` config'
        ))
        while True:
            self.allowed_group = questionary.checkbox(
                'Select allowed extensions',
                choices).unsafe_ask()
            if len(self.allowed_group) == 0:
                print('At least one extension group must be selected.')
            elif 'All' in self.allowed_group and len(self.allowed_group) != 1:
                print('Invalid choice.')
            else:
                break
