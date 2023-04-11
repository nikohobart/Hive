import grpc
import psutil

from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.proto import workerworker_pb2
from src.proto import workerworker_pb2_grpc
from src.utils import serialization
from src.utils.future import Future

class DriverWorkerService(driverworker_pb2_grpc.DriverWorkerServiceServicer):
    def __init__(self, object_store):
        self.object_store = object_store

    def Execute(self, request, context):
        print("DriverWorkerService: Execute RPC Called")

        depickled_func = serialization.deserialize(request.function)
        depickled_args = serialization.deserialize(request.args)
        depickled_object_locs = serialization.deserialize(request.object_locs)

        print(f"DriverWorkerService: Received task ({depickled_func.__name__}) with args ({depickled_args})")
        
        args = {}
        missing_args = {}

        # Create a dictionary of arguments : objects/object_ids
        # Create a dictionary of missing arguments : object_ids
        for arg in depickled_args:
            if isinstance(arg, Future):
                if self.object_store.contains(arg.get_id()):
                   args[arg] = self.object_store.get(arg)
                else:
                    args[arg] = arg.get_id()
                    missing_args[arg] = arg.get_id()

        # If object locations were returned, get the objects
        if depickled_object_locs:
            object_vals = self.get_objects(depickled_object_locs)
            for arg, id in missing_args:
                args[arg] = object_vals[id]
            for object_id, object in object_vals:
                self.object_store.set(object_id, object)
            
            # Execute and return
            result = depickled_func(*list(args.values()))
            object_ids = {"missing": [], "current": list(self.object_store.keys())}

            print("DriverWorkerService: Returning result:", result)
            return driverworker_pb2.TaskReply(task_id=request.task_id, result=serialization.serialize(result), object_ids=object_ids)

        # If object locations were not returned and there are missing arguments, get the object locations
        elif missing_args:
            missing_arg_ids = list(missing_args.values())
            object_ids = {"missing": missing_arg_ids, "current": list(self.object_store.keys())}

            print("DriverWorkerService: Returning missing ids:", missing_arg_ids)
            return driverworker_pb2.TaskReply(task_id=request.task_id, result=0, object_ids=object_ids)

        # If object locations were not returned and there are no missing arguments, execute and return
        else:
            object_ids = {"missing": [], "current": list(self.object_store.keys())}

            print("DriverWorkerService: Returning result:", result)
            return driverworker_pb2.TaskReply(task_id=request.task_id, result=serialization.serialize(result), object_ids=object_ids)
    
    # Return CPU load and memory utilization
    def GetLoad(self, request, context):
        cpu_load = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_used = memory_info.used

        return driverworker_pb2.LoadReply(cpu_load=serialization.serialize(cpu_load), memory_used=serialization.serialize(memory_used))
    
    # Helper function to get objects from other workers
    def get_objects(self, object_locs):
        # Dictionary of worker : [object_ids needed from worker]
        loc_objects = {}

        # Dictionary of object_ids : objects
        object_vals = {}

        # Fill loc_objects dictionary
        for object_id, loc in object_locs:
            if loc not in loc_objects:
                loc_objects[loc] = []
            loc_objects[loc].append(object_id)
        
        # Send RPC request from other workers
        for loc, object_ids in loc_objects:
            # Create RPC Channel
            host, port = loc
            channel = grpc.insecure_channel(f"{host}:{port}")
            stub = workerworker_pb2_grpc.WorkerWorkerServiceStub(channel)

            # Send RPC
            bin_object_ids = serialization.serialize(object_ids)
            bin_objects = stub.GetObject(workerworker_pb2.ObjectRequest(object_ids=bin_object_ids))
            temp_object_vals = serialization.deserialize(bin_objects)

            # Fill return dictionary
            for object_id, object in temp_object_vals:
                object_vals[object_id] = object
            
        return object_vals

        



        







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
        