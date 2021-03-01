from pathlib import Path
from .snapshot_file import SnapshotFile
from .snapshot import Snapshot


class OnDiskSnapshot(Snapshot):
    def __init__(self, base_path):
        self.base_path = base_path
        self.snapshot = {}

    def take_snapshot(self):
        base = Path(self.base_path)
        for item in base.rglob('*'):
            if item.is_file() and not item.name.startswith('.') and not item.name.endswith('.canvas_tmp'):
                stat = item.stat()
                self.snapshot[item.relative_to(base).as_posix()] = SnapshotFile(
                    item.name, stat.st_size, int(stat.st_mtime))
        return self.snapshot

    def get_snapshot(self):
        return self.snapshot
