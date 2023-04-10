
class Future:
    _lastId = 0

    def __init__(self):
        Future._lastId + 1
        self._object_id = Future._lastId
        self._result = None
        self._exception = None

    def set_result(self, result):
        self._result = result
    
    def set_exception(self, exception):
        self._exception = exception
    
    def get(self):
        if self._exception:
            raise self._exception
        return self._result
    
    def done(self):
        return self._result is not None or self._exception is not None