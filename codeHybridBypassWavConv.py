# -*- coding: utf-8 -*-

# SimLight by Konstantinos Delistavrou 2021, 2022, 2023, 2024, 2025, 2026
# Hybrid Bypass algorithm by Konstantinos Delistavrou, 2024
#
# command line arguments
#
# argv[0]	program file name
# argv[1]	network definition text file name
# argv[2]	average traffic load (X) index, where 0: X=2 Gbps, 1: X=4 Gbps, 2: X=6 Gbps, 3: X=8 Gbps, 4: X=10 Gbps, 5: X=15 Gbps, 6: X=20 Gbps, 7: X=30 Gbps, 8: X=40 Gbps, 9: X=50 Gbps, 10: X=60 Gbps, 11: X=80 Gbps, 12: X=100 Gbps, 13: X=120 Gbps, 14: X=160 Gbps, 15: X=200 Gbps, 16: X=320 Gbps, 17: X=640 Gbps, 18: X=960 Gbps, 19: X=1280 Gbps
# argv[3]	set the name of the experment
# argv[4]	execution report details
# argv[5]	generate random traffic demands or load them
# argv[6]	traffic demands text file name
# argv[7]	output execution report as pdf
# argv[8]	number of traffic demand queues
# argv[9]	keep the report and other generated files after the execution of the program
# argv[10]  name of the computer that execution takes place
# argv[11]  program folder path under: the root folder (on MS Windows), or the home folder (on GNU/Linux)
# argv[12]  distribution of random traffic loads
# argv[13]  scheduling strategy
# argv[14]  number of fibers per link (f)
# argv[15]  number of wavelengths per fiber (W)
# argv[16]  wavelength capacity (C)
# argv[17]  IP router port latency (Lr)
# argv[18]  WDM transponder latency (Lt)
# argv[19]  traffic share percent of Q_{HP} (percent) (traffic sgare of Q_{LP} is 100-argv[19])
# argv[20]  check for revisits on traffic grooming
# argv[21]  hard latency cap threshold for Q_{HP} (microsecond)
# argv[22]  hard latency cap threshold for Q_{LP} (microsecond)
# argv[23]  virtual Gbps Per Wavelength for Q_{HP} (Gbps)
# argv[24]  wavelength converter latency (microsecond)
# argv[25]  wavelength converter power consumption (Watt)
# argv[26]  number of shortest paths to consider during wavelength assignment : 1 will utilise Dijkstra's shortest path algorithm for the shortest path only, block traffic otherwise
#                                                                               k will try utilise Yen's algorithm to discover the 2nd, 3rd, ... k-th shortest alternatives, blocking traffic if wavelength assignment fails for all
#
# example
#
# python codeHybridBypass.py N6L8_STnet_NoWavConv.txt 9 TestRun detailreport gensave Traffic-Requests.txt nopdf 2 keepreport Laptop C:\simlight Uniform Hybrid2Q -1 3 100 30 100 50 CheckForRevisits -1.0 -1.0
# 
# dependencies
#
# install...
# pip install numpy   # NumPy library used for calculations
# pip install networkx
# pip install pyvis # PyVis used for visualisations
#                     network visualisation https://pyvis.readthedocs.io/en/latest/tutorial.html
#                                           https://pyvis.readthedocs.io/en/latest/install.html
# download sqlite-dll-win-x64-3450200.zip from https://www.sqlite.org/download.html, unpack, and copy sqlite sqlite3.dll and sqlite3.def files to the application directory
# to save as pdf install software for OS from https://wkhtmltopdf.org/
#                                             https://wkhtmltopdf.org/downloads.html
#                install wrapper for python $pip install pdfkit
#
#Legend... .................................................
#
#2DO : elaboration needed
#Done : elaboration completed
#>>> : elaboration priority
#
# SOP: Start of printout
# EOP: End of printout
# use ...
#     # SOP
#     if (GlobalSOP==True) :
#     ...
#     # EOP
#
#~><Section>: start of code section
# section statements
#~></Section>: end of code section
#
#...........................................................

from pydoc import doc
from turtle import update
from webbrowser import get
import sys
import numpy # type: ignore
import time
import timeit
from datetime import datetime
#from codeGusLibQueues import *
from random import randrange
import platform
import uuid
from DCinc.codeGusLibQueOOP import *
from DCinc.class_stderr_in_memory import stderrInMemory
from DCinc.module_utilspathslinks import *
from DCinc.class_spreadsheet import *


#fsqlInsert = open("SQL_INSERTINTO_RoutingTrafficRequestsOverVirtualTopology.txt","w")
#fsqlRTROVT = open("SQL_SELECT_RoutingTrafficRequestsOverVirtualTopology.txt","w")
#fsqlTR = open("SQL_SELECT_TrafficRequests.txt","w")
#fsqlVL = open("SQL_SELECT_VirtualLinks.txt","w")

#fsqlInsert.close()
#fsqlRTROVT.close()
#fsqlTR.close()
#fsqlVL.close()

#for i in range(len(sys.argv)):
#    print (i,":",sys.argv[i])

#if __name__ == '__main__':
#stop seeing np.float64
#numpy.set_printoptions(legacy='1.25')
numpy.set_printoptions(legacy='1.21')

#multiprocessing.freeze_support()

#set the name of the experment
if ( sys.argv[3] != ""):
    experimentName = sys.argv[3]
else:
    experimentName = "Default Experiment"


#create an error log
#errlog = open(experimentName+"_Errors.txt","w")

#22-6-2026 keep errors in RAM
#errlog = open(experimentName+"_Errors.txt","a")

#errlog.write(txtLine)
#errlog.close()

#22-6-2026 keep errors in RAM
#sys.stderr = errlog

#22-6-2026
error_catcher = stderrInMemory(experimentName+"_Errors.txt")
#print ("Main program is running...")
#Simulating an error
#print ("Warning: Something minor happened in the main loop.", file=sys.stderr)

#set the name of the algorithm
if sys.argv[8] == "1":
    Algorithm = "NotApplicable"
    error("Hybrid Bypass has been asked to run using one (1) queue,",7)
elif sys.argv[8] == "2":
    Algorithm = "HybridBypass"
else:
    error("No parameter for the number of Queues",8)

computername = sys.argv[10]

programfolder = sys.argv[11]

distributionForTReqs = sys.argv[12]

appDir = programfolder


# SOP: Start of printout
# EOP: End of printout
if (sys.argv[4]=="detailreport"):
    GlobalSOP = True
else:
    GlobalSOP = False
SetGlobalPrintout(GlobalSOP)

UUID = str(uuid.uuid4())
SetGlobalCurrentRunUUID(UUID)

'''
for use with...
#SOP
if (GlobalSOP==True) :
    ...
'''

# time calculation start # sources https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
                         #         https://docs.python.org/3/library/time.html#time.perf_counter
#start_processtime = time.process_time_ns()

start_processtime = timeit.default_timer()

#netName, N, L, Nm, Dist = readData(sys.argv[1])
netName, N, L, Nm, Dist, HasWavConv = readData(sys.argv[1]) # read network definition from text file


# first command line parameter is the text file with the network definition 
# example of a network text file:

'''
[Name]
GRNet_N4L5
[N]
SYR,SAM,RHO,HER
[L]
0,1 1,2 2,3 3,0 1,3
[Nm]
0:1,3 1:0,2,3 2:1,3 3:0,2,1
[Dist]
182.0,270.0,341.0,251.0,300.0
'''

if sys.argv[8] == "1":
    QueueNames = ["Single"]
elif sys.argv[8] == "2":
    QueueNames = ["High Priority", "Low Priority"]
elif sys.argv[8] == "2mix":
    QueueNames = ["High Priority", "Low Priority"]
elif sys.argv[8] == "2seq":
    QueueNames = ["High Priority", "Low Priority"]

lenQs = len(QueueNames)

# netName: name of the network
# N: list of nodes, nodeid is the index number, e.g. ['SYR', 'SAM', 'RHO', 'HER']
# L: list of links, linkid is the index number, e.g. [[0, 1], [1, 2], [2, 3], [3, 0], [1, 3]]
# Nm: dictionary of node neighbours, nodeid is the index number, e.g. {0: [1, 3], 1: [0, 2, 3], 2: [1, 3], 3: [0, 2, 1]}
# Dist: list of link distances in Km, linkid is the index number, e.g. [182.0, 270.0, 341.0, 251.0, 300.0]

# Nt is the list of nodes expressed as a tuple
Nt = nodes2tuple(N)

# Nmc is the network graph as a dictionary of dictionaries with transition costs
NmC = networkWithCosts(Nm,Nt,L,Dist)

# second command line parameter is the index of X
xi = int(sys.argv[2])

X = []
#original_X = [20, 40, 60, 80, 100, 120]
#original_X = [20, 40, 60, 80, 100, 120, 160, 320, 640, 960, 1280]
#original_X = [2, 4, 6, 8, 10, 15, 20] # to measure in the loads of Lee & Rhee paper
#original_X = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 640, 960, 1280]
original_X  = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 400, 640, 960, 1280]

for Xitem in original_X:
    #X.append(int(Xitem / lenQs)) # den tha xorizo edw ta X sta dyo H oxi analoga me to plithos twn Qs
    X.append(int(Xitem)) # o xwrismos analoga me to plithos twn Qs tha ginetai sti synartisi dimiourgias traffic requests

#other definitions
#X =  [10, 20, 30, 40, 50, 60]     # since I am using two queues traffic demand range parameter/multiplier is split to half #X for two queues
#X = [20, 40, 60, 80, 100, 120]   # traffic demand range parameter/multiplier                                              #X for one queue
xiName = X[xi]

