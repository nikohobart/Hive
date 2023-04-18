import numpy as np
import pyperf
import time

from hive import HiveCore


workers = ["localhost:5000", "localhost:5001", "localhost:5002", "localhost:5003", "localhost:5004"]
np.random.seed(0)
hive = HiveCore(workers)

@hive.remote()
def lineqn0(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

@hive.remote()
def lineqn1(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

@hive.remote()
def lineqn2(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

@hive.remote()
def lineqn3(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

@hive.remote()
def lineqn4(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

@hive.remote()
def lineqn5(n=10000):
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    start_time = time.time()
    x = np.linalg.solve(A, b)
    end_time = time.time()
    
    print("Time taken for solving the linear equation:", end_time - start_time, "seconds")
    return x

def lineqn(n=10000):
    #start_time = time.time()
    
    # Generate a large random matrix
    A = np.random.rand(n, n)

    # Generate a random vector b
    b = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    x = np.linalg.solve(A, b)
    
    # print("Time taken for solving the linear equation:", time.time() - start_time, "seconds")
    return x


if __name__ == '__main__':
    funcs = [lineqn0, lineqn1, lineqn2, lineqn3, lineqn4, lineqn5][0:5] # [s_ind, e_ind)
    matrix_sizes = [10, 100, 1000, 5000, 10000][4:5] # [s_ind, e_ind)
    for size in matrix_sizes:
        print("\nRunning sequential benchmark with size {}.\n".format(size))
        
        results = []
        start_time = time.time()
        for func in funcs:
            res = lineqn(size)
            results.append(res)
        seq_time = time.time() - start_time
        
        print("\nEnd. Starting Hive loop with size {}.\n".format(size))
        
        futures = []
        start_time = time.time()
        for func in funcs:
            future = func.remote(size)
            futures.append(future)
            
        values = [future.get() for future in futures]
        print("\nSequential took {} seconds".format(seq_time))
        print("Hive took {} seconds".format(time.time() - start_time))
        print("Loop done.\n")
