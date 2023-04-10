# import grpc
# from concurrent import futures

class LocalObjectStore():
    def __init__(self):
        self._store = {}

    def Put(self, object_id, data):
        self._store[object_id] = data
        return 1

    def Get(self, object_id, data):
        # check if object exists
        if object_id not in self._store:
            return None
        data = self._store.get(object_id)
        return data

    def Delete(self, object_id, data):
        # check if object exists
        if object_id not in self._store:
            return None
        del self._store[object_id]
        return 1

    # check if local worker has the object
    def hasAllObjects(self, object_ids, object):
        for id in object_ids:
            if self._store.get(id) is None:
                return False
        return True

    def MasterObjStroreHas():
        pass
    def sendToServerAndMaster():
        pass
    # update local object store
    def updateLocalObjStore(self, object_id, object):
        self._store[object_id] = object

    # get a list of object ids, return a list of objects
    def getFromLocalObjStore(self, object_ids):
        res = list()
        for id in object_ids:
            list.append(self._store.get(id))
        # get rest object ids from object_ids other than res
        missingObjs = [item for item in res if item not in object_ids]
        return res, missingObjs
        
    def notifyMaster():
        pass