#Energy Contribution
#Power parameters
Er = 1000.0 # energy consumption of an IP Router's port in Watts
Et = 73.0 # energy consumption of a WDM Transponder in Watts
Ee = 8.0 # energy consumption of an Erbium Doped Fiber Amplifier (EDFA) in Watts. 
EDFAdist = 80.0 #An EDFA is deployed every 80km. Link route: EDFA at node, [EDFA at 80km, ...]
S = EDFAdist # span distance between two neighbouring inline EDFAs
maxIProuterPorts = 32 #for Shen-Tucker test network (a) only 

#15-7-2026
Lwc = sys.argv[24] if sys.argv[24]!=None else 100.0
Ewc = sys.argv[25] if sys.argv[25]!=None else 50.0

#from the shen-tucker paper 
#maxFibersPerLink = -1       #no limit on the total number of fibers on each physical link
#25-9-2025 limitted fibers per link #22-9-2025
maxFibersPerLink = int(sys.argv[14]) #= 16
#28-9-2025
maxWavelengthsPerFiber = int(sys.argv[15]) #= 4 #max 16 wavelengths are multiplexed in each fiber
maxGbpsPerWavelength = int(sys.argv[16]) #= 40.0   #max wavelength capacity is 40 Gbps
B = maxGbpsPerWavelength   #max wavelength capacity
maxFiberCapacity = maxWavelengthsPerFiber * maxGbpsPerWavelength
maxLinkCapacity = maxFibersPerLink * maxWavelengthsPerFiber * maxGbpsPerWavelength

#7-4-2026
virtualGbpsPerWavelength = int(sys.argv[23])
if ( (virtualGbpsPerWavelength!=-1) and (virtualGbpsPerWavelength>maxGbpsPerWavelength) ):
    #error("Virtual wavelength capacity is greater than the actual wavelength capacity",993)
    #SOP
    if (GlobalSOP==True) :
        print ("Error: The virtual wavelength capacity is greater than the actual wavelength capacity!")
    #EOP
    error ("Error: The virtual wavelength capacity is greater than the actual wavelength capacity!",993)
    exit(993)

#SetGlobalLimits(maxFibersPerLink,maxWavelengthsPerFiber,maxGbpsPerWavelength,B,maxFiberCapacity,maxLinkCapacity)
SetGlobalLimitsVirtualGpW(maxFibersPerLink,maxWavelengthsPerFiber,maxGbpsPerWavelength,virtualGbpsPerWavelength,B,maxFiberCapacity,maxLinkCapacity)

# The physical topology G
G = (N, L) 

# Virtual topology data structure. The set of virtual links.

#VTobj = VirtualTopology("VT")

# VT: [i, j] => Logical/Virtual Link from node i to node j.
# The index of item [i, j] is the id of the logical/virtual link.
VT=[]

# A table to keep the virtual topology detailed data for post analysis
tblVTdata = []

# Virtual topology's (VT) capacity logistics
vT={}   # VT = {node:[neighbour, ...], ...}
vTL=[]   # VTL = [(tuple of source, destination of virtual link), ...]
vTfreeCap={}   #VTFreeCap = {(tuple of source, destination of virtual link):[free capacity], ...}
VTfinal={} # virtual topology for routing virtual links over physical topology

VirtLinkIDs = {}   # a dictionary to keep the unique virtual link IDs assigned to all virtual (lightpath) links.
                # VirtLinkIDs = {id:(tuple of source, destination of virtual link), ...}

#VirtualLinks = {}
VirtualLinkIDs = {} # = {(s,d):[0,1,2,...],...}
VirtualLinkTotals = {} # = {(s,d,id):[utilcap, freecap, number_of_TReqs_it_serves], ...}
VirtualLinkTReqs = {} # = {(s,d,id):[(que1,req1,cap1,"New"), (que2,req2,cap2,"Grm"),...], ...}

#OLD VTFreeCap = {link number:[free capacity], ...}
#OLD vTfreeCap={}   # VTFreeCapacities = {node:[free capacity to 1st neighbour, free capacity to 2nd neighbour, ...], ...}
ReqRouteInfo = {}   # req = {(queue, request number): [link and free capacity, ...], ...}   how request is routed; which links it uses and their capacity
#vLinkData # vLinkData = [request number, (src, dst of virtual link 1), case (new/groom), capacity used]

# Wmn: L:x => Link number L has a number of x used wavelengths between node m and n.
Wmn = {}
initialiseSet(Wmn,L,[])

# wavelengthids: dictionary of wavelgth ids for each fiber of each link 
# that keeps the IDs of wavelength per fiber per link (linkids, fiberids, wavelengthids are zero based)
# wavelengthids = {0:{0:16, 1:1}, 1:{0:3}, ...} when the fiber reaches the maxWavelengthsPerFiber, a new fiber is utilised
# wavelengthids = {<linkid>:{<fiberid>:<wavelengths count for this fiber of the link>, ...}, ...}
wavelegthids = {}
initialiseWavelegthids(wavelegthids,L)

#fmn: L:x => Link number L needs a number of x fibers between node m and n.
fmn = {}
initialiseSet(fmn,L,[])

fmn_Q0 = {}
fmn_Q1 = {}

# CUmn: [L,x] => Link number L (between node m and n) requires x Gbps. Utilised Capacity between nodes n and m.
CUmn = {}
initialiseSet(CUmn,L,[])

# Em: m => Node number m requires x Watts.
Em = {}

# El: Link number l requires x Watts.
El = {}

# SigmaLamda_id: total data traffic from low end routers at node i
SigmaLamda_id = {}


# Di: number of ports that are used to aggregate the data traffic from low end routers at node i
Di = {}

# Cij: number of wavelength channels on the virtual topology between node pair (i,j)
Cij = {}

# SigmaCij: number of wavelength channels on the virtual topology that start from node i
SigmaCij = {}

#Traffic data from low end routers at node i in Gbps for Queue
SigmaLamda_id_Q0 = {}
SigmaLamda_id_Q1 = {}

Di_Q0 = {}
Di_Q1 = {}

Cij_Q0 = {}
Cij_Q1 = {}

SigmaCij_Q0 = {}
SigmaCij_Q1 = {}

# Lmn: Physical distance of a physical link between nodes m and n
Lmn = {}
initialiseSet(Lmn,L,Dist)

# Amn: Number of EDFAs that should be deployed on each fiber of physical link (m,n)
Amn = {}
initialiseSet(Amn,L,[])

#wrong thought: there is no Amn_Q0 or Amn_Q1 because if a fiber is due to a traffic request then the fiber has predetermined number of EDFAs

#unique, standard colours for each node
Ncolours = []

#latency parameters 

LatencyTimeUnit = "&micro;sec"
LatencyTimeUnit4csv = "microsec"

LatRouterPort = float(sys.argv[17])   # 30 # microsecond
LatTransponder = float(sys.argv[18])  # 100 # microsecond
LatEDFA = 100 / 1000.0 # nanoseconds expressed as microseconds
LatFiberKilometer = 5 # microsecond

#main program's execution starts here #################################################################################################################

Ncolours = setNodeColours(N) # use function for consistent graph (network) node colours throughout the execution

alg = Algorithm.replace(' ', '_')

stdoutOriginal, sys.stdout, graphsPath = Log2path(appDir, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi]))

