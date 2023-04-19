import numpy as np
import pyperf
import time

from hive import HiveCore


workers = ["localhost:5000", "localhost:5001"]
np.random.seed(0)
hive = HiveCore("Round Robin", workers)

@hive.remote(server='localhost', server_port=8080)
def mat_sum(*args):
    result = np.add(args[0], args[1])
    return result
    
@hive.remote(server='localhost', server_port=8081)
def mat_mult(*args):
    result = np.dot(args[0], args[1])
    return result


def matPerfRemote(n=1000):
    #start_time = time.time()
    
    a = np.random.rand(n, n)
    b = np.random.rand(n)
    c = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    multFuture = mat_mult.remote(a, b) 
    sumFuture = mat_sum.remote(multFuture, c)

def matPerf(n=1000):
    #start_time = time.time()
    
    a = np.random.rand(n, n)
    b = np.random.rand(n)
    c = np.random.rand(n)

    # Solve the linear equation Ax = b using numpy.linalg.solve()
    mult = np.dot(a, b) 
    sum = np.add(mult, c)


if __name__ == '__main__':
    matrix_sizes = [10, 50, 100, 300, 500] # [s_ind, e_ind)
    for size in matrix_sizes:
        print("\nRunning sequential benchmark with size {}.\n".format(size))
        
        results = []
        start_time = time.time()
        matPerf(size)
        seq_time = time.time() - start_time
        
        print("\nEnd. Starting Hive loop with size {}.\n".format(size))
        
        matPerfRemote(size)
            
        print("\nSequential took {} seconds".format(seq_time))
        print("Loop done.\n")