import cloudpickle
from concurrent import futures
import logging

import grpc
from src.proto import tasks_pb2
from src.proto import tasks_pb2_grpc


class TaskService(tasks_pb2_grpc.TaskServiceServicer):
    
    def ExecuteTask(self, request, context):
        func = request.function
        args = request.args
        
        depickled_func = cloudpickle.loads(func)
        depickled_args = cloudpickle.loads(args)
        
        print("Received task with args:", depickled_args)
        
        # unpack arguments array
        result = depickled_func(*depickled_args)
        
        print("Returning:", result)
        
        return tasks_pb2.ExecuteReply(task_id=request.task_id, result=cloudpickle.dumps(result))
    

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tasks_pb2_grpc.add_TaskServiceServicer_to_server(TaskService(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()