#SOP
if (GlobalSOP==True) :
    sys.stdout.reconfigure(encoding='utf-8')
    htmlhead("Hybrid Bypass", lenQs, distributionForTReqs)

    printRunConfiguration(UUID)

    print ("<table class='table1c'>")
    print ("<tr><th colspan='2'>Simulator output details</th></tr>")
    print ("<tr><td>stdoutOriginal:</td><td>",stdoutOriginal,"</td></tr>")
    print ("<tr><td>sys.stdout:</td><td>",sys.stdout,"</td></tr>")
    print ("<tr><td>graphsPath:</td><td>",graphsPath,"</td></tr>")
    print ("</table>")

    print ("<table class='table1c'>")
    print ("<tr><th>Maximum fiber capacity</th></tr>")
    print ("<tr><td>Each wavelength capacity is ", maxGbpsPerWavelength, " Gbps</th></tr>")
    print ("<tr><td>Each fiber can multiplex up to ", ("&infin;" if maxWavelengthsPerFiber<0 else maxWavelengthsPerFiber), " wavelengths</td></tr>")
    print ("<tr><td>Therefore, the maximum fiber capacity can reach ", maxFiberCapacity, " Gbps</td></tr>")
    #7-4-2026
    if ( (virtualGbpsPerWavelength!=-1) and (virtualGbpsPerWavelength!=maxFiberCapacity) ):
        print (f"<tr><td>Each wavelength is considered to have a virtual capacity of {virtualGbpsPerWavelength:d} Gbps</td></tr>")
    print ("</table>")

    print ("<table class='table1c'>")
    print ("<tr><th>Maximum link capacity</th></tr>")
    print ("<tr><td>Each link can include up to ", ("&infin;" if maxFibersPerLink<0 else maxFibersPerLink), " fibers</td></tr>")
    print ("<tr><td>Therefore, the maximum link capacity can reach ", ("&infin;" if maxLinkCapacity<0 else maxLinkCapacity), " Gbps</td></tr>")
    print ("<tr><td>The links are bidirectional. Therefore, each fiber can transfer information in both directions.</td></tr>")
    print ("</table>")

    print ("<table class='table1c'>")
    print ("<tr><th>N: Set of nodes</th></tr>")
    for i in range(len(N)):
        print ("<tr><td>Node", i, "is", N[i],"</td>")
        print (f"<td>{("with wavelength converters" if HasWavConv[i]==1 else "without wavelength converters"):s}</td></tr>")
    print ("</table>")

    print ("<table class='table1c'>")
    print ("<tr><th>Nm: Set of neighbouring nodes</th></tr>")
    for i in range(len(Nm)):
        print ("<tr><td>Node", i, "neighbours ",Nm[i],"</td></tr>")
    print ("</table>")
    print ("<table class='table1c'>")
    print ("<tr><th>L: Set of bidirectional Links</th></tr>")
    print ("<tr><td>",L,"</td></tr>")
    print ("</table>")

    print ("<table class='table1c'>")
    print ("<tr><th>G: The physical topology</th></tr>")
    
    print ("<tr><td>",G,"</td></tr>")
    print ("</table>")

    #visualisePhysicalTopology(N,L, graphsPath, Ncolours, Dist, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output
    #14-4-2026 # ↻ wavelength conversion, ⇾ no wavelength conversion   # alternative symbols ↭⇎⇴⇸⇿⇶⇀⇼⇹⇸⇿⇾▨▩▮ ↭↜↝↺↻↹⇌⇜⇝⇼⇹⇷⇵⇆
    visualisePhysicalTopologyAndWavenengthConverters(N,L, graphsPath, Ncolours, Dist, (sys.argv[7]!="pdfout"), HasWavConv)

    print ("<table class='table1c'>")
    print ("<tr><th colspan=",len(N),">&lambda;: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi])
    print (f"for a total of {lenQs:d} queue{('s.' if lenQs>1 else '.'):s}")
    print (f"<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a {distributionForTReqs} distribution,")
    print (" which is centered at an identical average.") #"That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, the actual demand between a node pair is generated by a random function and values distributed following the Poisson process.")
    print ("</em></th></tr>")
#EOP

dbConnection = createSQLiteDB(graphsPath, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".db")
saveRunIDandRunConfig2sqlite(dbConnection, UUID, sys.argv)
saveQueues2sqlite(dbConnection, QueueNames)
savePhysicalLinks2sqlite(dbConnection, L, Dist, EDFAdist, LatEDFA, LatFiberKilometer, graphsPath)
saveNodes2sqlite(dbConnection, N)


#24-7-2026
#~><Section traffic requests and traffic load amount generation>

if sys.argv[5] == "gensave":
    demandsfilename = os.path.join(graphsPath, sys.argv[6])
    lamdatextfile = open(demandsfilename,"w") # since in the generateTrafficRequests() function the lamdatextfile is appended ("a"), I recreate it empty ("w") to avoid keepeing previous data.
    lamdatextfile.close()

TReqsForQueue = []

# 2-10-2025 varaiable traffic distribution among Qhp, Qlp queues
trafficPercentOfQueueHP = roundatdecimals( (int(sys.argv[19]) / 100.0), 3)
trafficPercentOfQueueLP = roundatdecimals( (1.0 - trafficPercentOfQueueHP), 3)

#24-7-2026
#2DO Na dimiourgisw functions gia TReq me Pareto gia LP kai Weibull gia HP

# 2-10-2025 varaiable traffic distribution among Qhp, Qlp queues
tempQ = generateTrafficRequestsVariableBalance(dbConnection, N, graphsPath, lenQs, X, xi, QueueNames[0], 0, distributionForTReqs, trafficPercentOfQueueHP)
TReqsForQueue.append(tempQ) # krataei ta traffic reqquests gia kathe queue
tempQ = generateTrafficRequestsVariableBalance(dbConnection, N, graphsPath, lenQs, X, xi, QueueNames[1], 1, distributionForTReqs, trafficPercentOfQueueLP)
TReqsForQueue.append(tempQ) # krataei ta traffic reqquests gia kathe queue



if lenQs==1:
    aggregatedTReqs = TReqsForQueue[0]
elif lenQs==2:
    #aggregate the traffic volume of the two queues
    aggregatedTReqs= AggregateRequestsTraffic(N, TReqsForQueue[0], TReqsForQueue[1])
else:
    error("<div>Error: Program designed for 1 or 2 queues so far.",999)
    exit(1)

sortTrafficRequestsDescending(aggregatedTReqs)

#SOP
if (GlobalSOP==True) :
    printTrafficRequests(aggregatedTReqs,N, "For the aggregated traffic from the traffic requests of all queues, per source, destination, in descending order.")
#EOP

# used for power calculation
# Di: number of ports that are used to aggregate the data traffic from low end routers at node i

# calculate for one or two queues
for req in aggregatedTReqs:
    #print ("<li>req",req)
    accumulatePowerParameters(SigmaLamda_id, req[0], req[2])

for key in SigmaLamda_id:
    slid = SigmaLamda_id.get(key)
    value = numpy.ceil(slid / B)
    Di.update({key:value})
#SOP

if (GlobalSOP==True) :
    printDi(Di, N, SigmaLamda_id)
#EOP

# if two (or more in the future) queues, also calculate each queue's contribution
if lenQs == 2:
    #for the Q0
    for req in TReqsForQueue[0]:
        #print ("<li>req",req)
        accumulatePowerParameters(SigmaLamda_id_Q0, req[0], req[2])

    for key in SigmaLamda_id_Q0:
        slid = SigmaLamda_id_Q0.get(key)
        value = numpy.ceil(slid / B)
        Di_Q0.update({key:value})

    #SOP
    if (GlobalSOP==True) :
        printDiPerQueue(QueueNames[0], Di_Q0, N, SigmaLamda_id_Q0)
    #EOP

    #for the Q1
    for req in TReqsForQueue[1]:
        #print ("<li>req",req)
        accumulatePowerParameters(SigmaLamda_id_Q1, req[0], req[2])

    for key in SigmaLamda_id_Q1:
        slid = SigmaLamda_id_Q1.get(key)
        value = numpy.ceil(slid / B)
        Di_Q1.update({key:value})

    #SOP
    if (GlobalSOP==True) :
        printDiPerQueue(QueueNames[1], Di_Q1, N, SigmaLamda_id_Q1)
    #EOP

#~></Section traffic requests and traffic load amount generation>


# Count total lightpaths
TotalLightpaths = [0] #how many lightpaths

# Count how many of the lightpaths were reused, 0 or 1 per lightpath
ReUsedLightpaths = [] #how many times lightspaths were reused - if a lightpath is reused more than once it counts as one - ReUsedLightpaths <= number of Lightpaths

# Count the reuses of the lightpaths, 0, 1, 2, or more per lightpath
LightpathReuses = [0] #how many reuses of lightpaths - if a lightpath is reused more than once I count all the reuse times - LightpathReuses maybe <, =, or > number of Lightpaths
# I use mutable objects (lists) beacuse if I pass the parameter as integer then it is a call by value and the value for the main program remains unchanged
# read: https://realpython.com/python-pass-by-reference/

#SOP
#if (GlobalSOP==True) :
# old, serving one traffic requests structure
# routeAllTrafficRequestsOverVirtualTopologyMultihopBypass(N,requests,vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal,R, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection)

#SOP not
#if (GlobalSOP==False) :
#    graphsPath = "no graphs path needed, since no printout"
#EOP

# new, serving two traffic request queues
if lenQs==2:
    startingstep = 1

    s="Virtual topology graph after processing request "
    VTgraph = graph_new(s, True)
    
    #route Q0 using direct bypass
    Q=0
    
    #7-4-2026 utilize virtualGbpsPerWavelength only for Q_{HP}
    if (virtualGbpsPerWavelength!=-1):
        startingstep = routeAllRequestsOfOneQueueOverVirtualTopologyDirectBypassUtilizeVirtualWavelengthCapacity(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, virtualGbpsPerWavelength)
    else:
        startingstep = routeAllRequestsOfOneQueueOverVirtualTopologyDirectBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)

    #route Q1 using multihop bypass
    Q=1
    # 12-10-2025 using hybrid bypass for Q1 (Q_LP): this is the original function
    # startingstep = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)
    # On 12-10-2025 I have to change the function to check for revisits in case of traffic grooming
    # created on 6-9-2025: On this routine I have to perform the wavelength assignment for each routing of a traffic request over a virtual link and check for no revisits in case of traffic grooming before I move to the next traffic request

    if sys.argv[20] == "Yes": # CheckForRevisits
        #8-4-2026
        startingstep, numberOfPathsWithRevisitWhichRoutedDirectly = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass_checkingForRevisits_usedbyHybridBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, N, Nt, NmC)
        
        #8-4-2026 δεν υπάρχει λόγος να γίνεται χρήση VirtWavelengthCapacity για Q_LP γιατί κάνει TG στον εαυτό του
        
        #7-4-2026 utilize virtualGbpsPerWavelength 
        #if (virtualGbpsPerWavelength!=-1):
        #    startingstep, numberOfPathsWithRevisitWhichRoutedDirectly = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass_checkingForRevisits_utilizeVirtualWavelengthCapacity_usedbyHybridBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, N, Nt, NmC, virtualGbpsPerWavelength)
        #else:
        #    startingstep, numberOfPathsWithRevisitWhichRoutedDirectly = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass_checkingForRevisits_usedbyHybridBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, N, Nt, NmC)    
    else:
        #7-4-2026
        #Virtual wavelength capacity is available only for when check for revisits activated (TGRC) because we want to further improve the HyB efficiency.
        if (virtualGbpsPerWavelength!=-1):
            error("Virtual wavelength capacity is applicable on the low priority traffic class only when the Traffic Grooming Rejection Criterion (TGRC) is enabled!",9999)
            #SOP
            if (GlobalSOP==True) :
                print ("<div>Virtual wavelength capacity is applicable on the low priority traffic class only when the Traffic Grooming Rejection Criterion (TGRC) is enabled!</div>")
            #EOP
        startingstep = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)
        numberOfPathsWithRevisitWhichRoutedDirectly = 0

    schedulingstrategy = sys.argv[13] if sys.argv[13]!=None else "HybridBypass2Q"
else:
    error("Hybrid Bypass runs only for two queues!",9988)
    #SOP
    if (GlobalSOP==True) :
        print ("<div>Hybrid Bypass runs only for two queues!</div>")
    #EOP
    exit(1)


