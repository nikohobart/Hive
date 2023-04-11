import uuid

class Future:
    def __init__(self):
        self.__object_id = uuid.uuid1()
        self.__result = None
        self.__exception = None

    def set_result(self, result):
        self.__result = result
    
    def set_exception(self, exception):
        self.__exception = exception

    def get_id(self):
        return self.__object_id
    
    def get(self):
        while self.__result is None and self.__exception is None:
            pass
        if self.__exception:
            raise self.__exception
        return self.__result
    
    def done(self):
        return self.__result is not None or self.__exception is not None