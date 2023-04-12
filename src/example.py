import time

from src.hive import HiveCore

if __name__ == '__main__':
    hive = HiveCore()
    
    @hive.remote(server='localhost', server_port=8080)
    def simple_sum(*args):
        time.sleep(1)
        sum = 0
        for arg in args:
            sum += arg
        return sum
    
    @hive.remote(server='localhost', server_port=8081)
    def simple_mult(*args):
        time.sleep(5)
        prod = 1
        for arg in args:
            prod *= arg
        return prod
    
    @hive.remote(server='localhost', server_port=8082)
    def simple_arithmetic(*args, **kwargs):
        print(kwargs)
        if "op" in kwargs:
            if kwargs["op"] == "add":
                sum = 0
                for arg in args:
                    sum += arg
                return sum
            elif kwargs["op"] == "mult":
                prod = 1
                for arg in args:
                    prod *= arg
                return prod
        if "val" in kwargs:
            if kwargs["val"] >= 5:
                prod = 1
                for arg in args:
                    prod *= arg
                return prod
            else:
                sum = 0
                for arg in args:
                    sum += arg
                return sum


    def simple_test():
        args = [1, 7]

        add_future = simple_sum.remote(*args)

        print(f"Client: Do other work here...")

        print(f"Client: Future returned: {add_future.get()}")


    def future_test():
        args = [3, 5]

        add_future = simple_sum.remote(*args)
        mult_future = simple_sum.remote(3, mult_future)

        print(f"Client: Futures returned: {add_future.get(), mult_future.get()}")

    
    def kwarg_test():
        args = [9, 12]
        kwargs = {"op" : "add"}

        add_future = simple_arithmetic.remote(*args, **kwargs)
        mult_future = simple_arithmetic.remote(*args, **kwargs)
        
        print(f"Client: Futures returned: {add_future.get(), mult_future.get()}")


    def kwarg_future_test():
        args = [9, 12]
        add_future = simple_sum.remote(*args)
        future = simple_arithmetic.remote(*args, val = add_future)

        print(f"Client: Future returned: {future.get()}")


    kwarg_future_test()

    '''
    for i in range(1, 100):
        @hive.remote(server='localhost', server_port=8081)
        def simplemult(x: int, y: int) -> int:
            time.sleep(5)
            return x * y

        ex_args2 = [5*i, 10*i]
        future = simplemult.remote(*ex_args2)
        print("Thread {}: Future Returned".format(i))

        print("Thread {}: Do Other Work Here...".format(i))

        value = future.get()
        print("Thread {}: Value Returned: {}".format(i, value))

        stored_values = hive.store.get(future.get_id())
        print("Thread {}: Value Stored: {}".format(i, stored_values))
    '''
        
        