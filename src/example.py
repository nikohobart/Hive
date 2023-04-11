import time

from src.hive import HiveCore


if __name__ == '__main__':
    hive = HiveCore()
    
    ex_args = [32, 478]
    
    @hive.remote(server='localhost', server_port=8080)
    def simplesum(x: int, y: int) -> int:
        time.sleep(5)
        return x + y
    
    future = simplesum.remote(*ex_args)
    print("Thread 1: Future Returned")

    print("Thread 1: Do Other Work Here...")

    value = future.get()
    print("Thread 1: Value Returned:", value)

    stored_values = hive.store.get(future._object_id)
    print("Thread 1: Value Stored:", *stored_values)