from client import Client


def optional_kwarg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, **kwargs)

            return real_decorator

    return wrapped_decorator


class RemoteFunction:
    def __init__(self, fn, server='localhost', server_port=50051):
        self.fn = fn
        self.server = server
        self.server_port = server_port
        
        self.client = Client()

    def remote(self, *args, **kwargs):
        res = self.client.get_execute_task(self.fn, args)
        return res


@optional_kwarg_decorator
def remote(fn, server='localhost', server_port=50051):
    return RemoteFunction(fn, server, server_port)


if __name__ == '__main__':
    ex_args = [32, 478]
    
    @remote(server='localhost')
    def simplesum(x: int, y: int) -> int:
        return x + y
    
    res = simplesum.remote(*ex_args)
    print("Success:", res)
    