import numpy as np
import time

from hive import HiveCore


hive = HiveCore()


@hive.remote(server_port=8080)
def lineqn_solve(n=10000):
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

@hive.remote(server_port=8081)
def matrix_mult(n=10000):
    # Generate two large random matrices
    n = 10000
    m = n // 2
    A = np.random.rand(n, m)
    B = np.random.rand(m, m)
    C = np.random.rand(m, 1)

    # Perform matrix multiplication using numpy.dot()
    start_time = time.time()
    D = np.dot(np.dot(A, B), C)
    end_time = time.time()

    print("Time taken for matrix multiplication:", end_time - start_time, "seconds")
    return D

if __name__ == '__main__':
    start_time = time.time()
    future1 = lineqn_solve.remote()
    print("Thread 1: Future Returned")

    print("Thread 1: Do Other Work Here...")
    future2 = matrix_mult.remote()

    value1 = future1.get()
    print("Thread 1: Value 1 Returned:", value1)
    
    value2 = future2.get()
    print("Thread 1: Value 2 Returned:", value2)
    
    print("Output: {} + {} = {}".format(value1, value2, value1+value2))
    print("Took {} seconds".format(time.time() - start_time))

    stored_values1 = hive.store.get(future1._object_id)
    stored_values2 = hive.store.get(future2._object_id)
    print("Thread 1: Values Stored:", *stored_values1)
    print("Thread 1: Values Stored:", *stored_values2)