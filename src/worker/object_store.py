
class ObjectStore():
    def __init__(self):
        self.__store = {}

    def get(self, object_id):
        if object_id not in self.__store:
            raise ValueError(f"Object {object_id} not found")
        return self.__store[object_id]

    def set(self, object_id, object):
        self.__store[object_id] = object

    def remove(self, object_id):
        if object_id not in self.__store:
            raise ValueError(f"Object {object_id} not found")
        del self.__store[object_id]

    def contains(self, object_id):
        return object_id in self.__store
    
    def keys(self):
        return self.__store.keys()
    