# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 2021, 2022, 2023, 2024

# usage: python <program name> <network> <X index> <experiment name for csv file>
# command line parameters example
# PS C:\STDMB> python               codeMix.py       N4L5_GRNetSubnet.txt      0         testexperiment                 detailreport      gensave                            lamda.txt                     pdfout                        1                  keepreport                         HomePC                 SimLight                                                      Uniform        Q0_75_Q1_25
# <prompt>     <python interpreter> <program name>   <network>                 <X index> <experiment name for csv file> <global printout> <save lamda matrix to text file>   <filename for lamda matrix>   <save web page to pdf or not> <number of Queues> <keep or not detailreport, if any> <name of the computer> <program folder under the root (Win) or home (Lin) directory> <distribution> <scheduling strategy>
#                                                                                                                       basicreport       load                                                             nopdf                         2                  removepreport                                                                                                           Poisson        Q0nextQ1    
#                                                                                                                       <no printout>     <load lamda matrix from text file>                                                                                                                                                                                                                       Q1nextQ0
#                                   argv[0]          argv[1]                   argv[2]   argv[3]                        argv[4]           argv[5]                            argv[6]                       argv[7]                       argv[8]            argv[9]                            argv[10]               argv[11]                                                      argv[12]       argv[13]
# Configuration file sections                        [Nets_start]...[Nets_end] [X]       [Name]                         [Printout]        [Lamda]                            [LamdaTextFile]               [PDFout]                      [Queues]           [KeepEveryNthReport]               [ComputerName]         [ProgramFolder]                                               [Distribution] [Strategy]
#
# PS C:\SimLight> python .\codeEnhMultihopBypassRWAsimTime.py N4L5_GRNetSubnet.txt 5 testexperiment Y gensave TReqsWqueues.txt pdfout
# PS C:\SimLight> python .\codeEnhMultihopBypassRWAsimTime.py N4L5_GRNetSubnet.txt 5 testexperiment Y gensave TReqsWqueues.txt nopdf
#
# dependencies

# to update python packages to the latest version
# pip install pip-review
# pip-review --local --auto

# install...
# pip install numpy   # NumPy library used for calculations
# pip install networkx
# pip install pyvis   # PyVis used for visualisations

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
from datetime import datetime
from codeGusLibQueues import *
from random import randrange
import platform

#stop seeing np.float64
numpy.set_printoptions(legacy='1.25')

#set the name of the experment
if ( sys.argv[3] != ""):
    experimentName = sys.argv[3]
else:
    experimentName = "Default Experiment"

#create an error log
errlog = open(experimentName+"_Errors.txt","w")
#errlog.write(txtLine)
#errlog.close()
sys.stderr = errlog

#set the name of the algorithm
if sys.argv[8] == "1":
    Algorithm = "not applicable"
elif sys.argv[8] == "2":
    Algorithm = "MixQ0directQ1multihop"
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

'''
for use with...
#SOP
if (GlobalSOP==True) :
    ...
'''

start_processtime = time.process_time_ns()

netName, N, L, Nm, Dist = readData(sys.argv[1])

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
    QueueNames = ["Video", "Best Effort"]
elif sys.argv[8] == "2mix":
    QueueNames = ["Video", "Best Effort"]
elif sys.argv[8] == "2seq":
    QueueNames = ["Video", "Best Effort"]

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
original_X = [20, 40, 60, 80, 100, 120, 160, 320, 640, 960, 1280]
for Xitem in original_X:
    X.append(int(Xitem / lenQs))

#other definitions
#X =  [10, 20, 30, 40, 50, 60]     # since I am using two queues traffic demand range parameter/multiplier is split to half #X for two queues
#X = [20, 40, 60, 80, 100, 120]   # traffic demand range parameter/multiplier                                              #X for one queue
xiName = X[xi]

