import grpc

from queue import Queue
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool

from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.utils import serialization
from src.utils.future import Future

class RRScheduler:
    def __init__(self, workers):
        self.task_queue = Queue()
        self.worker_queue = Queue()
        for worker in workers:
            self.worker_queue.put(worker)
        self.lock = Lock()

    def add_task(self, task):
        self.lock.acquire()
        self.task_queue.put(task)
        self.lock.release()

    def get_task(self):
        self.lock.acquire()
        task = self.task_queue.get()
        worker = self.worker_queue.get()
        self.worker_queue.put(worker)
        self.lock.release()

        return task, worker


class LoadBalancingScheduler(RRScheduler):
    def __init__(self, workers):
        self.task_queue = Queue()
        self.workers = workers
        self.lock = Lock()

    def get_task(self):
        self.lock.acquire()
        task = self.task_queue.get()
        self.lock.release()

        with ThreadPool(len(self.workers)) as pool:
            loads = pool.map(self.get_load, self.workers)

            min_load = 100
            min_worker = None

            for worker, load in zip(self.workers, loads):
                if load < min_load:
                    min_load = load
                    min_worker = worker

        return task, min_worker

    
    def get_load(self, worker):
        channel = grpc.insecure_channel(worker)
        stub = driverworker_pb2_grpc.DriverWorkerServiceStub(channel)

        response = stub.GetLoad(driverworker_pb2.LoadRequest())
        cpu_load = serialization.deserialize(response.cpu_load)

        return cpu_load
    

class LocalityAwareScheduler(RRScheduler):
    def __init__(self, workers, control_store):
        self.task_queue = Queue()
        self.workers = workers
        self.control_store = control_store
        self.lock = Lock()


    def get_task(self):
        self.lock.acquire()
        task = self.task_queue.get()
        self.lock.release()

        max_locality = -1
        max_worker = self.workers[0]

        for worker in self.workers:
            locality = self.get_locality(worker, task)
            if locality > max_locality:
                max_locality = locality
                max_worker = worker
        
        return task, max_worker


    def get_locality(self, worker, task):
        locality = 0
        for arg in task.args:
            if isinstance(arg, Future) and self.control_store.contains(arg) and worker in self.control_store.get(arg.get_id()):
                locality += 1
        if task.kwargs:
            if isinstance(arg, Future) and self.control_store.contains(arg) and worker in self.control_store.get(arg.get_id()):
                locality += 1

        return locality


    