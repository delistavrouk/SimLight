from hiero.codeGusLibQueOOP import *
from hiero.class_traffic_demands import TrafficDemands
import uuid
import timeit
import numpy # type: ignore

class CurrentRun:
    def __init__(self, sysArgv):

        numpy.set_printoptions(legacy='1.21')

        self.UUID = str(uuid.uuid4())
        SetGlobalCurrentRunUUID(self.UUID)

        self.networkFile = sysArgv[1]
        self.xi = int(sysArgv[2])
        
        #set the name of the experment
        if ( sysArgv[3] != ""):
            self.experimentName = sysArgv[3]
        else:
            self.experimentName = "Default Experiment"

        # SOP: Start of printout
        # EOP: End of printout
        if (sysArgv[4]=="detailreport"):
            self.GlobalSOP = True
        else:
            self.GlobalSOP = False
        SetGlobalPrintout(self.GlobalSOP)


        #set the name of the algorithm
        if sysArgv[8] == "2":
            self.algorithm = "HybridBypass"
            self.TrafficClassNames = ["High Priority", "Low Priority"]
        else:
            #self.algorithm = "NotApplicable"
            #error("Hybrid Bypass has been asked to run using one (1) queue,",7)
            error("Hybrid Bypass runs on two traffic classes",8)
        
        #23-6-2026
        #if sys.argv[8] == "1":
        #    QueueNames = ["Single"]
        #elif sys.argv[8] == "2":
        #    QueueNames = ["High Priority", "Low Priority"]
        #elif sys.argv[8] == "2mix":
        #    QueueNames = ["High Priority", "Low Priority"]
        #elif sys.argv[8] == "2seq":
        #    QueueNames = ["High Priority", "Low Priority"]
        #
        #lenQs = len(QueueNames)

        #self.TDVectors = sysArgv[8] #old self.lenQs
        
        #TD = TrafficDemands(self.TDVectors, self.xi)

        self.computername = sys.argv[10]
        self.programfolder = sys.argv[11]
        self.appDir = self.programfolder

        self.maxFibersPerLink = int(sysArgv[14]) #= 16
        self.maxWavelengthsPerFiber = int(sysArgv[15]) #= 4 #max 16 wavelengths are multiplexed in each fiber
        self.maxGbpsPerWavelength = int(sysArgv[16]) #= 40.0   #max wavelength capacity is 40 Gbps


    def getComputerName(self):
        return self.computername
    
    def getTrafficClassNames(self):
        return self.TrafficClassNames
        
    def getProgramFolder(self):
        return self.programfolder
    
    def getAppDir(self):
        return self.appDir

    def setStartProcessingTime(self):
        self.start_processtime = timeit.default_timer()

    def getGlobalSOP(self):
        return self.GlobalSOP

    def getExperimentName(self):
        return self.experimentName
    
    def getNetworkFile(self):
        return self.networkFile
    
    def getXi(self):
        return self.xi
    
    def setPhysicalTopologyOperationalParamters(self, PTobject):
        
        """
        Since pt_object is passed by reference, any changes made 
        here will reflect directly in the PT object in the main program.
        """
        
        PTobject.maxFibersPerLink = self.maxFibersPerLink
        PTobject.maxWavelengthsPerFiber = self.maxWavelengthsPerFiber
        PTobject.maxGbpsPerWavelength = self.maxGbpsPerWavelength
        
        

    def __repr__(self):
        str  = f"PhysicalTopology (G) (NetworkName={self.netName}, "
        str += f"Nodes (N) ({self.nodes}), "
        str += f"Links (L) ({self.links}))"
        return str