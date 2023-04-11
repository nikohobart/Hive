import heapq
from src.proto import driverworker_pb2
from src.proto import driverworker_pb2_grpc
from src.utils import serialization

class WorkerPQ:

    def __init__(self, serverAddresses):
        self.servers = serverAddresses
        self.loadPQ = []
    
    def addServer(self, server):
        self.servers.add(server)

    def removeServer(self, server):
        if server in self.servers:
            self.servers.remove(server)

    # update the server load priority queue by getting the resource load from each server
    def UpdateServerQueue(self, tasks_stub):
        for server in self.servers:
            resourceLoadResponse = tasks_stub.GetLoad(driverworker_pb2.LoadRequest())
            cur_cpu_load = serialization.deserialize(resourceLoadResponse.cpu_load)
            cur_mem_used = serialization.deserialize(resourceLoadResponse.memory_used)

            print("CPU Load: {}%".format(cur_cpu_load))
            print("Memory Used: {}%".format(cur_mem_used))
            
            # sort by cpu load, then by memory used
            server_load_tuple = (cur_cpu_load, cur_mem_used, server)
            
            heapq.heappush(self.loadPQ, server_load_tuple)

            # print("Sorted server loads:")
            # while self.server_load_priority_queue:
            #     cpu_load, memory_used, server_address = heapq.heappop(server_load_priority_queue)
            #     print(f"{server_address}: CPU Load: {cpu_load}%, Memory Used: {memory_used} bytes")
    
    def getServer(self, tasks_stub):
        self.UpdateServerQueue(tasks_stub)
        return self.loadPQ[0][2]
