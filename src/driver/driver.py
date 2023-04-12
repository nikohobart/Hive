import grpc
import time
import uuid

from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.utils import serialization
from src.utils.missing import Missing
from src.utils.task import Task

class Client(object):
    """Client used for sending actor and task execution requests
    """
    
    def __init__(self, scheduler, control_store, server='localhost', server_port=8080):
        self.scheduler = scheduler
        self.control_store = control_store

        self.server = server
        self.server_port = server_port

        self.worker = self.scheduler.workerPQ.getServer()

        if self.worker is None:
            self.channel = grpc.insecure_channel(f"{self.server}:{self.server_port}")
        else:
            self.channel = grpc.insecure_channel(self.worker)
        self.stub = driverworker_pb2_grpc.DriverWorkerServiceStub(self.channel)

    def get_worker(self):
        return self.worker

    def get_execute_task(self, future_id, func: callable, args: list, kwargs: dict):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """
        
        # Add new task to scheduler
        new_task = Task(func, args, kwargs)
        self.scheduler.addTask(new_task)
        
        # Get task from scheduler
        cur_task = self.scheduler.getTask()

        bin_task_id = serialization.serialize(cur_task.id)
        bin_future_id = serialization.serialize(future_id)
        bin_func = serialization.serialize(cur_task.func)
        bin_args = serialization.serialize(cur_task.args)
        bin_kwargs = serialization.serialize(cur_task.kwargs)
        bin_locs = serialization.serialize(0)
        
        print(f"Driver {self.server}:{self.server_port}: Sending Execute RPC on Worker {self.worker}: {func.__name__, args, kwargs}")

        response = self.stub.Execute(driverworker_pb2.TaskRequest(
            task_id=bin_task_id, future_id=bin_future_id, function=bin_func, args=bin_args, kwargs=bin_kwargs, object_locs=bin_locs
        ))
        result = serialization.deserialize(response.result)
        object_ids = serialization.deserialize(response.object_ids)

        self.update_store(object_ids["current"])

        if isinstance(result, Missing):
            print(f"Driver {self.server}:{self.server_port}: Received missing objects from Worker {self.worker}: {object_ids['missing']}")

            object_locs = self.get_locs(object_ids["missing"])
            bin_locs = serialization.serialize(object_locs)

            print(f"Driver {self.server}:{self.server_port}: Sending object locations to Worker {self.worker}: {object_locs}")

            response2 = self.stub.Execute(driverworker_pb2.TaskRequest(
                task_id=bin_task_id, future_id=bin_future_id, function=bin_func, args=bin_args, kwargs=bin_kwargs, object_locs=bin_locs
            ))
            result2 = serialization.deserialize(response2.result)

            print(f"Driver {self.server}:{self.server_port}: Received result from Worker {self.worker}: {result2}")

            return result2
        else:
            print(f"Driver {self.server}:{self.server_port}: Received result from Worker {self.worker}: {result}")

            return result

    # Update global control store
    def update_store(self, object_ids):
        self.control_store.set(self.worker, *object_ids)
        return

    # Send object locations
    def get_locs(self, object_ids):
        while not self.control_store.contains(*object_ids):
            time.sleep(0.1)

        return self.control_store.get(*object_ids)