#SOP
if (GlobalSOP==True) :
    print ("<h3 style='text-align:center'>Strategy utilised for the scheduling of the queue(s):", schedulingstrategy,"</h3>")
    
    print ("<table class='table1c'>")
    #print ("<tr><th>Free capacities for the Virtual Links of the Virtual Topology {(s, d): [<em>free capacity</em>], ...} (vTfreeCap) =",vTfreeCap,"</th></tr>")
    #2DO not use vTfreeCap
    
    print ("<tr><th>The Virtual Topology {node: [<em>list of neighbour nodes</em>], ...} (vT)") # =",vT,"</th></tr>")
    printVTdictionaryAsTable(vT)
    print ("</th></tr>")

    #print ("<tr><th>List of Virtual Links of Virtual Topology [(s, d),...] (vTL) =",vTL,"</th></tr>")
    #2DO not use vTL
    #print ("<tr><th>Virtual Links used for each traffic request {<em>(queue id, request id)</em>: [(s,d,type,capacity), ...], ...} (R)") #, ReqRouteInfo,"</th></tr>")
    
    print ("<tr><th>Virtual Links used for each traffic request {<em>(queue id, request id)</em>: [(virtual link (s,d,n), type, capacity utilised, step of routing the requested capacity, step's virtual link sequence number), ...], ...} (R)") #, ReqRouteInfo,"</th></tr>")
    printRequestRoutingInfoAsTable(ReqRouteInfo)
    print ("</th></tr>")
    
    print ("<tr><th>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
    printVLids(VirtualLinkIDs)
    print ("</th></tr>")

    print ("<tr><th>Virtual Link Traffic Requests = {(s,d,i):[(que,req,cap,type),...],...}")
    printVLTReqs(VirtualLinkTReqs)
    print ("</th></tr>")

    print ("<tr><th>Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...}")
    printVLTotals(VirtualLinkTotals)

    #print ("<li>Virtual Links per Request R=")
    #printFreeCapacitiesAsTable(ReqRouteInfo)

    print ("</th></tr>")
    print ("</table>")

#else:
    #routeAllTrafficRequestsOfTwoQueuesOverVirtualTopologyMultihopBypass(N,TReqsForQueue[0],TReqsForQueue[1],vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, "no graphs path needed, since no printout", Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)
#EOP

VirtualLinks = []

#print ("<div>VTfinal=",VTfinal,"</div>")

# edw allazw to vtfinal gia na exw sosta athroismata gia perissoteres apo 1 queues

newVTFinal = {}

for VLkey in VirtualLinkTotals:
    #print ("<li>VLKey",VLkey)
    s = VLkey[0]
    d = VLkey[1]
    num = VLkey[2]
    caputil = VirtualLinkTotals[VLkey][0]
    if caputil > maxGbpsPerWavelength:
        error("Virtual Link has greater capacity than the allowed limit",99)
    #print ("<li>capacity utilised",caputil)
    VTFinalKey = (s,d)
    #print ("<li>new VTFinal",newVTFinal)
    if VTFinalKey in newVTFinal:
        vtFinalvalue = newVTFinal[VTFinalKey]
        vtFinalvalue.append(caputil)
    else:
        vtFinalvalue = [caputil]
    newVTFinal.update({(s,d,num):vtFinalvalue})

#print ("<div>New VTfinal=",VTfinal,"</div>")

'''
#1-7-2026
#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c'>")
    print ("<tr><th colspan=5>The virtual topology for routing over physical topology</th></tr>")
    print ("<tr><th>source&rarr;destination </th><th>source (s)</th><th>destination (d)</th><th>number (n)</th><th>capacity</th>")
#EOP
'''

#1-7-2026
#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c'>")
    print ("<tr><th colspan=6>The virtual topology for routing over physical topology</th></tr>")
    print ("<tr><th>number</th><th>source&rarr;destination </th><th>source (s)</th><th>destination (d)</th><th>number (n)</th><th>capacity</th>")
#EOP

VTfinal = newVTFinal

counter=1
for link in VTfinal:
    capacities = VTfinal.get(link)
    lines = len(capacities)

    '''
    #1-7-2026
    #SOP
    if (GlobalSOP==True) :
        print ("<tr><td rowspan=",lines,">",N[link[0]],"&rarr;",N[link[1]],"</td>")
        print ("<td rowspan=",lines,">",link[0],"</td>")
        print ("<td rowspan=",lines,">",link[1],"</td>")
        print ("<td rowspan=",lines,">",link[2],"</td>")
    #EOP
    '''

    #SOP
    if (GlobalSOP==True) :
        print (f"<tr><td rowspan={lines}>{counter}</td><td rowspan={lines}>{N[link[0]]}&rarr;{N[link[1]]}</td>")
        print (f"<td rowspan={lines}>{link[0]}</td>")
        print (f"<td rowspan={lines}>{link[1]}</td>")
        print (f"<td rowspan={lines}>{link[2]}</td>")
    #EOP

    counter+=1

    for c in capacities:
        VirtualLinks.append([N[link[0]], N[link[1]], link[2], c])

        #SOP
        if (GlobalSOP==True) :
            print ("<td>",c,"</td>")
            print ("</tr>")
        #EOP

#SOP
if (GlobalSOP==True) :
    print ("</table>")
#EOP

VT = VirtualLinks

#print ("<div>Virtual Links for routing over physical topology<p>")
#print (VT)

# used for power calculation
#Cij: calculated as the number of virtual links (lightpaths) between a node pair (i,j) 
for vl in VT:
    t=(nodenumber(N,vl[0]),nodenumber(N,vl[1]))
    accumulatePowerParameters(Cij, t, 1)

#SOP
if (GlobalSOP==True) :
    printCij(Cij, N)
#EOP

#SigmaCij: calculated as the number of virtual links (lightpaths) that originate from a node i
for k in Cij:    
    val = Cij.get(k)
    accumulatePowerParameters(SigmaCij, k[0], val)

#SOP
if (GlobalSOP==True) :
    printSigmaCij(SigmaCij, N)
#EOP



'''#14-7-2026 put wavelength assignment later
#RoutingOfVirtualLinksOverWavelengths = {}

#>>>>>> 6-7-2026 blocking due to limitations during wavelength assignment, not afterwards
#phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)




#14-7-2026 Assign wavelengths and enforce limited fibers & wavelength continuity directly in one step!
phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithLimitsConsideration(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
                                                                                              Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
                                                                                              EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)
'''

#old phyLinks = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, dbConnection)
#older #phyLinks = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VirtualLinks, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist)


# 1-7-2026: Δεν ελέγχω πλέον τα revisit εδώ καθώς αυτό γίνεται στη φάση του routing του διανύσματος traffic demands Low Priority (πρώην Q_LP), οπότε αν υπάρχει revisit λόγω του TGRC δεν γίνεται traffic grooming αλλά το φορτίο δρομολογείται με νέο VL με τη λογική Direct Bypass.
# 12-10-2025: merge here this step of the no revisits functionality 
# 3-9-2025: briskw ta revisit apo ta dedomena tis database
#dbConnectionCopy = dbConnection
#print ("<li>#########")
#revisits = getRevisitsFromSQLite(dbConnectionCopy)



#~><Section Hard Latency Cap>

# 12-10-2025 apply hard latency cap

'''
# 10-7-2026 προς το παρόν δεν θα λογίζεται το hard latency cap καθώς εσφαλμένα υπολογίζεται κατά VL ενώ πρέπει να υπολογίζεται κατά traffic request όπως υπολογίζεται και το latency
#           και γενικά στη βιβλιογραφία όταν μιλούν για blocking of traffic αναφέρονται στα request/demands

# με την πρώτη ευκαιρία θα αναπροσαρμοστεί το hard latency cap ώστε να υπολογίζεται META το routing και ΠΡΙΝ το wavelength assignment, καθώς αφορά τη διαδρομή και όχι συγκεκριμένα κανάλια wavelength

# >>> το hard latency cap υπολογίζεται από εδώ...
'''
#prepei na ginetai kata ti diarkeia tou routing! oxi meta!
RoutingOfVirtualLinksOverWavelengths = {}
numberOf_LPs_checkedForHardLatencyCap = -1
countBlockedVL_Q_HP = -1
countBlockedVL_Q_LP = -1

if (sys.argv[21]!="-1") or (sys.argv[22]!="-1"):
    #SOP
    if (GlobalSOP==True) :
        print ("<p/><hr><li><em>Virtual Links before the hard latency cap:",RoutingOfVirtualLinksOverWavelengths)
    #EOP

Q_HP_latency_cap = float(sys.argv[21]) if sys.argv[21]!=None else 0.0   # microsecond 
Q_LP_latency_cap = float(sys.argv[22]) if sys.argv[22]!=None else 0.0   # microsecond 

blockedDueToHardLatencyCap = {}

if (Q_HP_latency_cap > 0.0) or (Q_LP_latency_cap > 0.0):

    numberOf_LPs_checkedForHardLatencyCap = len(RoutingOfVirtualLinksOverWavelengths) if RoutingOfVirtualLinksOverWavelengths!=None else -1
    #blockedDueToHardLatencyCap = {}
    countBlockedVL_Q_HP = -1 # -1 means hard latency cap not applied for Q_HP (Q0)
    countBlockedVL_Q_LP = -1 # -1 means hard latency cap not applied for Q_LP (Q1)

    RoutingOfVirtualLinksOverWavelengths, blockedDueToHardLatencyCap, countBlockedVL_Q_HP, countBlockedVL_Q_LP = blockTrafficAccordingToHardLatencyCap(dbConnection, RoutingOfVirtualLinksOverWavelengths, Q_HP_latency_cap, Q_LP_latency_cap)

if (sys.argv[21]!="-1") or (sys.argv[22]!="-1"):
    #SOP
    if (GlobalSOP==True) :
        print ("<li><em>Results of the hard latency cap:",blockedDueToHardLatencyCap)
        print ("<li><em>Routings of Virtual Links who passed the hard latency cap:",RoutingOfVirtualLinksOverWavelengths)
    #EOP
'''
# <<< το hard latency cap υπολογίζεται μέχρι εδώ
'''
#~></Section Hard Latency Cap>


#~><Section Wavelength assignment with limitations>

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

#14-7-2026 wavelength assignment WITH limitations
RoutingOfVirtualLinksOverWavelengths = {}
newRoutingOfVirtualLinksOverWavelengthsWithLimits = {}

#>>>>>> 6-7-2026 blocking due to limitations during wavelength assignment, not afterwards
#phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)

#14-7-2026 τα limitations θα υπολογίζονται πλέον κατά τη διάρκεια του wavelength assignment
# 29-9-2025 apply limitations after the routing of the virtual links over the physical topology
limitations = decideLimitations(N, HasWavConv, maxFibersPerLink)

#SOP
if (GlobalSOP==True) :
    #print (f"<p/><hr><div>Before limitations: RoutingOfVirtualLinksOverWavelengths={RoutingOfVirtualLinksOverWavelengths}</div>")
    print ("<li><em>Limitations:",limitations)
#EOP

#10-4-2026


# Define this globally before the match block so all cases and loggers can access it
NumberOfShortestPaths = 1 if sys.argv[26]==None else int(sys.argv[26])

match limitations:
    #case 1
    case ["UnlimitedFibersPerLink", "NoWavContConstr"] :
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>No Blocking of any traffic requests. Considering unlimited fibers per link. Consider wavelength converters exist on every node. (case: UnlimitedFibersPerLink, NoWavContConstr)</div>")
        #EOP

        phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(
            VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
            Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
            EDFAdist, networkWithCosts, wavelegthids, LatRouterPort, LatTransponder, dbConnection
        )

        NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(1)] for _ in range(len(L))]
        
        newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults = assignUnlimitedFibers_NoWavContConstr(
            L, 
            RoutingOfVirtualLinksOverWavelengths, 
            NetworkWavelengthsMap
        )
        
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
        #EOP

    #case 2
    case ["UnlimitedFibersPerLink", "FullWavContConstr"] :
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>No Blocking of any traffic requests. Considering unlimited fibers per link. Consider no wavelength converters exist.</div>")
        #EOP
        
        phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(
            VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
            Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
            EDFAdist, networkWithCosts, wavelegthids, LatRouterPort, LatTransponder, dbConnection
        )

        NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(1)] for _ in range(len(L))]
        
        newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults = assignUnlimitedFibers_FullWavContConstr(
            L, 
            RoutingOfVirtualLinksOverWavelengths, 
            NetworkWavelengthsMap
        )
        
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
        #EOP

    #case 3
    case ["UnlimitedFibersPerLink", "PartialWavContConstr"] :
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>No Blocking of any traffic requests. Considering unlimited fibers per link. Consider that only some nodes have wavelength converters, while the rest of the nodes do not.</div>")
        #EOP
        
        phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(
            VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
            Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
            EDFAdist, networkWithCosts, wavelegthids, LatRouterPort, LatTransponder, dbConnection
        )

        NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(1)] for _ in range(len(L))]
                
        newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults = assignUnlimitedFibers_PartialWavContConstr(
            L, 
            RoutingOfVirtualLinksOverWavelengths, 
            NetworkWavelengthsMap,
            HasWavConv # <--- Pass the converters mapping here
        )
        
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
        #EOP

    #case 4
    case ["LimitedFibersPerLink", "NoWavContConstr"]:
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>Blocking of traffic requests. Considering limited fibers per link. Consider wavelength converters exist on every node.</div>")
        #EOP
        
        phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(
            VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
            Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
            EDFAdist, networkWithCosts, wavelegthids, LatRouterPort, LatTransponder, dbConnection
        )
        
        NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(maxFibersPerLink)] for _ in range(len(L))]
        
        newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults = assignLimitedFibers_NoWavContConstr(
            L, 
            RoutingOfVirtualLinksOverWavelengths, 
            NetworkWavelengthsMap
        )
        
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
        #EOP

    #case 5
    case ["LimitedFibersPerLink", "FullWavContConstr"]:
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>Blocking of traffic requests. Considering limited fibers per link. Consider no wavelength converters exist.</div>")
        #EOP

        phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(
            VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
            Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
            EDFAdist, networkWithCosts, wavelegthids, LatRouterPort, LatTransponder, dbConnection
        )

        newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults, netmap = blockTrafficAccordingToCriteria(
            L, 
            RoutingOfVirtualLinksOverWavelengths, 
            limitations, 
            HasWavConv
        )
        
        NetworkWavelengthsMap = netmap
        
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
        #EOP

    #case 6
    case ["LimitedFibersPerLink", "PartialWavContConstr"]:
        #SOP
        if (GlobalSOP==True) :
            print ("<div><li>Blocking of traffic requests. Considering limited fibers per link. Consider that only some nodes have wavelength converters, while the rest of the nodes do not.</div>")
        #EOP
        
        # Initialize the network map with STRICT limits (it will NOT expand)
        NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(maxFibersPerLink)] for _ in range(len(L))]

        #15-7-2026
        #Lwc = sys.argv[24] if sys.argv[24]!=None else 100.0
        #Ewc = sys.argv[25] if sys.argv[25]!=None else 50.0        ``
        
        #old function (a) First function (it was designed just to assign wavelengths without considering traffic limitations):
        #phyLinks, RoutingOfVirtualLinksOverWavelengths = WavelengthsAssignmentWithoutLimitsConsideration(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, 
        #                                                                                                 Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, 
        #                                                                                                 EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)

        #old function (b) Second function (it was designed just to apply traffic limitations after the original assignment of wavelengths):
        #newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResult = assignLimitedFibers_PartialWavContConstr(
        #    L, 
        #    RoutingOfVirtualLinksOverWavelengths, 
        #    NetworkWavelengthsMap,
        #    HasWavConv) # <--- Pass the converters mapping here

        #new integrated function
        #16-7-2026

        #21-8-2026
        #NumberOfShortestPaths = 1 if sys.argv[26]==None else int(sys.argv[26])

        if NumberOfShortestPaths==1:
            phyLinks, RoutingOfVirtualLinksOverWavelengths, routingResults = WavelengthsAssignmentWithConstraints(VT, N, Nt, maxGbpsPerWavelength, NetworkWavelengthsMap, HasWavConv,
                                                                                                                  Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist,
                                                                                                                  networkWithCosts, LatRouterPort, LatTransponder, dbConnection)
        else:
            #16-7-2026 rely on k-shortest paths, not a single shortest path 
            phyLinks, RoutingOfVirtualLinksOverWavelengths, routingResults = WavelengthsAssignmentWithConstraintsUsingKShortestPaths(VT, N, Nt, maxGbpsPerWavelength, NetworkWavelengthsMap, HasWavConv,
                                                                                                                                     Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist,
                                                                                                                                     networkWithCosts, LatRouterPort, LatTransponder, dbConnection, NumberOfShortestPaths)
            
        #SOP
        if (GlobalSOP==True) :
            print_reservations(NetworkWavelengthsMap, L)
            #1-7-2026 new function to print lightpaths' route of wavelenghts
            print_lightpath_routes(NetworkWavelengthsMap, L)
        #EOP



    case _:
        error("Invalid Combination of Limitations!",555)
        exit(555)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#~></Section Wavelength assignment with limitations>


