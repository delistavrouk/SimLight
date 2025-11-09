# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 2021, 2022, 2023, 2024, 2025
# Enhanced version of Shen & Tucker 2009 heuristic algorithm 2 "multi-hop bypass" serves traffic requests from 2 queues one high priority (video) one low priority (best effort)

# usage: python <program name> <network> <X index> <experiment name for csv file>
# command line parameters example
# PS C:\STDMB> python               codeHybrid.py    N4L5_GRNetSubnet.txt      0         testexperiment                 detailreport      gensave                            lamda.txt                     pdfout                        1                  keepreport                         HomePC                 SimLight                                                      Uniform        Q0_75_Q1_25           2                 4                               40
# <prompt>     <python interpreter> <program name>   <network>                 <X index> <experiment name for csv file> <global printout> <save lamda matrix to text file>   <filename for lamda matrix>   <save web page to pdf or not> <number of Queues> <keep or not detailreport, if any> <name of the computer> <program folder under the root (Win) or home (Lin) directory> <distribution> <scheduling strategy> <fibers per link> <wavelength channels per fiber> <wavelngth channel capacity in Gbps>
#                                                                                                                       basicreport       load                                                             nopdf                         2                  removepreport                                                                                                           Poisson        Q0nextQ1    
#                                                                                                                       <no printout>     <load lamda matrix from text file>                                                                                                                                                                                                                       Q1nextQ0
#                                   argv[0]          argv[1]                   argv[2]   argv[3]                        argv[4]           argv[5]                            argv[6]                       argv[7]                       argv[8]            argv[9]                            argv[10]               argv[11]                                                      argv[12]       argv[13]              argv[14]          argv[15]                        argv[16]
# Configuration file sections                        [Nets_start]...[Nets_end] [X]       [Name]                         [Printout]        [Lamda]                            [LamdaTextFile]               [PDFout]                      [Queues]           [KeepEveryNthReport]               [ComputerName]         [ProgramFolder]                                               [Distribution] [Strategy]
#
# command line example for Hottest First And Comparison algorithm
#
# PS C:\SimLight> python codeHottestFirstAndComparison.v01.measurelatencyNewAndOldFormula.py N6L8_ShnTckr_a.txt 0 _HfaC detailreport gensave lambda.txt nopdf 1 keepreport Desktop C:\\SimLight Uniform HottestFirstAndComparison -1 4 40
#
# dependencies

# to update python packages to the latest version
# pip install pip-review
# pip-review --local --auto

# install...
# pip install numpy   # NumPy library used for calculations
# pip install networkx
# pip install pyvis   # PyVis used for visualisations
                      # network visualisation https://pyvis.readthedocs.io/en/latest/tutorial.html
                      #                       https://pyvis.readthedocs.io/en/latest/install.html
# download sqlite-dll-win-x64-3450200.zip from https://www.sqlite.org/download.html, unpack, and copy sqlite sqlite3.dll and sqlite3.def files to the application directory
# save as pdf
#   install software for OS from https://wkhtmltopdf.org/
#                                https://wkhtmltopdf.org/downloads.html
#   install wrapper for python $pip install pdfkit

#2DO : elaboration needed
#Done : elaboration completed
#>>> : elaboration priority
#Novelties

from pydoc import doc
from turtle import update
from webbrowser import get
import sys
import numpy # type: ignore
import time
import timeit
from datetime import datetime
from codeGusLibQueues import *
from random import randrange
import platform
import uuid

#fsqlInsert = open("SQL_INSERTINTO_RoutingTrafficRequestsOverVirtualTopology.txt","w")
#fsqlRTROVT = open("SQL_SELECT_RoutingTrafficRequestsOverVirtualTopology.txt","w")
#fsqlTR = open("SQL_SELECT_TrafficRequests.txt","w")
#fsqlVL = open("SQL_SELECT_VirtualLinks.txt","w")

#fsqlInsert.close()
#fsqlRTROVT.close()
#fsqlTR.close()
#fsqlVL.close()

#for i in range(len(sys.argv)):
#    print(i,":",sys.argv[i])

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
errlog = open(experimentName+"_Errors.txt","a")
#errlog.write(txtLine)
#errlog.close()
sys.stderr = errlog

#set the name of the algorithm
if sys.argv[8] == "1":
    Algorithm = "HottestAndComparison"
elif sys.argv[8] == "2":
    Algorithm = "NotApplicable"
    error("HottestAndComparison has been asked to run using one (1) queue,",7)
else:
    error("No parameter for the number of Queues",8)

computername = sys.argv[10]

programfolder = sys.argv[11]

#select app dir based on the host OS
'''
if platform.system() == 'Windows':
    appDir = 'C:\\'+programfolder
elif platform.system() == 'Linux':
    appDir = "/home/kostas/"+programfolder
else:
    appDir = "/home/kostas/"+programfolder
'''
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

netName, N, L, Nm, Dist, HasWavConv = readData(sys.argv[1]) # read network definition from text file

# first command line parameter is the text file with the network definition 
# example of a network text file:


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
original_X = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 400, 640, 960, 1280]

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

