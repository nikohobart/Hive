import numpy as np
import time

from src.hive import HiveCore

np.random.seed(0)

workers = [f"localhost:{5000 + i}" for i in range(10)]

hive = HiveCore("Round Robin", workers)

@hive.remote()
def mat_sum(*args):
    result = np.add(args[0], args[1])
    return result

@hive.remote()
def mat_mult(*args):
    result = np.dot(args[0], args[1])
    return result

@hive.remote()
def add(*args):
    time.sleep(1)
    sum = 0
    for arg in args:
        sum += arg
    return sum

def matPerfRemote(n=1000):
    a = np.random.rand(n, n)
    b = np.random.rand(n)
    c = np.random.rand(n)

    multFuture = mat_mult.remote(a, b) 
    sumFuture = mat_sum.remote(multFuture, c)

def matPerf(n=1000):
    a = np.random.rand(n, n)
    b = np.random.rand(n)
    c = np.random.rand(n)

    mult = np.dot(a, b) 
    sum = np.add(mult, c)

def locality_task(n_tasks):
    futures = []
    values = []
    times = []
    for i in range(n_tasks):
        start = time.time()
        future = add.remote(*futures[:i])
        futures.append(future)
        values.append(future.get())
        times.append(time.time() - start)
    return times

if __name__ == '__main__':
    # Number of experiment iterations
    iters = 5
    n_tasks = 10

    # Varies matrix size
    print(f"______________________________ \n Running benchmark with {iters} iterations, {n_tasks} tasks: \n ______________________________")

    times_total = [0 for i in range(n_tasks)]

    for iter in range(iters):
        times = locality_task(n_tasks)
        times_total = [times_total[i] + times[i] for i in range(n_tasks)]

    times_total = [t/iters for t in times_total]

    print(f"Hive took {times_total} seconds for different numbers of futures.")


# if __name__ == '__main__':
#     matrix_sizes = [10, 50, 100, 300, 500] # [s_ind, e_ind)
#     for size in matrix_sizes:
#         print("\nRunning sequential benchmark with size {}.\n".format(size))

#         results = []
#         start_time = time.time()
#         matPerf(size)
#         seq_time = time.time() - start_time

#         print("\nEnd. Starting Hive loop with size {}.\n".format(size))

#         matPerfRemote(size)

#         print("\nSequential took {} seconds".format(seq_time))
#         print("Loop done.\n")