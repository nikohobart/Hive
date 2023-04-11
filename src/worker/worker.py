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
    driverworker_pb2_grpc.add_DriverWorkerServiceServicer_to_server(DriverWorkerService(), server)
    workerworker_pb2_grpc.add_WorkerWorkerServiceServicer_to_server(WorkerWorkerService(), server)
    
    
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
    
    add_services(server.instance)
    server.serve()