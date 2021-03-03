from dataclasses import dataclass


@dataclass
class SnapshotFile:
    """A snapshot of file, which only includes metadata.
    """
    name: str
    size: int
    modified_at: int
    created_at: int = 0
    url: str = ''
    file_id: int = 0


def from_canvas_file(file):
    """Create a `SnapshotFile` from canvasapi file object

    Args:
        file (canvasapi.file.File): File object to use

    Returns:
        SnapshotFile: the metadata of file, or so-called `SnapshotFile`.
    """
    return SnapshotFile(file.display_name, file.size, int(file.modified_at_date.timestamp()), int(file.created_at_date.timestamp()), file.url, file.id)
