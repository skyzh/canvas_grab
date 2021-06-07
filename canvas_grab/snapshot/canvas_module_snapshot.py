import re
from termcolor import colored

from .snapshot import Snapshot
from .snapshot_file import from_canvas_file
from .snapshot_link import SnapshotLink
from ..utils import file_regex
from ..request_batcher import RequestBatcher


class CanvasModuleSnapshot(Snapshot):
    """Take a snapshot of files on Canvas, organized by module tab.

    ``CanvasModuleSnapshot`` generates a snapshot of Canvas by scanning the module tab.
    This is useful if 1) "File" tab is not available 2) Users want to organize files
    by module. If "File" tab is available, the snapshot-taker will first acquire all
    files in "File" tab, which batches the requests and greatly improves performance.
    If `with_link` is enabled, pages and external links will be included in snapshot.
    """

    def __init__(self, course, with_link=False):
        """Create a module-based Canvas snapshot-taker

        Args:
            course (canvasapi.course.Course): The course object
            with_link (bool, optional): If true, pages will be included in snapshot. Defaults to False.
        """
        self.course = course
        self.snapshot = {}
        self.with_link = with_link

    def add_to_snapshot(self, key, value):
        """Add a key-value pair into snapshot. If duplicated, this function will report error and ignore the pair.

        Args:
            key (str): key or path of the object
            value (any): content of the object
        """
        if key in self.snapshot:
            print(colored(
                f'  Duplicated file found: {key}, please download it using web browser.', 'yellow'))
            return
        self.snapshot[key] = value

    def take_snapshot(self):
        """Take a snapshot

         Returns:
             dict: snapshot of Canvas in `SnapshotFile` or `SnapshotLink` type.
        """
        for _ in self.yield_take_snapshot():
            pass
        return self.get_snapshot()

    def yield_take_snapshot(self):
        course = self.course
        request_batcher = RequestBatcher(course)
        accessed_files = []
        yield (0, '请稍候', '正在获取模块列表')

        modules = (request_batcher.get_modules() or {}).items()
        download_idx = 0
        for _, module in modules:
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

            yield (download_idx / len(modules) * 0.2, '正在获取模块列表', f'{module_name} (包含 {module_item_count} 个对象)')
            download_idx += 1

            for item in module.get_module_items():
                if item.type == 'File':
                    file_id = item.content_id
                    file = request_batcher.get_file(file_id)
                    file.display_name = re.sub(file_regex, '_', file.display_name)
                    snapshot_file = from_canvas_file(file)
                    accessed_files.append(file_id)
                    filename = f'{module_name}/{snapshot_file.name}'
                    self.add_to_snapshot(filename, snapshot_file)
                if self.with_link:
                    if item.type == 'ExternalUrl' or item.type == 'Page':
                        item.title = re.sub(file_regex, '_', item.title)
                        key = f'{module_name}/{item.title}.html'
                        value = SnapshotLink(
                            item.title, item.html_url, module_name)
                        self.add_to_snapshot(key, value)

        files = request_batcher.get_files()
        if files:
            unmoduled_files = 0
            for file_id, file in files.items():
                if file_id not in accessed_files:
                    file.display_name = re.sub(file_regex, '_', file.display_name)
                    snapshot_file = from_canvas_file(file)
                    filename = f'unmoduled/{snapshot_file.name}'
                    self.add_to_snapshot(filename, snapshot_file)
                    unmoduled_files += 1
            print(
                f'  {colored("Unmoduled files", "cyan")} ({unmoduled_files} items)')
            yield (0.2, '正在获取模块列表', f'还有 {unmoduled_files} 个不在模块中的文件')

    def get_snapshot(self):
        """Get the previously-taken snapshot

        Returns:
            dict: snapshot of Canvas
        """
        return self.snapshot
