import re
from termcolor import colored

from .snapshot_file import from_canvas_file
from .snapshot_link import SnapshotLink
from canvas_grab.utils import file_regex


class CanvasModuleSnapshot(object):
    def __init__(self, course, with_link=False):
        self.course = course
        self.snapshot = {}
        self.with_link = with_link

    def add_to_snapshot(self, key, value):
        if key in self.snapshot:
            print(colored(
                f'  Duplicated file found: {key}, please download it using web browser.', 'yellow'))
            return
        self.snapshot[key] = value

    def take_snapshot(self):
        course = self.course

        folders = {
            folder.id: folder.full_name
            for folder in course.get_folders()
        }

        files_cache = {}
        if 'files' in [tab.id for tab in course.get_tabs()]:
            for file in course.get_files():
                files_cache[file.id] = file

        for module in course.get_modules():
            # replace invalid characters in name
            name = re.sub(file_regex, "_", module.name)
            # consolidate spaces
            name = " ".join(name.split())

            # get module index
            idx = str(module.position)

            # folder format
            module_name = f'{idx} {name}'

            module_item_count = module.items_count
            print(
                f'  Module {colored(module_name, "cyan")} ({module_item_count} items)')

            for item in module.get_module_items():
                if item.type == 'File':
                    file_id = item.content_id
                    if file_id in files_cache:
                        snapshot_file = from_canvas_file(files_cache[file_id])
                        del files_cache[file_id]
                    else:
                        snapshot_file = from_canvas_file(
                            course.get_file(file_id))
                    filename = f'{module_name}/{snapshot_file.name}'
                    self.add_to_snapshot(filename, snapshot_file)
                if self.with_link:
                    if item.type == 'ExternalUrl' or item.type == 'Page':
                        key = f'{module_name}/{item.title}.html'
                        value = SnapshotLink(
                            item.title, item.html_url, module_name)
                        self.add_to_snapshot(key, value)

        if len(files_cache) > 0:
            print(
                f'  {colored("Unmoduled files", "cyan")} ({len(files_cache)} items)')

        for _, file in files_cache.items():
            snapshot_file = from_canvas_file(file)
            filename = f'unmoduled/{snapshot_file.name}'
            self.add_to_snapshot(filename, snapshot_file)

        return self.snapshot

    def get_snapshot(self):
        return self.snapshot
