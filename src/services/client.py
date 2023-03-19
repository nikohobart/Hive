import cloudpickle
import logging

import grpc
from src.proto import tasks_pb2
from src.proto import tasks_pb2_grpc


def run():
    example_args = [32, 478]
    def example_func(x: int, y: int) -> int:
        return x + y
    
    pickled_args = cloudpickle.dumps(example_args)
    pickled_func = cloudpickle.dumps(example_func)
    
    print("Sending function to worker")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = tasks_pb2_grpc.TaskServiceStub(channel)
        response = stub.ExecuteTask(tasks_pb2.ExecuteRequest(
            task_id=int.to_bytes(1), function=pickled_func, args=pickled_args)
        )
        
    result = cloudpickle.loads(response.result)
    print("Response received:", result)
    
if __name__ == '__main__':
    logging.basicConfig()
    run()
    