#22-8-2026 

# Count total converters used per Virtual Link (Lightpath)
vl_converter_counts = {}
for vl_key, value in RoutingOfVirtualLinksOverWavelengths.items():
    converters = 0
    
    # Extract the hops list safely without modifying the original dictionary
    hops = value[0] if (len(value) > 0 and isinstance(value[0], list)) else value
    
    if len(hops) > 1:
        wave_index = 6  # Make sure this is your correct wavelength ID index
        
        for i in range(len(hops) - 1):
            # Safety check: Ensure both hops are valid tuples/lists long enough to contain wave_index
            if isinstance(hops[i], (list, tuple)) and len(hops[i]) > wave_index and \
                isinstance(hops[i+1], (list, tuple)) and len(hops[i+1]) > wave_index:
                
                if hops[i][wave_index] != hops[i+1][wave_index]:
                    converters += 1
                    
    vl_converter_counts[vl_key] = converters

total_pow_overhead_HP = 0.0
total_pow_overhead_LP = 0.0
lat_overheads_HP = []
lat_overheads_LP = []

# List to hold detailed DB records: (TReqQueNum, TReqReqNum, ConvertersUsed, LatencyOverhead, PowerOverhead)
detailed_request_overheads = []

# Map converters back to specific Traffic Requests
for (que, req), route_info_list in ReqRouteInfo.items():
    req_converters = 0
    for step_data in route_info_list:
        vl_tuple = (step_data[0], step_data[1], step_data[2]) 
        if vl_tuple in vl_converter_counts:
            req_converters += vl_converter_counts[vl_tuple]
    
    # Calculate exact overheads for this specific traffic request
    req_lat_overhead = req_converters * float(Lwc)
    req_pow_overhead = req_converters * float(Ewc)
    
    # Save to the detailed list for the database
    detailed_request_overheads.append((que, req, req_converters, req_lat_overhead, req_pow_overhead))
    
    # Aggregate metrics by Queue
    if que == 0:
        total_pow_overhead_HP += req_pow_overhead
        lat_overheads_HP.append(req_lat_overhead)
    elif que == 1:
        total_pow_overhead_LP += req_pow_overhead
        lat_overheads_LP.append(req_lat_overhead)

# Save the detailed metrics to SQLite
saveConverterOverheads2sqlite(dbConnection, detailed_request_overheads)

