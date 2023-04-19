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

    def get_execute_task(self, future_id, func: callable, args: list, kwargs: dict):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
        """
        
        # Add new task to scheduler
        new_task = Task(func, args, kwargs)
        self.scheduler.add_task(new_task)

        task, worker = self.scheduler.get_task()
        self.control_store.set(worker, future_id)

        channel = grpc.insecure_channel(worker)
        stub = driverworker_pb2_grpc.DriverWorkerServiceStub(channel)

        bin_task_id = serialization.serialize(task.id)
        bin_future_id = serialization.serialize(future_id)
        bin_func = serialization.serialize(task.func)
        bin_args = serialization.serialize(task.args)
        bin_kwargs = serialization.serialize(task.kwargs)
        bin_locs = serialization.serialize(0)
        
        print(f"Driver {self.server}:{self.server_port}: Sending Execute RPC on Worker {worker}: {func.__name__, args, kwargs}")

        response = stub.Execute(driverworker_pb2.TaskRequest(
            task_id=bin_task_id, future_id=bin_future_id, function=bin_func, args=bin_args, kwargs=bin_kwargs, object_locs=bin_locs
        ))
        result = serialization.deserialize(response.result)
        object_ids = serialization.deserialize(response.object_ids)

        self.control_store.set(worker, *object_ids["current"])

        if isinstance(result, Missing):
            print(f"Driver {self.server}:{self.server_port}: Received missing objects from Worker {worker}: {object_ids['missing']}")

            object_locs = self.get_locs(object_ids["missing"])
            bin_locs = serialization.serialize(object_locs)

            print(f"Driver {self.server}:{self.server_port}: Sending object locations to Worker {worker}: {object_locs}")

            response2 = stub.Execute(driverworker_pb2.TaskRequest(
                task_id=bin_task_id, future_id=bin_future_id, function=bin_func, args=bin_args, kwargs=bin_kwargs, object_locs=bin_locs
            ))
            result2 = serialization.deserialize(response2.result)
            
            self.control_store.set(worker, *object_ids["missing"])

            print(f"Driver {self.server}:{self.server_port}: Received result from Worker {worker}: {result2}")

            return result2
        else:
            print(f"Driver {self.server}:{self.server_port}: Received result from Worker {worker}: {result}")

            return result

    # Send object locations
    def get_locs(self, object_ids):
        while not self.control_store.contains(*object_ids):
            time.sleep(0.1)

        return self.control_store.get(*object_ids)
