import time

from src.proto import workerworker_pb2 as workerworker_pb2
from src.proto import workerworker_pb2_grpc
from src.utils import serialization


class WorkerWorkerService(workerworker_pb2_grpc.WorkerWorkerServiceServicer):
    def __init__(self, object_store, address, port):
        self.object_store = object_store
        self.address = address
        self.port = port

    def GetObject(self, request, context):
        object_ids = serialization.deserialize(request.object_ids)

        # print(f"Worker {self.address}:{self.port}: GetObject RPC: Received object ids:", object_ids)

        while self.object_store.missing(*object_ids) or self.object_store.none(*object_ids):
            time.sleep(0.1)

        objects = self.object_store.get(*object_ids)
        
        # print(f"Worker {self.address}:{self.port}: GetObject RPC: Sending objects:", objects)

        return workerworker_pb2.ObjectReply(objects=serialization.serialize(objects))