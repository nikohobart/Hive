import cloudpickle
import logging

import grpc
from proto import actors_pb2
from proto import actors_pb2_grpc
from proto import tasks_pb2
from proto import tasks_pb2_grpc


class Client(object):
    """Client used for sending actor and task execution requests
    """
    
    def __init__(self, server='localhost', server_port=50051):
        # configure the host and the
        # the port to which the client should connect to
        self.host = server
        self.server_port = server_port

        # instantiate a communication channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client to the task service server channel and
        # the actor service server channel
        self.tasks_stub = tasks_pb2_grpc.TaskServiceStub(self.channel)
        self.actors_stub = actors_pb2_grpc.ActorServiceStub(self.channel)
        
        # self task id generator 
        #TODO: this should probably be moved to a different part of the architecture
        self.task_iter = 0
        
    def get_execute_task(self, f: callable, args: list):
        """Executes task on client's host

        Args:
            f (callable): function to be executed
            args (list): arguments for function
            
        Returns:
        any: the value retrieved from the remote call
        """
        print('Serializing function ({}) and arguments ({})'.format(f.__name__, args))
        bin_func = cloudpickle.dumps(f)
        bin_args = cloudpickle.dumps(args)
        
        print("Sending function to worker ({}:{})".format(self.host, self.server_port))
        response = self.tasks_stub.ExecuteTask(tasks_pb2.ExecuteRequest(
            task_id=int.to_bytes(self.task_iter), function=bin_func, args=bin_args
        ))
        self.task_iter += 1
        
        result = cloudpickle.loads(response.result)
        print("Response received:", result)
        return result
        
    def set_actor(self, obj: object):
        """Sets an actor on client's host

        Args:
            obj (object): object to be turned into an actor
        """
        print('Serializing object: {}'.format(obj))
        bin_obj = cloudpickle.dumps(obj)
        
        print("Sending object to worker ({})".format(self.host))
        response = self.actors_stub.RegisterActor(actors_pb2.RegisterRequest(
            actor_id=int.to_bytes(1), owner_id=int.to_bytes(1), obj=bin_obj #TODO: currently just sets to 1 everytime
        ))
        
        result = cloudpickle.loads(response.obj)
        print("Response received:", result)
        
    #FIXME: not working
    def get_actor_task(self, f: callable):
        bin_func = cloudpickle.dumps(f)
        
        response = self.actors_stub.UpdateActor(actors_pb2.UpdateRequest(
            actor_id=int.to_bytes(self.task_iter), owner_id=bin_func, function=bin_func, #args=
        ))
        
        result = cloudpickle.loads(response.obj)
        print("Response received:", result)
        
    
if __name__ == '__main__':
    logging.basicConfig()
    
    client = Client()
    
    # example function and args
    ex_args = [32, 478]
    def ex_func(x: int, y: int) -> int:
        return x + y
    
    # example class
    class Dog:
        def __init__(self, name="Bolt"):
            self.name = name
            self.speed = 1
        
        def train(self):
            self.speed += 1
            print("{} now has a speed of {}".format(self.name, self.speed))
        
        def bark(self):
            print("{} just barked! that was loud...".format(self.name))
            
        def __str__(self):
            return "{} the dog with a speed of {}".format(self.name, self.speed)
    
    client.get_execute_task(ex_func, ex_args)
    d = Dog("Dennis")
    client.set_actor(d)
    # for i in range(3):
    #     client.get_actor_task(d.train)
    