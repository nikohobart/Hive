
class ControlStore:
    def __init__(self):
        # Object ID : [(Server Address, Server Port)]
        self.__store = {}

    def get(self, *object_ids):
        ret = {}
        for object_id in object_ids:
            if object_id not in self.__store:
                raise ValueError(f"Object {object_id} not found")
            ret[object_id] = self.__store.get(object_id)
        return ret

    def set(self, worker_id, *object_ids):
        for object_id in object_ids:
            if object_id not in self.__store:
                self.__store[object_id] = []
            self.__store[object_id].append(worker_id)

    def remove(self, worker_id, *object_ids):
        for object_id in object_ids:
            if object_id not in self.__store:
                raise ValueError(f"Object {object_id} not found")
            self.__store[object_id].remove(worker_id)
            if self.__store.get(object_id) == []:
                del self.__store[object_id]

    def contains(self, *object_ids):
        for object_id in object_ids:
            if object_id not in self.__store:
                return False
        return True