# Calculate Mean Latency Overheads
mean_lat_overhead_HP = sum(lat_overheads_HP) / len(lat_overheads_HP) if lat_overheads_HP else 0.0
mean_lat_overhead_LP = sum(lat_overheads_LP) / len(lat_overheads_LP) if lat_overheads_LP else 0.0

if GlobalSOP:
    print(f"<li>Saved {len(detailed_request_overheads)} detailed request overheads to WavelengthConverterOverheads table.</li>")


#SOP
#if (GlobalSOP==True) :    
#    for vl in newRoutingOfVirtualLinksOverWavelengthsWithLimits.keys():
#        print_vl_reservation(newRoutingOfVirtualLinksOverWavelengthsWithLimits, netmap, vl, vlIDtoTag(vl))
#EOP

#25-9-2025 Done: prepei na mpei mia stili me to result pass/block >>> DONE

#SOP
if (GlobalSOP==True) :    
    #visualiseRoutingOfVirtualLinksOverPhysicalTopology(phyLinks, N, graphsPath, Ncolours, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output
    #14-4-2026 # ↻ wavelength conversion, ⇾ no wavelength conversion   # alternative symbols ↭⇎⇴⇸⇿⇶⇀⇼⇹⇸⇿⇾▨▩▮ ↭↜↝↺↻↹⇌⇜⇝⇼⇹⇷⇵⇆
    visualiseRoutingOfVirtualLinksOverPhysicalTopologyAndWavenengthConverters(phyLinks, N, graphsPath, Ncolours, (sys.argv[7]!="pdfout"), HasWavConv) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output

    print ("<p><li><em>Routing of VLs over PT table (-1 on wavelength ID means the VL is blocked):")

    


    for k, v in RoutingOfVirtualLinksOverWavelengths.items():
        if len(v) > 0 and isinstance(v[0], list):
            RoutingOfVirtualLinksOverWavelengths[k] = v[0]
    

    printRoutingOfVirtualLinksOverWavelengthsAsTable(RoutingOfVirtualLinksOverWavelengths)   
    
    #print ("<p><li><em>NEW Routing of VLs over PT table after limitations:")
    #printRoutingOfVirtualLinksOverWavelengthsWithLimitResultsAsTable(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults)
#EOP


# 29-9-2025 calculate physical link statistics and power consumption using the data before limitations

CUmn = getCUmnFromDB(CUmn, L, dbConnection)
Wmn = getWmnFromDB(Wmn, L, dbConnection)
SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)

#8-2-2026 do not calculate stats and power before limitations because Amn after limitations becomes +300%
# wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParametersBeforeLimitations(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection) # before updating limits and blockings
# PowerIP, PowerTransponders, PowerEDFAs, PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)

# 29-9-2025 update the databases according to the limitations

#<28-9-2025> statistics about the traffic requests that were blocked due to limitations
#for each lightpath (virtual link) whether it was passed or blocked

passLPs, blockedLPs = resultsDBUpdateOfVLs_LPs(routingResults, dbConnection)

totalLPs = len(routingResults) #how many lightpaths 
countPassLPs = len(passLPs) #how many of the lightpaths were passed
countBlockedLPs = len(blockedLPs) #how many of the lightpaths were blocked
passLPsPercent = roundatdecimals((countPassLPs/totalLPs*100.0),1) if totalLPs>0 else 0.0
blockedLPsPercent = roundatdecimals((countBlockedLPs/totalLPs*100.0),1) if totalLPs>0 else 0.0

#SOP
#20-7-2026 >>>>>>>>>>>>>>>>>>>>>>>>>>>
if (GlobalSOP==True) :
    print ("<table width='60%' class='data'>")
    print ("<tr><th colspan=1>New statistics after limits</th></tr>")
    print ("<tr><th colspan=1>Total lightpaths (virtual links)",totalLPs,", Pass",countPassLPs,", ",passLPsPercent,"%</th></tr>")
    print ("<tr><th colspan=1>Total lightpaths (virtual links)",totalLPs,", Blocked",countBlockedLPs,", ",blockedLPsPercent,"%</th></tr>")
    for lp in passLPs:
        print ("<tr><td>Pass lightpath (virtual link) ",lp,"from",N[lp[0]],"to",N[lp[1]],"number",lp[2],"</td></tr>")
    for lp in blockedLPs:
        print ("<tr><td>Blocked lightpath (virtual link) ",lp,"from",N[lp[0]],"to",N[lp[1]],"number",lp[2],"</td></tr>")
    print ("</table>")
#EOP

#for each traffic request whether it was passed or blocked

passTRs, blockedTRs = resultsDBUpdateOfTRs(dbConnection)

#print ("<li>Passed traffic requests:",passTRs)
#print ("<li>Blocked traffic requests:",blockedTRs)

updateDB_RoutingVirtualLinksOverPhysicalTopology(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults, dbConnection)

removeDB_BlockedVirtualLinksOverPhysicalTopology(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResults, dbConnection)

totalTRs = len(passTRs) + len(blockedTRs) #how many traffic requests
countPassTRs = len(passTRs) #how many of the traffic requests were passed
countBlockedTRs = len(blockedTRs) #how many of the traffic requests were blocked
passTRsPercent = roundatdecimals((countPassTRs/totalTRs*100.0),1) if totalTRs>0 else 0.0
blockedTRsPercent = roundatdecimals((countBlockedTRs/totalTRs*100.0),1) if totalTRs>0 else 0.0

#SOP
if (GlobalSOP==True) :
    print ("<table width='60%' class='data'>")
    print ("<tr><th colspan=1>New statistics after limits</th></tr>")
    print ("<tr><th colspan=1>Total traffic requests",totalTRs,", Pass",countPassTRs,", ",passTRsPercent,"%</th></tr>")
    print ("<tr><th colspan=1>Total traffic requests",totalTRs,", Blocked",countBlockedTRs,", ",blockedTRsPercent,"%</th></tr>")
    for trq in passTRs:
        print ("<tr><td>Pass traffic request ",trq,"queue",trq[0],"number",trq[1],"</td></tr>")
    for trq in blockedTRs:
        print ("<tr><td>Blocked traffic request ",trq,"queue",trq[0],"number",trq[1],"</td></tr>")
    print ("</table>")
#EOP

#</28-9-2025>



# 29-9-2025 calculate physical link statistics and power consumption using the data AFTER limitations



CUmn = getCUmnFromDB(CUmn, L, dbConnection)
Wmn = getWmnFromDB(Wmn, L, dbConnection)
SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)

wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParametersAfterLimitations(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection) # before updating limits and blockings

PowerIP, PowerTransponders, PowerEDFAs, PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)

#7-2-2026
PowerQ_HP, PowerQ_LP = evaluatePowerConsumptionPerQueue(dbConnection, Di, Di_Q0, Di_Q1, Er, Et, Ee, SigmaCij, N, L)




#22-8-2026
# Add wavelength converter overheads to total power consumption
PowerQ_HP += total_pow_overhead_HP
PowerQ_LP += total_pow_overhead_LP
PowerTotal = PowerTotal + total_pow_overhead_HP + total_pow_overhead_LP

'''
# Add wavelength converter overheads to average latencies
if len(averageLatPerQueue) > 0:
    avgLatQ_HP = roundatdecimals(averageLatPerQueue[0] + mean_lat_overhead_HP, 3)
else:
    avgLatQ_HP = roundatdecimals(mean_lat_overhead_HP, 3)

avgLatQ_LP = roundatdecimals(averageLatPerQueue[1] + mean_lat_overhead_LP, 3)
'''


#SOP
if (GlobalSOP==True) :
    print ("<table class='tableLat'>")
    print ("<tr><td>LatRouterPort:",LatRouterPort," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatTransponder:",LatTransponder," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatEDFA:",LatEDFA," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatFiberKilometer:",LatFiberKilometer," ",LatencyTimeUnit,"</td></tr>")
    print ("</table>")   
#EOP

#now = datetime.now()
#timeStamp = "y"+str(now.year)+"_m"+str(now.month)+"_d"+str(now.day)+"_h"+str(now.hour)+"_m"+str(now.minute)+"_s"+str(now.second)+"_u"+str(now.microsecond)

if ( sys.argv[3] != ""):
    experimentName = sys.argv[3]
else:
    experimentName = "Default Experiment"

if not filexists(experimentName+".csv"):
    writeCaptions = True
    fileMode = "w"
else:
    writeCaptions = False
    fileMode = "a"

# I need the CSV in every case (detailreport OR basicreport)
fout = open(experimentName+".csv",fileMode)

# time calculation end
# print ("--- %s seconds ---" % (time.time() - start_time))
#end_processtime = time.process_time_ns()

end_processtime = timeit.default_timer()
ProcessTime = end_processtime - start_processtime

TotalCapacity = calculateTotalCapacity(aggregatedTReqs)
TotalCapacity = roundatdecimals(TotalCapacity,3)

# Write the output to text file

#print ("<h3>Virtual Link Totals", VirtualLinkTotals,"</h3>")

# reused = len(ReUsedLightpaths) #old way to count reused lightpaths
#reused = 0 # no reused lightpaths (virtual links) for Direct # reused, reuses = CountLightpathsReusedReuses(VirtualLinkTotals)
#reuses = 0 # no reused lightpaths (virtual links) for Direct # reused, reuses = CountLightpathsReusedReuses(VirtualLinkTotals)

#Mix uses both direct and multihop bypass
reused, reuses = CountLightpathsReusedReuses(VirtualLinkTotals)


#print ("<h4>reused",reused, "reuses", reuses,"</h4>")

lightpaths = len(VirtualLinkTotals) #TotalLightpaths[0] # number of virtual (lightpath) links

