from src.driver.driver import Client


def optional_kwarg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, **kwargs)

            return real_decorator

    return wrapped_decorator


class HiveCore:
    def __init__(self):
        self.store = 'placeholder'
        self.scheduler = 'placeholder'
        
    @optional_kwarg_decorator
    def remote(fn, server='localhost', server_port=50051):
        return RemoteFunction(fn, server, server_port)


class RemoteFunction:
    def __init__(self, fn, server='localhost', server_port=50051, scheduler=None, objstore=None):
        self.fn = fn
        self.server = server
        self.server_port = server_port
        
        self.client = Client(self.server, self.server_port)

    def remote(self, *args, **kwargs):
        res = self.client.get_execute_task(self.fn, args)
        return res


if __name__ == '__main__':
    hive = HiveCore()
    
    ex_args = [32, 478]
    
    @hive.remote(server='localhost', server_port=8080)
    def simplesum(x: int, y: int) -> int:
        return x + y
    
    res = simplesum.remote(*ex_args)
    print("Success:", res)