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

    for i in range(1, 6):
        @hive.remote(server='localhost', server_port=8081)
        def simplemult(x: int, y: int) -> int:
            time.sleep(5)
            return x * y

        ex_args2 = [5*i, 10*i]
        future = simplemult.remote(*ex_args2)
        print("Thread {}: Future Returned".format(i))

        print("Thread {}: Do Other Work Here...".format(i))

        value = future.get()
        print("Thread {}: Value Returned: {}".format(i, value))

        stored_values = hive.store.get(future._object_id)
        print("Thread {}: Value Stored: {}".format(i, *stored_values))