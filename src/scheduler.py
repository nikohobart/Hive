# # import concurrent.futures
# # import task

# # def schedule_tasks(tasks):
# #     results = []

# #     # Use a ThreadPoolExecutor to distribute tasks across threads
# #     with concurrent.futures.ThreadPoolExecutor() as executor:
# #         future_to_task = {executor.submit(task.perform_task, x, y): (x, y) for x, y in tasks}

# #         # Wait for the tasks to complete and collect the results
# #         for future in concurrent.futures.as_completed(future_to_task):
# #             x, y = future_to_task[future]
# #             try:
# #                 result = future.result()
# #             except Exception as exc:
# #                 print(f'Task ({x}, {y}) generated an exception: {exc}')
# #             else:
# #                 print(f'Task ({x}, {y}) result: {result}')
# #                 results.append(result)

# #     return results

# # if __name__ == "__main__":
# #     tasks_to_schedule = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
# #     results =



# import os
# from multiprocessing.managers import SyncManager
# from functools import partial
# import multiprocessing
# from Queue import Queue as _Queue

# class Queue(_Queue):
#     """A (more) picklable queue."""   
#     def __getstate__(self):
#         # Only pickle the state we care about
#         return (self.maxsize, self.queue, self.unfinished_tasks)

#     def __setstate__(self, state):
#         # Re-initialize the object, then overwrite the default
#         # state with our pickled state.
#         Queue.__init__(self)
#         self.maxsize = state[0]
#         self.queue = state[1]
#         self.unfinished_tasks = state[2]


# def return_arg(arg):
#     """Simply return whats given, picklable alternative to
#     lambda x: x
#     """
#     return arg


# class QueueManager(SyncManager):
#     pass

# class SharedConst(object):
#     def __init__(self, value):
#         self.value = value
#     def update(self, value):
#         self.value = value

# def make_server(function, port, authkey, qsize=None):
#     """Create a manager containing input and output queues, and a function
#     to map inputs over. A connecting client can read the stored function,
#     apply it to items in the input queue and post back to the output
#     queue
#     :param function: function to apply to inputs
#     :param port: port over which to server
#     :param authkey: authorization key
#     """
#     QueueManager.register('get_job_q',callable=partial(return_arg, Queue(maxsize=qsize)))
#     QueueManager.register('get_result_q',
#         callable=partial(return_arg, Queue(maxsize=qsize)))
#     QueueManager.register('get_function',
#         callable=partial(return_arg, function))
#     QueueManager.register('q_closed',
#         callable=partial(return_arg, SharedConst(False)))

#     # on windows host='' doesn't work, but 'localhost' breaks
#     #   remote connections. Documentation terrible in this respect.
#     #   So we're not supporting distributed compute on windows.
#     host = 'localhost' if os.name == 'nt' else ''
#     manager = QueueManager(address=(host, port), authkey=authkey)
#     manager.start()
#     return manager


# def make_client(ip, port, authkey):
#     """Create a manager to connect to our server manager
#     :param ip: ip address of server
#     :param port: port over which to server
#     :param authkey: authorization key
#     """
#     QueueManager.register('get_job_q')
#     QueueManager.register('get_result_q')
#     QueueManager.register('get_function')
#     QueueManager.register('q_closed')

#     manager = QueueManager(address=(ip, port), authkey=authkey)
#     manager.connect()
#     return manager
from enum import Enum

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

class TaskQueue:
    def init(self):
    self.task_list = []
    self.task_map = {}
    self.current_resource_load = ResourceSet()

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

    def debug_string(self):
        # This method should return a string representation of the SchedulingQueue for debugging purposes
        pass

    def record_metrics(self):
        # This method should record metrics for the SchedulingQueue
        pass

    def get_ready_queue_resources(self):
        return self.ready_queue.get_resource_load()