#Energy Contribution
Er = 1000.0 # energy consumption of an IP Router's port in Watts
Et = 73.0 # energy consumption of a WDM Transponder in Watts
Ee = 8.0 # energy consumption of an Erbium Doped Fiber Amplifier (EDFA) in Watts. 
EDFAdist = 80.0 #An EDFA is deployed every 80km. Link route: EDFA at node, [EDFA at 80km, ...]
S = EDFAdist # span distance between two neighbouring inline EDFAs
maxIProuterPorts = 32 #for Shen-Tucker test network (a) only 

#from the shen-tucker paper 
maxFibersPerLink = -1       #no limit on the total number of fibers on each physical link
maxWavelengthsPerFiber = 16 #max 16 wavelengths are multiplexed in each fiber
maxGbpsPerWavelength = 40.0   #max wavelength capacity is 40 Gbps
B = maxGbpsPerWavelength   #max wavelength capacity
maxFiberCapacity = maxWavelengthsPerFiber * maxGbpsPerWavelength
maxLinkCapacity = maxFibersPerLink * maxWavelengthsPerFiber * maxGbpsPerWavelength

SetGlobalLimits(maxFibersPerLink,maxWavelengthsPerFiber,maxGbpsPerWavelength,B,maxFiberCapacity,maxLinkCapacity)

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
LatencyTimeUnit4csv = 'micro'+"sec"

LatRouterPort = 30 # microsecond
LatTransponder = 100 # microsecond
LatEDFA = 100 / 1000.0 # nanosecond
LatFiberKilometer = 5 # microsecond

#main program's execution starts here #################################################################################################################

Ncolours = setNodeColours(N) # use function for consistent graph (network) node colours throughout the execution

alg = Algorithm.replace(' ', '_')

stdoutOriginal, sys.stdout, graphsPath = Log2path(appDir, "Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi]))

#SOP
if (GlobalSOP==True) :
    sys.stdout.reconfigure(encoding='utf-8')
    htmlhead("Mix (Direct &amp; Multihop) bypass", lenQs)

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
        print ("<tr><td>Node", i, "is", N[i],"</td></tr>")
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
    print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a Poisson distribution,")
    print (" which is centered at an identical average.") #"That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, the actual demand between a node pair is generated by a random function and values distributed following the Poisson process.")
    print ("</em></th></tr>")
#EOP

#SOP
#if (GlobalSOP==True) :
dbConnection = createSQLiteDB(graphsPath)
saveQueues2sqlite(dbConnection, QueueNames)
savePhysicalLinks2sqlite(dbConnection, L, Dist, EDFAdist, LatEDFA, LatFiberKilometer, graphsPath)
saveNodes2sqlite(dbConnection, N)
#EOP

if sys.argv[5] == "gensave":
    lamdatextfile = open(sys.argv[6],"w") # since in the generateTrafficRequests() function the lamdatextfile is appended ("a"), I recreate it empty ("w") to avoid keepeing previous data.
    lamdatextfile.close()

#nextReqID = 1
TReqsForQueue = []
for i in range(lenQs):
    #queueBestEffort, nextReqID = generateTrafficRequests(dbConnection, N, graphsPath, X, xi, "Queue Video", nextReqID)
    #queueBestEffort, nextReqID = generateTrafficRequests(dbConnection, N, graphsPath, X, xi, "Queue BestEffort", nextReqID)
    
    #tempQ, nextReqID = generateTrafficRequests(dbConnection, N, graphsPath, X, xi, QueueNames[i], i, nextReqID) # i is the queue number (queueID), nextReqID is the request number (reqID)
    #tempQ = generateTrafficRequests(dbConnection, N, graphsPath, X, xi, QueueNames[i], i) # i is the queue number (queueID)
    tempQ = generateTrafficRequests(dbConnection, N, graphsPath, X, xi, QueueNames[i], i, sys.argv[12]) # i is the queue number (queueID), sys.argv[12] is the distribution name Uniform/Poisson
    
    TReqsForQueue.append(tempQ) # krataei ta traffic reqquests gia kathe queue

#print("<li>Queue",QueueNames[0])
#print("<li>QueItem",TReqsForQueue[0])

#print("<li>Queue",QueueNames[1])
#print("<li>QueItem",TReqsForQueue[1])

#print ("<p>Queue Video<br>",queueVideo)
#print ("<p>Queue Best Effort<br>",queueBestEffort)
#print ("<p></p>")

if lenQs==1:
    aggregatedTReqs = TReqsForQueue[0]
elif lenQs==2:
    #aggregate the traffic volume of the two queues
    aggregatedTReqs= AggregateRequestsTraffic(N, TReqsForQueue[0], TReqsForQueue[1])
else:
    print("<div>Error: Program designed for 1 or 2 queues so far.")
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

# Count total lightpaths
TotalLightpaths = [0] #how many lightpaths

# Count how many of the lightpaths were reused, 0 or 1 per lightpath
ReUsedLightpaths = [] #how many times lightspaths were reused - if a lightpath is reused more than once it counts as one - ReUsedLightpaths <= number of Lightpaths

# Count the reuses of the lightpaths, 0, 1, 2, or more per lightpath
LightpathReuses = [0] #how many reuses of lightpaths - if a lightpath is reused more than once I count all the reuse times - LightpathReuses maybe <, =, or > number of Lightpaths

# new, serving two traffic request queues
if lenQs==2:
    startingstep = 1
    s="Virtual topology graph after processing request "
    VTgraph = graph_new(s, True)
    
    #route Q0 using direct bypass
    Q=0
    startingstep = routeAllRequestsOfOneQueueOverVirtualTopologyDirectBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)

    #route Q1 using multihop bypass
    Q=1
    startingstep = routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass(startingstep, VTgraph, N, TReqsForQueue[Q], Q, vT,vTL,vTfreeCap,maxGbpsPerWavelength,VTfinal, ReqRouteInfo, graphsPath, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VirtLinkIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals)
    
    schedulingstrategy = "Q0DirectQ1Multihop"
