import re
from termcolor import colored

from .snapshot_file import from_canvas_file
from .snapshot_link import SnapshotLink
from ..utils import file_regex
from ..request_batcher import RequestBatcher


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
        request_batcher = RequestBatcher(course)
        accessed_files = []

        for _, module in (request_batcher.get_modules() or {}).items():
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
                    snapshot_file = from_canvas_file(
                        request_batcher.get_file(file_id))
                    accessed_files.append(file_id)
                    filename = f'{module_name}/{snapshot_file.name}'
                    self.add_to_snapshot(filename, snapshot_file)
                if self.with_link:
                    if item.type == 'ExternalUrl' or item.type == 'Page':
                        key = f'{module_name}/{item.title}.html'
                        value = SnapshotLink(
                            item.title, item.html_url, module_name)
                        self.add_to_snapshot(key, value)

        files = request_batcher.get_files()
        if files:
            unmoduled_files = 0
            for file_id, file in files.items():
                if file_id not in accessed_files:
                    snapshot_file = from_canvas_file(file)
                    filename = f'unmoduled/{snapshot_file.name}'
                    self.add_to_snapshot(filename, snapshot_file)
                    unmoduled_files += 1
            print(
                f'  {colored("Unmoduled files", "cyan")} ({unmoduled_files} items)')

        return self.snapshot

    def get_snapshot(self):
        return self.snapshot
