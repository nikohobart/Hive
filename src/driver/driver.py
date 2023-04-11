import grpc
import logging

from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.utils import serialization


class Client(object):
    """Client used for sending actor and task execution requests
    """
    
    def __init__(self, server='localhost', server_port=50051):
        # configure the host and the
        # the port to which the client should connect to
        self.host = server
        self.server_port = server_port

        # instantiate a communication channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client to the task service server channel and
        # the actor service server channel
        self.stub = driverworker_pb2_grpc.DriverWorkerServiceStub(self.channel)

        # self task id generator 
        self.task_iter = 0


    def get_execute_task(self, func: callable, args: list):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """
        print(f"Driver: Serializing task ({func.__name__}) and arguments ({args})")
        bin_func = serialization.serialize(func)
        bin_args = serialization.serialize(args)
        
        print(f"Driver: Sending task to worker ({self.host}:{self.server_port})")

        response = self.stub.Execute(driverworker_pb2.TaskRequest(
            task_id=(self.task_iter).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args
        ))
        self.task_iter += 1
        
        result = serialization.deserialize(response.result)
        print("Driver: Result received:", result)

        return result
        
