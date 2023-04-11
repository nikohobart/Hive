from client import Client
from src.utils import future
import threading


def optional_kwarg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, **kwargs)

            return real_decorator

    return wrapped_decorator

objstore={}

class HiveCore:
    def __init__(self):
        self.store = {}
        self.scheduler = 'placeholder'
        
    @optional_kwarg_decorator
    def remote(fn, server='localhost', server_port=50051):
        return RemoteFunction(fn, server, server_port, objstore=objstore)


class RemoteFunction:
    def __init__(self, fn, server='localhost', server_port=50051, scheduler=None, objstore=None):
        self.fn = fn
        self.server = server
        self.server_port = server_port
        self.objstore = objstore
        
        self.client = Client(self.server, self.server_port)

    def exec(self, f, *args):
        ret = self.client.get_execute_task(self.fn, args)
        self.objstore[f._object_id] = ret
        f.set_result(ret)

    def remote(self, *args, **kwargs):
        f = future.Future()
        threading.Thread(target = self.exec, args = (f, *args)).start()
        return f


if __name__ == '__main__':
    hive = HiveCore()
    
    ex_args = [32, 478]
    
    @hive.remote(server='localhost', server_port=8080)
    def simplesum(x: int, y: int) -> int:
        return x + y
    
    res = simplesum.remote(*ex_args)
    print("Success:", res)
    