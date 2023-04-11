import cloudpickle
import logging
from .scheduler import SchedulingQueue

import grpc
from src.proto import driver_pb2
from src.proto import driver_pb2_grpc
from src.proto import worker_pb2
from src.proto import worker_pb2_grpc


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
        self.tasks_stub = worker_pb2_grpc.WorkerServiceStub(self.channel)
        self.actors_stub = driver_pb2_grpc.DriverServiceStub(self.channel)
        
        # self task id generator 
        #TODO: this should probably be moved to a different part of the architecture
        self.task_iter = 0
        self.scheduler = SchedulingQueue()

        
    def get_execute_task(self, f: callable, args: list):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """
        print('Serializing function ({}) and arguments ({})'.format(f.__name__, args))
        bin_func = cloudpickle.dumps(f)
        bin_args = cloudpickle.dumps(args)
        
        print("Sending function to worker ({}:{})".format(self.host, self.server_port))

        # Add task to scheduling queue
        # TODO: how to get server addresses?
        #response = self.scheduler.add_task(self.task_iter, bin_func, bin_args, self.task_iter, self.tasks_stub, [])
        response = self.tasks_stub.Execute(worker_pb2.TaskRequest(
            task_id=(self.task_iter).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args
        ))
        self.task_iter += 1
        
        result = cloudpickle.loads(response.result)
        print("Response received:", result)
        
