import grpc
import psutil
import time
from multiprocessing.pool import ThreadPool

from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.proto import workerworker_pb2
from src.proto import workerworker_pb2_grpc
from src.utils import serialization
from src.utils.future import Future
from src.utils.missing import Missing

class DriverWorkerService(driverworker_pb2_grpc.DriverWorkerServiceServicer):
    def __init__(self, object_store, address, port):
        self.object_store = object_store
        self.address = address
        self.port = port

    def Execute(self, request, context):
        future_id = serialization.deserialize(request.future_id)
        func = serialization.deserialize(request.function)
        args = serialization.deserialize(request.args)
        kwargs = serialization.deserialize(request.kwargs)
        object_locs = serialization.deserialize(request.object_locs)

        self.object_store.set({future_id : None})

        object_ids = []
        for arg in args:
            if isinstance(arg, Future):
                object_ids.append(arg.get_id())

        if kwargs:
            for arg in kwargs.values():
                if isinstance(arg, Future):
                    object_ids.append(arg.get_id())

        missing = self.object_store.missing(*object_ids)

        # If there are no missing arguments, execute
        if not missing:
            #print(f"Worker {self.address}:{self.port}: Execute RPC: Received function and arguments: {func.__name__, args, kwargs}")

            result = self.execute(func, args, kwargs, object_ids)
            self.object_store.set({future_id : result})

            object_ret = {"missing" : [], "current" : self.object_store.keys()}
            bin_result = serialization.serialize(result)
            bin_object_ret = serialization.serialize(object_ret)

            #print(f"Worker {self.address}:{self.port}: Execute RPC: Sending result: {result}")

            return driverworker_pb2.TaskReply(task_id=request.task_id, result=bin_result, object_ids=bin_object_ret)
        
        else:

            # If there are missing arguments and no object locations, get object locations from the driver
            if object_locs == 0:
                #print(f"Worker {self.address}:{self.port}: Execute RPC: Received function and arguments: {func.__name__, args, kwargs}")

                object_ret = {"missing" : missing, "current" : self.object_store.keys()}

                bin_object_ret = serialization.serialize(object_ret)
                bin_ret = serialization.serialize(Missing())

                #print(f"Worker {self.address}:{self.port}: Execute RPC: Sending missing objects: {missing}")
                
                return driverworker_pb2.TaskReply(task_id=request.task_id, result=bin_ret, object_ids=bin_object_ret)
            
            # If there are missing arguments and object locations, get objects from the workers
            else:
                #print(f"Worker {self.address}:{self.port}: Execute RPC: Received object locations: {object_locs}")

                self.get_objects(object_locs)

                result = self.execute(func, args, kwargs, object_ids)
                self.object_store.set({future_id : result})

                object_ret = {"missing" : [], "current" : self.object_store.keys()}
                bin_result = serialization.serialize(result)
                bin_object_ret = serialization.serialize(object_ret)

                #print(f"Worker {self.address}:{self.port}: Execute RPC: Sending result: {result}")

                return driverworker_pb2.TaskReply(task_id=request.task_id, result=bin_result, object_ids=bin_object_ret)
    
    # Return CPU load and memory utilization
    def GetLoad(self, request, context):
        cpu_percent = psutil.Process().cpu_percent()
        mem_percent = psutil.Process().memory_percent()

        return driverworker_pb2.LoadReply(cpu_load=serialization.serialize(cpu_percent), memory_used=serialization.serialize(mem_percent))

    # Helper function to get objects from other workers
    def get_objects(self, object_locs):
        # worker : [object_ids needed from worker]
        loc_objects = {}

        for object_id, locs in object_locs.items():
            if locs[0] != f"{self.address}:{self.port}":
                if locs[0] not in loc_objects:
                    loc_objects[locs[0]] = []
                loc_objects[locs[0]].append(object_id)

        with ThreadPool(len(loc_objects.keys())) as pool:
            args = [(loc, object_ids) for loc, object_ids in loc_objects.items()]
            pool.starmap(self.get_objects_exec, args)
        
        return
    
    def get_objects_exec(self, loc, object_ids):
        channel = grpc.insecure_channel(loc)
        stub = workerworker_pb2_grpc.WorkerWorkerServiceStub(channel)

        bin_object_ids = serialization.serialize(object_ids)

        #print(f"Worker {self.address}:{self.port}: Execute RPC: Sending GetObject RPC to Worker {loc}: {object_ids}")
        start_time = time.time()
        result = stub.GetObject(workerworker_pb2.ObjectRequest(object_ids=bin_object_ids))
        time_took = time.time() - start_time
        print("\nWorker took {} seconds".format(time_took))
        objects = serialization.deserialize(result.objects)

        self.object_store.set(objects)

        #print(f"Worker {self.address}:{self.port}: Execute RPC: Received objects from Worker {loc}: {objects}")

        return
    
    def execute(self, func, args, kwargs, object_ids):
        while self.object_store.missing(*object_ids) or self.object_store.none(*object_ids):
            time.sleep(0.1)

        objects = self.object_store.get(*object_ids)

        args = [objects[arg.get_id()] if isinstance(arg, Future) else arg for arg in args]
        if kwargs:
            kwargs = {key : (objects[arg.get_id()] if isinstance(arg, Future) else arg) for (key, arg) in kwargs.items()}
            result = func(*args, **kwargs)
        else:
            result = func(*args)

        return result

        