else:
    print("<div>Mix bypass runs only for two queues!</div>")
    exit(1)

#SOP
if (GlobalSOP==True) :
    print ("<h3 style='text-align:center'>Strategy utilised for the scheduling of the queue(s):", schedulingstrategy,"</h3>")
    
    print ("<table class='table1c'>")
    #print ("<tr><th>Free capacities for the Virtual Links of the Virtual Topology {(s, d): [<em>free capacity</em>], ...} (vTfreeCap) =",vTfreeCap,"</th></tr>")
    #2DO not use vTfreeCap
    print ("<tr><th>The Virtual Topology {node: [<em>list of neighbour nodes</em>], ...} (vT)") # =",vT,"</th></tr>")
    printVTdictionaryAsTable(vT)
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

VirtualLinks = []

#print ("<div>VTfinal=",VTfinal,"</div>")

# edw allazw to vtfinal gia na exw sosta athroismata gia perissoteres apo 1 queues

newVTFinal = {}

for VLkey in VirtualLinkTotals:
    #print("<li>VLKey",VLkey)
    s = VLkey[0]
    d = VLkey[1]
    num = VLkey[2]
    caputil = VirtualLinkTotals[VLkey][0]
    if caputil > maxGbpsPerWavelength:
        error("Virtual Link has greater capacity than the allowed limit",99)
    #print("<li>capacity utilised",caputil)
    VTFinalKey = (s,d)
    #print("<li>new VTFinal",newVTFinal)
    if VTFinalKey in newVTFinal:
        vtFinalvalue = newVTFinal[VTFinalKey]
        vtFinalvalue.append(caputil)
    else:
        vtFinalvalue = [caputil]
    newVTFinal.update({(s,d,num):vtFinalvalue})

#print ("<div>New VTfinal=",VTfinal,"</div>")

#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c'>")
    print ("<tr><th colspan=5>The virtual topology for routing over physical topology</th></tr>")
    print ("<tr><th>source&rarr;destination </th><th>source (s)</th><th>destination (d)</th><th>number (n)</th><th>capacity</th>")
#EOP

VTfinal = newVTFinal

