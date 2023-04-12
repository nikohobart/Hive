
class ObjectStore():
    def __init__(self):
        # Object ID : Object
        self.__store = {}

    def get(self, *object_ids):
        ret = {}
        for object_id in object_ids:
            if object_id not in self.__store:
                raise ValueError(f"Object {object_id} not found")
            ret[object_id] = self.__store.get(object_id)
        return ret

    def set(self, object_id, object):
        self.__store[object_id] = object

    def remove(self, *object_ids):
        for object_id in object_ids:
            if object_id not in self.__store:
                raise ValueError(f"Object {object_id} not found")
            del self.__store[object_id]

    def missing(self, *object_ids):
        ret = []
        if not object_ids:
            return ret
        else:
            for object_id in object_ids:
                if object_id not in self.__store:
                    ret.append(object_id)
            return ret
    
    def keys(self):
        return self.__store.keys()
    