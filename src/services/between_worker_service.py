
from src.proto import worker_pb2
from src.proto import worker_pb2_grpc
from src.worker import object_store
from src.util import serialization

class BetweenWorkerService(worker_pb2_grpc.BetweenWorkerServiceServicer):
    def init(self):
        self._object_store = object_store.ObjectStore()
    
    # send a response back the worker
    # TODO cheng the args below
    def GetObjectLoc(self, request, context):
        # TODO: get obj from object store
        return worker_pb2_grpc.ObjResponse(data="Obj from Worker B")