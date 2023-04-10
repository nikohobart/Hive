
class ControlStore:
    def __init__(self):
        self._store = {}

    def get(self, *object_ids):
        worker_ids = []
        for object_id in object_ids:
            if object_id not in self._store:
                raise ValueError(f"Object {object_id} not found")
            worker_ids.append(self._store.get(object_id))
        return worker_ids

    def set(self, worker_id, *object_ids):
        for object_id in object_ids:
            self._store[object_id] = worker_id

    def remove(self, *object_ids):
        for object_id in object_ids:
            if object_id not in self._store:
                raise ValueError(f"Object {object_id} not found")
            del self._store[object_id]

    def contains(self, *object_ids):
        for object_id in object_ids:
            if object_id not in self._store:
                return False
        return True

