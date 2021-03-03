from pathlib import Path
from .snapshot_file import SnapshotFile
from .snapshot import Snapshot


class OnDiskSnapshot(Snapshot):
    """Take an on-disk snapshot.

    This snapshot-taker will scan all files inside a folder. On Windows, backslash will be
    replaced by slash.
    """

    def __init__(self, base_path):
        """Create an on-disk snapshot-taker

        Args:
            base_path (str): Base path of the snapshot
        """
        self.base_path = base_path
        self.snapshot = {}

    def take_snapshot(self):
        """Take an on-disk snapshot

        Returns:
            dict: snapshot on disk. All objects are of type `SnapshotFile`.
        """
        base = Path(self.base_path)
        for item in base.rglob('*'):
            if item.is_file() and not item.name.startswith('.') and not item.name.endswith('.canvas_tmp'):
                stat = item.stat()
                self.snapshot[item.relative_to(base).as_posix()] = SnapshotFile(
                    item.name, stat.st_size, int(stat.st_mtime))
        return self.snapshot

    def get_snapshot(self):
        """Get the previously-taken snapshot

        Returns:
            dict: snapshot of Canvas
        """
        return self.snapshot
