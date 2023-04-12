from src.proto import workerworker_pb2_grpc
from src.utils import serialization
from src.proto import workerworker_pb2 as workerworker_pb2


class WorkerWorkerService(workerworker_pb2_grpc.WorkerWorkerServiceServicer):
    def __init__(self, object_store):
        self.object_store = object_store

    def GetObject(self, request, context):
        print("WorkerWorkerService: GetObject RPC Called")

        depickled_object_ids = serialization.deserialize(request.object_ids)

        print("WorkerWorkerService: Received object ids:", depickled_object_ids)

        object_vals = {id : self.object_store.get(id) for id in depickled_object_ids}
        
        print("WorkerWorkerService: Returning objects:", object_vals)

        return workerworker_pb2.ObjectReply(objects=serialization.serialize(object_vals))