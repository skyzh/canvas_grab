from termcolor import colored

from .snapshot import Snapshot
from .snapshot_file import from_canvas_file
from .snapshot_link import SnapshotLink
from ..request_batcher import RequestBatcher
from canvasapi.exceptions import ResourceDoesNotExist


class CanvasFileSnapshot(Snapshot):
    """Takes a snapshot of files on Canvas, organized by file tab.

    ``CanvasFileSnapshot`` generates a snapshot of files on Canvas. In this snapshot mode,
    all files under "File" tab will be scanned as-is. Besides, it will add pages into
    the snapshot at `pages/xxx` path, if `with_link` option is enabled.
    """

    def __init__(self, course, with_link=False):
        """Create a file-based Canvas snapshot-taker

        Args:
            course (canvasapi.course.Course): The course object
            with_link (bool, optional): If true, pages will be included in snapshot. Defaults to False.
        """
        self.course = course
        self.with_link = with_link
        self.snapshot = {}

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

        Raises:
            ResourceDoesNotExist: this exception will be raised if file tab is not available

        Returns:
            dict: snapshot of Canvas in `SnapshotFile` or `SnapshotLink` type.
        """
        course = self.course
        request_batcher = RequestBatcher(course)

        files = request_batcher.get_files()
        if files is None:
            raise ResourceDoesNotExist("File tab is not supported.")

        folders = request_batcher.get_folders()

        for _, file in files.items():
            folder = folders[file.folder_id].full_name + "/"
            if folder.startswith("course files/"):
                folder = folder[len("course files/"):]
            snapshot_file = from_canvas_file(file)
            filename = f'{folder}{snapshot_file.name}'
            self.add_to_snapshot(filename, snapshot_file)

        print(f'  {len(files)} files in total')
        if self.with_link:
            pages = request_batcher.get_pages() or []
            for page in pages:
                key = f'pages/{page.title}.html'
                value = SnapshotLink(
                    page.title, page.html_url, "Page")
                self.add_to_snapshot(key, value)
            print(f'  {len(pages)} pages in total')

        return self.snapshot

    def get_snapshot(self):
        """Get the previously-taken snapshot

        Returns:
            dict: snapshot of Canvas
        """
        return self.snapshot
