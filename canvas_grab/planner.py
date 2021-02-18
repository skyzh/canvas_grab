class Planner(object):
    def plan(self, snapshot_from, snapshot_to):
        plans = []
        for key, from_item in snapshot_from.items():
            if key not in snapshot_to:
                plans.append((key, from_item))
            else:
                to_item = snapshot_to[key]
                if to_item.size != from_item.size or to_item.modified_at != from_item.modified_at:
                    plans.append((key, from_item))
        return plans