for link in VTfinal:
    capacities = VTfinal.get(link)
    lines = len(capacities)

    #SOP
    if (GlobalSOP==True) :
        print ("<tr><td rowspan=",lines,">",N[link[0]],"&rarr;",N[link[1]],"</td>")
        print ("<td rowspan=",lines,">",link[0],"</td>")
        print ("<td rowspan=",lines,">",link[1],"</td>")
        print ("<td rowspan=",lines,">",link[2],"</td>")
    #EOP

    for c in capacities:
        VirtualLinks.append([N[link[0]], N[link[1]], link[2], c])

        #SOP
        if (GlobalSOP==True) :
            print ("<td>",c,"</td>")
            print("</tr>")
        #EOP

#SOP
if (GlobalSOP==True) :
    print ("</table>")
#EOP

VT = VirtualLinks

#print ("<div>Virtual Links for routing over physical topology<p>")
#print (VT)

# used for power calculation
for vl in VT:
    t=(nodenumber(N,vl[0]),nodenumber(N,vl[1]))
    accumulatePowerParameters(Cij, t, 1)

#SOP
if (GlobalSOP==True) :
    printCij(Cij, N)
#EOP

for k in Cij:    
    val = Cij.get(k)
    accumulatePowerParameters(SigmaCij, k[0], val)

#SOP
if (GlobalSOP==True) :
    printSigmaCij(SigmaCij, N)
#EOP

'''
#visualisation of virtual topology is now done at the end of routeAllTrafficRequestQueuesOverVirtualTopologyMultihopBypass()
#SOP
if (GlobalSOP==True) :
    visualiseVirtualTopology_Build_VT_from_scratch(VirtualLinks, N, graphsPath, Ncolours, maxGbpsPerWavelength, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output
#EOP
'''

RoutingOfVirtualLinksOverWavelengths = {}

phyLinks, RoutingOfVirtualLinksOverWavelengths = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder, dbConnection)
#old phyLinks = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VT,  N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, dbConnection)
#older #phyLinks = routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VirtualLinks, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist)

#SOP
if (GlobalSOP==True) :    
    visualiseRoutingOfVirtualLinksOverPhysicalTopology(phyLinks, N, graphsPath, Ncolours, (sys.argv[7]!="pdfout")) # if pdfout then it will not include graph in HTML and PDF, else it will include graph in HTML since no PDF output

    printRoutingOfVirtualLinksOverWavelengthsAsTable(RoutingOfVirtualLinksOverWavelengths)
#EOP

# used for power calculation
#SOP
if (GlobalSOP==True) :
    print ("<table class='data'>")
    print ("<tr><th colspan=9>Statistics about Physical Links</th></tr>")
    print ("<tr><th>Physical Link</th><th>Wavelengths w<sub>mn</sub></th>")
    print ("<th>Fibers f<sub>mn</sub></th><th>Distance L<sub>mn</sub> (km)</th>")
    print ("<th>Capacity requested (Gbps)</th><th>Free capacity (Gbps)</th>")
    print ("<th>Reserved capacity for wavelengths (Gbps)</th>")
    print ("<th>Wavelegth Utilisation (%)<br><span style='font-size:0.6em;'>Capacity requested / Capacity of the wavelengths</span></th>")
    print ("<th>Fiber Link Utilisation (%)<br><span style='font-size:0.6em;'>Capacity requested / Capacity of the fibers</span></th></tr>")
#EOP

#Statistics about Physical Links

wUtotal = 0.0 # wavelength utilisation total
fUtotal = 0.0 # fiber utilisation total

