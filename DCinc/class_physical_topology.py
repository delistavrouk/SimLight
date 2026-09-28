from hiero.codeGusLibQueOOP import *
from hiero.class_node import Node
from hiero.class_link import Link

class PhysicalTopology:
    
    #if you declare valriables here (on top of the class) they belong to the class, not the object instances of the class

    '''
    def __init__(self, filepath):
        data = readData(filepath) # read network definition from text file
        (
            self.netName, 
            self.N, 
            self.L, 
            self.Nm, 
            self.Dist, 
            self.HasWavConv
        ) = data
    '''

    def __init__(self, log_filepath):

        # 1. Read the raw data
        netName, N, L, Nm, Dist, HasWavConv = readData(log_filepath)
        
        self.netName = netName
        
        # 2. Build the Node objects
        # We will store them in a dictionary for easy lookup by their ID
        self.nodes = {} 
        
        for node_id in range(len(N)):
            # Extract the specific data for this node from the raw lists/dicts
            name = N[node_id]
            has_conv = HasWavConv[node_id] 
            neighbors = Nm[node_id]

            # Create the Node object and save it
            self.nodes[node_id] = Node(node_id, name, neighbors, has_conv)

        # 3. Build the Link objects
        self.links = {}
        
        for i, link_data in enumerate(L):
            src = link_data[0]   # L = [[0,1], [1,2], [2,3], ...]
            dst = link_data[1]
            distance = Dist[i]   # Dist = [182.0, 270.0, 341.0, ...]
            
            # Create the Link object and save it
            self.links[i] = Link(src, dst, distance)
        
        #print (self.nodes)
        #print (self.links)

        self.G = (self.nodes, self.links) 

        self.EDFAdist = 80.0 #An EDFA is deployed every 80km. Link route: EDFA at node, [EDFA at 80km, ...]
        self.S = self.EDFAdist # span distance between two neighbouring inline EDFAs
        self.maxIProuterPorts = 32 #for Shen-Tucker test network (a) only 

        self.maxFibersPerLink = None
        self.maxWavelengthsPerFiber = None
        self.maxGbpsPerWavelength = None

    def getNt(self):
        # Nt is the list of nodes expressed as a tuple

        #2DO >>> will need to convert it 
        self.Nt = nodes2tuple(self.N)

        return self.Nt

    def getNmC(self):
        # Nmc is the network graph as a dictionary of dictionaries with transition costs
        self.NmC = networkWithCosts(self.Nm,self.Nt,self.L,self.Dist)

        return self.NmC

    def __repr__(self):
        str  = f"PhysicalTopology (G) (NetworkName={self.netName}, "
        str += f"Nodes (N) ({self.nodes}), "
        str += f"Links (L) ({self.links}))"
        return str
    
   