class Task:
    __id = 0

    def __init__(self, func, args, kwargs = None):
        Task.__id += 1
        self.id = Task.__id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        

    def execute(self):
        result = self.func(*self.args, **self.kwargs)
        return result