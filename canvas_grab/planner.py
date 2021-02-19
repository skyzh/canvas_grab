class Planner(object):
    def __init__(self, remove_local_file):
        self.remove_local_file = remove_local_file

    def plan(self, snapshot_from, snapshot_to):
        plans = []
        # Add and update files
        for key, from_item in snapshot_from.items():
            if key not in snapshot_to:
                plans.append(('add', key, from_item))
            else:
                to_item = snapshot_to[key]
                if to_item.size != from_item.size or to_item.modified_at != from_item.modified_at:
                    plans.append(('update', key, from_item))
        # Remove files
        for key, to_item in snapshot_to.items():
            if key not in snapshot_from:
                plans.append(('delete', key, to_item))
        return plans
