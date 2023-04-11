import numpy as np
import time


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
    value1 = lineqn_solve()
    value2 = matrix_mult()
    
    print("Output: {} + {} = {}".format(value1, value2, value1+value2))
    print("Took {} seconds".format(time.time() - start_time))