import os
import re
from enum import Enum

from canvasapi.canvas import Course, File
from canvasapi.exceptions import ResourceDoesNotExist, Unauthorized
from colorama import Back, Fore, Style

from config import Config
from course_files import CourseFiles
from utils import file_regex

__all__ = ['FileOrganizer']

file_manager = CourseFiles()


class FileOrganizer:
    class By(Enum):
        MODULE_WITH_FILE = "module_with_file"
        FILE = "file"
        MODULE = "module"

    def __init__(self, course: Course, by: By, config: Config):
        assert isinstance(by, self.By)

        self._course = course
        self._by = by
        self._config = config

    def get(self) -> (File, str):
        if self._by == self.By.MODULE_WITH_FILE:
            for (file, path) in self._by_module_with_file():
                yield (file, path)
        elif self._by == self.By.FILE:
            for (file, path) in self._by_file():
                yield (file, path)
        elif self._by == self.By.MODULE:
            for (file, path) in self._by_module():
                yield (file, path)

    def _by_file(self) -> (File, str):
        folders = {
            folder.id: folder.full_name
            for folder in self._course.get_folders()
        }

        for file in file_manager.get_files(self._course):
            folder = folders[file.folder_id] + "/"
            if folder.startswith("course files/"):
                folder = folder[len("course files/"):]

            yield (file, folder)

    def _by_module(self) -> (File, str):
        for module in self._course.get_modules():
            # NAME
            name = re.sub(file_regex, "_", module.name.replace("（", "(").replace("）", ")"))
            if self._config.CONSOLIDATE_MODULE_SPACE:
                name = " ".join(name.split())

            # IDX
            module_item_position = module.position - 1  # it begins with 1
            idx = str(module_item_position + self._config.MODULE_FOLDER_IDX_BEGIN_WITH)

            # FORMAT
            module_name = self._config.MODULE_FOLDER_TEMPLATE.format(NAME=name, IDX=idx)

            module_item_count = module.items_count
            print(f"    Module {Fore.CYAN}{module_name} ({module_item_count} items){Style.RESET_ALL}")

            for item in module.get_module_items():
                if item.type == "File":
                    yield file_manager.get_file(self._course, item.content_id), module_name
                elif item.type in ["Page", "Discussion", "Assignment"]:
                    _page_url = item.html_url
                elif item.type == "ExternalUrl":
                    _page_url = item.external_url
                elif item.type == "SubHeader":
                    pass
                else:
                    if self._config.VERBOSE_MODE:
                        print(f"    {Fore.YELLOW}Unsupported item type: {item.type}{Style.RESET_ALL}")

    def _by_module_with_file(self) -> (File, str):
        module_files_id = []

        try:
            for (file, path) in self._by_module():
                yield (file, path)
                module_files_id.append(file.id)
        except (ResourceDoesNotExist, Unauthorized):
            pass

        print(f"    {Fore.CYAN}File not in module{Style.RESET_ALL}")
        module_files_id = set(module_files_id)
        for (file, path) in self._by_file():
            if file.id not in module_files_id:
                yield (file, os.path.join("unmoduled", path))