limitations = decideLimitations(N, HasWavConv, maxFibersPerLink)

"""
decideLimitations()

Assume:
    Each link has the same number of fibers, and each fiber the same number of wavelength channels

Return:
    "NoBlocking"
    "NumFibers"         Wavelength converters everywhere - No Wavelength Continuity Constraint
    "WavContinuity"     Some wavelength converters - Wavelength Continuity Constraint depending on each link's nodes
"""

SetGlobalLimits(maxFibersPerLink,maxWavelengthsPerFiber,maxGbpsPerWavelength,B,maxFiberCapacity,maxLinkCapacity)

# The physical topology G
G = (N, L) 

# Virtual topology data structure. The set of virtual links.

#VTobj = VirtualTopology("VT")

# VT: [i, j] => Logical/Virtual Link from node i to node j.
# VT is the old virtual topology structure
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


#Since 2024-Aug I use the following 3 dictionaries to keep information related to routing
#print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
#printVLids(VirtualLinkIDs)
#print("<li>Virtual Link Traffic Requests = {(s,d,i):[(que,req,cap,type),...],...}")
#printVLTReqs(VirtualLinkTReq)
#print("<li>Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...}")
#printVLTotals(VirtualLinkTotals)


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

#there is no Amn_Q0 or Amn_Q1 because if a fiber is due to a traffic request then the fiber has predetermined number of EDFAs

#unique, standard colours for each node
Ncolours = []

#latency parameters 

LatencyTimeUnit = "&micro;sec"
LatencyTimeUnit4csv = "microsec"

LatRouterPort = float(sys.argv[17])   # 30 # microsecond
LatTransponder = float(sys.argv[18])  # 100 # microsecond
LatEDFA = 100 / 1000.0 # nanosecond
LatFiberKilometer = 5 # microsecond

#main program's execution starts here #################################################################################################################

Ncolours = setNodeColours(N) # use function for consistent graph (network) node colours throughout the execution

alg = Algorithm.replace(' ', '_')

stdoutOriginal, sys.stdout, graphsPath = Log2path(appDir, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi]))

