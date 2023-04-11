import heapq
from src.proto import worker_pb2
from src.proto import worker_pb2_grpc

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
            
            resourceLoadResponse = tasks_stub.GetLoad(worker_pb2.LoadRequest())

            print("CPU Load: {}%".format(resourceLoadResponse.cpu_load))
            print("Memory Used: {}%".format(resourceLoadResponse.memory_used))
            
            # sort by cpu load, then by memory used
            server_load_tuple = (resourceLoadResponse.cpu_load, resourceLoadResponse.memory_used, server)
            
            heapq.heappush(self.loadPQ, server_load_tuple)

            # print("Sorted server loads:")
            # while self.server_load_priority_queue:
            #     cpu_load, memory_used, server_address = heapq.heappop(server_load_priority_queue)
            #     print(f"{server_address}: CPU Load: {cpu_load}%, Memory Used: {memory_used} bytes")
    
    def getServer(self, tasks_stub):
        self.UpdateServerQueue(tasks_stub)
        return self.loadPQ[0][2]
