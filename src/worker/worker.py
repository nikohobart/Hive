from concurrent import futures
import logging
import signal
import sys

import grpc
from src.proto import worker_pb2_grpc
from src.proto import driver_pb2_grpc
from src.services.worker_service import WorkerService
from src.services.driver_service import DriverService


class Server(object):
    
    @property
    def instance(self):
        return self.__server
    
    def __init__(self, address='localhost', port=8080, max_workers=10):
        self.__address = address
        self.__port = port
        self.__server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        
    def serve(self):
        endpoint = f'{self.__address}:{str(self.__port)}'

        print(f'Started server at {endpoint}')
        print('Serving...')

        self.__server.add_insecure_port(endpoint)
        self.__server.start()
        self.__server.wait_for_termination()

    def stop(self):
        print("Stopping server gracefully")
        self.__server.stop(3)        


def add_services(server):
    worker_pb2_grpc.add_WorkerServiceServicer_to_server(WorkerService(), server)
    driver_pb2_grpc.add_DriverServiceServicer_to_server(DriverService(), server)
    
    
def signalHandler(signal, frame):
    print('Process Interrupted!\n\a')
    server.stop()
    sys.exit(0)
    

if __name__ == '__main__':
    logging.basicConfig()
    
    server = Server()
    signal.signal(signal.SIGINT, signalHandler)
    
    add_services(server.instance)
    server.serve()