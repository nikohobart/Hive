import time

from src.hive import HiveCore

if __name__ == '__main__':
    workers = ["localhost:5000", "localhost:5001", "localhost:5002"]

    hive = HiveCore(workers)
    
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
        mult_future = simple_mult.remote(3, add_future)

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


    def simple_fibonnaci():
        fibonacci = [1, 1]
        for i in range(20):
            fibonacci.append(simple_sum.remote(fibonacci[i], fibonacci[i + 1]))
        print(fibonacci[21].get())

    kwarg_future_test()

    