# import grpc
# from concurrent import futures

class MasterObjectStore():
    def __init__(self):
        self._store = {}

    def Put(self, object_id, serverID):
        self._store[object_id] = serverID
        return 1

    def Get(self, object_id, serverID):
        # check if object exists
        if object_id not in self._store:
            return None
        serverID = self._store.get(object_id)
        return serverID

    def Delete(self, object_id, serverID):
        # check if object exists
        if object_id not in self._store:
            return None
        del self._store[object_id]
        return 1

    # check if MASTER has the object mapping
    def MasterObjStroreHasLocation(self, object_ids):
        for id in object_ids:
            if self._store.get(id) is None:
                return False
        return True

    # update local object store
    # get a list of object ids, and ONE server addresses, save the mapping
    def updateLocalObjStoreLocation(self, objects, serverID):
        for object in objects:
            self._store[object] = serverID

    # get a list of object ids, return a list of server addresses
    def getFromMasterObjStore(self, object_ids):
        res = list()
        for id in object_ids:
            list.append(self._store.get(id))
        return res 
        

