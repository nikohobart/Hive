# import concurrent.futures
# import task

# def schedule_tasks(tasks):
#     results = []

#     # Use a ThreadPoolExecutor to distribute tasks across threads
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_task = {executor.submit(task.perform_task, x, y): (x, y) for x, y in tasks}

#         # Wait for the tasks to complete and collect the results
#         for future in concurrent.futures.as_completed(future_to_task):
#             x, y = future_to_task[future]
#             try:
#                 result = future.result()
#             except Exception as exc:
#                 print(f'Task ({x}, {y}) generated an exception: {exc}')
#             else:
#                 print(f'Task ({x}, {y}) result: {result}')
#                 results.append(result)

#     return results

# if __name__ == "__main__":
#     tasks_to_schedule = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
#     results =



import os
from multiprocessing.managers import SyncManager
from functools import partial
import multiprocessing
from Queue import Queue as _Queue

class Queue(_Queue):
    """A (more) picklable queue."""   
    def __getstate__(self):
        # Only pickle the state we care about
        return (self.maxsize, self.queue, self.unfinished_tasks)

    def __setstate__(self, state):
        # Re-initialize the object, then overwrite the default
        # state with our pickled state.
        Queue.__init__(self)
        self.maxsize = state[0]
        self.queue = state[1]
        self.unfinished_tasks = state[2]


def return_arg(arg):
    """Simply return whats given, picklable alternative to
    lambda x: x
    """
    return arg


class QueueManager(SyncManager):
    pass

class SharedConst(object):
    def __init__(self, value):
        self.value = value
    def update(self, value):
        self.value = value

def make_server(function, port, authkey, qsize=None):
    """Create a manager containing input and output queues, and a function
    to map inputs over. A connecting client can read the stored function,
    apply it to items in the input queue and post back to the output
    queue
    :param function: function to apply to inputs
    :param port: port over which to server
    :param authkey: authorization key
    """
    QueueManager.register('get_job_q',
        callable=partial(return_arg, Queue(maxsize=qsize)))
    QueueManager.register('get_result_q',
        callable=partial(return_arg, Queue(maxsize=qsize)))
    QueueManager.register('get_function',
        callable=partial(return_arg, function))
    QueueManager.register('q_closed',
        callable=partial(return_arg, SharedConst(False)))

    # on windows host='' doesn't work, but 'localhost' breaks
    #   remote connections. Documentation terrible in this respect.
    #   So we're not supporting distributed compute on windows.
    host = 'localhost' if os.name == 'nt' else ''
    manager = QueueManager(address=(host, port), authkey=authkey)
    manager.start()
    return manager


def make_client(ip, port, authkey):
    """Create a manager to connect to our server manager
    :param ip: ip address of server
    :param port: port over which to server
    :param authkey: authorization key
    """
    QueueManager.register('get_job_q')
    QueueManager.register('get_result_q')
    QueueManager.register('get_function')
    QueueManager.register('q_closed')

    manager = QueueManager(address=(ip, port), authkey=authkey)
    manager.connect()
    return manager