#SOP
if (GlobalSOP==True) :
    sys.stdout.reconfigure(encoding='utf-8')
    htmlhead("Hottest First And Comparison", lenQs, sys.argv[12])

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

    visualisePhysicalTopology(N,L, graphsPath, Ncolours, Dist, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output

    print ("<table class='table1c'>")
    print ("<tr><th colspan=",len(N),">&lambda;: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi])
    print (f"for a total of {lenQs:d} queue{('s.' if lenQs>1 else '.'):s}")
    print (f"<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a {sys.argv[12]} distribution,")
    print (" which is centered at an identical average.") #"That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, the actual demand between a node pair is generated by a random function and values distributed following the Poisson process.")
    print ("</em></th></tr>")
#EOP

#SOP
#if (GlobalSOP==True) :
dbConnection = createSQLiteDB(graphsPath, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".db")
saveUUID2sqlite(dbConnection, UUID)
saveQueues2sqlite(dbConnection, QueueNames)
savePhysicalLinks2sqlite(dbConnection, L, Dist, EDFAdist, LatEDFA, LatFiberKilometer, graphsPath)
saveNodes2sqlite(dbConnection, N)
#EOP

if sys.argv[5] == "gensave":
    demandsfilename = os.path.join(graphsPath, sys.argv[6])
    lamdatextfile = open(demandsfilename,"w") # since in the generateTrafficRequests() function the lamdatextfile is appended ("a"), I recreate it empty ("w") to avoid keepeing previous data.
    lamdatextfile.close()

# Lee & Rhee Table I, step 1. Initialization

#nextReqID = 1
TReqsForQueue = []
for i in range(lenQs):
    tempQ = generateTrafficRequests_0_2X(dbConnection, N, graphsPath, lenQs, X, xi, QueueNames[i], i, sys.argv[12]) # i is the queue number (queueID), sys.argv[12] is the distribution name Uniform/Poisson
    
    TReqsForQueue.append(tempQ) # krataei ta traffic reqquests gia kathe queue

if lenQs==1:
    aggregatedTReqs = TReqsForQueue[0]
else:
    print("<div>Error: Hottest First And Comparison Designed for 1 queue") # Program designed for 1 or 2 queues so far.")
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

'''
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
'''

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
    print("<div>Hottest and Comparison runs only for one queue!</div>")
    exit(1)
else:
    startingstep = 1

    s="Virtual topology graph after processing request "
    VTgraph = graph_new(s, True)
    
    #route Q0 using Hottest and comparison
    Q=0

    # 30-9-2025
    # startingstep = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyHeaviestFirstAndComparison(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)

    # Hottest First and Comparison for one queue

    # data

    G = {}                  # vT={}   # VT = {node:[neighbour, ...], ...}
    Glist = []              # vTL=[]   # VTL = [(tuple of source, destination of virtual link), ...]
    Gfreecap = {}           # vTfreeCap={}   #VTFreeCap = {(tuple of source, destination of virtual link):[free capacity], ...}
    Gfinal = {}             # VTfinal={} # virtual topology for routing virtual links over physical topology

    GvlIDs = {}             # VirtLinkIDs = {}  # a dictionary to keep the unique virtual link IDs assigned to all virtual (lightpath) links.
                                                # VirtLinkIDs = {id:(tuple of source, destination of virtual link), ...}
    GVLIDsYetAnother = {}   # VirtLinkIDsYetAnother = {}  # a dictionary to keep the unique virtual link IDs assigned to all virtual (lightpath) links. 
                            # {id: [src, dst, free], ...} 

    GvirtualLinkIDs = {}        # VirtualLinkIDs = {} # = {(s,d):[0,1,2,...],...}
    GvirtualLinkTotals = {}     # VirtualLinkTotals = {} # = {(s,d,id):[utilcap, freecap, number_of_TReqs_it_serves], ...}
    GvirtualLinkTReqs = {}      # VirtualLinkTReqs = {} # = {(s,d,id):[(que1,req1,cap1,"New"), (que2,req2,cap2,"Grm"),...], ...}
    GreqRouteInfo = {}           # ReqRouteInfo = {}   # req = {(queue, request n`umber): [link and free capacity, ...], ...}   how request is routed; which links it uses and their capacity
    
    RoutingOfRequestedTrafficStep = 0 
    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

    # start 
    
    print("<li>Routing traffic requests of single queue using Hottest First and Comparison algorithm</li>")
    
    TReqs = TReqsForQueue[Q]

    #1-10-2025
    # sort traffic requests by hottest first (traffic demand of a request / shortest hop distance of the request)
    TReqs = sortTrafficRequestsByHottestAndComparison(TReqs, N, Nt, NmC)

    G = {}

    print("<li>virtual topology G is ", G)
          
    # Lee & Rhee Table I, step 2. Iteration

    for TRnum in range(len(TReqs)):     
    
        currentTR = TReqs[TRnum]
        src = currentTR[0]
        dst = currentTR[1]
        requiredCap = currentTR[2]  # in Gbps

        print("<hr><li>Current traffic request (flow) is",TRnum,"::",currentTR, "from",src,"to",dst,"requiring",requiredCap,"Gbps</li>")

        G1 = {}
        G2 = {}

        print("<li>virtual topology G1 is ", G1)
        print("<li>virtual topology G2 is ", G2)

        # Lee & Rhee Table I, step 2.1 Traffic grooming routing

        print("<li>Attempt to route using traffic grooming</li>")

        if (routeOneVirtualLinkOverTheVirtualTopologyWithTrafficGroomingForHeaviestHottestAndComparison(N, Q, TRnum, src, dst, G, Glist, Gfreecap, requiredCap, maxGbpsPerWavelength, Gfinal, ReqRouteInfo, ReUsedLightpaths, LightpathReuses, GVLIDsYetAnother, dbConnection, GvirtualLinkIDs, GvirtualLinkTReqs, GvirtualLinkTotals, RoutingOfRequestedTrafficStep, tag="G1temp") == 0): 
            
            print("<li>routing using traffic grooming succeeded</li>")
        
            RoutingOfRequestedTrafficStep += 1
            
            G1 = G.copy()
            G1virtualLinkTotals = GvirtualLinkTotals.copy()

            G1VT, VTfinal = convertVTtoOldFormatForRoutingOverPhysicalTopology(G1virtualLinkTotals, N)

            Cij, SigmaCij = calculateSomePowerParametersForNodesAndLinks(G1VT, N, Cij, SigmaCij)

            RoutingOfVirtualLinksOverWavelengths = {}

            # 4-10-2025: does routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass() insert multiple records?
            #5-10-2025 no insert to DB 
            phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyForHeaviestHottestAndComparison(G1VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder)

            CUmn = getCUmnFromDB(CUmn, L, dbConnection)
            Wmn = getWmnFromDB(Wmn, L, dbConnection)
            SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)

            wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection)

            PowerIP, PowerTransponders, PowerEDFAs, G1PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)
            G1EnergyIP, G1EnergyWDM, G1Energy = evaluatePowerConsumptionUsingLeeRheeFormula(G1virtualLinkTotals, RoutingOfVirtualLinksOverWavelengths, G1, N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)

            print("<li>virtual topology G1 is ", G1, "</li>")
            print(f"<li>Request {TRnum:d} routed using grooming with G1 power {G1PowerTotal:.3f} Watts (Shen & Tucker formula)</li>")
            print(f"<li>Request {TRnum:d} routed using grooming with G1 power {G1Energy:.3f} Watts (Lee & Rhee formula)</li>")
        
        else:

            G1 = {}
            G1PowerTotal = float('inf')
            G1Energy = float('inf')

            print("<li>routing using traffic grooming failed</li>")
            print("<li>virtual topology G1 is ", G1, "</li>")
            print(f"<li>G1 power is {G1PowerTotal:.3f} kWatts (Shen & Tucker)</li>")
            print(f"<li>G1 power is {G1Energy:.3f} kWatts (Lee & Rhee)</li>")

        # Lee & Rhee Table I, step 2.2 Direct bypass routing

        print("<li>also route using direct bypass</li>")

        if (addNewVirtualLinkToTheVirtualTopologyWithoutGroomingDirectBypassRoutingForHeaviestHottestAndComparison(N, Q, TRnum, src, dst, G, Glist, Gfreecap, requiredCap, maxGbpsPerWavelength, Gfinal, ReqRouteInfo, GVLIDsYetAnother, dbConnection, GvirtualLinkIDs, GvirtualLinkTReqs, GvirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber, tag="G2temp") == 0):
            
            print("<li>routing using direct bypass succeeded</li>")                

            #if adding succeded
            RoutingOfRequestedTrafficStep += 1
            RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

            #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni, Nj, vt, vtl, vtfrcap, cap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
            #added new link to route required capacity successfully
            #remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
            #remain = remain - CapForTheLogicalLink
            #remain=numpy.round(remain, decimals=3, out=None)

            # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
            TotalLightpaths[0] += 1

            G2 = G.copy()
            G2virtualLinkTotals = GvirtualLinkTotals.copy()

            G2VT, VTfinal = convertVTtoOldFormatForRoutingOverPhysicalTopology(G2virtualLinkTotals, N)

            Cij, SigmaCij = calculateSomePowerParametersForNodesAndLinks(G2VT, N, Cij, SigmaCij)

            RoutingOfVirtualLinksOverWavelengths = {}

            #5-10-2025 no insert to DB 
            phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyForHeaviestHottestAndComparison(G2VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder)

            CUmn = getCUmnFromDB(CUmn, L, dbConnection)
            Wmn = getWmnFromDB(Wmn, L, dbConnection)
            SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)

            wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection)

            PowerIP, PowerTransponders, PowerEDFAs, G2PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)
            G2EnergyIP, G2EnergyWDM, G2Energy = evaluatePowerConsumptionUsingLeeRheeFormula(G2virtualLinkTotals, RoutingOfVirtualLinksOverWavelengths, G2, N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)

            print("<li>virtual topology G2 is ", G2, "</li>")
            print(f"<li>Request {TRnum:d} routed using direct bypass with G2 power {G2PowerTotal:.3f} kWatts (Shen & Tucker formula)</li>")
            print(f"<li>Request {TRnum:d} routed using direct bypass with G2 power {G2Energy:.3f} kWatts (Lee & Rhee formula)</li>")

        # Lee & Rhee Table I, step 2.3 Routing selection

        dbConnection.commit()

        print("<li>select the routing with the least power consumption:</li>")
        print(f"<li>G1 power is {G1PowerTotal:.3f} kWatts (Shen & Tucker formula)</li>")
        print(f"<li>G1 power is {G1Energy:.3f} kWatts (Lee & Rhee formula)</li>")
        print(f"<li>G2 power is {G2PowerTotal:.3f} kWatts (Shen & Tucker formula)</li>")
        print(f"<li>G2 power is {G2Energy:.3f} kWatts (Lee & Rhee formula)</li>")
        print("<li>according to Shen & Tucker formula the selected routing is:",("G1" if G1PowerTotal < G2PowerTotal else "G2"),"</li>")
        print("<li>according to Lee & Rhee formula the selected routing is:",("G1" if G1Energy < G2Energy else "G2"),"</li>")
        
        #if (G1PowerTotal < G2PowerTotal):
        if (G1Energy < G2Energy):
            G = G1.copy()
            GvirtualLinkTotals = G1virtualLinkTotals.copy()
            GVT = G1VT.copy()
            #print("<li>Request",TRnum,"routed using grooming with power",G1PowerTotal)
            print(f"<div style='color:green;font-weight:bold;'>Request {TRnum:d} routed using grooming (G1) with power {G1PowerTotal:.3f} kWatts</div>")

            try:
                sqlUndoG2 = "DELETE FROM RoutingTrafficRequestsOverVirtualTopology WHERE result = 'G2temp';"
                dbConnection.execute(sqlUndoG2)
                dbConnection.commit()
            except sqlite3.IntegrityError:
                print(f"Cannot delete the Routing of Traffic Requests Over Virtual Topology due to related data exist.")

            sqlUndoG2 = "UPDATE RoutingTrafficRequestsOverVirtualTopology SET result = 'G1' WHERE result = 'G1temp';"
            dbConnection.execute(sqlUndoG2)
            dbConnection.commit()

            try:
                sqlUndoG2 = "DELETE FROM VirtualLinks WHERE result = 'G2temp';"
                dbConnection.execute(sqlUndoG2)
                dbConnection.commit()
            except sqlite3.IntegrityError:
                print(f"Cannot delete the Virtual Link(s) due to related data exist.")

            sqlUndoG2 = "UPDATE VirtualLinks SET result = 'G1' WHERE result = 'G1temp';"
            dbConnection.execute(sqlUndoG2)
            dbConnection.commit()

        else:
            G = G2.copy()
            GvirtualLinkTotals = G2virtualLinkTotals.copy()
            GVT = G2VT.copy()
            #print("<li>Request",TRnum,"routed using direct bypass with power",G2PowerTotal)
            print(f"<div style='color:blue;font-weight:bold;'>Request {TRnum:d} routed using direct bypass (G2) with power {G2PowerTotal:.3f} kWatts</div>")

            try:
                sqlUndoG1 = "DELETE FROM RoutingTrafficRequestsOverVirtualTopology WHERE result = 'G1temp';"
                dbConnection.execute(sqlUndoG1)
                dbConnection.commit()
            except sqlite3.IntegrityError:
                print(f"Cannot delete the Routing of Traffic Requests Over Virtual Topology due to related data exist.")
            
            sqlUndoG1 = "UPDATE RoutingTrafficRequestsOverVirtualTopology SET result = 'G2' WHERE result = 'G2temp';"
            dbConnection.execute(sqlUndoG1)
            dbConnection.commit()

            try:
                sqlUndoG1 = "DELETE FROM VirtualLinks WHERE result = 'G1temp';"
                dbConnection.execute(sqlUndoG1)
                dbConnection.commit()
            except sqlite3.IntegrityError:
                print(f"Cannot delete the Routing of Traffic Requests Over Virtual Topology due to related data exist.")
            
            sqlUndoG1 = "UPDATE VirtualLinks SET result = 'G2' WHERE result = 'G2temp';"
            dbConnection.execute(sqlUndoG1)
            dbConnection.commit()
        #endif (G1PowerTotal < G2PowerTotal):
        
        print("<li>virtual topology G after processing request ",TRnum," is ", G, "</li>")

    #end for TRnum

    #5-10-2025: αφού γίνει η επιλογή της τελικής εικονικής τοπολογίας, τότε γίνεται το routing των virtual links της τελικής εικονικής τοπολογίας πάνω στην φυσική τοπολογία

    #G, VTfinal = convertVTtoOldFormatForRoutingOverPhysicalTopology(G1virtualLinkTotals, N)
    G, VTfinal = convertVTtoOldFormatForRoutingOverPhysicalTopology(GvirtualLinkTotals, N)
    Cij, SigmaCij = calculateSomePowerParametersForNodesAndLinks(GVT, N, Cij, SigmaCij)

    RoutingOfVirtualLinksOverWavelengths = {}
    phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(G, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)

    CUmn = getCUmnFromDB(CUmn, L, dbConnection)
    Wmn = getWmnFromDB(Wmn, L, dbConnection)
    SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)
    wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection)
    PowerIP, PowerTransponders, PowerEDFAs, G2PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)

    schedulingstrategy = sys.argv[13] if sys.argv[13]!=None else "HottestAndComparison"

    vT = G
    VirtualLinkTotals = GvirtualLinkTotals
    vTL = Glist
    vTfreeCap = Gfreecap
    VTfinal = Gfinal