keys = list(Wmn.keys())
keys.sort()
for key in keys:
    wl = Wmn.get(key)
    #fibers = int((wl/maxWavelengthsPerFiber)+1)
    fibers=numpy.ceil(wl/maxWavelengthsPerFiber) 
    CU = roundatdecimals(CUmn.get(key),3)                                 # CU : capacity utilised
    CR = wl * maxGbpsPerWavelength                                        # CR : capacity required
    CF = roundatdecimals((CR - CU), 3)                                    # CF : capacity free
    wU = roundatdecimals((CU / CR * 100.0), 1)                            # wU : wavelength utilisation percentage
    fU = roundatdecimals((CU / (fibers * maxFiberCapacity) * 100.0), 1)   # fU : fiber link utilisation percentage

    wUtotal += wU
    fUtotal += fU

    updateTotals(fmn, key, fibers)
    distance = Lmn.get(key)

    #SOP
    if (GlobalSOP==True) :
        print("<tr><td>",N[L[key][0]]+"-"+N[L[key][1]],"</td><td>",wl,"</td><td>",fibers,"</td><td>",distance,"</td><td>",CU,"</td><td>",CF,"</td><td>",CR,"</td><td>",wU,"</td><td>",fU,"</td></tr>")
    #EOP

wUaverage = wUtotal / len(keys)
fUaverage = fUtotal / len(keys)

wUaverage = roundatdecimals(wUaverage,1)
fUaverage = roundatdecimals(fUaverage,1)

#SOP
if (GlobalSOP==True) :
    print("</table>")
#EOP

##########used for power calculation
##########key = linknumber(L, sp[0],sp[1])
##########numOfEDFAs = int ( ( dist[key] / distEDFA - 1.0 ) + 2.0 )

for physicallink in L:
    key = linknumber(L,physicallink[0],physicallink[1])
    LmnValue = Lmn.get(key)
    value = numpy.ceil(LmnValue / S - 1.0) + 2
    accumulatePowerParameters(Amn, key, value)

#SOP
if (GlobalSOP==True) :
    printAmn(Amn, N, L)
#EOP

# Evaluate Power (start) >>>

ValueOfPower = 0.0

#SOP
if (GlobalSOP==True) :
    print ("<table class='tablePow'>")
    print ("<tr><th colspan=2>Energy consumption evaluation in the IP layer</th></tr>")
    print ("<tr><th>Node</th><th>Power consumption ",mathPowerFormulaIP()," in Watts</th></tr>")
#EOP

PowerIP = 0.0
keys = list(SigmaCij.keys())
keys.sort()
for k in keys:
    valSigmaCij = SigmaCij.get(k) * 1.0
    valDi = Di.get(k)
    ValueOfPower = Er * ( valDi + valSigmaCij )
    PowerIP += ValueOfPower

    #SOP
    if (GlobalSOP==True) :
        print("<tr><td>",N[k],"</td><td>",Er, "* (",valDi,"+",valSigmaCij,") =",ValueOfPower,"</td></tr>")
    #EOP

#SOP
if (GlobalSOP==True) :
    print("<tr><th colspan=2>Total:",PowerIP,"Watts</th></tr>")
    print("</table>")

    print ("<table class='tablePow'>")
    print ("<tr><th colspan=2>Energy consumption evaluation in the optical layer (Transponders)</th></tr>")
    print ("<tr><th>Node</th><th>Power consumption ",mathPowerFormulaTransponders(),"in Watts</th></tr>")
#EOP

PowerTransponders = 0.0
for i in range(len(L)):
    key = linknumber(L, L[i][0],L[i][1])
    valWmn = Wmn.get(key)
    ValueOfPower = Et * valWmn
    PowerTransponders += ValueOfPower

    #SOP
    if (GlobalSOP==True) :
        print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>",Et, "*",valWmn,"=",ValueOfPower,"</td></tr>")
    #EOP

#SOP
if (GlobalSOP==True) :
    print("<tr><th colspan=2>Total:",PowerTransponders,"Watts</th></tr>")
    print("</table>")

    print ("<table class='tablePow'>")
    print ("<tr><th colspan=2>Energy consumption evaluation in the optical layer (EDFAs)</th></tr>")
    print ("<tr><th>Node</th><th>Power consumption ",mathPowerFormulaEDFA()," in Watts</th></tr>")
#EOP

