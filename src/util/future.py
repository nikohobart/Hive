import uuid

class Future:
    def __init__(self):
        self._object_id = uuid.uuid1()
        self._result = None
        self._exception = None

    def set_result(self, result):
        self._result = result
    
    def set_exception(self, exception):
        self._exception = exception
    
    def get(self):
        while not self.done():
            pass
        if self._exception:
            raise self._exception
        else:
            return self._result
    
    def done(self):
        return self._result is not None or self._exception is not None