#SOP
if (GlobalSOP==True) :
    print ("<h3 style='text-align:center'>Strategy utilised for the scheduling of the queue(s):", schedulingstrategy,"</h3>")
    
    print ("<table class='table1c'>")
    #print ("<tr><th>Free capacities for the Virtual Links of the Virtual Topology {(s, d): [<em>free capacity</em>], ...} (vTfreeCap) =",vTfreeCap,"</th></tr>")
    #2DO not use vTfreeCap
    print ("<tr><th>The Virtual Topology {node: [<em>list of neighbour nodes</em>], ...} (vT)") # =",vT,"</th></tr>")
    #5-10-2025: do not print printVTdictionaryAsTable(vT)
    print("</th></tr>")
    #print ("<tr><th>List of Virtual Links of Virtual Topology [(s, d),...] (vTL) =",vTL,"</th></tr>")
    #2DO not use vTL
    #print ("<tr><th>Virtual Links used for each traffic request {<em>(queue id, request id)</em>: [(s,d,type,capacity), ...], ...} (R)") #, ReqRouteInfo,"</th></tr>")
    print ("<tr><th>Virtual Links used for each traffic request {<em>(queue id, request id)</em>: [(virtual link (s,d,n), type, capacity utilised, step of routing the requested capacity, step's virtual link sequence number), ...], ...} (R)") #, ReqRouteInfo,"</th></tr>")
    printRequestRoutingInfoAsTable(ReqRouteInfo)
    
    print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
    printVLids(VirtualLinkIDs)
    print("<li>Virtual Link Traffic Requests = {(s,d,i):[(que,req,cap,type),...],...}")
    printVLTReqs(VirtualLinkTReqs)
    print("<li>Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...}")
    printVLTotals(VirtualLinkTotals)

    #print("<li>Virtual Links per Request R=")
    #printFreeCapacitiesAsTable(ReqRouteInfo)

    print("</th></tr>")
    print ("</table>")