PowerEDFAs = 0.0
for i in range(len(L)):
    key = linknumber(L, L[i][0],L[i][1])
    valAmn = Amn.get(key)
    valfmn = fmn.get(key)
    ValueOfPower = Ee * valAmn * valfmn
    PowerEDFAs += ValueOfPower

    #SOP
    if (GlobalSOP==True) :
        print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>",Ee, "*",valAmn,"*",valfmn,"=",ValueOfPower,"</td></tr>")
    #EOP

#SOP
if (GlobalSOP==True) :
    print("<tr><th colspan=2>Total:",PowerEDFAs,"Watts</th></tr>")
    print("</table>")
#EOP

PowerTotal = PowerIP + PowerTransponders + PowerEDFAs
PowerTotal = roundatdecimals(PowerTotal/1000.0,3)

PowerIP = roundatdecimals(PowerIP/1000.0,3)
PowerTransponders = roundatdecimals(PowerTransponders/1000.0,3)
PowerEDFAs = roundatdecimals(PowerEDFAs/1000.0,3)

#SOP
if (GlobalSOP==True) :
    print ("<table class='tablePow'>")
    print ("<tr><th>Evaluation of total energy consumption in the network</th></tr>")
    print ("<tr><td>",mathPowerFormula(),"</td></tr>")
    print ("<tr><th>Total power consumption",PowerTotal,"kWatts</th></tr>")
    print ("</table>")
#EOP

# >>> Evaluate Power (end)

# >>> Evaluate Latency (the wrong way, cummulative)

'''
LatencyTotal = EvaluateLatencyAggregated(LatRouterPort,LatencyTimeUnit,LatTransponder,LatEDFA,LatFiberKilometer,SigmaCij,Di,N,L,Wmn,Amn,fmn,Dist)

#print("<ul>")
#print("<li>Di",Di)
Di_Q0 = getDiPerQueueFromSQLite(dbConnection, 0, maxGbpsPerWavelength)
if lenQs==2:
    Di_Q1 = getDiPerQueueFromSQLite(dbConnection, 1, maxGbpsPerWavelength)

#print("<li>Cij",SigmaCij)
#Cij_Q0 = getCijPerQueueFromSQLite(dbConnection, 0)
#Cij_Q1 = getCijPerQueueFromSQLite(dbConnection, 1)

#print("<li>SigmaCij",SigmaCij)
SigmaCij_Q0 = getSigmaCijPerQueueFromSQLite(dbConnection, 0)
if lenQs==2:
    SigmaCij_Q1 = getSigmaCijPerQueueFromSQLite(dbConnection, 1)

#print("<li>Wmn",Wmn)
Wmn_Q0 = getWmnPerQueueFromSQLite(dbConnection, 0, L)
if lenQs==2:
    Wmn_Q1 = getWmnPerQueueFromSQLite(dbConnection, 1, L)

LatFibLen_Q0 = getLatFibLenPerQueueFromSQLite(dbConnection, 0)
#print("</ul>")

fmn_Q0 = getfmnPerQueueFromSQLite(dbConnection, 0, L, maxWavelengthsPerFiber)
if lenQs==2:
    fmn_Q1 = getfmnPerQueueFromSQLite(dbConnection, 1, L, maxWavelengthsPerFiber)

LatencyTotal_Q0 = EvaluateLatencyPerQueue(0, LatRouterPort,LatencyTimeUnit,LatTransponder,LatEDFA,LatFiberKilometer,SigmaCij_Q0,Di_Q0,N,L,Wmn_Q0,Amn,fmn_Q0,Dist)
if lenQs==2:
    LatencyTotal_Q1 = EvaluateLatencyPerQueue(1, LatRouterPort,LatencyTimeUnit,LatTransponder,LatEDFA,LatFiberKilometer,SigmaCij_Q1,Di_Q1,N,L,Wmn_Q1,Amn,fmn_Q1,Dist)
'''

