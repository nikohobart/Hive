import threading


from src.driver.control_store import ControlStore
from src.driver.driver import Client
from src.driver.scheduler import RRScheduler, LoadBalancingScheduler, LocalityAwareScheduler
from src.utils.future import Future

class HiveCore:
    def __init__(self, workers):
        # Initialize global scheduler and global control store
        self.control_store = ControlStore()
        #self.scheduler = LocalityAwareScheduler(workers, self.control_store)
        #self.scheduler = LoadBalancingScheduler(workers)
        self.scheduler = RRScheduler(workers)
        
    def remote(self, server='localhost', server_port=8080):
        # Return wrapped function
        def outer(func):
            return RemoteFunction(func, self.scheduler, self.control_store, server, server_port)
        return outer

class RemoteFunction:
    def __init__(self, func, scheduler, control_store, server='localhost', server_port=8080):
        self.func = func
        self.scheduler = scheduler
        self.control_store = control_store

        self.server = server
        self.server_port = server_port

        self.client = Client(self.scheduler, self.control_store, self.server, self.server_port)

    def exec(self, future, args, kwargs):
        ret = self.client.get_execute_task(future.get_id(), self.func, args, kwargs)
        future.set_result(ret)

    def remote(self, *args, **kwargs):
        future = Future()
        threading.Thread(target = self.exec, args = (future, args, kwargs)).start()
        return future
    