#else:
    #routeAllTrafficRequestsOfTwoQueuesOverVirtualTopologyMultihopBypass(N,TReqsForQueue[0],TReqsForQueue[1],vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, "no graphs path needed, since no printout", Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)
#EOP

# 1-10-2025
#VT, VTfinal = convertVTtoOldFormatForRoutingOverPhysicalTopology(VirtualLinkTotals, N)
#Cij, SigmaCij = calculateSomePowerParametersForNodesAndLinks(VT, N, Cij, SigmaCij)
#RoutingOfVirtualLinksOverWavelengths = {}
#phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)

# 29-9-2025 apply limitations after the routing of the virtual links over the physical topology
print("<li><em>Limitation:",limitations)

if limitations == "NoBlocking":
    newRoutingOfVirtualLinksOverWavelengthsWithLimits = RoutingOfVirtualLinksOverWavelengths
    routingResult = {}
    for k in RoutingOfVirtualLinksOverWavelengths.keys():
        routingResult[k] = "Pass"

else:
    newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResult, netmap = blockTrafficAccordingToCriteria(L, RoutingOfVirtualLinksOverWavelengths, limitations, HasWavConv)

#SOP
#if (GlobalSOP==True) :    
#    for vl in newRoutingOfVirtualLinksOverWavelengthsWithLimits.keys():
#        print_vl_reservation(newRoutingOfVirtualLinksOverWavelengthsWithLimits, netmap, vl, vlIDtoTag(vl))
#EOP

