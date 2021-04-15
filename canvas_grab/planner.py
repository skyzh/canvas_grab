from .snapshot import SnapshotFile, SnapshotLink


class Planner(object):
    """Planner generates a transfer plan from two snapshots
    """

    def __init__(self, remove_local_file):
        self.remove_local_file = remove_local_file

    def plan(self, snapshot_from, snapshot_to, file_filter):
        """plan a transfer

        Args:
            snapshot_from (dict): source snapshot
            snapshot_to (dict): target snapshot
            file_filter (canvas_grab.file_filter.FileFilter): file filter

        Returns:
            transfer plan
        """
        snapshot_from_filter = file_filter.filter_files(snapshot_from)

        plans = []
        # Add and update files
        for key, from_item in snapshot_from.items():
            if key not in snapshot_from_filter:
                plans.append(('ignore', key, from_item))
            elif key not in snapshot_to:
                plans.append(('add', key, from_item))
            else:
                to_item = snapshot_to[key]
                if isinstance(from_item, SnapshotFile):
                    if to_item.size != from_item.size or to_item.modified_at != from_item.modified_at:
                        plans.append(('update', key, from_item))
                if isinstance(from_item, SnapshotLink):
                    content_length = len(from_item.content().encode('utf-8'))
                    if to_item.size != content_length:
                        plans.append(('update', key, from_item))
        for key, to_item in snapshot_to.items():
            if key not in snapshot_from_filter:
                if self.remove_local_file:
                    plans.append(('delete', key, to_item))
                else:
                    plans.append(('try-remove', key, to_item))
        return plans
