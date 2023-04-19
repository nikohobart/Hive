import numpy as np
import time

from src.hive import HiveCore

np.random.seed(0)

n_workers = 3
workers = [f"localhost:{5000 + i}" for i in range(10)]

hive = HiveCore("Locality Aware", workers[:n_workers])

def seq_lineq(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    x = np.linalg.solve(A, b)

    return x

@hive.remote()
def hive_lineq(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    x = np.linalg.solve(A, b)

    return x

def seq_benchmark(n_tasks, size):
    results = []
    start = time.time()
    for i in range(n_tasks):
        res = seq_lineq(size)
        results.append(res)
    return time.time() - start

def hive_benchmark(n_tasks, size):
    futures = []
    start = time.time()
    for i in range(n_tasks):
        future = hive_lineq.remote(size)
        futures.append(future)
    values = [future.get() for future in futures]
    return time.time() - start


if __name__ == '__main__':
    # Number of experiment iterations
    iters = 5

    # List of matrix sizes and number of tasks per iteration
    sizes = [500 * (n + 1) for n in range(10)]
    n_tasks = [i + 1 for i in range(10)]

    seq_sizes = []
    hive_sizes = []

    # # Varies matrix size
    # for size in sizes:
    #     print(f"______________________________ \n Running benchmark with {iters} iterations, {n_workers} workers, {size} size, and 5 tasks: \n ______________________________")

    #     seq_total = 0
    #     hive_total = 0

    #     for iter in range(iters):
    #         seq_time = seq_benchmark(5, size)
    #         hive_time = hive_benchmark(5, size)       

    #         seq_total += seq_time
    #         hive_total += hive_time

    #     print(f"Sequential took {seq_total/iters} seconds on average")
    #     print(f"Hive took {hive_total/iters} seconds on average")

    # # Varies number of tasks per iteration
    # for n_task in n_tasks:
    #     print(f"______________________________ \n Running benchmark with {iters} iterations, {n_workers} workers, 2500 size, and {n_task} tasks: \n ______________________________")

    #     seq_total = 0
    #     hive_total = 0

    #     for iter in range(iters):
    #         seq_time = seq_benchmark(n_task, 2500)
    #         hive_time = hive_benchmark(n_task, 2500)       

    #         seq_total += seq_time
    #         hive_total += hive_time

    #     print(f"Sequential took {seq_total/iters} seconds on average")
    #     print(f"Hive took {hive_total/iters} seconds on average")

    # Run this to vary number of workers.  Change n_workers on line 8
    print(f"______________________________ \n Running benchmark with {iters} iterations, {n_workers} workers, 2500 size, and 10 tasks: \n ______________________________")

    hive_total = 0

    for iter in range(iters):
        hive_time = hive_benchmark(10, 2500)      
        hive_total += hive_time

    print(f"Hive took {hive_total/iters} seconds on average")
