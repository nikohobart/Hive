import psutil

from src.proto import workerworker_pb2_grpc
from src.utils import serialization
from src.proto import workerworker_pb2 as workerworker_pb2


class WorkerWorkerService(workerworker_pb2_grpc.WorkerWorkerServiceServicer):
    def GetObject(self, request, context):
        print("Worker: GetObject RPC Called")

        depickled_object_ids = serialization.deserialize(request.object_ids)

        print("Worker: Received object ids:", depickled_object_ids)

        # TODO: Implement object getting
        objects = []
        
        # return result to worker
        print("Worker: Returning objects:", objects)
        return workerworker_pb2.TaskReply(objects=serialization.serialize(objects))