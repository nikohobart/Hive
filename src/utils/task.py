import uuid

class Task:
    def __init__(self, func, args, kwargs = None):
        self.id = uuid.uuid1().int>>64
        self.func = func
        self.args = args
        self.kwargs = kwargs
        

    def execute(self):
        result = self.func(*self.args, **self.kwargs)
        return result