from src.proto import driver_pb2
from src.proto import driver_pb2_grpc
from src.worker import object_store
from src.util import serialization


class DriverService(driver_pb2_grpc.DriverServiceServicer):
    pass