#SOP
if (GlobalSOP==True) :
    
    print ("<table class='tableLat'>")
    print ("<tr><td>LatRouterPort:",LatRouterPort," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatTransponder:",LatTransponder," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatEDFA:",LatEDFA," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatFiberKilometer:",LatFiberKilometer," ",LatencyTimeUnit,"</td></tr>")
    print ("</table>")

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
#EOP

#now = datetime.now()
#timeStamp = "y"+str(now.year)+"_m"+str(now.month)+"_d"+str(now.day)+"_h"+str(now.hour)+"_m"+str(now.minute)+"_s"+str(now.second)+"_u"+str(now.microsecond)

if ( sys.argv[3] != ""):
    experimentName = sys.argv[3]
else:
    experimentName = "Default Experiment"

# I need the CSV in every case (detailreport OR basicreport)
fout = open(experimentName+".csv","a")

# time calculation end
# print("--- %s seconds ---" % (time.time() - start_time))
end_processtime = time.process_time_ns()
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
txtX = str(X[xi]) if lenQs==1 else str(X[xi]*lenQs)
txtCap = str(TotalCapacity)
#txtCap = txtCap.replace(".", ",") # replace decimal point . with decimal point , for Greek regional settings
txtPowerIP = str(PowerIP)
txtPowerTransponders = str(PowerTransponders)
txtPowerEDFAs = str(PowerEDFAs)
txtPower = str(PowerTotal)
#txtPower = txtPower.replace(".", ",") # replace decimal point . with decimal point , for Greek regional settings
txtProcess = str(roundatdecimals(ProcessTime*1.0e-9, 6))
#txtProcess = txtProcess.replace(".", ",") # replace decimal point . with decimal point , for Greek regional settings
txtLightpaths = str(lightpaths)
txtReusedLightpaths = str(reused)
txtPercentReusedLightpaths = str(roundatdecimals(PercentReusedLightpaths,1))
txtAverageLightpathReuses = str(roundatdecimals(AverageLightpathReuses,3))
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
txtCaptions  =  "Timestamp;Computer Name;Program Folder;Algorithm;NumOfQueues;Scheduling Strategy;Experiment name;Network;Number of nodes;Number of links;X (Gbps);"
txtCaptions +=  "Distribution;Total capacity processed (Gbps);Power of IP routers (kWatt);Power of WDM Transponders (kWatt);"
txtCaptions +=  "Power of EDFAs (kWatt);TotalPower (kWatt);Process Time (sec);Total lightpaths;Reused Lightpaths;"
txtCaptions +=  "Percentage of reused lightpaths (Reused Lightpaths/Total Lightpaths);Average Lightpath Reuses (Lightpath Reuses / Reused Lightpaths);"
txtCaptions +=  "Average Wavelengths Utilisation (%) (capacity utilised / maximum capacity of the current number of wavelengths);"
txtCaptions +=  "Average Fiber Links Utilisation (%) (capacity utilised / maximum capacity of the current number of fibers;"

txtCaptions +=  "TR_AvgLat_AllQ_AnyTypeRoutingOverVT;TR_MinLat_AllQ_AnyTypeRoutingOverVT;TR_MaxLat_AllQ_AnyTypeRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_AllQ_NewVLRoutingOverVT;TR_MinLat_AllQ_NewVLRoutingOverVT;TR_MaxLat_AllQ_NewVLRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_AllQ_GrmOverVT;TR_MinLat_AllQ_GrmOverVT;TR_MaxLat_AllQ_GrmOverVT;"

txtCaptions +=  "TR_AvgLat_Q0_AnyTypeRoutingOverVT;TR_MinLat_Q0_AnyTypeRoutingOverVT;TR_MaxLat_Q0_AnyTypeRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_Q0_NewVLRoutingOverVT;TR_MinLat_Q0_NewVLRoutingOverVT;TR_MaxLat_Q0_NewVLRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_Q0_GrmOverVT;TR_MinLat_Q0_GrmOverVT;TR_MaxLat_Q0_GrmOverVT;"

