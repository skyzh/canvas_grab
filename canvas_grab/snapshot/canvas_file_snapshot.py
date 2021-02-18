from .snapshot_file import from_canvas_file
from canvasapi.exceptions import ResourceDoesNotExist


class CanvasFileSnapshot(object):
    def __init__(self, course):
        self.course = course
        self.snapshot = {}

    def take_snapshot(self):
        course = self.course

        if 'files' not in [tab.id for tab in course.get_tabs()]:
            raise ResourceDoesNotExist("File tab is not supported.")

        folders = {
            folder.id: folder.full_name
            for folder in course.get_folders()
        }

        for file in course.get_files():
            folder = folders[file.folder_id] + "/"
            if folder.startswith("course files/"):
                folder = folder[len("course files/"):]
            snapshot_file = from_canvas_file(file)
            filename = f'{folder}{snapshot_file.name}'
            if filename in self.snapshot:
                print(colored(
                    f'  Duplicated file found: {filename}, please download it using web browser.', 'yellow'))
                continue
            self.snapshot[filename] = snapshot_file

        return self.snapshot

    def get_snapshot(self):
        return self.snapshot
