import cloudpickle
import logging
from src.driver.scheduler import SchedulingQueue

import grpc
from src.driver.WorkerPQ import WorkerPQ
from src.proto import driver_pb2
from src.proto import driver_pb2_grpc
from src.proto import worker_pb2
from src.proto import worker_pb2_grpc
from src.util import task


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
        self.scheduler = SchedulingQueue()
        self.workerPQ = WorkerPQ(['{}:{}'.format(self.host, self.server_port)]) 

        
    def get_execute_task(self, f: callable, args: list):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """

        # Add task to scheduling queue
        # TODO: how to get server addresses?
        #response = self.scheduler.add_task(self.task_iter, bin_func, bin_args, self.task_iter, self.tasks_stub, [])
        
        # Get worker with least load
        workerAddr = self.workerPQ.getServer(self.tasks_stub)
        
        # Add current task to waiting queue
        newTask = task.Task(f, args)
        self.scheduler.addTask(newTask)
        
        # Get a FIFO task from scheduler
        curTask = self.scheduler.getTask()
        print('Serializing function ({}) and arguments ({})'.format(curTask.func.__name__, curTask.args))
        bin_func = cloudpickle.dumps(curTask.func)
        bin_args = cloudpickle.dumps(curTask.args)
        
        print("Sending function to worker ({}:{})".format(self.host, self.server_port))


        response = self.tasks_stub.Execute(worker_pb2.TaskRequest(
            task_id=(curTask.id).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args
        ))
        
        result = cloudpickle.loads(response.result)
        print("Response received:", result)

        return result
        
