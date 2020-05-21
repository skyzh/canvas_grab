import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

__all__ = ['Checkpoint', 'CheckpointItem']


@dataclass
class CheckpointItem:
    updated_at: datetime
    id: str
    session: str


class CheckpointItemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CheckpointItem):
            return obj.__dict__
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


class Checkpoint:
    _path: Path
    _checkpoint = {}  # {str: CheckpointItem}

    def __init__(self, checkpoint_file):
        self._path = Path(checkpoint_file)
        os.makedirs(Path(self._path).parent, exist_ok=True)

    def get(self, key: str) -> CheckpointItem:
        return self._checkpoint.get(key)

    def __getitem__(self, key: str) -> CheckpointItem:
        return self._checkpoint[key]

    def __setitem__(self, key: str, value: CheckpointItem):
        self._checkpoint[key] = value

    def __contains__(self, key: str):
        return key in self._checkpoint

    def load(self):
        with open(self._path, 'r') as fp:
            self._checkpoint = json.load(fp)

        for k, v in self._checkpoint.items():
            v['updated_at'] = datetime.strptime(
                v['updated_at'], r'%Y-%m-%dT%H:%M:%S%z')
            self._checkpoint[k] = CheckpointItem(**v)

    def dump(self):
        tmp = self._path.with_name(self._path.name + '.canvas_tmp')
        with open(tmp, 'w') as file:
            json.dump(self._checkpoint, file, cls=CheckpointItemEncoder)
        os.replace(tmp, self._path)
