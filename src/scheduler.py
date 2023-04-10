import heapq

class Task:
    def init(self, task_id, task_func, task_func_args):
        self.task_id = task_id
        self.task_func = task_func
        self.task_func_args = task_func_args
        self.state = TaskState.PLACEABLE

class TaskState(Enum):
    PLACEABLE = 1
    WAITING = 2
    READY = 3
    RUNNING = 4
    INFEASIBLE = 5
    WAITING_FOR_ACTOR_CREATION = 6
    SWAP = 7
    kNumTaskQueues = 8
    BLOCKED = 9
    DRIVER = 10
    DEAD = 11

class TaskQueue:
    def init(self):
        self.task_list = []
        self.task_map = {}
    # self.current_resource_load = ResourceSet()

    def append_task(self, task_id, task):
        if task_id in self.task_map:
            return False
        self.task_list.append(task)
        self.task_map[task_id] = self.task_list[-1]
        self.current_resource_load += task.resources
        return True

    def remove_task(self, task_id, removed_tasks=None):
        if task_id not in self.task_map:
            return False
        task = self.task_map[task_id]
        self.current_resource_load -= task.resources
        self.task_list.remove(task)
        del self.task_map[task_id]
        if removed_tasks is not None:
            removed_tasks.append(task)
        return True

    def has_task(self, task_id):
        return task_id in self.task_map

    def get_tasks(self):
        return self.task_list

    def get_task(self, task_id):
        if task_id not in self.task_map:
            raise KeyError(f"Task with ID {task_id} not found.")
        return self.task_map[task_id]

    def get_current_resource_load(self):
        return self.current_resource_load


class SchedulingQueue:
    def init(self):
        self.ready_queue = ReadyQueue()
        self.task_queues = {
        task_state: (self.ready_queue if task_state == TaskState.READY else TaskQueue())
        for task_state in [
            TaskState.PLACEABLE,
            TaskState.WAITING,
            TaskState.READY,
            TaskState.RUNNING,
            TaskState.INFEASIBLE,
            TaskState.WAITING_FOR_ACTOR_CREATION,
            TaskState.SWAP,
            ]}
        self.blocked_task_ids = set()
        self.driver_task_ids = set()
        self.server_load_priority_queue = []


    def get_resource_load(self):
        return self.ready_queue.get_resource_load()

    def has_task(self, task_id):
        return any(queue.has_task(task_id) for queue in self.task_queues.values())

    def get_task_of_state(self, task_id, task_state):
        return self.task_queues[task_state].get_task(task_id)

    def remove_task(self, task_id, removed_task=None, removed_task_state=None):
        for task_state, queue in self.task_queues.items():
            if queue.has_task(task_id):
                if removed_task is not None:
                    removed_task = queue.get_task(task_id)
                if removed_task_state is not None:
                    removed_task_state = task_state
                return queue.remove_task(task_id)
        return False

    def get_ready_tasks_with_resources(self):
        return self.ready_queue.get_tasks_with_resources()

    def get_tasks(self, task_state):
        return self.task_queues[task_state].get_tasks()

    def remove_tasks(self, task_ids):
        removed_tasks = []
        for task_id in task_ids:
            self.remove_task(task_id, removed_tasks)
        return removed_tasks

    def queue_tasks(self, tasks, task_state):
        for task in tasks:
            self.task_queues[task_state].append_task(task.task_id, task)

    def move_tasks(self, task_ids, src_state, dst_state):
        tasks_to_move = self.remove_tasks(task_ids)
        self.queue_tasks(tasks_to_move, dst_state)

    def filter_state(self, task_ids, filter_state):
        return {task_id for task_id in task_ids if self.task_queues[filter_state].has_task(task_id)}

    def get_task_ids_for_job(self, job_id):
        return {task.task_id for queue in self.task_queues.values() for task in queue.get_tasks() if task.job_id == job_id}

    def get_task_ids_for_actor(self, actor_id):
        return {task.task_id for queue in self.task_queues.values() for task in queue.get_tasks() if task.actor_id == actor_id}

    def get_blocked_task_ids(self):
        return self.blocked_task_ids

    def get_driver_task_ids(self):
        return self.driver_task_ids

    def add_blocked_task_id(self, task_id):
        self.blocked_task_ids.add(task_id)

    def remove_blocked_task_id(self, task_id):
        self.blocked_task_ids.discard(task_id)

    def add_driver_task_id(self, task_id):
        self.driver_task_ids.add(task_id)

    def remove_driver_task_id(self, task_id):
        self.driver_task_ids.discard(task_id)

    # update the server load priority queue by getting the resource load from each server
    def UpdateServerQueue(self, client_stub, server_addresses):

        for server_address in server_addresses:
            resourceLoadResponse = self.tasks_stu.GetResourceLoad(tasks_pb2.GetResourceLoadRequest())
            print("CPU Load: {}%".format(resourceLoadResponse.cpu_load))
            print("Memory Used: {}%".format(resourceLoadResponse.memory_used))
            
            # sort by cpu load, then by memory used
            server_load_tuple = (resourceLoadResponse.cpu_load, resourceLoadResponse.memory_used, server_address)
            heapq.heappush(self.server_load_priority_queue, server_load_tuple)

            # print("Sorted server loads:")
            # while server_load_priority_queue:
            #     cpu_load, memory_used, server_address = heapq.heappop(server_load_priority_queue)
            #     print(f"{server_address}: CPU Load: {cpu_load}%, Memory Used: {memory_used} bytes")

    # send task to a specific server
    def sendTaskToServer(self, request, context, client_stub, sever_address):
        client_stub.SendTask(request, context, sever_address)
        
    # send task to the server with the lowest load
    def PickServerAndSendTask(self, request, context, client_stub, server_addresses):
        # update the queue
        self.updateServerQueue(client_stub, server_addresses)
        
        # send the task to the server with the lowest load
        self.sendTaskToServer(request, context, client_stub, self.server_load_priority_queue[0][2])
  

    
    
    
    
    
    
    
    # def debug_string(self):
    #     # This method should return a string representation of the SchedulingQueue for debugging purposes
    #     pass

    # def record_metrics(self):
    #     # This method should record metrics for the SchedulingQueue
    #     pass

    # def get_ready_queue_resources(self):
    #     return self.ready_queue.get_resource_load()
