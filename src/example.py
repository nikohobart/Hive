import hive


if __name__ == '__main__':
    ex_args = [32, 478]
    
    @hive.remote(server='localhost')
    def simplesum(x: int, y: int) -> int:
        return x + y
    
    res = simplesum.remote(*ex_args)
    print("Success:", res)