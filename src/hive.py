import time
import threading

from src.driver.driver import Client
from src.utils.future import Future
from src.worker.object_store import ObjectStore
from src.driver.scheduler import SchedulingQueue
from src.driver.control_store import ControlStore

class HiveCore:
    def __init__(self):
        self.store = ObjectStore()
        self.controlStore = ControlStore()
        self.scheduler=SchedulingQueue()
        
    def remote(self, server='localhost', server_port=8080):
        def outer(func):
            return RemoteFunction(func, server, server_port, store=self.store, scheduler=self.scheduler, controlStore=self.controlStore)

        return outer

class RemoteFunction:
    def __init__(self, func, server='localhost', server_port=8080, store=None, scheduler=None, controlStore=None):
        self.func = func
        self.server = server
        self.server_port = server_port
        self.controlStore = controlStore

        self.store=store
        self.scheduler = scheduler
        self.scheduler.workerPQ.addServer('{}:{}'.format(server, server_port))

        self.client = Client(self.server, self.server_port, self.scheduler, controlStore)

    def exec(self, future, *args):
        workerAddr = self.client.getWorker()
        self.controlStore.set(workerAddr, [future.get_id()])
        ret = self.client.get_execute_task(self.func, args, future.get_id())
        self.store.set(future.get_id(), ret)
        future.set_result(ret)
        print("Thread 2: Returned")

    def remote(self, *args, **kwargs):
        future = Future()
        threading.Thread(target = self.exec, args = (future, *args)).start()
        return future


if __name__ == '__main__':
    hive = HiveCore()
    
    ex_args = [32, 478]
    
    @hive.remote(server='localhost', server_port=8081)
    def simplesum(x: int, y: int) -> int:
        time.sleep(5)
        return x + y
    
    future = simplesum.remote(*ex_args)
    print("Thread 1: Future Returned")

    print("Thread 1: Do Other Work Here...")

    value = future.get()
    print("Thread 1: Value Returned:", value)

    stored_values = hive.store.get(future._object_id)
    print("Thread 1: Value Stored:", *stored_values)