#25-9-2025 2DO prepei na mpei mia stili me to result pass/block >>> DONE

#SOP
if (GlobalSOP==True) :    
    visualiseRoutingOfVirtualLinksOverPhysicalTopology(phyLinks, N, graphsPath, Ncolours, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output

    print("<p><li><em>PREVIOUS Routing of VLs over PT table:")
    printRoutingOfVirtualLinksOverWavelengthsAsTable(RoutingOfVirtualLinksOverWavelengths)

    print("<p><li><em>NEW Routing of VLs over PT table after limitations:")
    printRoutingOfVirtualLinksOverWavelengthsWithLimitResultsAsTableForHeaviestHottestFirstAndComparison(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResult)
#EOP

# 29-9-2025 calculate physical link statistics and power consumption using the data before limitations

CUmn = getCUmnFromDB(CUmn, L, dbConnection)
Wmn = getWmnFromDB(Wmn, L, dbConnection)
SigmaCij = getSigmaCijFromDB(SigmaCij, N, dbConnection)

wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection) # before updating limits and blockings

#9-10-2025:edw prepei na ypologizetai to power me ta data meta ta limits symfwna me Lee & Rhee formula
#apla twra den me endiaferei to power to teliko alla mono symfwna me Lee & Rhee formula gia na epilegw poia topologia na krataw se kathe bima
#PowerIP, PowerTransponders, PowerEDFAs, PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)
GEnergyIP, GEnergyWDM, GEnergy = evaluatePowerConsumptionUsingLeeRheeFormula(GvirtualLinkTotals, RoutingOfVirtualLinksOverWavelengths, G, N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)
PowerTotal = GEnergy
PowerIP = GEnergyIP
PowerEDFAs = GEnergyWDM
PowerTransponders = 0.0 # not calculated separately in Lee & Rhee formula

# 29-9-2025 update the databases according to the limitations

#<28-9-2025> statistics about the traffic requests that were blocked due to limitations
#for each lightpath (virtual link) whether it was passed or blocked

passLPs, blockedLPs = resultsDBUpdateOfVLs_LPs(routingResult, dbConnection)

totalLPs = len(routingResult) #how many lightpaths 
countPassLPs = len(passLPs) +1 #how many of the lightpaths were passed # 12-10-2025 fix the always -1 error
countBlockedLPs = len(blockedLPs) #how many of the lightpaths were blocked
passLPsPercent = roundatdecimals((countPassLPs/totalLPs*100.0),1) if totalLPs>0 else 0.0
blockedLPsPercent = roundatdecimals((countBlockedLPs/totalLPs*100.0),1) if totalLPs>0 else 0.0

#SOP
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

#print("<li>Passed traffic requests:",passTRs)
#print("<li>Blocked traffic requests:",blockedTRs)

updateDB_RoutingVirtualLinksOverPhysicalTopology_forHeaviestHottestAndComparison(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResult, dbConnection)

removeDB_BlockedVirtualLinksOverPhysicalTopology(newRoutingOfVirtualLinksOverWavelengthsWithLimits, routingResult, dbConnection)

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

wUaverage, fUaverage = calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection) # before updating limits and blockings

PowerIP, PowerTransponders, PowerEDFAs, PowerTotal = evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B)


#SOP
if (GlobalSOP==True) :
    
    print ("<table class='tableLat'>")
    print ("<tr><td>LatRouterPort:",LatRouterPort," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatTransponder:",LatTransponder," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatEDFA:",LatEDFA," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatFiberKilometer:",LatFiberKilometer," ",LatencyTimeUnit,"</td></tr>")
    print ("</table>")

    '''
    printLatenciesPerTrafficRequest(dbConnection, "All", "All")
    printLatenciesPerTrafficRequest(dbConnection, "All", "New")
    printLatenciesPerTrafficRequest(dbConnection, "All", "Grm")
    printLatenciesPerTrafficRequest(dbConnection, 0, "All")
    printLatenciesPerTrafficRequest(dbConnection, 0, "New")
    printLatenciesPerTrafficRequest(dbConnection, 0, "Grm")
    if lenQs==2:
        printLatenciesPerTrafficRequest(dbConnection, 1, "All")
        printLatenciesPerTrafficRequest(dbConnection, 1, "New")
        printLatenciesPerTrafficRequest(dbConnection, 1, "Grm")
    '''
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
# print("--- %s seconds ---" % (time.time() - start_time))
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
AverageLightpathReuses = reuses/reused if reused>0 else "NotApplicable"

