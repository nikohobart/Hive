import random
import time

from src.hive import HiveCore

workers = [f"localhost:{5000 + i}" for i in range(5)]

hive = HiveCore("Locality Aware", workers)

@hive.remote()
def add(*args):
    time.sleep(1)
    sum = 0
    for arg in args:
        sum += arg
    return sum

def non_locality_task(n_tasks):
    futures = []
    start = time.time()
    for i in range(n_tasks):
        future = add.remote(1, 1)
        futures.append(future)
    values = [future.get() for future in futures]
    return time.time() - start

def locality_task(n_tasks):
    futures = []
    start = time.time()
    for i in range(n_tasks):
        future = add.remote(*futures[:i])
        futures.append(future)
    values = [future.get() for future in futures]
    return time.time() - start

if __name__ == '__main__':
    # Number of experiment iterations
    iters = 5
    n_tasks = 10

    # Varies matrix size
    print(f"______________________________ \n Running benchmark with {iters} iterations, {n_tasks} tasks: \n ______________________________")

    non_locality = 0
    locality = 0

    for iter in range(iters):
        non_locality += non_locality_task(n_tasks)
        locality += locality_task(n_tasks)

    print(f"Hive took {non_locality/iters} seconds on average for the non-locality test")
    print(f"Hive took {locality/iters} seconds on average for the locality test")