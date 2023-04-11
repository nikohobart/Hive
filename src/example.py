import hive
import time


if __name__ == '__main__':

    h = hive.HiveCore()
    ex_args = [42, 478]
    
    @h.remote(server='localhost', server_port=8080)
    def simplesum(x: int, y: int) -> int:
        time.sleep(10)
        return x + y
    
    res = simplesum.remote(*ex_args)
    print("Future Returned")

    print("Value Returned", res.get())