txtN = str(len(N))
txtL = str(len(L))
#txtX = str(X[xi]) if lenQs==1 else str(X[xi]*lenQs)
txtX = str(X[xi])
txtCap = str(TotalCapacity)
txtPowerIP = str(PowerIP)
txtPowerTransponders = str(PowerTransponders)
txtPowerEDFAs = str(PowerEDFAs)
txtPower = str(PowerTotal)
#txtProcess = str(roundatdecimals(ProcessTime*1.0e-9, 6))
txtProcess = str(roundatdecimals(ProcessTime, 3))
txtLightpaths = str(lightpaths)
txtReusedLightpaths = str(reused)
txtPercentReusedLightpaths = str(roundatdecimals(PercentReusedLightpaths,1))
#txtAverageLightpathReuses = str(roundatdecimals(AverageLightpathReuses,3))
txtAverageLightpathReuses = str(roundatdecimals(AverageLightpathReuses,3)) if isinstance(AverageLightpathReuses, float) else AverageLightpathReuses
#txtLightpathReuses = str(LightpathReuses[0])
#txtLightpathReuses = str(reuses)
txtLatencyTotal = "-" #str(LatencyTotal)
txtLatencyTotal_Q0 = "-" #str(LatencyTotal_Q0)
txtDistribution = sys.argv[12]

if lenQs == 1:
    txtLatencyTotal_Q1 = "-"
if lenQs == 2:
    txtLatencyTotal_Q1 = "-" #str(LatencyTotal_Q1)

txtwUaverage = str(wUaverage)
txtfUaverage = str(fUaverage)

# 20-9-2025 calculate and save to the lightbase database latencies per traffic request and per traffic request thread (routing step, concurrent transmissions)
saveLatencyPerTrafficRequestToDatabase(dbConnection)
saveLatencyPerTrafficRequestToDatabase_according_to_the_old_latency_formula(dbConnection)

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
txtLine += txtPowerEDFAs+";"+txtPower+";"+txtProcess+";"+txtLightpaths+";"+txtReusedLightpaths+";"
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

txtLine += limitations+";"
txtLine += str(maxFibersPerLink)+";"
txtLine += str(maxWavelengthsPerFiber)+";"
txtLine += str(maxGbpsPerWavelength)+";"
txtLine += str(LatRouterPort)+";"
txtLine += str(LatTransponder)+";"

txtLine += "Empty;" #txtLine += str(trafficPercentOfQueueHP)+";" not for heaviest and comparison
txtLine += "Empty;" #txtLine += str(trafficPercentOfQueueLP)+";"

txtLine += str(countPassLPs)+";"
txtLine += str(countBlockedLPs)+";"
txtLine += str(passLPsPercent)+";"
txtLine += str(blockedLPsPercent)+";"

txtLine += str(countPassTRs)+";"
txtLine += str(countBlockedTRs)+";"
txtLine += str(passTRsPercent)+";"
txtLine += str(blockedTRsPercent)+";"

txtLine += AverageLatencyOfTrafficRequests(dbConnection)+";"

txtLine += "Empty;" # Not for Hottest the... if sys.argv[20] == "CheckForRevisits":
txtLine += "Empty;" # Not for Hottest the... txtLine += str(numberOfPathsWithRevisitWhichRoutedDirectly)+";"

txtLine += "Empty;" # Not for Hottest the... str(numberOf_LPs_checkedForHardLatencyCap)+";"
txtLine += "Empty;" # Not for Hottest the... if countBlockedVL_Q_HP == -1
txtLine += "Empty;" # Not for Hottest the... if countBlockedVL_Q_LP == -1

txtLine += getListOfLatenciesForAllTrafficRequestsOLDformula(dbConnection)+";"
txtLine += getListOfLatenciesForAllTrafficRequestsNEWformula(dbConnection)+";"

txtLine += "\n"

#keep the dot (.) as the decimal separator symbol for processing by my Grapher application
#txtLine = txtLine.replace(".", ",") #for Greek regional settings (comma is the decimals' separator)

fout.write(txtLine)
fout.close()