PercentReusedLightpaths = reused / lightpaths * 100
AverageLightpathReuses = reuses / reused if reused > 0 else "NotApplicable"

txtN = str(len(N))
txtL = str(len(L))
#txtX = str(X[xi]) if lenQs==1 else str(X[xi]*lenQs)
txtX = str(X[xi])
txtCap = str(TotalCapacity)
txtPowerIP = str(PowerIP)
txtPowerTransponders = str(PowerTransponders)
txtPowerEDFAs = str(PowerEDFAs)
txtPower = str(PowerTotal)
#7-2-2026
txtPowerQ_HP = str(PowerQ_HP)
txtPowerQ_LP = str(PowerQ_LP)

#txtProcess = str(roundatdecimals(ProcessTime*1.0e-9, 6))
txtProcess = str(roundatdecimals(ProcessTime, 3))

txtLightpaths = str(lightpaths)
txtReusedLightpaths = str(reused) 

txtPercentReusedLightpaths = str(roundatdecimals(PercentReusedLightpaths,1))

#21-8-2026
#txtAverageLightpathReuses = str(roundatdecimals(AverageLightpathReuses,3))
# Calculate and format the average reuses safely
if reused > 0:
    AverageLightpathReuses = reuses / reused
    txtAverageLightpathReuses = str(roundatdecimals(AverageLightpathReuses, 3))
else:
    txtAverageLightpathReuses = "NotApplicable"


#txtLightpathReuses = str(LightpathReuses[0])
#txtLightpathReuses = str(reuses)


txtLatencyTotal = "-" #str(LatencyTotal)
txtLatencyTotal_Q0 = "-" #str(LatencyTotal_Q0)
txtDistribution = distributionForTReqs

if lenQs == 1:
    txtLatencyTotal_Q1 = "-"
if lenQs == 2:
    txtLatencyTotal_Q1 = "-" #str(LatencyTotal_Q1)

txtwUaverage = str(wUaverage)
txtfUaverage = str(fUaverage)

#18-5-2026 start of markup
#20-9-2025 calculate and save to the lightbase database latencies per traffic request and per traffic request thread (routing step, concurrent transmissions)
saveLatencyPerTrafficRequestToDatabase(dbConnection)
saveLatencyPerTrafficRequestToDatabase_according_to_the_old_latency_formula(dbConnection)


#22-8-2026
#PROSOXI! Η ΚΛΗΣΗ ΤΗΣ latencyPerQueueNewFormula() ΠΡΕΠΕΙ ΝΑ ΕΠΕΤΑΙ ΤΩΝ saveLatencyPerTrafficRequestToDatabase() ΚΑΙ saveLatencyPerTrafficRequestToDatabase_according_to_the_old_latency_formula() ΓΙΑΤΙ ΧΡΗΣΙΜΟΠΟΙΕΙ ΤΟΝ ΠΙΝΑΚΑ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ ΠΟΥ ΟΡΙΖΟΥΝ ΑΥΤΕΣ ΟΙ ΣΥΝΑΡΤΗΣΕΙΣ!
averageLatPerQueue = latencyPerQueueNewFormula(dbConnection)

#22-8-2026

if len(averageLatPerQueue) > 1:
    avgLatQ_HP = roundatdecimals(averageLatPerQueue[0] + mean_lat_overhead_HP, 3)
    avgLatQ_LP = roundatdecimals(averageLatPerQueue[1] + mean_lat_overhead_LP, 3)
elif len(averageLatPerQueue) == 1:
    avgLatQ_HP = roundatdecimals(averageLatPerQueue[0] + mean_lat_overhead_HP, 3)
    avgLatQ_LP = roundatdecimals(mean_lat_overhead_LP, 3)
else:
    avgLatQ_HP = roundatdecimals(mean_lat_overhead_HP, 3)
    avgLatQ_LP = roundatdecimals(mean_lat_overhead_LP, 3)


#18-5-2026 end of markup

#get latencies from DB
LatQAnyTypeAny = getLatencyStatsPerTrafficRequest(dbConnection, "%", "%") # Like % in SQL describes any value
LatQAnyTypeNew = getLatencyStatsPerTrafficRequest(dbConnection, "%", "New")
LatQAnyTypeGrm = getLatencyStatsPerTrafficRequest(dbConnection, "%", "Grm")

#get latencies from DB for Q0 Direct!
LatQ0TypeAny   = getLatencyStatsPerTrafficRequest(dbConnection, "0", "%")
LatQ0TypeNew   = getLatencyStatsPerTrafficRequest(dbConnection, "0", "New")
LatQ0TypeGrm   = ["Empty","Empty","Empty"] # no Grm for Direct #getLatencyStatsPerTrafficRequest(dbConnection, "0", "Grm")

#get latencies from DB for Q1 Multihop!
LatQ1TypeAny = getLatencyStatsPerTrafficRequest(dbConnection, "1", "%")   if lenQs == 2 else ["Empty","Empty","Empty"]
LatQ1TypeNew = getLatencyStatsPerTrafficRequest(dbConnection, "1", "New") if lenQs == 2 else ["Empty","Empty","Empty"]
LatQ1TypeGrm = getLatencyStatsPerTrafficRequest(dbConnection, "1", "Grm") if lenQs == 2 else ["Empty","Empty","Empty"]

#create and write CSV caption
txtCaptions = ""

if writeCaptions:
    txtCaptions = setTextCaptions(LatencyTimeUnit4csv)

    fout.write(txtCaptions)

#accumulating latency is not correct way to calculate it, hence it is not included in the CSV by replacing the values with dashes
txtLatencyTotal    = "-"
txtLatencyTotal_Q0 = "-"
txtLatencyTotal_Q1 = "-"

ts = datetime.now()

timeStamp = f"y{ts.year:04d}_m{ts.month:02d}_d{ts.day:02d}_h{ts.hour:02d}_m{ts.minute:02d}_s{ts.second:02d}_u{ts.microsecond:06d}"


txtLine  = UUID+";"
txtLine += timeStamp+";"+computername+";"+programfolder+";"+Algorithm+";"+str(lenQs)+";"+schedulingstrategy+";"+experimentName+";"+netName+";"+txtN+";"+txtL+";"+txtX+";"
txtLine += txtDistribution+";"+txtCap+";"+txtPowerIP+";"+txtPowerTransponders+";"
txtLine += txtPowerEDFAs+";"+txtPower+";"+txtPowerQ_HP+";"+txtPowerQ_LP+";"+txtProcess+";"

#18-5-2026
#txtLine += f"{avgLatQ_HP};{avgLatQ_LP};"
txtLine += f"{avgLatQ_HP:.3f};{avgLatQ_LP:.3f};"

txtLine += txtLightpaths+";"+txtReusedLightpaths+";"
txtLine += txtPercentReusedLightpaths+";"+txtAverageLightpathReuses+";"
txtLine += txtwUaverage+";"
txtLine += txtfUaverage+";"

for stat in LatQAnyTypeAny:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQAnyTypeNew:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQAnyTypeGrm:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ0TypeAny:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ0TypeNew:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ0TypeGrm:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ1TypeAny:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ1TypeNew:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

for stat in LatQ1TypeGrm:
    token = ""
    if stat == None:
        token = "Empty;"
    elif type(stat) is str:
        token = f"{stat:s};"
    else:
        token = f"{stat:.3f};"
    txtLine += token

txtLine += list2string(limitations,",")+";"
txtLine += str(maxFibersPerLink)+";"
txtLine += str(maxWavelengthsPerFiber)+";"
txtLine += str(maxGbpsPerWavelength)+";"
txtLine += str(LatRouterPort)+";"
txtLine += str(LatTransponder)+";"
txtLine += str(trafficPercentOfQueueHP)+";"
txtLine += str(trafficPercentOfQueueLP)+";"
txtLine += str(countPassLPs)+";"
txtLine += str(countBlockedLPs)+";"
txtLine += str(passLPsPercent)+";"
txtLine += str(blockedLPsPercent)+";"
txtLine += str(countPassTRs)+";"
txtLine += str(countBlockedTRs)+";"
txtLine += str(passTRsPercent)+";"
txtLine += str(blockedTRsPercent)+";"

#txtLine += AverageLatencyOfTrafficRequests(dbConnection)+";"

if sys.argv[20] == "Yes": #CheckForRevisits
    txtLine += "Not_Allowed;"
else:
    txtLine += "Allowed;"

txtLine += str(numberOfPathsWithRevisitWhichRoutedDirectly)+";"

txtLine += str(numberOf_LPs_checkedForHardLatencyCap)+";"

txtLine += ("Empty" if countBlockedVL_Q_HP == -1 else str(countBlockedVL_Q_HP))+";" # -1 means hard latency cap not applied for Q_HP (Q0)
txtLine += ("Empty" if countBlockedVL_Q_LP == -1 else str(countBlockedVL_Q_LP))+";" # -1 means hard latency cap not applied for Q_LP (Q1)

#txtLine += getListOfLatenciesForAllTrafficRequestsOLDformula(dbConnection)+";"
#txtLine += getListOfLatenciesForAllTrafficRequestsNEWformula(dbConnection)+";"

#18-8-2026
txtLine += str(Lwc)+";"
txtLine += str(Ewc)+";"
txtLine += str(NumberOfShortestPaths)+";"



#22-8-2026
# Add the specific converter overheads to the end of the CSV line
txtLine += f"{total_pow_overhead_HP:.3f};"
txtLine += f"{total_pow_overhead_LP:.3f};"
txtLine += f"{mean_lat_overhead_HP:.3f};"
txtLine += f"{mean_lat_overhead_LP:.3f};"



txtLine += "\n"


#keep the dot (.) as the decimal separator symbol for processing by my Grapher application
#txtLine = txtLine.replace(".", ",") #for Greek regional settings (comma is the decimals' separator)

fout.write(txtLine)
fout.close()