txtCaptions +=  "TR_AvgLat_Q1_AnyTypeRoutingOverVT;TR_MinLat_Q1_AnyTypeRoutingOverVT;TR_MaxLat_Q1_AnyTypeRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_Q1_NewVLRoutingOverVT;TR_MinLat_Q1_NewVLRoutingOverVT;TR_MaxLat_Q1_NewVLRoutingOverVT;"
txtCaptions +=  "TR_AvgLat_Q1_GrmOverVT;TR_MinLat_Q1_GrmOverVT;TR_MaxLat_Q1_GrmOverVT\n"

fout.write(txtCaptions)

#accumulating latency is not correct way to calculate it, hence it is not included in the CSV by replacing the values with dashes
txtLatencyTotal    = "-"
txtLatencyTotal_Q0 = "-"
txtLatencyTotal_Q1 = "-"

ts = datetime.now()

timeStamp = f"y{ts.year:04d}_m{ts.month:02d}_d{ts.day:02d}_h{ts.hour:02d}_m{ts.minute:02d}_s{ts.second:02d}_u{ts.microsecond:06d}"

txtLine  = timeStamp+";"+computername+";"+programfolder+";"+Algorithm+";"+str(lenQs)+";"+schedulingstrategy+";"+experimentName+";"+netName+";"+txtN+";"+txtL+";"+txtX+";"
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

txtLine += "\n"

txtLine = txtLine.replace(".", ",") #for Greek regional settings (comma is the decimals' separator)

fout.write(txtLine)
fout.close()

#SOP
if (GlobalSOP==True) :
    print ("<table class='table1c' id='results'>")
    
    print ("<tr><th>Algorithm</th><th>Experiment name</th><th>Network</th><th>Number of nodes</th><th>Number of links</th><th>X (Gbps)</th><th>Total capacity processed (Gbps)</th><th>Power of IP routers (kWatt)</th><th>Power of WDM Transponders (kWatt)</th><th>Power of EDFAs (kWatt)</th><th>TotalPower (kWatt)</th><th>Process Time (sec)</th>")
    print ("<th>Total lightpaths</th><th>Reused Lightpaths</th><th>Percent of Reused Lightpaths (%)</th><th>Average Lightpaths Reuses</th><th>Average wavelengths utilisation (%)</th><th>Average fiber links utilisation (%)</th></tr>")

    print ("<tr><th>"+Algorithm+"</th><th>"+experimentName+"</th><th>"+netName+"</th><th>"+txtN+"</th><th>"+txtL+"</th><th>"+txtX+"</th><th>"+txtCap+"</th><th>"+txtPowerIP+"</th><th>"+txtPowerTransponders+"</th><th>"+txtPowerEDFAs+"</th><th>"+txtPower+"</th><th>"+txtProcess+"</th>")
    print("<th>"+txtLightpaths+"</th><th>"+txtReusedLightpaths+"</th><th>"+txtPercentReusedLightpaths+"</th><th>"+txtAverageLightpathReuses+"</th><th>"+txtwUaverage+"</th><th>"+txtfUaverage+"</th></tr>")
    
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
        'encoding': 'UTF-8',
        'enable-local-file-access': None, #To be able to access CSS
        'orientation': 'Landscape',
        'page-size': 'A3',
        'header-right':'[page]/[toPage]'
    }
    #pdfkit.from_url(inHTML, outPDF, verbose=True, configuration=config, options=options)

    if platform.system() == 'Windows':
        inHTML = graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html"
        outPDF = graphsPath+"\\"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".pdf"
    elif platform.system() == 'Linux':
        inHTML = graphsPath+"/"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".html"
        outPDF = graphsPath+"/"+"Alg_"+alg+"_Net-"+netName+"_X-"+str(X[xi])+".pdf"

    pdfkit.from_file(inHTML, outPDF, verbose=False, configuration=config, options=options)

#if sys.argv[4] == "detailreport" and sys.argv[9] == "removereport":
if sys.argv[9] == "removereport":
    removeTree(graphsPath)

#close the error log
#errlog = open(experimentName+"_Errors.csv","w")
#errlog.write(txtLine)
errlog.close()