#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c' id='results'>")
    
    print ("<tr><th>RunID (UUID)</th><th>Algorithm</th><th>Experiment name</th><th>Network</th><th>Number of nodes</th><th>Number of links</th><th>X (Gbps)</th><th>Total capacity processed (Gbps)</th><th>Power of IP routers (kWatt)</th><th>Power of WDM Transponders (kWatt)</th><th>Power of EDFAs (kWatt)</th><th>TotalPower (kWatt)</th><th>Process Time (sec)</th>")
    print ("<th>Total lightpaths</th><th>Reused Lightpaths</th><th>Percent of Reused Lightpaths (%)</th><th>Average Lightpaths Reuses</th><th>Average wavelengths utilisation (%)</th><th>Average fiber links utilisation (%)</th>")
    print ("<th>limitations</th>")
    print ("<th>maxFibersPerLink</th>")
    print ("<th>maxWavelengthsPerFiber</th>")
    print ("<th>maxGbpsPerWavelength</th>")
    print ("<th>LatRouterPort ("+LatencyTimeUnit+")</th>")
    print ("<th>LatTransponder ("+LatencyTimeUnit+")</th>")
    #print ("<th>Traffic_QueueHP (%)</th>") not for heaviest and comparison
    #print ("<th>Traffic_QueueLP (%)</th>")
    print ("</tr>")

    print ("<tr><th>"+UUID+"</th><th>"+Algorithm+"</th><th>"+experimentName+"</th><th>"+netName+"</th><th>"+txtN+"</th><th>"+txtL+"</th><th>"+txtX+"</th><th>"+txtCap+"</th><th>"+txtPowerIP+"</th><th>"+txtPowerTransponders+"</th><th>"+txtPowerEDFAs+"</th><th>"+txtPower+"</th><th>"+txtProcess+"</th>")
    print("<th>"+txtLightpaths+"</th><th>"+txtReusedLightpaths+"</th><th>"+txtPercentReusedLightpaths+"</th><th>"+txtAverageLightpathReuses+"</th><th>"+txtwUaverage+"</th><th>"+txtfUaverage+"</th>")
    print("<th>"+limitations+"</th>")
    print("<th>"+str(maxFibersPerLink)+"</th>")
    print("<th>"+str(maxWavelengthsPerFiber)+"</th>")
    print("<th>"+str(maxGbpsPerWavelength)+"</th>")
    print("<th>"+str(LatRouterPort)+"</th>")
    print("<th>"+str(LatTransponder)+"</th>")
    #print("<th>"+str(trafficPercentOfQueueHP)+"</th>") not for heaviest and comparison
    #print("<th>"+str(trafficPercentOfQueueLP)+"</th>")

    print("</tr>")
    
    print("</table>")
    
    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeAny:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeNew:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for All Queues, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQAnyTypeGrm:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeAny:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeNew:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 0, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ0TypeGrm:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, All Types of routing traffic requests over the virtual topology</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeAny:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")
    
    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, routing of traffic requests over the virtual topology utilising new virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeNew:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")

    print ("<table class='tableLat0'>")
    print ("<tr><th colspan='3'>Measuring Latency per Traffic Request. Statistics for Queue 1, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links</th></tr>")
    print ("<tr><th>Average Latency of traffic requests</th><th>Minimum Latency of a traffic request</th><th>Maximum Latency of a traffic request</th></tr>")
    print ("<tr>")
    for stat in LatQ1TypeGrm:
        #print(f"<th>{stat:.3f}</th>" if stat != None   else   "<th>Empty</th>")
        if stat == None:
            print("<th>Empty</th>")
        elif type(stat) is str:
            print(f"<th>{stat:s}</th>")
        else:
            print(f"<th>{stat:.3f}</th>")
    print("</tr></table>")    
    
    print("</body></html>")
#EOP

#close DB connection
if dbConnection:
    dbConnection.close()

#logging 
#SOP
if (GlobalSOP==True) :
    #if dbConnection:
        #dbConnection.close()
    sys.stdout.close()
    sys.stdout=stdoutOriginal
#EOP

if (sys.argv[4] == "detailreport") and (sys.argv[7]=="pdfout"):

    '''
    print()
    print (graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html")
    print()
    print(graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".pdf")
    print()
    '''

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
errlog.close()

'''
    #pip install html2image
    #from html2image import Html2Image
    #hti = Html2Image(size=(900, 300))  # Set the desired image size

    #pip install imgkit
    import imgkit

    inHTML = graphsPath+"\\"+"PhysicalTopology.html"
    #outPDF = graphsPath+"\\"+"PhysicalTopology.pdf"
    outPNG = graphsPath+"\\"+"PhysicalTopology.png"
    #pdfkit.from_file(inHTML, outPDF, verbose=False, configuration=config, options=options)
    imgkit.from_file(inHTML, outPNG, configuration=config, options=options)

    inHTML = graphsPath+"\\"+"VirtualTopology.html"
    #outPDF = graphsPath+"\\"+"VirtualTopology.pdf"
    outPNG = graphsPath+"\\"+"VirtualTopology.png"
    #pdfkit.from_file(inHTML, outPDF, verbose=False, configuration=config, options=options)
    #hti.screenshot(html_file=inHTML, save_as='test.png')
    imgkit.from_file(inHTML, outPNG, configuration=config, options=options)

    inHTML = graphsPath+"\\"+"RoutingVirtualLinksOverPhysicalTopology.html"
    #outPDF = graphsPath+"\\"+"RoutingVirtualLinksOverPhysicalTopology.pdf"
    outPNG = graphsPath+"\\"+"RoutingVirtualLinksOverPhysicalTopology.png"
    #pdfkit.from_file(inHTML, outPDF, verbose=False, configuration=config, options=options)
    imgkit.from_file(inHTML, outPNG, configuration=config, options=options)
    '''
