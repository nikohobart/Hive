import cloudpickle

from src.proto import actors_pb2
from src.proto import actors_pb2_grpc


class ActorService(actors_pb2_grpc.ActorServiceServicer):
    def __init__(self, actor=None):
        self.actor = actor
    
    def RegisterActor(self, request, context):
        print("RegisterActor RPC Called")
        
        # assign object to this server's actor service
        self.actor = cloudpickle.loads(request.obj)
        
        # return result to client
        print("Returning:", self.actor)
        return actors_pb2.ActorState(obj=cloudpickle.dumps(self.actor))
    
    def UpdateActor(self, request, context):
        print("UpdateActor RPC Called")
        
        func = cloudpickle.loads(request.function)
        print("Received task ({}) with args ({})".format(func.__name__, None))
        
        func() # FIXME: temporary stand in since not working
        
        # return result to client
        print("Returning:", self.actor)
        return actors_pb2.ActorState(obj=cloudpickle.dumps(self.actor))