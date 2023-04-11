from src.hive import HiveCore


if __name__ == '__main__':
    hive = HiveCore()
    
    ex_args = [32, 478]

    @hive.remote(server='localhost', server_port=8080)
    def simplesum(x: int, y: int) -> int:
        return x + y

    res = simplesum.remote(*ex_args)
    print("Success:", res)