import argparse
import logging
import signal
import sys

from concurrent import futures

import grpc
from src.proto import driverworker_pb2_grpc
from src.proto import workerworker_pb2_grpc
from src.services.driverworker_service import DriverWorkerService
from src.services.workerworker_service import WorkerWorkerService
from src.worker.object_store import ObjectStore


class Server(object):

    @property
    def instance(self):
        return self.__server
    
    def __init__(self, address='localhost', port=5000, max_workers=10):
        self.__address = address
        self.__port = port
        self.__server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        self.__object_store = ObjectStore()

        self.__add_services()
        
    def serve(self):
        print(f"Server {self.__address}:{self.__port}: Starting")

        endpoint = f"{self.__address}:{self.__port}"
        self.__server.add_insecure_port(endpoint)
        self.__server.start()
        self.__server.wait_for_termination()

    def stop(self):
        print(f"Server {self.__address}:{self.__port}: Stopping")
        self.__server.stop(3)        

    def __add_services(self):
        driverworker_pb2_grpc.add_DriverWorkerServiceServicer_to_server(DriverWorkerService(self.__object_store, self.__address, self.__port), self.__server)
        workerworker_pb2_grpc.add_WorkerWorkerServiceServicer_to_server(WorkerWorkerService(self.__object_store, self.__address, self.__port), self.__server)
    
    
def signalHandler(signal, frame):
    print('Process Interrupted!\n\a')
    server.stop()
    sys.exit(0)
    

if __name__ == '__main__':
    logging.basicConfig()
    
    parser = argparse.ArgumentParser(description='Runs a Hive worker')
    parser.add_argument('-p', '--port', type=int, help='Port Number', required=True)
    args = parser.parse_args()

    server = Server(port=args.port)
    signal.signal(signal.SIGINT, signalHandler)
    server.serve()