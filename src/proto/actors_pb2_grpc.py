# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

#import actors_pb2 as actors__pb2
from src.proto import actors_pb2 as actors__pb2

class ActorServiceStub(object):
    """Service responsible for actors
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RegisterActor = channel.unary_unary(
                '/actors.ActorService/RegisterActor',
                request_serializer=actors__pb2.RegisterRequest.SerializeToString,
                response_deserializer=actors__pb2.ActorState.FromString,
                )
        self.UpdateActor = channel.unary_unary(
                '/actors.ActorService/UpdateActor',
                request_serializer=actors__pb2.UpdateRequest.SerializeToString,
                response_deserializer=actors__pb2.ActorState.FromString,
                )


class ActorServiceServicer(object):
    """Service responsible for actors
    """

    def RegisterActor(self, request, context):
        """Registers an actor with the scheduler
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateActor(self, request, context):
        """Updates an actor on a server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ActorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RegisterActor': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterActor,
                    request_deserializer=actors__pb2.RegisterRequest.FromString,
                    response_serializer=actors__pb2.ActorState.SerializeToString,
            ),
            'UpdateActor': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateActor,
                    request_deserializer=actors__pb2.UpdateRequest.FromString,
                    response_serializer=actors__pb2.ActorState.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'actors.ActorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ActorService(object):
    """Service responsible for actors
    """

    @staticmethod
    def RegisterActor(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/actors.ActorService/RegisterActor',
            actors__pb2.RegisterRequest.SerializeToString,
            actors__pb2.ActorState.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateActor(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/actors.ActorService/UpdateActor',
            actors__pb2.UpdateRequest.SerializeToString,
            actors__pb2.ActorState.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
