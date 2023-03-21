import cloudpickle

from src.proto import tasks_pb2
from src.proto import tasks_pb2_grpc


class TaskService(tasks_pb2_grpc.TaskServiceServicer):
    def ExecuteTask(self, request, context):
        print("ExecuteTask RPC Called")

        depickled_func = cloudpickle.loads(request.function)
        depickled_args = cloudpickle.loads(request.args)
        print("Received task ({}) with args ({})".format(depickled_func.__name__, depickled_args))
        
        # unpack arguments array
        result = depickled_func(*depickled_args)
        
        # return result to client
        print("Returning:", result)
        return tasks_pb2.ExecuteReply(task_id=request.task_id, result=cloudpickle.dumps(result))
    
    def CancelTask(self, request, context):
        # TODO:
        pass
    