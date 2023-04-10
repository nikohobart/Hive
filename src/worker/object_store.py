
class ObjectStore():
    def __init__(self):
        self._store = {}

    def get(self, *object_ids):
        objects = []
        for object_id in object_ids:
            if object_id not in self._store:
                raise ValueError(f"Object {object_id} not found")
            objects.append(self._store.get(object_id))
        return objects

    def set(self, object_id, object):
        self._store[object_id] = object

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
    