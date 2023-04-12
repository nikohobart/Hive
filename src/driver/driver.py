import grpc
import logging

from src.driver.scheduler import SchedulingQueue

import grpc
from src.driver.WorkerPQ import WorkerPQ
from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.proto import workerworker_pb2
from src.proto import workerworker_pb2_grpc
from src.utils import task
from src.utils import serialization
from src.driver.control_store import ControlStore

class Client(object):
    """Client used for sending actor and task execution requests
    """
    
    def __init__(self, server='localhost', server_port=50051, scheduler=None):
        # configure the host and the
        # the port to which the client should connect to
        self.server_port = server_port
        self.controlStore = ControlStore()
        self.scheduler = scheduler

        # Get worker with least load
        self.workerAddr = self.scheduler.workerPQ.getServer()

        if self.workerAddr is None:
            s = '{}:{}'.format(server, self.server_port)
            self.updateChannel(s)
        else:
            self.updateChannel(self.workerAddr)

        # self task id generator 
        #TODO: this should probably be moved to a different part of the architecture
        #self.workerPQ = WorkerPQ(['{}:{}'.format(self.host, self.server_port)]) 


    def get_execute_task(self, func: callable, args: list):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """

        # Add task to scheduling queue
        # TODO: how to get server addresses?
        #response = self.scheduler.add_task(self.task_iter, bin_func, bin_args, self.task_iter, self.tasks_stub, [])
        
        # Add current task to waiting queue
        newTask = task.Task(func, args)
        self.scheduler.addTask(newTask)
        
        # Get a FIFO task from scheduler
        curTask = self.scheduler.getTask()
        print('Serializing function ({}) and arguments ({})'.format(curTask.func.__name__, curTask.args))
        bin_func = serialization.serialize(curTask.func)
        bin_args = serialization.serialize(curTask.args)
        
        print("Sending function to worker ({})".format(self.workerAddr))


        response = self.stub.Execute(driverworker_pb2.TaskRequest(
            task_id=(curTask.id).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args
        ))
        
        result = serialization.deserialize(response.result)
        print("Client: Result received:", response)

        # Updating ControlStore
        #self.updateStore(response)
        
        return result

    
    def updateChannel(self, server):
         # instantiate a communication channel
        self.channel = grpc.insecure_channel(server)

        # bind the client to the task service server channel and
        # the actor service server channel
        self.stub = driverworker_pb2_grpc.DriverWorkerServiceStub(self.channel)

    # This method is used to update ControlServer on basis of current objects stored by worker
    # It also sends worker associated with required objects    
    def updateStore(self, response):
        objectIds = serialization.deserialize(response.object_ids)
        requiredIds = objectIds["missing"]
        currentIds = objectIds["current"]
        self.controlStore.set(self.workerAddr, currentIds)
        if len(requiredIds) != 0:
            self.sendObjects(requiredIds)

    def sendObjects(self, requiredIds):
        objectLocs = {}
        for id in requiredIds:
            objectLocs[id] = self.get(id[0])
        #self.stub.Execute(driverworker_pb2.TaskRequest(
        
# Checking if reply has object IDs
# send request with workerIDs