#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c' id='results'>")
    print ("<tr><th>RunID (UUID)</th><th>Algorithm</th><th>Experiment name</th><th>Network</th><th>Number of nodes</th><th>Number of links</th><th>X (Gbps)</th><th>Total capacity processed (Gbps)</th><th>Power of IP routers (kWatt)</th><th>Power of WDM Transponders (kWatt)</th><th>Power of EDFAs (kWatt)</th><th>TotalPower (kWatt)</th><th>Power Q<sub>HP</sub>(kWatt)</th><th>Power Q<sub>LP</sub>(kWatt)</th><th>Process Time (sec)</th>")
    
    #18-5-2026
    print ("<th>Average Latency for the traffic demands of Q<sub>HP</sub>("+LatencyTimeUnit+")</th><th>Average Latency for the traffic demands of Q<sub>LP</sub>("+LatencyTimeUnit+")</th>")
    
    print ("<th>Total lightpaths</th><th>Reused Lightpaths</th><th>Percent of Reused Lightpaths (%)</th><th>Average Lightpaths Reuses</th><th>Average wavelengths utilisation (%)</th><th>Average fiber links utilisation (%)</th>")
    print ("<th>limitations</th>")
    print ("<th>maxFibersPerLink</th>")
    print ("<th>maxWavelengthsPerFiber</th>")
    print ("<th>maxGbpsPerWavelength</th>")
    print ("<th>LatRouterPort ("+LatencyTimeUnit+")</th>")
    print ("<th>LatTransponder ("+LatencyTimeUnit+")</th>")
    print ("<th>Traffic_QueueHP (%)</th>")
    print ("<th>Traffic_QueueLP (%)</th>")
    print ("</tr>")
    
    print ("<tr><th>"+UUID+"</th><th>"+Algorithm+"</th><th>"+experimentName+"</th><th>"+netName+"</th><th>"+txtN+"</th><th>"+txtL+"</th><th>"+txtX+"</th><th>"+txtCap+"</th><th>"+txtPowerIP+"</th><th>"+txtPowerTransponders+"</th><th>"+txtPowerEDFAs+"</th><th>"+txtPower+"</th><th>"+txtPowerQ_HP+"</th><th>"+txtPowerQ_LP+"</th><th>"+txtProcess+"</th>")
    
    #18-5-2026
    print (f"<th>{avgLatQ_HP:.3f}</th><th>{avgLatQ_LP:.3f}</th>")
    
    print ("<th>"+txtLightpaths+"</th><th>"+txtReusedLightpaths+"</th><th>"+txtPercentReusedLightpaths+"</th><th>"+txtAverageLightpathReuses+"</th><th>"+txtwUaverage+"</th><th>"+txtfUaverage+"</th>")
    print ("<th>"+list2string(limitations,",")+"</th>")
    print ("<th>"+str(maxFibersPerLink)+"</th>")
    print ("<th>"+str(maxWavelengthsPerFiber)+"</th>")
    print ("<th>"+str(maxGbpsPerWavelength)+"</th>")
    print ("<th>"+str(LatRouterPort)+"</th>")
    print ("<th>"+str(LatTransponder)+"</th>")
    print ("<th>"+str(trafficPercentOfQueueHP)+"</th>")
    print ("<th>"+str(trafficPercentOfQueueLP)+"</th>")

    print ("</tr>")
    
    print ("</table>")
    
    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeAny:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeNew:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeGrm:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeAny:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeNew:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeGrm:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeAny:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")
    
    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeNew:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeGrm:
        #print (f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print ("<th>Empty</th>")
        elif type(stat) is str:
            print (f"<th>{stat:s}</th>")
        else:
            print (f"<th>{stat:.3f}</th>")
    print ("</tr></table>")    

    print ("</body></html>")
#EOP

#22-7-2026 moved closing DB at the end
'''
#close DB connection
if dbConnection:
    dbConnection.close()
'''

#logging 
#SOP
if (GlobalSOP==True) :
    #if dbConnection:
        #dbConnection.close()
    sys.stdout.close()
    sys.stdout=stdoutOriginal
#EOP

if (sys.argv[4] == "detailreport") and (sys.argv[7]=="pdfout"):
    # Convert Google search page to PDF
    # install software for OS from https://wkhtmltopdf.org/
    #                              https://wkhtmltopdf.org/downloads.html
    # install wrapper for python $pip install pdfkit
    # add bin directory of installation to Path system variable, e.g. "C:\Program Files\wkhtmltopdf\bin"
    
    import pdfkit # type: ignore

    if platform.system() == 'Windows':
        path_wkhtmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    elif platform.system() == 'Linux':
        path_wkhtmltopdf = r'/usr/bin/wkhtmltopdf' 
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    #inHTML = protocol+graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html"

    # Allow access to local files
    options = {
        # https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        #'javascript-delay':'10', #Optional
        'encoding': 'UTF-8',
        'enable-local-file-access': None, #To be able to access CSS
        'orientation': 'Landscape',
        'page-size': 'A3',
        'header-right':'[page]/[toPage]'
    }
    #pdfkit.from_url(inHTML, outPDF, verbose=True, configuration=config, options=options)

    if platform.system() == 'Windows':
        inHTML = UUID+"_"+graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html"
        outPDF = UUID+"_"+graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".pdf"
    elif platform.system() == 'Linux':
        inHTML = UUID+"_"+graphsPath+"/"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html"
        outPDF = UUID+"_"+graphsPath+"/"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".pdf"

    pdfkit.from_file(inHTML, outPDF, verbose=False, configuration=config, options=options)

#if sys.argv[4] == "detailreport" and sys.argv[9] == "removereport":
if sys.argv[9] == "removereport":
    removeTree(graphsPath)

if sys.argv[9] == "keepDBonly":
    #keep_and_rename_file(UUID, graphsPath, "lightbase.db")
    keep_and_rename_file(UUID, graphsPath, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".db")


#close the error log
#errlog = open(experimentName+"_Errors.csv","w")
#errlog.write(txtLine)

#22-6-2026 no need to close errlog anymore, now using the memStderr class for error logs
#errlog.close()

#22-7-2026 export to MS Excel spreadsheet
spr = Spreadsheet()

cursor = dbConnection.execute("SELECT * from RunID;")
data2excel = cursor.fetchall()
spr.export_run_ID(data2excel)

cursor = dbConnection.execute("SELECT * from RunConfiguration;")
data2excel = cursor.fetchall()
spr.export_run_configuration(data2excel)

cursor = dbConnection.execute("SELECT * from Nodes;")
data2excel = cursor.fetchall()
spr.export_network_nodes(data2excel)

cursor = dbConnection.execute("SELECT * from PhysicalLinks;")
data2excel = cursor.fetchall()
spr.export_network_links(data2excel)

cursor = dbConnection.execute("SELECT * from Queues;")
data2excel = cursor.fetchall()
spr.export_queues(data2excel)

cursor = dbConnection.execute("SELECT * from TrafficRequests;")
data2excel = cursor.fetchall()
spr.export_traffic_requests(data2excel)

cursor = dbConnection.execute("SELECT * from VirtualLinks;")
data2excel = cursor.fetchall()
spr.export_virtual_links(data2excel)

cursor = dbConnection.execute("SELECT * from RoutingVirtualLinksOverPhysicalTopology;")
data2excel = cursor.fetchall()
spr.export_routing_vl_over_pt(data2excel)

cursor = dbConnection.execute("SELECT * from RoutingTrafficRequestsOverVirtualTopology;")
data2excel = cursor.fetchall()
spr.export_routing_tr_over_vt(data2excel)

cursor = dbConnection.execute("SELECT * from LatencyOfThreadOfTrafficRequest;")
data2excel = cursor.fetchall()
spr.export_latency_of_thread_of_traffic_request(data2excel)

cursor = dbConnection.execute("SELECT * from LatencyOfTrafficRequest;")
data2excel = cursor.fetchall()
spr.export_latency_of_traffic_request(data2excel)

cursor = dbConnection.execute("""
    select             
        TReqQueNum, TReqReqNum, TReqSrc, TReqDst, TReqCap, TReqResult, VLsrc,
        VLdst, VLnum, VLcaputil, VLcapfree, VLresult, routeTReqOverVTtype,
        routeTReqOverVTroutingStep, routeTReqOverVTroutStepVLseqnum,
        routeTReqOverVTresult, routeVLoverPT_PLsrc, routeVLoverPT_PLdst,
        routeVLoverPT_fiberID, routeVLoverPT_waveID, routeVLoverPT_type,
        routeVLoverPT_HopSeqNum, routeVLoverPT_NumOfHops, routeVLoverPT_shPathAsInt,
        routeVLoverPT_shPathAsStr, routeVLoverPT_PLdir, routeVLoverPT_currSrc, 
        routeVLoverPT_currDest, routeVLoverPT_LatIP, routeVLoverPT_LatTransp,
        routeVLoverPT_result, PLdistance, PLlatEDFA, PLlatFibLen
    from 
        route_traffic_requests_over_virtual_and_physical_topology;
""")
data2excel = cursor.fetchall()
spr.export_route_tr_over_vt_and_pt(data2excel)

spr.export_vt_dictionary(vT)
spr.export_request_routing_info(ReqRouteInfo)
spr.export_vl_ids(VirtualLinkIDs)
spr.export_vl_traffic_reqs(VirtualLinkTReqs)
spr.export_vl_totals(VirtualLinkTotals)
spr.export_reservations(NetworkWavelengthsMap, L)
spr.export_lightpath_routes(NetworkWavelengthsMap, L)

spreadsheet_filename = f"{graphsPath}\\Alg_{alg}_Net-{netName}_X-{str(X[xi])}.xlsx"
spr.save(spreadsheet_filename)

#close DB connection
if dbConnection:
    dbConnection.close()

