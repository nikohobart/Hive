import cloudpickle
import psutil
from src.scheduler import SchedulingQueue
from src.serverObjStore import LocalObjectStore

from src.proto import tasks_pb2
from src.proto import tasks_pb2_grpc


class TaskService(tasks_pb2_grpc.TaskServiceServicer):
    # initialize scheduler
    def init(self):
        self.scheduling_queue = SchedulingQueue()

    def ExecuteTask(self, request, context):
        print("ExecuteTask RPC Called")

        depickled_func = cloudpickle.loads(request.function)
        depickled_args = cloudpickle.loads(request.args)
        print("Received task ({}) with args ({})".format(depickled_func.__name__, depickled_args))
        
        # if need local has all objects
        # TODO:
        localObjectStore = LocalObjectStore()
        if localObjectStore.hasAllObjects(request.object_ids, depickled_args):
            
        else:
            storedObj, missingObj = localObjectStore.getFromLocalObjStore(request.object_ids)
            serverAddr = master_has_all_objects(request.object_ids, depickled_args):
                send_request_to_worker(request, depickled_args)
                pass   
            else:
                # excute as normal
                pass
                
        
        # unpack arguments array
        result = depickled_func(*depickled_args)
        
        # return result to client
        print("Returning:", result)
        return tasks_pb2.ExecuteReply(task_id=request.task_id, result=cloudpickle.dumps(result))
    
    # worker send grpc to master to check if master has all objects, return 
    def MasterHasObjectsMapping():
        pass
    
    # send grpc to worker to get resource load  
    def GetResourceLoad(self, request, context):
        cpu_load = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_used = memory_info.used

        return tasks_pb2.GetResourceLoadResponse(cpu_load=cpu_load, memory_used=memory_used)

    def CancelTask(self, request, context):
        # TODO:
        pass
    
    # Helper functions
    # convert a request to an internal Task representation
    # def task_from_request(self, request):
    #         # Convert a request to an internal Task representation
    #         depickled_func = cloudpickle.loads(request.function)
    #         depickled_args = cloudpickle.loads(request.args)
    #         return Task(
    #             task_id=request.id,
    #             # resources=request.resources,
    #             function=depickled_func,
    #             args=depickled_args,
    #             state=TaskState.READY,
    #         )

    # def SubmitTask(self, task1):
    #     scheduling_queue.queue_tasks([task1], TaskState.PLACEABLE)
    #     print(scheduling_queue.has_task("task1"))  # This should print True
        
    #     scheduling_queue.move_tasks(["task1"], TaskState.PLACEABLE, TaskState.RUNNING)