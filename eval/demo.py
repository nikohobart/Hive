import time

from src.hive import HiveCore

workers = ["localhost:5000", "localhost:5001"]
hive = HiveCore(workers)

@hive.remote()
def simple_sum(*args):
    time.sleep(5)
    sum = 0
    for arg in args:
        sum += arg
    return sum

@hive.remote()
def simple_mult(*args):
    time.sleep(5)
    prod = 1
    for arg in args:
        prod *= arg
    return prod

def simple_demo():
    add_future = simple_sum.remote(53, 47)

    while not add_future.done():
        print(f"Client: Do other work here...")

    print(f"Client: Future returned: {add_future.get()}")

simple_demo()

def future_demo():
    add_future = simple_sum.remote(6, 9)
    mult_future = simple_mult.remote(4, add_future)

    while not mult_future.done():
        print(f"Client: Do other work here...")

    print(f"Client: Future returned: {mult_future.get()}")

future_demo()
