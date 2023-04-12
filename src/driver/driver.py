import grpc
import logging
import uuid
from src.driver.scheduler import SchedulingQueue
import time
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
    
    def __init__(self, server='localhost', server_port=50051, scheduler=None, controlStore=None):
        # configure the host and the
        # the port to which the client should connect to
        self.server_port = server_port
        self.controlStore = controlStore
        self.scheduler = scheduler

        # Get worker with least load
        self.workerAddr = self.scheduler.workerPQ.getServer()
        #print("client Received: ", self.workerAddr)
        if self.workerAddr is None:
            s = '{}:{}'.format(server, self.server_port)
            self.updateChannel(s)
        else:
            self.updateChannel(self.workerAddr)

        # self task id generator 
        #TODO: this should probably be moved to a different part of the architecture
        #self.workerPQ = WorkerPQ(['{}:{}'.format(self.host, self.server_port)]) 

    def getWorker(self):
        return self.workerAddr

    def get_execute_task(self, func: callable, args: list, future_id=None):
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
        bin_locs = serialization.serialize(0)
        self.futureIdserial =  serialization.serialize(future_id)
        
        print("Sending function to worker ({})".format(self.workerAddr))

        response = self.stub.Execute(driverworker_pb2.TaskRequest(
            task_id=(curTask.id).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args, object_locs=bin_locs, future_id=self.futureIdserial
        ))
        
        result = serialization.deserialize(response.result)
        print("Client: Result received:", result)

        # Updating ControlStore
        if result == "MissingArgument":
            return self.updateStore(response, bin_func, bin_args)
        else:
            return result

    
    def updateChannel(self, server):
         # instantiate a communication channel
        self.channel = grpc.insecure_channel(server)

        # bind the client to the task service server channel and
        # the actor service server channel
        self.stub = driverworker_pb2_grpc.DriverWorkerServiceStub(self.channel)

    # This method is used to update ControlServer on basis of current objects stored by worker
    # It also sends worker associated with required objects    
    def updateStore(self, response, bin_func, bin_args):
        objectIds = serialization.deserialize(response.object_ids)
        requiredIds = objectIds["missing"]
        currentIds = objectIds["current"]
        print("CURRENTID: ", currentIds)
        self.controlStore.set(self.workerAddr, currentIds)
        if len(requiredIds) != 0:
            print("ID: ", requiredIds)
            return self.sendObjects(requiredIds, bin_func, bin_args)
        else:
            return None

    # This method sends workers associated with required objects 
    def sendObjects(self, requiredIds, bin_func, bin_args):
        objectLocs = {}
        
        for id in requiredIds:
            print("ID: ", id)
            if self.controlStore.contains(id):
                objectLocs[id] = self.controlStore.get([id])[0]
            else:
                start_time = time.time()
                while True:
                    if self.controlStore.contains(id):
                         print("VALUE: ", self.controlStore.get([id])[0])
                         objectLocs[id] = self.controlStore.get([id])[0]
                         break
                     
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= 10:
                            print("Timeout reached, didn't find")
                            break
                    time.sleep(0.1)
                    
        binObjects = serialization.serialize(objectLocs)
        print("OBJECTS: ", objectLocs)
        serialId = uuid.uuid1().int>>64
        response = self.stub.Execute(driverworker_pb2.TaskRequest(task_id=(serialId).to_bytes(length=10, byteorder='little'), function=bin_func, args=bin_args, object_locs = binObjects,  future_id=self.futureIdserial))
        result = serialization.deserialize(response.result)
        print("TESTERRRRRRR: ", result)
        return result
