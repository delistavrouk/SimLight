# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 2021, 2022, 2023, 2024
# Library of subroutines for Shen & Tucker 2009 heuristic algorithms

protocol = "File:///"
#protocol = "http://"

# SOP: Start of printout
# EOP: End of printout

#2DO : elaboration needed
#Done : elaboration completed
#>>> : elaboration priority
#Novelties

GlobalPrintOutEnabled = False

maxFibersPerLink       = 0
maxWavelengthsPerFiber = 0
maxGbpsPerWavelength   = 0
B                      = 0
maxFiberCapacity       = 0
maxLinkCapacity        = 0

GlobalVirtLinkID = 0

GlobalStringOutcomes = ""

'''
defined in codeDirect_x_.py and codeMultihop_x_.py for use with...
#SOP
if (GlobalPrintOutEnabled==True) :
    ...
'''

import numpy   # NumPy library used for calculations
import random
import sys
import os
import re
import threading
import time
import operator
import sqlite3
from datetime import datetime
import platform
from pyvis.network import Network

class ShPthDijkstra:
    def __init__(self, nodes, net):
        self.nodes = nodes 
        self.net = net

    def find_path(self, src, dst):
        notvisit = {}
        for n in self.nodes:
            notvisit[n] = float("inf")
        notvisit[src] = 0  
        par = {}  
        visit = {}  
        while notvisit:
            min_node = min(notvisit, key=notvisit.get) 
            for neighbor, _ in self.graph.get(min_node, {}).items():
                if neighbor in visit:
                    continue
                dist = notvisit[min_node] + self.graph[min_node].get(neighbor, float("inf"))
                if dist < notvisit[neighbor]:
                    notvisit[neighbor] = dist
                    par[neighbor] = min_node
            visit[min_node] = notvisit[min_node]
            notvisit.pop(min_node)
            if min_node == dst:
                break
        return par, visit

    @staticmethod
    def create_path(par, src, dst):
        path = [dst]
        while True:
            key = par[path[0]]
            path.insert(0, key)
            if key == src:
                break
        return path

def SetGlobalPrintout(value):
    global GlobalPrintOutEnabled
    GlobalPrintOutEnabled = value
    
def SetGlobalLimits(maxFpL,maxWpF,maxGpW,b,maxFiC,maxLiC):
    global maxFibersPerLink
    global maxWavelengthsPerFiber
    global maxGbpsPerWavelength
    global B
    global maxGbpsPerWavelength
    global maxFiberCapacity
    global maxLinkCapacity

    maxFibersPerLink       = maxFpL
    maxWavelengthsPerFiber = maxWpF
    maxGbpsPerWavelength   = maxGpW
    B                      = b
    maxFiberCapacity       = maxFiC
    maxLinkCapacity        = maxLiC

def find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,src_str,dst_str):
    global GlobalPrintOutEnabled

    input_nodes = Nt
    input_net = NmC
    src = src_str
    dst = dst_str
    shpth = ShPthDijkstra(input_nodes, input_net)
    p, v = shpth.find_path(src, dst)
    se = shpth.create_path(p, src, dst)
    
    pth=[]
    for i in range(len(se)):
        pth.append(nodenumber(N,se[i]))
    
    return pth

def randomcolor(x):
    # generate a random color to use for the network graph visualisation
    random.seed(x)
    R = random.randint(0,255)
    G = random.randint(0,255)
    B = random.randint(0,255)

    C = "#"+hex(R).split('x')[-1]+hex(G).split('x')[-1]+hex(B).split('x')[-1]
    return C

def setNodeColours(nodes):
    # set the colours of the network nodes
    out = []
    for node in nodes:
        r = randomcolor(node)
        if (out != []):
            while (r in out):
                r = randomcolor(node)
        out.append(r)
    return out

def graph_new(name, directedgraph):
    # create a new graph instance
    #net = Network(directed=True, heading=name)
    #net = Network()
    net = Network(directed=directedgraph)
    #net.repulsion(node_distance=200, spring_length=400)
    #net.toggle_physics(True) # true elastic network graph - false static
    net.toggle_physics(True)
    net.repulsion(node_distance=200, central_gravity=0.1, spring_length=400, spring_strength=0.1, damping=0.1)
    return net

def graph_add_node(gr,id,l,colours):
    #add a node to a graph
    gr.add_node(id,title=str(id),label=l,color=colours[id])
            
def graph_add_edge(gr,apo,pros,t,l):
    #add an adge between two nodes of a graph
    gr.add_edge(apo, pros, weight=0.90, color="#000000", title=t, label=l, arrowStrikethrough=False)

def graph_show(gr,path):
    #show the graph
    s='graph_'+ gr.heading +'.html'
    filename = os.path.join(path, s)
    #gr.show_buttons()
    gr.show(s)
    
def graph_save(gr, path, name):
    filename = name
    #gr.save_graph(filename)
    newfilename = os.path.join(path, filename)
    gr.save_graph(newfilename)
    #shutil.copyfile(filename, newfilename)

def graph_update_edge(gr,que,req,s,d,free,max,reqcap): #Done updated edge after grooming with correct que and req numbers
    edges = gr.get_edges()
    #print ("List of graph edges")
    for edg in edges:
        #print(edg)
        #token = str(s)+"&rarr;"+str(d)+",cp:"+str(roundatdecimals(max-free,3))+",fr:"+str(roundatdecimals(free,3))+","
        cap = max-free
        if (edg['from'] == s) and (edg['to'] == d):
            token = "cp:"+str(roundatdecimals(cap,3))+",fr:"+str(roundatdecimals(free,3))
            #print(token)
            #"title": "rq:6,Node0-\u003eNode5,cp:11.497,fr:28.503",
            if (token in edg['title']): #search for the 'title' key to change the edge labels
                #print ("found!!!")
                substr=edg['title']
                for i in range(len(substr)): #search for the "rq:6,"
                    if (substr[i] == ","):
                        break
                #print ("position of first comma is",i)
                #$$$
                for j in range(i+1, len(substr)): #search for the "Node0-\u003eNode5,"
                    if (substr[j] == ","):
                        break
                #$$$ print ("position of first comma is",j)
                fpart = substr[0:i]
                linkname = substr[i+1:j]
                #print ("first part is",fpart)
                #fpart = "Grm:"+fpart + "+" + str(rq) + ","
                #fpart = "+Grm("+fpart + "que:" + str(que)+"req:"+str(req) + "," + linkname + ","
                fpart = "Grm:"+fpart + "+" +"que:"+str(que)+"req:"+str(req) + "," + linkname + ","
                free = free + reqcap
                cap = cap - reqcap
                token = fpart +"cp:"+str(roundatdecimals(cap,3))+",fr:"+str(roundatdecimals(free,3))
                d = {'title':token}
                edg.update(d)
                token = "Grm,fr:"+str(roundatdecimals(free,3))
                d = {'label':token}
                edg.update(d)
            #$$$
            #"label": "fr:25.446",
            #"color": "#000000",
            token = "fr:0.0"
            if (token not in edg['label']): #search for the 'label' key that is not free 0.0, so it has some free capacity    
                token = "#000000"
                if (token in edg['color']): #search for the 'color' key to change the edge color
                    #print ("found!!!")
                    substr=edg['color']
                    #print ("substr",substr)
                    substr="#00bb00"                
                    d = {'color':substr}
                    edg.update(d)

def visualiseRoutingOfVirtualLinksOverPhysicalTopology(pL, N, grpath, colours, IncludeNetworkGraphInHTML):
    
    s="Routing of Virtual Links over the Physical Topology"
    gr = graph_new(s, True)
    graph_filename='RoutingVirtualLinksOverPhysicalTopology.html'
    for pl in pL:
        Ni=pl[0]
        Nj=pl[1]
        cap=pl[2]
        free=pl[3]
        graph_add_node(gr,Ni,N[Ni],colours)
        graph_add_node(gr,Nj,N[Nj],colours)
        graph_add_edge(gr,Ni,Nj,str(N[Ni])+"&rarr;"+str(N[Nj])+",cp:"+str(cap)+",fr:"+str(free), "fr:"+str(free))

    graph_save(gr, grpath, graph_filename)

    if IncludeNetworkGraphInHTML == True:
        newfilename = os.path.join(grpath, graph_filename)
        
        print("<div style='margin-left:auto;margin-right:auto;'>")
        print("<h3>Routing of Virtual Links over the Physical Topology</h3>")
        #print("<h4><a href='"+protocol+newfilename+"' target='_blank'>"+newfilename+"</a></h4>")
        print("<h4><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></h4>")
        print("<br><iframe src='"+graph_filename+"' style='border:2px solid red;width:500px;height:500px;' title='"+newfilename+"'></iframe></div>")
    
def visualisePhysicalTopology(N,L,grpath,colours,costs, IncludeNetworkGraphInHTML):
    net = graph_new("Physical Topology", False)
    #net = Network()
    #net.set_edge_smooth('dynamic')
    #net.repulsion(node_distance=100, central_gravity=0.2, spring_length=200, spring_strength=0.01, damping=0.09)
    #net.repulsion(node_distance=100)
    #net.repulsion(node_distance=200, spring_length=400)
    #net.toggle_physics(True) # true elastic network graph - false static
    #net.repulsion(node_distance=300, central_gravity=0.01, spring_length=100, spring_strength=0.01)
    for i in range(len(N)):
        net.add_node(i,title=N[i],label=N[i]+" node:"+str(i),color=colours[i]) #for graphical representation
    for i in range(len(L)):
        #net.add_edge(L[i][0],L[i][1], weight=0.90, color="#000000")
        #net.add_edge(L[i][0],L[i][1], weight=0.90, color=randomcolor())
        l = linknumber(L, L[i][0],L[i][1])
        #net.add_edge(L[i][0],L[i][1], weight=0.90, color="#000000", title="Dist. "+str(costs[l]), label="Dist. "+str(costs[l]), arrowStrikethrough=False, physics=False) # without elasticity
        net.add_edge(L[i][0],L[i][1], weight=0.90, color="#000000", title="Dist. "+str(costs[l]), label="Dist. "+str(costs[l]), arrowStrikethrough=False) # with elasticity
    filename = 'PhysicalTopology.html'
    newfilename = os.path.join(grpath, filename)
    graph_save(net, grpath, filename)
    #net.save_graph(filename)
    #net.save_graph(newfilename)
    #shutil.copyfile(filename, newfilename)
    #os.remove(filename)
    #os. rename(filename, newfilename)
    if IncludeNetworkGraphInHTML == True:
        print("<div style='margin-left:auto;margin-right:auto;'>")
        print("<h3>The Physical Topology</h3>")
        #print("<h4><a href='"+protocol+newfilename+"' target='_blank'>"+newfilename+"</a></h4>")
        print("<h4><a href='"+filename+"' target='_blank'>"+filename+"</a></h4>")
        #print("<br><iframe src='"+protocol+newfilename+"' style='border:2px solid red;width:500px;height:500px;' title='"+newfilename+"'></iframe></div>")
        print("<br><iframe src='"+filename+"' style='border:2px solid red;width:500px;height:500px;' title='"+filename+"'></iframe></div>")

def visualiseVirtualTopology_Build_VT_from_scratch(VT, nodes, graph_path, Ncolours, maxGbpsPerWave, IncludeNetworkGraphInHTML) :
    #αυτη η function διαβαζει την εικονικη τοπολογια και δημιουργει από την αρχή ένα γράφο
    #καλύτερο αποτέλεσμα βγάζει το τελευταίο βήμα της σταδιακής δημιουργίας γράφων για την εικονική τοπολογία οπότε χρησιμοποιώ αυτό
    #δηλαδή απλά κάνω ένα αντίγραφο του "VT_after_StepΧ_QueΥ_ReqΖ.html" και το ονομάζω "VirtualTopology.html"

    s="The Virtual topology graph"
    gr = graph_new(s, True)
    graph_filename="VirtualTopology.html"
    for vl in VT:
        Ni=nodenumber(nodes,vl[0])
        Nj=nodenumber(nodes,vl[1])
        cap=vl[2]
        free=roundatdecimals(maxGbpsPerWave-cap,3)
        graph_add_node(gr,Ni,vl[0],Ncolours)
        graph_add_node(gr,Nj,vl[1],Ncolours)
        graph_add_edge(gr,Ni,Nj,str(Ni)+"&rarr;"+str(Nj)+",cp:"+str(cap)+",fr:"+str(free), "fr:"+str(free))

    graph_save(gr, graph_path, graph_filename)

    if IncludeNetworkGraphInHTML == True:
        newfilename = os.path.join(graph_path, graph_filename)
        #shutil.copyfile(graph_filename, newfilename)
        #os.remove(graph_filename)
        #os. rename(filename, newfilename)
        #print("<div style='margin-left:auto;margin-right:auto;'><iframe src='"+newfilename+"' style='border:2px solid red;width:500px;height:500px;' title='"+newfilename+"'></iframe>")
        #print("<br><br><a href='"+newfilename+"'>"+newfilename+"</a></div>")
        print("<div style='margin-left:auto;margin-right:auto;'>")
        print("<h3>The Virtual Topology</h3>")
        #print("<h4><a href='"+protocol+newfilename+"' target='_blank'>"+newfilename+"</a></h4>")
        print("<h4><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></h4>")
        print("<br><iframe src='"+graph_filename+"' style='border:2px solid red;width:500px;height:500px;' title='"+newfilename+"'></iframe></div>")
        #os.remove('graph_Virtual topology graph.html')

def visualiseVirtualTopology(graph_filename,IncludeNetworkGraphInHTML):
    #αυτη η function διαβαζει την εικονικη τοπολογια και δημιουργει από την αρχή ένα γράφο
    #καλύτερο αποτέλεσμα βγάζει το τελευταίο βήμα της σταδιακής δημιουργίας γράφων για την εικονική τοπολογία οπότε χρησιμοποιώ αυτό
    #δηλαδή απλά κάνω ένα αντίγραφο του "VT_after_StepΧ_QueΥ_ReqΖ.html" και το ονομάζω "VirtualTopology.html"
    
    if IncludeNetworkGraphInHTML == True:
        #newfilename = os.path.join(graph_path, graph_filename)
        #shutil.copyfile(graph_filename, newfilename)
        #os.remove(graph_filename)
        #os. rename(filename, newfilename)
        #print("<div style='margin-left:auto;margin-right:auto;'><iframe src='"+newfilename+"' style='border:2px solid red;width:500px;height:500px;' title='"+newfilename+"'></iframe>")
        #print("<br><br><a href='"+newfilename+"'>"+newfilename+"</a></div>")
        print("<div style='margin-left:auto;margin-right:auto;'>")
        print("<h3>The Virtual Topology</h3>")
        #print("<h4><a href='"+protocol+newfilename+"' target='_blank'>"+newfilename+"</a></h4>")
        #print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")

        print("<h4><a href='"+graph_filename+"' target='_blank'>"+"The final Virtual Topology"+"</a></h4>")
        print("<br><iframe src='"+graph_filename+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe></div>")
        #os.remove('graph_Virtual topology graph.html')


def linkSrcDst(link):
    # Return the source and destination of a link, given its link number
    return link[0], link[1]

def linknumber(data, m, n):
    # Return the number of a link, given its source and destination nodes
    for i in range(len(data)):
        if ( (data[i][0]==m) and (data[i][1]==n) ) or ( (data[i][0]==n) and (data[i][1]==m) ):
            return i

def virtuallinknumber(data, m, n):
    # Return the number of a virtual link, given its source and destination nodes
    for i in range(len(data)):
        if ( (data[i][0]==m) and (data[i][1]==n) ) :
            return i

def nodename(data, n):
    # Return the name of a node, given its number
    return data[n]

def nodenumber(data, m):
    # Return the number of a node, given its name
    for i in range(len(data)):
        if (data[i]==m):
            return i
        
def path2str(path,N):
    # Convert a list of node ids to a list of node names
    sep = ", "
    out = "["
    first=True
    for i in range(len(path)):
        n = path[i]
        if isinstance(n, list):
            if (first):
                out = out + path2str(n)
                first=False
            else:
                out = out + sep + path2str(n)
        else:
            if (first):
                out = out + N[n]
                first=False
            else:
                out = out + sep + N[n]
    out = out + "]"
    return out

def path2links(path):
    # Convert a path to a list of links
    out = []
    for i in range(len(path)-1):
        out.append([path[i],path[i+1]])
    return out

def printLinks(data):
    # Print Links
    for d in range(len(data)):
        print("L=",d,",","nodes=[",data[d][0],",",data[d][1],"]")

def sortTrafficRequestsAscending(data):
    # Sort according to the 3rd item of each triplet which corresponds to the requested Gbps [m,n,req]

    data.sort(key = operator.itemgetter(2))
                
def sortTrafficRequestsDescending(data):
    # Sort according to the 3rd item of each triplet which corresponds to the requested Gbps [m,n,req]
    n = len(data)
    for i in range(n):
        for j in range(0, n-1):
            if data[j][2] < data[j+1][2] :
                data[j], data[j+1] = data[j+1], data[j]

def sortDecoratedTrafficRequestsClassAscendingTrafficDemandDescending(data):
    data.sort(key = operator.itemgetter(3,-2))

def printTrafficRequests(data, nodes, comment):
    # print traffic requests
    print ("<table class='table1c'>")
    print ("<tr><th>&lambda;: Descending order of the traffic demand per node pair (requests) in Gbps</th></tr>")
    print (f"<tr><th>{comment:s}</th></tr>")
    n = len(data)
    reqid=0
    # Traverse through all array elements
    for i in range(n):
        reqcap = roundatdecimals(data[i][2], 3)
        print("<tr><td>Request ",reqid,".",nodes[data[i][0]], "&rarr;",nodes[data[i][1]], "required capacity",reqcap,"</td></tr>")
        reqid+=1 # req numbers start at 0 (not 1)
    print ("</table>")

def createSQLiteDB(path):

    db_filename='lightbase.db'
    newfilename = os.path.join(path, db_filename)
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect(newfilename)

        sqliteConnection.execute(''' 
            PRAGMA foreign_keys = ON;
        ''')

        sqliteConnection.execute(''' 
            CREATE TABLE IF NOT EXISTS Nodes (
                num integer NOT NULL,
                name text NOT NULL,
                PRIMARY KEY (num)
            );
        ''')

        sqliteConnection.execute(''' 
            CREATE TABLE IF NOT EXISTS Queues (
                num integer NOT NULL,
                name text NOT NULL,
                PRIMARY KEY (num)
            );
        ''')

        sqliteConnection.execute(''' 	
            CREATE TABLE IF NOT EXISTS TrafficRequests (
                quenum integer NOT NULL,
                num integer NOT NULL,
                src integer NOT NULL,
                dst integer NOT NULL,
                cap real NOT NULL,
                PRIMARY KEY (quenum, num),
                FOREIGN KEY (quenum) REFERENCES Queues (num)
            );
        ''')

        sqliteConnection.execute('''	
            CREATE TABLE IF NOT EXISTS PhysicalLinks (
                src integer NOT NULL,
                dst integer NOT NULL,
                dist real NOT NULL,
                LatEDFAs real NOT NULL,
                LatFibLen real NOT NULL,
                PRIMARY KEY (src, dst)
            );
        ''')

        sqliteConnection.execute('''
            CREATE TABLE IF NOT EXISTS VirtualLinks (
                src integer NOT NULL,
                dst integer NOT NULL,
                num integer NOT NULL,
                caputil real NOT NULL,
                capfree real NOT NULL,
                PRIMARY KEY (src, dst, num)
            );
        ''')

        sqliteConnection.execute('''
            CREATE TABLE IF NOT EXISTS RoutingTrafficRequestsOverVirtualTopology (
                reqquenum integer NOT NULL,
                reqnum integer NOT NULL,
                vlsrc integer NOT NULL,
                vldst integer NOT NULL,
                vlnum integer NOT NULL,
                utilcap real NOT NULL,
                freecap real NOT NULL,
                type text NOT NULL,
                routingStep integer NOT NULL,
                routStepVLseqnum integer NOT NULL,
                PRIMARY KEY (reqquenum, reqnum, vlsrc, vldst, vlnum),
                FOREIGN key (reqquenum, reqnum) REFERENCES TrafficRequests (quenum, num),
                FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num)
            );
        ''')

        sqliteConnection.execute('''
            CREATE TABLE IF NOT EXISTS RoutingVirtualLinksOverPhysicalTopology (
                vlsrc integer NOT NULL,
                vldst integer NOT NULL,
                vlnum integer NOT NULL,
                plsrc integer NOT NULL,
                pldst integer NOT NULL,
                fiberid integer NOT NULL,
                waveid integer NOT NULL,
                type text NOT NULL,
                NumberOfHops integer NOT NULL,
                ShortestpathAsInt text NOT NULL,
                ShortestpathAsStr text NOT NULL, 
                PhysicalLinkDirection text NOT NULL,
                PhysicalLinkCurrentSource integer NOT NULL,
                PhysicalLinkCurrentDestination integer NOT NULL,
                LatIP real NOT NULL,
                LatTransp real NOT NULL,
                PRIMARY KEY (vlsrc, vldst,vlnum, plsrc, pldst, fiberid, waveid),
                FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num)
                FOREIGN key (plsrc, pldst) REFERENCES PhysicalLinks (src, dst) 
            );
        ''')

        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS route_traffic_requests_over_virtual_and_physical_topology 
            AS
            SELECT
                Queues.name,
                Queues.num,
            
                TrafficRequests.quenum as TReqQueNum,
                TrafficRequests.num as TReqReqNum,
                TrafficRequests.src as TReqSrc,
                TrafficRequests.dst as TReqDst,
                TrafficRequests.cap as TReqCap,
            
                RoutingTrafficRequestsOverVirtualTopology.reqquenum as routeTReqOverVTreqquenum,
                RoutingTrafficRequestsOverVirtualTopology.reqnum as routeTReqOverVTreqnum,
                RoutingTrafficRequestsOverVirtualTopology.vlsrc as routeTReqOverVT_VLsrc,
                RoutingTrafficRequestsOverVirtualTopology.vldst as routeTReqOverVT_VLdst,
                RoutingTrafficRequestsOverVirtualTopology.vlnum as routeTReqOverVT_VLnum,
                RoutingTrafficRequestsOverVirtualTopology.utilcap as routeTReqOverVTutilCap,
                RoutingTrafficRequestsOverVirtualTopology.freecap as routeTReqOverVTfreeCap,
                RoutingTrafficRequestsOverVirtualTopology.type as routeTReqOverVTtype,
                RoutingTrafficRequestsOverVirtualTopology.routingStep as routeTReqOverVTroutingStep,
                RoutingTrafficRequestsOverVirtualTopology.routStepVLseqnum as routeTReqOverVTroutStepVLseqnum,
                            
                VirtualLinks.src as VLsrc,
                VirtualLinks.dst as VLdst,
                VirtualLinks.num as VLnum,
                VirtualLinks.caputil as VLcaputil,
                VirtualLinks.capfree as VLcapfree,
            
                RoutingVirtualLinksOverPhysicalTopology.vlsrc as routeVLoverPT_VLsrc,
                RoutingVirtualLinksOverPhysicalTopology.vldst as routeVLoverPT_VLdst,
                RoutingVirtualLinksOverPhysicalTopology.vlnum as routeVLoverPT_VLnum,
                RoutingVirtualLinksOverPhysicalTopology.plsrc as routeVLoverPT_PLsrc,
                RoutingVirtualLinksOverPhysicalTopology.pldst as routeVLoverPT_PLdst,
                RoutingVirtualLinksOverPhysicalTopology.fiberid as routeVLoverPT_fiberID,
                RoutingVirtualLinksOverPhysicalTopology.waveid as routeVLoverPT_waveID,
                RoutingVirtualLinksOverPhysicalTopology.type as routeVLoverPT_type,
                RoutingVirtualLinksOverPhysicalTopology.NumberOfHops as routeVLoverPT_NumOfHops,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsInt as routeVLoverPT_shPathAsInt,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsStr  as routeVLoverPT_shPathAsStr,
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkDirection as routeVLoverPT_PLdir, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentSource as routeVLoverPT_currSrc, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentDestination as routeVLoverPT_currDest,
                RoutingVirtualLinksOverPhysicalTopology.LatIP as routeVLoverPT_LatIP,
                RoutingVirtualLinksOverPhysicalTopology.LatTransp as routeVLoverPT_LatTransp,
            
                PhysicalLinks.src as PLsrc,
                PhysicalLinks.dst as PLdst,
                PhysicalLinks.dist as PLdistance,
                PhysicalLinks.LatEDFAs as PLlatEDFA,
                PhysicalLinks.LatFibLen as PLlatFibLen
            
            FROM
                Queues, 
                TrafficRequests, 
                VirtualLinks,
                PhysicalLinks,
                RoutingTrafficRequestsOverVirtualTopology,
                RoutingVirtualLinksOverPhysicalTopology
            
            WHERE
                    Queues.num = TrafficRequests.quenum
            
                AND TrafficRequests.quenum = RoutingTrafficRequestsOverVirtualTopology.reqquenum
                AND TrafficRequests.num = RoutingTrafficRequestsOverVirtualTopology.reqnum
                AND RoutingTrafficRequestsOverVirtualTopology.vlsrc = VirtualLinks.src
                AND RoutingTrafficRequestsOverVirtualTopology.vldst = VirtualLinks.dst
                AND RoutingTrafficRequestsOverVirtualTopology.vlnum = VirtualLinks.num
            
                AND VirtualLinks.src = RoutingVirtualLinksOverPhysicalTopology.vlsrc
                AND VirtualLinks.dst = RoutingVirtualLinksOverPhysicalTopology.vldst
                AND VirtualLinks.num = RoutingVirtualLinksOverPhysicalTopology.vlnum
            
                AND RoutingVirtualLinksOverPhysicalTopology.plsrc = PhysicalLinks.src
                AND RoutingVirtualLinksOverPhysicalTopology.pldst = PhysicalLinks.dst
            
            ORDER BY
                TrafficRequests.quenum,
                TrafficRequests.num
                ASC;
        ''')

        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS RouteTRoverVTandPT 
            AS
            SELECT
                Queues.name,
            
                TrafficRequests.quenum as TReqQueNum,
                TrafficRequests.num as TReqReqNum,
                TrafficRequests.src as TReqSrc,
                TrafficRequests.dst as TReqDst,
                TrafficRequests.cap as TReqCap,

                VirtualLinks.src as VLsrc,
                VirtualLinks.dst as VLdst,
                VirtualLinks.num as VLnum,
                VirtualLinks.caputil as VLcaputil,
                VirtualLinks.capfree as VLcapfree,
                RoutingTrafficRequestsOverVirtualTopology.type as rtTRoverVT_type,
                RoutingTrafficRequestsOverVirtualTopology.routingStep as rtTRoverVTroutingStep,
                RoutingTrafficRequestsOverVirtualTopology.routStepVLseqnum as rtTRoverVTroutStpVLseqnum,
                                 
                PhysicalLinks.src as PLsrc,
                PhysicalLinks.dst as PLdst,
                PhysicalLinks.dist as PLdistance,
                PhysicalLinks.LatEDFAs as PLlatEDFA,
                PhysicalLinks.LatFibLen as PLlatFibLen,
            
                RoutingVirtualLinksOverPhysicalTopology.fiberid as rtVLoverPTfiberID,
                RoutingVirtualLinksOverPhysicalTopology.waveid as rtVLoverPTwaveID,
                RoutingVirtualLinksOverPhysicalTopology.type as rtVLoverPTtype,
                RoutingVirtualLinksOverPhysicalTopology.NumberOfHops as rtVLoverPTnumOfHops,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsInt as rtVLoverPTshrtPathAsInt,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsStr  as rtVLoverPTshrtPathAsStr,
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkDirection as rtVLoverPTphysLinkDir, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentSource as rtVLoverPTcurrSrc, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentDestination as rtVLoverPTcurrDst,
                RoutingVirtualLinksOverPhysicalTopology.LatIP as rtVLoverPTlatIP,
                RoutingVirtualLinksOverPhysicalTopology.LatTransp as rtVLoverPTlatTranspndr
            
            FROM
                Queues, 
                TrafficRequests, 
                VirtualLinks,
                PhysicalLinks,
                RoutingTrafficRequestsOverVirtualTopology,
                RoutingVirtualLinksOverPhysicalTopology
            
            WHERE
                    Queues.num = TrafficRequests.quenum
            
                AND TrafficRequests.quenum = RoutingTrafficRequestsOverVirtualTopology.reqquenum
                AND TrafficRequests.num = RoutingTrafficRequestsOverVirtualTopology.reqnum
                AND RoutingTrafficRequestsOverVirtualTopology.vlsrc = VirtualLinks.src
                AND RoutingTrafficRequestsOverVirtualTopology.vldst = VirtualLinks.dst
                AND RoutingTrafficRequestsOverVirtualTopology.vlnum = VirtualLinks.num
            
                AND VirtualLinks.src = RoutingVirtualLinksOverPhysicalTopology.vlsrc
                AND VirtualLinks.dst = RoutingVirtualLinksOverPhysicalTopology.vldst
                AND VirtualLinks.num = RoutingVirtualLinksOverPhysicalTopology.vlnum
            
                AND RoutingVirtualLinksOverPhysicalTopology.plsrc = PhysicalLinks.src
                AND RoutingVirtualLinksOverPhysicalTopology.pldst = PhysicalLinks.dst
            
            ORDER BY
                TrafficRequests.quenum,
                TrafficRequests.num
                ASC;
        ''')

        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_allQueues
            AS
            SELECT
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep,
            routeTReqOverVTtype,

            /*
            TReqSrc,
            TReqDst,
            VLsrc,
            VLdst,
            VLnum,
            routeTReqOverVTtype,
            PLsrc,
            PLdst,
            routeVLoverPT_PLdir,
            routeTReqOverVTroutStepVLseqnum,
            --(routeTReqOverVTroutStepVLseqnum + 1) as routeVLoverPT_NumOfOpticalHops,
            routeVLoverPT_NumOfHops,
            routeVLoverPT_LatIP,
            routeVLoverPT_LatTransp,
            PLlatEDFA,
            PLlatFibLen,
            (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as Latency,
            */

            sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency

            from 
                (
                    select 
                        * 
                    from 
                        route_traffic_requests_over_virtual_and_physical_topology 

                    --where
                    --		TReqQueNum = 0
                    --	and TReqReqNum = 10
                    order by
                        TReqQueNum,
                        TReqReqNum
                )
            /*
            WHERE
                routeTReqOverVTtype = 'Grm'
            */
            group by
                TReqQueNum,
                TReqReqNum,
                routeTReqOverVTroutingStep
            order by
                TReqQueNum ASC,
                TReqReqNum ASC
                --routeTReqOverVTroutingStep DESC, routeTReqOverVTroutStepVLseqnum DESC
        ''')

        sqliteConnection.execute('''        
            Create View If not EXISTS LatenciesPerTrafficRequest
            AS SELECT
                TReqQueNum,
                TReqReqNum,
                routeTReqOverVTroutingStep,
                routeTReqOverVTtype,
                sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency
                from (select * from route_traffic_requests_over_virtual_and_physical_topology 
                    order by TReqQueNum,
                            TReqReqNum)
                group by
                    TReqQueNum,
                    TReqReqNum,
                    routeTReqOverVTroutingStep
                order by
                    TReqQueNum ASC,
                    TReqReqNum ASC;
        ''')

        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_allQueues_NewVL
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest_allQueues Where routeTReqOverVTtype = 'New'
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_allQueues_Grm
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest_allQueues Where routeTReqOverVTtype = 'Grm'
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_Q0_Grm
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest Where TReqQueNum = 0 AND routeTReqOverVTtype = 'Grm'
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_Q1_Grm
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest Where TReqQueNum = 1 AND routeTReqOverVTtype = 'Grm'
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_Q0_NewVL
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest Where TReqQueNum = 0 AND routeTReqOverVTtype = 'New'
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS GetTotalLatencyPerTrafficRequest_Q1_NewVL
            AS
            SELECT * From GetTotalLatencyPerTrafficRequest Where TReqQueNum = 1 AND routeTReqOverVTtype = 'New'
        ''')

        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS LatencyStatsPerTrafficRequest_Q0_alltypes
            AS
            SELECT avg(TotalLatency) as avgLatencyQ0, min(TotalLatency) as minLatencyQ0, max(TotalLatency) as maxLatencyQ0
            FROM (	SELECT
                    TReqQueNum,
                    TReqReqNum,
                    routeTReqOverVTroutingStep,
                    routeTReqOverVTtype,
                    sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency
                    FROM (
                        select * 
                        from route_traffic_requests_over_virtual_and_physical_topology 
                        order by
                            TReqQueNum,
                            TReqReqNum
                    )
                    WHERE
                        TReqQueNum = 0
                        --routeTReqOverVTtype = 'Grm'

                    group by
                        TReqQueNum,
                        TReqReqNum,
                        routeTReqOverVTroutingStep
                    order by
                        TReqQueNum ASC,
                        TReqReqNum ASC
            )
        ''')
        
        sqliteConnection.execute('''
            CREATE VIEW IF NOT EXISTS LatencyStatsPerTrafficRequest_Q1_alltypes
            AS
            SELECT avg(TotalLatency) as avgLatencyQ1, min(TotalLatency) as minLatencyQ1, max(TotalLatency) as maxLatencyQ1
            FROM (	SELECT
                    TReqQueNum,
                    TReqReqNum,
                    routeTReqOverVTroutingStep,
                    routeTReqOverVTtype,
                    sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency
                    FROM (
                        select * 
                        from route_traffic_requests_over_virtual_and_physical_topology 
                        order by
                            TReqQueNum,
                            TReqReqNum
                    )
                    WHERE
                        TReqQueNum = 1
                        --routeTReqOverVTtype = 'Grm'

                    group by
                        TReqQueNum,
                        TReqReqNum,
                        routeTReqOverVTroutingStep
                    order by
                        TReqQueNum ASC,
                        TReqReqNum ASC
            )
        ''')

        #sqliteConnection.execute('''
        #   write SQL here            
        #''')

        sqliteConnection.commit()

    # Handle errors
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during SQLite tables and view creation. "+err.sqlite_errorname,err.sqlite_errorcode)
    
    return sqliteConnection

def insertRoutingVirtualLinksOverPhysicalTopology2sqlite(sqliteConnection, vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, type, numHops, shPathAsInt, shPathAsStr, plDirection, plCurrentSource, plCurrentDestination, LatIP, LatTransp):
    plFound = False
    try:
        # since links are dibirectional, only one record is inserted for both (src, dst), (dst, src)
        # therefore I have to check if either (src, dst) or (dst, src) exists
        
        if getPhysicalLinkFromSQLite(sqliteConnection, plsrc, pldst) == 1: # if fwd link direction
            plSource = plsrc
            plDestination = pldst
            plFound = True
        elif getPhysicalLinkFromSQLite(sqliteConnection, pldst, plsrc) == 1: # if rev link direction
            plSource = pldst
            plDestination = plsrc
            plFound = True
        else:
            error("Physical Link not found in the database.",55)

        if plFound:
            sql  = "INSERT INTO RoutingVirtualLinksOverPhysicalTopology "
            sql += "(vlsrc,vldst,vlnum,plsrc,pldst,fiberid,waveid,type,NumberOfHops,ShortestpathAsInt,ShortestpathAsStr,PhysicalLinkDirection,PhysicalLinkCurrentSource,PhysicalLinkCurrentDestination,LatIP,LatTransp) "
            sql += "VALUES (%d, %d, %d, %d, %d, %d, %d, '%s', %d, '%s', '%s', '%s', %d, %d, %.3f, %.3f);" % (vlsrc, vldst, vlnum, plSource, plDestination, fiberid, waveid, type, numHops, shPathAsInt, shPathAsStr, plDirection, plCurrentSource, plCurrentDestination, LatIP, LatTransp)

            sqliteConnection.execute(sql)
            sqliteConnection.commit()

    except sqlite3.Error as err:

        sql = "SELECT * FROM VirtualLinks"
        cursor = sqliteConnection.execute(sql)
        print("<li style='list-style-type: circle;'>VirtualLinks")
        dataset = cursor.fetchall() 
        for row in dataset: 
            print("<li>",row) 
        sqliteConnection.commit()

        sql = "SELECT * FROM PhysicalLinks"
        cursor = sqliteConnection.execute(sql)
        print("<li style='list-style-type: circle;'>PhysicalLinks")
        dataset = cursor.fetchall() 
        for row in dataset: 
            print("<li>",row) 
        sqliteConnection.commit()

        #print('<div class="error">Error occurred during FiberWavelengthAssignments - ', err,"</div>")
        error(err.sqlite_errorname,err.sqlite_errorcode)

def getPhysicalLinkFromSQLite(sqliteConnection, plsrc, pldst):
    sql = f"SELECT * FROM PhysicalLinks WHERE src={plsrc:d} AND dst={pldst:d};"
    cursor = sqliteConnection.execute(sql)
    
    dataset = cursor.fetchall() 
    #for row in dataset: 
    #    print("<li>",row) 
    sqliteConnection.commit()
    #print(f"<li style='list-style-type: circle;'>PhysicalLinks having source={plsrc:d} and destination={pldst:d}: {len(dataset):d}.")
    return len(dataset)

#>>> new get totals from DB

def getDiPerQueueFromSQLite(sqliteConnection, quenum, B):

    sql  =  "select src, sum(cap) "
    sql +=  "from TrafficRequests "
    sql += f"where quenum = {quenum:d} "
    sql +=  "group by src; "
    
    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)
    
    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset: 
        #print("<li>",row) 
        value = numpy.ceil(row[1] / B)
        dict.update({row[0]:value})

    sqliteConnection.commit()
    
    #print(f"<li style='list-style-type: circle;'>PhysicalLinks having source={plsrc:d} and destination={pldst:d}: {len(dataset):d}.")
    
    #print (f"<li>Di for queue {quenum:d} ",dict)

    return dict

def getCijPerQueueFromSQLite(sqliteConnection, quenum):
    
    sql  =   "select vlsrc, vldst, count(vlnum) "
    sql +=  "from RoutingTrafficRequestsOverVirtualTopology "
    sql += f"where reqquenum = {quenum:d} "
    sql +=  "GROUP by vlsrc, vldst; "
    
    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)
    
    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset:
        key = (row[0],row[1])
        value = row[2]
        dict.update({key:value})

    sqliteConnection.commit()

    #print (f"<li>C<sub>ij</sub> for queue {quenum:d} ",dict)

    return dict

def getSigmaCijPerQueueFromSQLite(sqliteConnection, quenum):
    
    #sql  =  "select reqquenum, vlsrc, count(vldst) "
    sql  =  " select vlsrc, count(vldst) "
    sql +=  " from RoutingTrafficRequestsOverVirtualTopology "
    sql += f" where reqquenum = {quenum:d} "
    sql +=  " and RoutingTrafficRequestsOverVirtualTopology.type = 'New' " 
    sql +=  " GROUP by vlsrc; "
    
    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)
    
    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset:
        key = row[0]
        value = row[1]
        dict.update({key:value})

    sqliteConnection.commit()
  
    return dict

def getWmnPerQueueFromSQLite(sqliteConnection, quenum, L):
    
    sql  =  "select rvlopt.plsrc, rvlopt.pldst, n1.name as src, n2.name as dst, count(rvlopt.waveid) "
    sql +=  "from RoutingVirtualLinksOverPhysicalTopology rvlopt, RoutingTrafficRequestsOverVirtualTopology rtrovt, Nodes n1, Nodes n2 "
    sql += f"where rtrovt.reqquenum = {quenum:d} "
    sql +=  "and   rtrovt.type <> 'Grm' "
    sql +=  "and   rvlopt.vlsrc = rtrovt.vlsrc "
    sql +=  "and   rvlopt.vldst = rtrovt.vldst "
    sql +=  "and   rvlopt.vlnum = rtrovt.vlnum "
    sql +=  "and   rvlopt.plsrc = n1.num "
    sql +=  "and   rvlopt.pldst = n2.num "
    sql +=  "GROUP by rvlopt.plsrc, rvlopt.pldst; "
    
    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)
    
    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset:
        #key = (row[0],row[1])
        key = linknumber(L, row[0], row[1])
        value = row[4]
        dict.update({key:value})

    sqliteConnection.commit()

    #print (f"<li>W<sub>mn</sub> for queue {quenum:d} ",dict)

    return dict


def getfmnPerQueueFromSQLite(sqliteConnection, quenum, L, WavelengthsPerFiber): 
    #get the number of wavelengths; the number of fibers is the ceiling of the fraction of the number of wavelengths to the wavelengths per fiber  
    
    sql  =  " select rvlopt.plsrc, rvlopt.pldst, n1.name as src, n2.name as dst, count(rvlopt.waveid) "
    sql +=  " from RoutingVirtualLinksOverPhysicalTopology rvlopt, RoutingTrafficRequestsOverVirtualTopology rtrovt, Nodes n1, Nodes n2 "
    sql += f" where rtrovt.reqquenum = {quenum:d} "
    sql +=  " and   rtrovt.type <> 'Grm' "
    sql +=  " and   rvlopt.vlsrc = rtrovt.vlsrc "
    sql +=  " and   rvlopt.vldst = rtrovt.vldst "
    sql +=  " and   rvlopt.vlnum = rtrovt.vlnum "
    sql +=  " and   rvlopt.plsrc = n1.num "
    sql +=  " and   rvlopt.pldst = n2.num "
    sql +=  " GROUP by rvlopt.plsrc, rvlopt.pldst; "
    
    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)
    
    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset:
        key = linknumber(L, row[0], row[1])
        value = numpy.ceil(row[4] / WavelengthsPerFiber)
        dict.update({key:value})

    sqliteConnection.commit()

    #print (f"<li>f<sub>mn</sub> for queue {quenum:d} ",dict)
    
    return dict

def getLatFibLenPerQueueFromSQLite(sqliteConnection, quenum):
    
    #sql  =  "select rtrovt.reqquenum, n1.name as src, n2.name as dst, pl.LatFibLen "
    sql  =  "select n1.name as src, n2.name as dst, pl.LatFibLen "
    sql +=  "from RoutingVirtualLinksOverPhysicalTopology rvlopt, RoutingTrafficRequestsOverVirtualTopology rtrovt, Nodes n1, Nodes n2, PhysicalLinks pl "
    sql += f"where rtrovt.reqquenum = {quenum:d} "
    sql +=  "and   rtrovt.type <> 'Grm' "
    sql +=  "and   rvlopt.vlsrc = rtrovt.vlsrc " 
    sql +=  "and   rvlopt.vldst = rtrovt.vldst "
    sql +=  "and   rvlopt.vlnum = rtrovt.vlnum "
    sql +=  "and   rvlopt.plsrc = n1.num "
    sql +=  "and   rvlopt.pldst = n2.num "
    sql +=  "and   pl.src = rvlopt.plsrc "
    sql +=  "and   pl.dst = rvlopt.pldst "
    sql +=  "GROUP by rvlopt.plsrc, rvlopt.pldst; "

    #print ("<li>SQL query ",sql)

    cursor = sqliteConnection.execute(sql)

    dict = {}

    dataset = cursor.fetchall() 
    for row in dataset:
        key = (row[0],row[1])
        value = row[2]
        dict.update({key:value})

    sqliteConnection.commit()

    #print (f"<li>LatFibLen for queue {quenum:d} ",dict)

    return dict

def updateVirtualLink2sqlite(sqliteConnection, vl, utilcap, freecap):
    
    try:
        sql = f"UPDATE VirtualLinks SET caputil = {utilcap:.3f}, capfree = {freecap:.3f} WHERE src = {vl[0]:0d} AND dst = {vl[1]:0d} AND num = {vl[2]:0d};"

        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)
        sqliteConnection.commit()

    except sqlite3.Error as err:
        #print('<div class="error">Error occurred during INSERT INTO VirtualLinks - ', err,"</div>")
        error("Error occurred during UPDATE VirtualLinks. "+err.sqlite_errorname,err.sqlite_errorcode)

def insertVirtualLinkLightPaths2sqlite(sqliteConnection, src, dst, num, caputil, capfree):
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    try:
        sql = "INSERT INTO VirtualLinks (src, dst, num, caputil, capfree) VALUES (%d, %d, %d, %.3f, %.3f);" % (src, dst, num, caputil, capfree)

        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)
        sqliteConnection.commit()

    except sqlite3.Error as err:
        #print('<div class="error">Error occurred during INSERT INTO VirtualLinks - ', err,"</div>")
        error("Error occurred during INSERT INTO VirtualLinks. "+err.sqlite_errorname,err.sqlite_errorcode)

def insertRoutingOfTrafficRequests2sqlite(sqliteConnection, que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum):
    #insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm")   # insert routing to sqlite table.
    try:
        sql =  "INSERT INTO RoutingTrafficRequestsOverVirtualTopology "
        sql += "(reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, type, routingStep, routStepVLseqnum) "
        sql += "VALUES (%d, %d, %d, %d, %d, %.3f, %.3f, '%s', %d, %d);" % (que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum)
        
        ###17-9-2024 #>>> #@@@
        print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)

        sqliteConnection.commit()

        ###17-9-2024 #>>> #@@@
        #fsqlInsert = open("SQL_INSERTINTO_RoutingTrafficRequestsOverVirtualTopology.txt","a")
        #fsqlInsert.write(sql+'\n')
        #fsqlInsert.close()

    except sqlite3.Error as err:
        '''
        #fsqlRTROVT = open("SQL_SELECT_RoutingTrafficRequestsOverVirtualTopology.txt","a")
        sql = "SELECT * FROM RoutingTrafficRequestsOverVirtualTopology"
        cursor = sqliteConnection.execute(sql)
        print("<li style='list-style-type: circle;'>RoutingTrafficRequestsOverVirtualTopology")
        dataset = cursor.fetchall() 
        for row in dataset: 
            print("<li>",row)
            #fsqlRTROVT.write(row+'\n')
        sqliteConnection.commit()
        #fsqlRTROVT.close()

        #fsqlTR = open("SQL_SELECT_TrafficRequests.txt","a")
        sql = "SELECT * FROM TrafficRequests"
        cursor = sqliteConnection.execute(sql)
        print("<li style='list-style-type: circle;'>TrafficRequests")
        dataset = cursor.fetchall() 
        for row in dataset: 
            print("<li>",row+'\n')
            #fsqlTR.write(row)
        sqliteConnection.commit()
        #fsqlTR.close()

        #fsqlVL = open("SQL_SELECT_VirtualLinks.txt","a")
        sql = "SELECT * FROM VirtualLinks"
        cursor = sqliteConnection.execute(sql)
        print("<li style='list-style-type: circle;'>VirtualLinks")
        dataset = cursor.fetchall() 
        for row in dataset: 
            print("<li>",row) 
            #fsqlVL.write(row+'\n')
        sqliteConnection.commit()
        #fsqlVL.close()
        '''
        #print('<div class="error">Error occurred during INSERT INTO RoutingTrafficRequestsOverVirtualTopology. ', err,"</div>")
        error("Error occurred during INSERT INTO RoutingTrafficRequestsOverVirtualTopology. " + err.sqlite_errorname,err.sqlite_errorcode)

def saveQueues2sqlite(sqliteConnection, Q):
    try:
        # Traverse through all array elements
        for i in range(len(Q)):
            sql = "INSERT INTO Queues (num, name) VALUES (%d, '%s');" % (i, Q[i])

            #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

            sqliteConnection.execute(sql)
            
        sqliteConnection.commit()
   
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during instertion to Queues table. "+err.sqlite_errorname, err.sqlite_errorcode)

def saveNodes2sqlite(sqliteConnection, N):
    try:
        # Traverse through all array elements
        for i in range(len(N)):
            sql = "INSERT INTO Nodes (num, name) VALUES (%d, '%s');" % (i, N[i])

            #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

            sqliteConnection.execute(sql)
            
        sqliteConnection.commit()
   
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during instertion to Nodes table. "+err.sqlite_errorname, err.sqlite_errorcode)

def savePhysicalLinks2sqlite(sqliteConnection, data, Dist, EDFAdist, LatEDFA, LatFiberKilometer, graphsPath):
    #savePhysicalLinks2sqlite(dbConnection,     L,    Dist, EDFAdist, LatEDFA, LatFiberKilometer, graphsPath)
    try:
        n = len(data)
        #physlinkid=0
        # Traverse through all array elements
        for i in range(n):
            LatEDFAs = LatEDFA * (numpy.ceil(Dist[i] / EDFAdist - 1.0) + 2)
            LatFibLen = roundatdecimals(LatFiberKilometer * Dist[i], 3)
            sql = "INSERT INTO PhysicalLinks (src, dst, dist, LatEDFAs, LatFibLen) VALUES (%d, %d, %.3f, %.3f, %.3f);" % (data[i][0], data[i][1], Dist[i], LatEDFAs, LatFibLen)
            
            #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")
            
            sqliteConnection.execute(sql)
            #physlinkid+=1
        
        sqliteConnection.commit()
   
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during insertion of physical links to SQLite. "+err.sqlite_errorname,err.sqlite_errorcode)

def saveTrafficRequests2sqlite(sqliteConnection,          TReqs,    nodes, path,       Qlabel,     QueueID): #, firstidvalue):
    #nextReqID = saveTrafficRequests2sqlite(dbConnection, requests, N,     graphsPath, Queuelabel, queueID)  #, startReqID)
    
    try:
        n = len(TReqs)
        #count=firstidvalue
        # Traverse through all array elements
        for reqID in range(n):
            #sql = "INSERT INTO trafficrequests (reqid, src, dst, reqcap, queuelabel) VALUES (%d, %d, %d, %.3f, '%s');" % (count, data[i][0], data[i][1], data[i][2], Qlabel)
            sql = "INSERT INTO TrafficRequests (quenum, num, src, dst, cap) VALUES (%d, %d, %d, %d, %.3f);" % (QueueID, reqID, TReqs[reqID][0], TReqs[reqID][1], TReqs[reqID][2])

            #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

            sqliteConnection.execute(sql)
            #count+=1
        
        sqliteConnection.commit()

        #cursor = sqliteConnection.execute("SELECT * from TrafficRequests;")
 
        # display all data from hotel table
        #for row in cursor:
        #    print('<div class="error">Data', row,"</div>")
    
        # Close the cursor
        #cursor.close()
   
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during insert into TrafficRequests. "+err.sqlite_errorname,err.sqlite_errorcode)

    # Close DB Connection irrespective of success or failure
    #finally:
    #    if sqliteConnection:
    #        sqliteConnection.close()
    #        #print('SQLite Connection closed')
    #return count #the request id number to be used for the next request id if any (e.g. for a second queue)

def saveTrafficRequests2csv(data, nodes, path, Qlabel):

    filename='trafficrequests.csv'
    newfilename = os.path.join(path, filename)

    fout = open(newfilename,"w")
    count = 0
    for d in data:
        count += 1
        fout.write(str(count)+","+Qlabel+","+str(d[0])+","+str(d[1])+","+"{:0.3f}".format(d[2])+"\n")
    fout.close()

def EvaluateLatencyAggregated(LatRouterPort,LatencyTimeUnit,LatTransponder,LatEDFA,LatFiberKilometer,SigmaCij,Di,N,L,Wmn,Amn,fmn,Dist):

    global GlobalPrintOutEnabled

    # Evaluate Latency (start) >>>

    '''
    LatencyTimeUnit = "&micro;sec"

    LatRouterPort = 30 # microsecond
    LatTransponder = 100 # microsecond
    LatEDFA = 100 / 1000.0 # nanosecond
    LatFiberKilometer = 5 # microsecond
    '''

    print ("<table class='tableLat'>")
    print ("<tr><td>LatRouterPort:",LatRouterPort," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatTransponder:",LatTransponder," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatEDFA:",LatEDFA," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatFiberKilometer:",LatFiberKilometer," ",LatencyTimeUnit,"</td></tr>")
    print ("</table>")

    #Latency Aggregated

    valueOfLatency = 0.0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='tableLat'>")
        print ("<tr><th colspan=2>Latency evaluation in the IP layer: Processing and queuing, a.k.a. electronic switching latency</th></tr>")
        print ("<tr><th>Node</th><th>Latency L<sub>r</sub> * (&Delta;<sub>i</sub> + &Sigma; C<sub>ij</sub>) in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    LatencyIP = 0.0
    keys = list(SigmaCij.keys())
    keys.sort()
    for k in keys:
        valSigmaCij = SigmaCij.get(k)
        valDi = Di.get(k)
        valueOfLatency = LatRouterPort * ( valDi + valSigmaCij )
        LatencyIP += valueOfLatency
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[k],"</td><td>", LatRouterPort, "* (",valDi,"+",(valSigmaCij * 1.0),") =",valueOfLatency,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total:",LatencyIP," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")

        print ("<table class='tableLat'>")
        print ("<tr><th colspan=2>Latency evaluation in the optical layer - Part A: Optical switching latency of the transponders (OTU)</th></tr>")
        print ("<tr><th>Node</th><th>Latency &Sigma; &Sigma; L<sub>t</sub> * w<sub>mn</sub> in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    LatencyTransponders = nanosecond(0.0)
    for i in range(len(L)):
        key = linknumber(L, L[i][0],L[i][1])
        #>>>
        print("<li>aggregated Wmn", Wmn)

        valWmn = Wmn.get(key)
        valueOfLatency = LatTransponder * valWmn
        LatencyTransponders += valueOfLatency
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>", LatTransponder, "*",valWmn,"=",valueOfLatency,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total:",LatencyTransponders," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")

        print ("<table class='tableLat'>")
        print ("<tr><th colspan=4>Latency evaluation in the optical layer - Part B: Optical propagation latency relative to the number of EDFAs and the length of the fibers</th></tr>")
        print ("<tr><th>Node</th><th>Latency &Sigma; &Sigma; L<sub>e</sub> * A<sub>mn</sub> * f<sub>mn</sub> in ",LatencyTimeUnit,"</th><th>Distance in km</th><th>Distance latency in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    LatencyEDFAs = 0.0
    LatencyFiberLength = 0.0
    TotalDistance = 0.0
    for i in range(len(L)):
        key = linknumber(L, L[i][0],L[i][1])
        valAmn = Amn.get(key)
        valfmn = fmn.get(key)
        valueOfLatency = LatEDFA * valAmn * valfmn
        LatencyEDFAs += valueOfLatency
        LatFiber = LatFiberKilometer * Dist[key]
        LatencyFiberLength += LatFiber
        TotalDistance += Dist[key]
        valueOfLatency = roundatdecimals(valueOfLatency,3)
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>", LatEDFA, "*",valAmn,"*",valfmn,"=",valueOfLatency,"</td><td>",Dist[key],"</td><td>",LatFiber,"</td></tr>")
        #EOP

    LatencyTotal = LatencyIP + LatencyTransponders + LatencyEDFAs + LatencyFiberLength

    LatencyTotal = roundatdecimals(LatencyTotal,3)
    LatencyIP = roundatdecimals(LatencyIP,3) 
    LatencyTransponders = roundatdecimals(LatencyTransponders,3) 
    LatencyEDFAs = roundatdecimals(LatencyEDFAs,3) 
    LatencyFiberLength = roundatdecimals(LatencyFiberLength,3) 

    #LatencyTotal = roundatdecimals(LatencyTotal/1000.0,3) in seconds
    #LatencyIP = roundatdecimals(LatencyIP/1000.0,3) in seconds
    #LatencyTransponders = roundatdecimals(LatencyTransponders/1000.0,3) in seconds
    #LatencyEDFAs = roundatdecimals(LatencyEDFAs/1000.0,3) in seconds

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total Latency EDFAs:",LatencyEDFAs," ",LatencyTimeUnit,"</th>")
        print("<th>Total distance in km:",TotalDistance,"km</th>")
        print("<th>Total Latency Fiber Length:",LatencyFiberLength," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")
    #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='tableLat'>")
        print ("<tr><th>Evaluation of total latency in the network</th></tr>")
        print ("<tr><th>Transmission Latency in ",LatencyTimeUnit,"</th></tr>")
        print("<tr><th>",LatencyTotal," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")
    #EOP

    # >>> Evaluate Latency (end)

    return LatencyTotal


def printLatenciesPerTrafficRequest(sqliteConnection, Q, Type):

    #global GlobalPrintOutEnabled
    
    sqlconditional = ""
    tabletitle = ""
    
    #print("<li># Q", Q)
    #print("<li># Type", Type)


    if   Q == "All" and Type == "All":
        tabletitle = "Per Traffic Request Latencies for All Queues, All Types of routing traffic requests over the virtual topology"
        sqlconditional = ""
    elif Q == "All" and Type == "New":
        tabletitle = "Per Traffic Request Latencies for All Queues, routing of traffic requests over the virtual topology utilising new virtual links"
        sqlconditional = " WHERE routeTReqOverVTtype = 'New'"
    elif Q == "All" and Type == "Grm":
        tabletitle = "Per Traffic Request Latencies for All Queues, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links"
        sqlconditional = " WHERE routeTReqOverVTtype = 'Grm'"
    elif Q == 0 and Type == "All":
        tabletitle = "Per Traffic Request Latencies for Queue 0, All Types of routing traffic requests over the virtual topology"
        sqlconditional = " WHERE TReqQueNum = 0"
    elif Q == 1 and Type == "All":
        tabletitle = "Per Traffic Request Latencies for Queue 1, All Types of routing traffic requests over the virtual topology"
        sqlconditional = " WHERE TReqQueNum = 1"
    elif Q == 0 and Type == "New":
        tabletitle = "Per Traffic Request Latencies for Queue 0, routing of traffic requests over the virtual topology utilising new virtual links"
        sqlconditional = " WHERE TReqQueNum = 0 AND routeTReqOverVTtype = 'New'"
    elif Q == 1 and Type == "New":
        tabletitle = "Per Traffic Request Latencies for Queue 1, routing of traffic requests over the virtual topology utilising new virtual links"
        sqlconditional = " WHERE TReqQueNum = 1 AND routeTReqOverVTtype = 'New'"
    elif Q == 0 and Type == "Grm":
        tabletitle = "Per Traffic Request Latencies for Queue 0, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links"
        sqlconditional = " WHERE TReqQueNum = 0 AND routeTReqOverVTtype = 'Grm'"
    elif Q == 1 and Type == "Grm":
        tabletitle = "Per Traffic Request Latencies for Queue 1, routing of traffic requests over the virtual topology utilising traffic grooming through existing virtual links"
        sqlconditional = " WHERE TReqQueNum = 1 AND routeTReqOverVTtype = 'Grm'"

    sql  = " SELECT "
    sql += " TReqQueNum, "
    sql += " TReqReqNum, "
    sql += " routeTReqOverVTroutingStep, "
    sql += " routeTReqOverVTtype, "
    sql += " TotalLatency "
    sql += " FROM "
    sql += " LatenciesPerTrafficRequest "
    sql += sqlconditional    

    #print ("<li>SQL=",sql)
    
    cursor = sqliteConnection.execute(sql)
    
    sqliteConnection.commit()
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='tableLat0'>")
        print ("<tr><th colspan=5>",tabletitle,"</th></tr>")
        print ("<tr><th>TReqQueNum</th><th>TReqReqNum</th><th>routeTReqOverVTroutingStep</th><th>routeTReqOverVTtype</th><th>TotalLatency</th></tr>")
    #EOP

    dataset = cursor.fetchall() 
    for row in dataset: 
        print (f"<tr><th>{row[0]:0d}</th><th>{row[1]:0d}</th><th>{row[2]:0d}</th><th>{row[3]:s}</th><th>{row[4]:.3f}</th></tr>")
    #EOP
    print("</table>")



def getLatencyStatsPerTrafficRequest(sqliteConnection, Q, Type):

    #global GlobalPrintOutEnabled
        
    #print("<li># Q", Q)
    #print("<li># Type", Type)

    sql  = " SELECT avg(TotalLatency) as avgLat, min(TotalLatency) as minLat, max(TotalLatency) as maxLat   "
    sql += " FROM (	SELECT                                                                                  "
    sql += " TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep,	routeTReqOverVTtype,                    "
    sql += " sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency  "
    sql += " FROM (select * from route_traffic_requests_over_virtual_and_physical_topology                  "
    sql += " order by TReqQueNum,                                                                           "
    sql += " TReqReqNum)                                                                                    "
    sql += " WHERE                                                                                          "
    sql += f" TReqQueNum like '{Q:s}'                                                                            "
    sql += f" AND routeTReqOverVTtype like '{Type:s}'                                                             "
    sql += " group by                                                                                       "
    sql += " TReqQueNum, TReqReqNum,	routeTReqOverVTroutingStep                                          "
    sql += " order by                                                                                       "
    sql += " TReqQueNum ASC,	TReqReqNum ASC)                                                             "

    #print ("<li>SQL=",sql)
    
    cursor = sqliteConnection.execute(sql)
    
    sqliteConnection.commit()
    
    stats = []

    dataset = cursor.fetchall() 
    for row in dataset: 
        stats = [row[0], row[1], row[2]]
    #EOP
    
    return stats



def EvaluateLatencyPerQueue(QueueIDNum,LatRouterPort,LatencyTimeUnit,LatTransponder,LatEDFA,LatFiberKilometer,SigmaCij,Di,N,L,Wmn,Amn,fmn,Dist):

    global GlobalPrintOutEnabled

    # Evaluate Latency (start) >>>

    '''
    LatencyTimeUnit = "&micro;sec"

    LatRouterPort = 30 # microsecond
    LatTransponder = 100 # microsecond
    LatEDFA = 100 / 1000.0 # nanosecond
    LatFiberKilometer = 5 # microsecond
    '''

    '''
    print ("<table class='tableLat'>")
    print ("<tr><td>LatRouterPort:",LatRouterPort," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatTransponder:",LatTransponder," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatEDFA:",LatEDFA," ",LatencyTimeUnit,"</td></tr>")
    print ("<tr><td>LatFiberKilometer:",LatFiberKilometer," ",LatencyTimeUnit,"</td></tr>")
    print ("</table>")
    '''

    #Latency per Queue

    valueOfLatency = 0.0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print (f"<table class='tableLat{QueueIDNum:d}'>")
        print ("<tr><th colspan=2>Latency evaluation in the IP layer: Processing and queuing, a.k.a. electronic switching latency for Queue:",QueueIDNum,"</th></tr>")
        print ("<tr><th>Node</th><th>Latency L<sub>r</sub> * (&Delta;<sub>i</sub> + &Sigma; C<sub>ij</sub>) in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    
    #print("<h3>Evaluate IP latency</<h3>")
    #print("<li>Sigma Cij",SigmaCij)
    #print("<li>Di",Di)
    
    
    
    
    LatencyIP = 0.0
    keys = list(SigmaCij.keys())
    keys.sort()
    for k in keys:
        valSigmaCij = SigmaCij.get(k)
        valDi = Di.get(k)
        valueOfLatency = LatRouterPort * ( valDi + valSigmaCij )
        LatencyIP += valueOfLatency
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[k],"</td><td>", LatRouterPort, "* (",valDi,"+",(valSigmaCij * 1.0),") =",valueOfLatency,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total:",LatencyIP," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")

        print (f"<table class='tableLat{QueueIDNum:d}'>")
        print ("<tr><th colspan=2>Latency evaluation in the optical layer - Part A: Optical switching latency of the transponders (OTU)</th></tr>")
        print ("<tr><th>Node</th><th>Latency &Sigma; &Sigma; L<sub>t</sub> * w<sub>mn</sub> in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    LatencyTransponders = nanosecond(0.0)
    #print("<li>Wmn Q",QueueIDNum,"=",Wmn)
    for i in range(len(L)):
        key = linknumber(L, L[i][0],L[i][1])
        valWmn = Wmn.get(key)
        print("<li>val Wmn for Link ",key,"=",valWmn)
        if valWmn != None:
            valueOfLatency = LatTransponder * valWmn
            LatencyTransponders += valueOfLatency
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>", LatTransponder, "*",valWmn,"=",valueOfLatency,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total:",LatencyTransponders," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")

        print (f"<table class='tableLat{QueueIDNum:d}'>")
        print ("<tr><th colspan=4>Latency evaluation in the optical layer - Part B: Optical propagation latency relative to the number of EDFAs and the length of the fibers</th></tr>")
        print ("<tr><th>Node</th><th>Latency &Sigma; &Sigma; L<sub>e</sub> * A<sub>mn</sub> * f<sub>mn</sub> in ",LatencyTimeUnit,"</th><th>Distance in km</th><th>Distance latency in ",LatencyTimeUnit,"</th></tr>")
    #EOP

    LatencyEDFAs = 0.0
    LatencyFiberLength = 0.0
    TotalDistance = 0.0
    for i in range(len(L)):
        key = linknumber(L, L[i][0],L[i][1])
        valAmn = Amn.get(key)
        valfmn = fmn.get(key)
        if valAmn != None and valfmn != None:
            valueOfLatency = LatEDFA * valAmn * valfmn
            LatencyEDFAs += valueOfLatency
            LatFiber = LatFiberKilometer * Dist[key]
            LatencyFiberLength += LatFiber
            TotalDistance += Dist[key]
            valueOfLatency = roundatdecimals(valueOfLatency,3)
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>", LatEDFA, "*",valAmn,"*",valfmn,"=",valueOfLatency,"</td><td>",Dist[key],"</td><td>",LatFiber,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total Latency EDFAs:",LatencyEDFAs," ",LatencyTimeUnit,"</th>")
        print("<th>Total distance in km:",TotalDistance,"km</th>")
        print("<th>Total Latency Fiber Length:",LatencyFiberLength," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")
    #EOP

    LatencyTotal = LatencyIP + LatencyTransponders + LatencyEDFAs + LatencyFiberLength

    LatencyTotal = roundatdecimals(LatencyTotal,3)
    LatencyIP = roundatdecimals(LatencyIP,3) 
    LatencyTransponders = roundatdecimals(LatencyTransponders,3) 
    LatencyEDFAs = roundatdecimals(LatencyEDFAs,3) 
    LatencyFiberLength = roundatdecimals(LatencyFiberLength,3) 

    #LatencyTotal = roundatdecimals(LatencyTotal/1000.0,3) in seconds
    #LatencyIP = roundatdecimals(LatencyIP/1000.0,3) in seconds
    #LatencyTransponders = roundatdecimals(LatencyTransponders/1000.0,3) in seconds
    #LatencyEDFAs = roundatdecimals(LatencyEDFAs/1000.0,3) in seconds

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='tableLat'>")
        print ("<tr><th>Evaluation of total latency in the network</th></tr>")
        print ("<tr><th>Transmission Latency in ",LatencyTimeUnit,"</th></tr>")
        print("<tr><th>",LatencyTotal," ",LatencyTimeUnit,"</th></tr>")
        print("</table>")
    #EOP

    # >>> Evaluate Latency (end)

    return LatencyTotal

def generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(x, num):
    
    import numpy as np
    from scipy.stats import poisson
    data = poisson.rvs(mu=x, size=num)
    
    data=roundatdecimals(data, 3)

    return data

def generateUniformlyDistributedTrafficRequestValues(x, num):
    from numpy.random import default_rng

    margin = 10.0

    if x<=10:
        margin = x / 2.0
    
    rng = default_rng()
    #data = rng.uniform(low=10.0, high=2.0*x-10.0, size=num)
    data = rng.uniform(low=margin, high=2.0*x-margin, size=num)
    
    data=roundatdecimals(data, 3)
    #rnd=1 #assuming one (1) request per virtual link i.e. that all the traffic of a traffic request comes from one source and not multiple sources so that the traffic is the aggregation of all these sources
    #rnd may be: rnd=numpy.random.randint(0, 10) #no requests to e.g. 10 requests per virtual link, randomly
    #noprintout#print (rnd,"random traffic amount",data,end=" for ")
    return data

def find_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if start not in graph:
        return None
    for node in graph[start]:
        if node not in path:
            newpath = find_path(graph, node, end, path)
            if newpath: return newpath
    return None

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def find_shortest_path_using_bfs(graph, src, dst):
    from collections import deque

    global GlobalPrintOutEnabled
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>[Finding shortest path with minimum hops] Input graph:",graph,"<li>Source:",src,"<li>Destination:",dst)
    #EOP

    # Create a queue for BFS with a tuple (current_node, path_so_far)
    queue = deque([(src, [src])])
    
    # Set to keep track of visited nodes
    visited = set()
    
    while queue:
        # Dequeue a node and the path leading to it
        (vertex, path) = queue.popleft()
        
        # Check if the current node is the destination
        if vertex == dst:
            return path
        
        # Skip visited nodes
        if vertex not in visited:
            visited.add(vertex)
            
            # Enqueue all adjacent nodes that haven't been visited
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
    
    # If no path is found, return an empty list
    return []

def getPhysicalPathCost(L,C,p):
    #print(p)
    links = path2links(p)
    dAllCosts = {}
    for i in range(len(L)):
        l = tuple(L[i])
        dAllCosts.update({l:C[i]})
    #print("all costs",dAllCosts)
    Cost = 0.0
    for l in links:
        k = tuple(l)
        #print("key",k)
        if k not in dAllCosts.keys():
            l = [l[1],l[0]]
            k = tuple(l)
            #print("swap key",k)
        val = dAllCosts.get(k)
        #print ("cost",val)
        Cost += val
    return Cost

def getPhysicalPathWithMinCost(Nm,L,C,s,d):
    allpaths = find_all_paths(Nm,s,d)
    min = numpy.inf #numpy infinite value
    path = []
    for i in range(len(allpaths)):
        cost = getPhysicalPathCost(L,C,allpaths[i])
        #print('path ',allpaths[i],'from',s,'to',d,'cost',cost)
        if cost < min:
            min = cost
            path = allpaths[i]
    return path

def nodes2tuple(L):
    T=tuple(L)
    return T

def networkWithCosts(Net,Nodes,Links,Costs):
    netWcosts = {}
    for key in Net.keys():
        nodeWcosts={}
        for node in Net[key]:
            linknum = linknumber(Links, key,node)
            linkcost = Costs[linknum]
            nodeWcosts.update({Nodes[node]:linkcost})
        netWcosts.update({Nodes[key]:nodeWcosts})    
    return netWcosts

def calculateLamdaMatrixSums(x):
    sum=0
    for i in range(len(x)):
        sum = sum + x[i]
    return sum

def getVirtualLinkFreeCapacity(vtl, vtfrcap, linktuple):
    global GlobalPrintOutEnabled
    
    cap = None
    cap = vtfrcap.get(linktuple)
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Free capacity for",linktuple,"is",cap,".")
    #EOP
    return cap

def updateVitualLinkFreeCapacity(vtfrcap, linktuple, value):
    global GlobalPrintOutEnabled

    c = 0.0
    #print ("vtl",vtl)
    #print ("vt free capacities",vtfrcap)
    #print ("src",src)
    #print("dst",dst)
    cap = vtfrcap.get(linktuple)
    c = cap[0]
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<li>Update value is",value)
    #EOP

    c = c + value
    c = roundatdecimals(c,3)
    #c = numpy.round(c, decimals=3, out=None)
    cap[0] = c
    vtfrcap.update({linktuple:cap})
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
        #print("<li>Free capacity for",linktuple,"updated to",cap,".")
    #EOP

    return cap

def roundatdecimals(val, dec):
    return numpy.round(val, decimals=dec, out=None)
    
def microsecond(t):
    return numpy.double(t*0.000001)

def nanosecond(t):
    return numpy.double(t*0.000000001)

def millisecond(t):
    return numpy.double(t*0.001)

def appendVT(graph, node, newneighbour):
    global GlobalPrintOutEnabled

    neighbours = graph.get(node)
    
    if (neighbours==None):
        neighbours=[newneighbour]
    else:
        if (newneighbour not in neighbours):
            neighbours.append(newneighbour)
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>New neighbour",newneighbour,"is appended.")
            #EOP
        #SOP
        elif (GlobalPrintOutEnabled==True) :
            print ("<li>Neighbour not appended, since it is already in the neighbours list.")
        #EOP
    graph.update({node:neighbours})   #append virtual topology with new neighbour Nj for Ni
        
def appendVTL(list, src, dst):
    global GlobalPrintOutEnabled

    t = tuple([src, dst])
    if (t not in list):
        list.append(t)   #append virtual links with new source,destination pair
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<li>New virtual link",t,"is appended.")
        #EOP
    #SOP
    elif (GlobalPrintOutEnabled==True) :
        print ("<li>Link not appended, since it is already in the links list.")
    #EOP
        
def appendCapacities(data,src,dst,cap):
    global GlobalPrintOutEnabled

    t = tuple([src, dst])
    capacities=data.get(t)

    if (capacities==None):
        capacities=[cap]
    else:
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<li>Capacities of the link ",src,"&rarr;",dst,"are =",capacities)
        #EOP
        if (capacities[0]==0.0):
            capacities[0] = cap
        #SOP
        elif len(capacities)>1 and (GlobalPrintOutEnabled==True) :
            print ("<li>Error! more than one capacities in the capacities list!") # this is because there is only one virtual link between a source and a destination to have free capacity. e.g. a request HER->SAM of 210Gbps will result to 5 virtual links of 40Gbps each and a virtual link of 10Gbps that will have free capacity 30Gbps
            print("<li>Capacities",capacities)
        #EOP
    data.update({t:capacities})   #append free capacities for links with free capacity for new virtual link
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Capacities are",capacities)
    #EOP

def appendVLIDs(data,src,dst,id,free): #keep id for each and every virtual link (lightpath) created.
                                       #(not sure:keep virtual (lightpath) link IDs only for virtual links that have free capacity)
    global GlobalPrintOutEnabled

    data.update({id:[src, dst, free]})

    #print ("<li>VLIDs",data)

def getVLIDwithfreecapacity(VLIDs,Ni,Nj):
    id = 0
    #print ("<li>VLIDs",VLIDs)
    #print ("<li>source",Ni)
    #print ("<li>dest",Nj)
    for key, value in VLIDs.items():
        if ( (value[0]==Ni) and (value[1]==Nj) and (value[2]>0.0) ):
            id = key
    return id

def appendPerRequestLinks(data,que,req,newVL,type,cpcty,step,stepseqnum):  

    global GlobalStringOutcomes

    GlobalStringOutcomes += "<table class='dictionary'>"
    GlobalStringOutcomes += "<tr><th colspan='3'>Update of the Virtual Links per Request R <br>{(queue, request number): [(virtual link (s,d,n), type, capacity utilised, step of routing the requested capacity, step's virtual link sequence number), ...], ...}</th></tr>"
    GlobalStringOutcomes += "<tr><th>Justification</th><th>Key</th><th>Value</th></tr>"

    # function that appends the list R of links and their free capacity
    src = newVL[0]
    dst = newVL[1]
    num = newVL[2]
    t = tuple([src, dst, num, type, cpcty, step, stepseqnum])
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print(f"<li>que {que:0d} req {req:0d} (src {src:0d} dst {dst:0d} num {num:0d}) type {type:s} capacity {cpcty:.3f} step of routing reqquested traffic {step:0d} step's virtual link sequence number {stepseqnum:0d}</li>")
    #EOP

    links=data.get((que,req))
    #print("<li>links",links,"</li>")
    if (links==None):
        links=[t]
    else:
        links.append(t)

    data.update({(que,req):links})  #append the dictionary that holds the links used for each request

    #appendFinalVT(VTfinal,nodes,Ni,Nj,cap,"New") 
    #appendFinalVT(VTfinal,nodes,s,d,requiredcap,"Grm")

    #print("<h1>links",links)
    GlobalStringOutcomes += "<tr><td>Update key value</td>"    
    GlobalStringOutcomes += f"<td>({que:d},{req:d})</td><td>["
    for j in range(len(links)):
        GlobalStringOutcomes += f"({links[j][0]:d},{links[j][1]:d},{links[j][2]:d},'{links[j][3]:s}',{links[j][4]:.3f},{links[j][5]:d},{links[j][6]:d}),"
    GlobalStringOutcomes = GlobalStringOutcomes[:-1] # remove last character that is a comma (,)
    GlobalStringOutcomes += "]</td></tr>"
    GlobalStringOutcomes += "</table>"

def appendFinalVT(data,n,src,dst,cpcty, type):
#def appendFinalVTwhenNewVirtualLink(data,n,src,dst,cpcty):
    #             data=VTfinal
    # function that appends the list R of links and their free capacity
    #type="New"
    t = cpcty
    link=tuple([src,dst])
    links=data.get(link)
    if (links==None):
        links=[t]
    elif (type=="Grm"): #an prokeitai gia grooming tote to virtual link sto opoio tha prostheso ta Gbps tou grooming tha einai to teleutaio pou exei prostethei sta virtual links tou virtual topology
                        #LATHOS ayto prepei na allaxei kai na prostithetai se auto to virtual link pou afora (pou eixe elefthero capacity gia na ginei to grooming) Giayto prepei na krateitai kai to id toy link sto opoio egine grooming
                        #Done diorthothike
        links=data.get(link)
        l = len(links)
        val = links[l-1]
        val = val + cpcty
        val = roundatdecimals(val, 3)
        links[l-1] = val
    else:
        links.append(t)
    data.update({link:links})   #append the dictionary that holds the links used for each request

def updateFinalVTwhenGroomingOnVirtualLink(data,n,src,dst,cpcty):
    #             data=VTfinal
    # function that appends the list R of links and their free capacity
    type="Grm"
    t = cpcty
    link=tuple([src,dst])
    links=data.get(link)
    if (links==None):
        links=[t]
    elif (type=="Grm"): #an prokeitai gia grooming tote to virtual link sto opoio tha prostheso ta Gbps tou grooming tha einai to teleutaio pou exei prostethei sta virtual links tou virtual topology
                        #LATHOS ayto prepei na allaxei kai na prostithetai se auto to virtual link pou afora (pou eixe elefthero capacity gia na ginei to grooming) Giayto prepei na krateitai kai to id toy link sto opoio egine grooming
                        #Done diorthothike
        links=data.get(link)
        l = len(links)
        val = links[l-1]
        val = val + cpcty
        val = roundatdecimals(val, 3)
        links[l-1] = val
    else:
        links.append(t)
    data.update({link:links})   #append the dictionary that holds the links used for each request

def htmlhead(title, lenQs):
    global GlobalPrintOutEnabled

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<!DOCTYPE html>")
        print("<html>")
        print("<head>")
        print("<meta charset='utf-8'>")
        print("<meta name='description' content='Shen & Tucker Multihop Bypass'>")
        print("<meta name='keywords' content='Passive Optical Networks, University of Macedonia'>   ")
        print("<meta name='author' content='Constantinos Delistavrou'>")
        print("<meta name='author' content='&Kappa;&omega;&nu;&sigma;&tau;&alpha;&nu;&tau;&acute;&iota;&nu;&omicron;&sigmaf; &Delta;&epsilon;&lambda;&eta;&sigma;&tau;&alpha;&acute;&upsilon;&rho;&omicron;&upsilon;'>")
        print("<title>Shen & Tucker Multihop Bypass</title>")
        print("<style>")
                
        print(".error {")
        print("color: white;")
        print("background-color: coral;")
        print("}")

        print("div {")
        print("text-align: center; ")
        print("padding: 3px; ")
        print("margin: 0px; ")
        print("background-color: white;")
        print("}")
        
        print("table { ")
        print("border-collapse: collapse;")
        print("}")

        print("table.data { ")
        print("border: 2px solid #000099; ")
        print("background: linear-gradient(140deg, #e8fab1, #b1fae7); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, sans-serif;")
        print("}")

        print("th, td { ")
        print("border: 1px solid #331122; ")
        print("}")
        
        print("table.table1c { ")
        print("border: 1px solid #000099; ")
        print("background: linear-gradient(140deg, #ddffcc, #44ff88); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")

        print("table.dictionary { ")
        print("border: 1px solid #000099; ")
        print("background: linear-gradient(240deg, #ffffcc, #0088ff); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")
        
        print("table.tablePow { ")
        print("border: 1px solid #009900; ")
        print("background: linear-gradient(160deg, #D9E8F5, #6DC0C9); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")

        print("table.tableLat { ")
        print("border: 1px solid #990000; ")
        print("background: linear-gradient(120deg, #ffffcc, #ff4433); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")

        print("table.tableLat0 { ")
        print("border: 1px solid #990000; ")
        print("background: linear-gradient(180deg, #ffcc00, #ff4433); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")

        print("table.tableLat1 { ")
        print("border: 1px solid #990000; ")
        print("background: linear-gradient(240deg, #00ffcc, #ff4433); ")
        print("text-align: left;")
        print("margin-left: auto; ")
        print("margin-right: auto; ")
        print("margin-bottom: 10px;")
        print("font-family: monospace, Arial, Helvetica, sans-serif;")
        print("}")


        print("table.data td {")
        print("width: 200px;")
        print("inline-size: 200px;")
        print("overflow-wrap: break-word;")
        print("font-size: 0.8em;")
        print("text-align: left;")
        print("border: 1px solid #000099; ")
        print("padding: 3px 3px 3px 3px;")
        print("inline-size: 150px;")
        print("} ")
        
        print("table.data th { ")
        print("inline-size: 100px;")
        print("overflow-wrap: break-word;")
        print("font-size: 0.8em;")
        print("text-align: center;")
        print("padding-top: 3px; ")
        print("padding-bottom: 3px; ")
        print("}  ")
        
        print("table.data td.actions { ")
        print("width: 500px;")
        print("inline-size: 500px;")
        print("font-size:0.8em;")
        print("overflow-wrap: break-word;")
        print("} ")
        
        print("</style> ")
        print("</head>  ")
        print("<body>   ")
        print("<h1 style='text-align:center'>"+title+" Simulation</h1>")
        print(f"<h2><em>Shen & Tucker's Routing and Wavelength Assignment algorithm for traffic requests on a {('single queue' if lenQs==1 else 'couple of queues'):s}, having requested capacity randomised following a Poisson process.</em></h2>")
        print("<h3 style='text-align:center'>Implementation by <em>Konstantinos Delistavrou</em> &copy; 2021-2024</h3><hr>")
    #EOP

def mathPowerFormula():
    s = ""
    s+="<math display='block'>"
    s+="    <mrow>"
    s+="        <munder>"
    s+="            <mo>&sum;</mo>"
    s+="            <mrow>"
    s+="                <mi>i</mi>"
    s+="                <mo>&isin;</mo>"
    s+="                <mi>N</mi>"
    s+="            </mrow>"
    s+="        </munder>"
    s+="        <mrow>"
    s+="            <msub>"
    s+="                <mrow>"
    s+="                    <mi>E</mi>"
    s+="                </mrow>"
    s+="                <mrow>"
    s+="                    <mi>r</mi>"
    s+="                </mrow>"
    s+="            </msub>"
    s+="            <mo>&middot;</mo>"
    s+="            <mo>(</mo>"
    s+="                <mrow>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>&Delta;</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>i</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                    <mo>+</mo>"
    s+="                    <mrow>"
    s+="                        <munder>"
    s+="                            <mo>&sum;</mo>"
    s+="                            <mrow>"
    s+="                                <mi>i</mi>"
    s+="                                <mo>&isin;</mo>"
    s+="                                <mi>N</mi>"
    s+="                                <mo>:</mo>"
    s+="                                <mi>i</mi>"
    s+="                                <mo>&NotEqual;</mo>"
    s+="                                <mi>j</mi>"
    s+="                            </mrow>"
    s+="                        </munder>"
    s+="                        <mrow>"
    s+="                            <msub>"
    s+="                                <mrow>"
    s+="                                    <mi>C</mi>"
    s+="                                </mrow>"
    s+="                                <mrow>"
    s+="                                    <mi>i</mi>"
    s+="                                    <mi>j</mi>"
    s+="                                </mrow>"
    s+="                            </msub>"
    s+="                        </mrow>"
    s+="                    </mrow>"
    s+="                </mrow>"
    s+="            <mo>)</mo>"
    s+="        </mrow>"
    s+="    </mrow>"
    s+="    <mo>+</mo>"
    s+="    <mrow>"
    s+="        <munder>"
    s+="            <mo>&sum;</mo>"
    s+="            <mrow>"
    s+="                <mi>m</mi>"
    s+="                <mo>&isin;</mo>"
    s+="                <mi>N</mi>"
    s+="            </mrow>"
    s+="        </munder>"
    s+="        <mrow><mrow>"
    s+="            <munder>"
    s+="                <mo>&sum;</mo>"
    s+="                <mrow>"
    s+="                    <mi>n</mi>"
    s+="                    <mo>&isin;</mo>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>N</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>m</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </munder>"
    s+="            <mrow>"
    s+="                <msub>"
    s+="                    <mrow>"
    s+="                        <mi>E</mi>"
    s+="                    </mrow>"
    s+="                    <mrow>"
    s+="                        <mi>t</mi>"
    s+="                    </mrow>"
    s+="                </msub>"
    s+="            </mrow>"
    s+="        </mrow>"
    s+="        <mo>&middot;</mo>"
    s+="        <msub>"
    s+="            <mrow>"
    s+="                <mi>w</mi>"
    s+="            </mrow>"
    s+="            <mrow>"
    s+="                <mi>m</mi>"
    s+="                <mi>n</mi>"
    s+="            </mrow>"
    s+="        </msub>"
    s+="    </mrow>"
    s+="</mrow>"
    s+="<mo>+</mo>"
    s+="<mrow>"
    s+="    <munder>"
    s+="        <mo>&sum;</mo>"
    s+="        <mrow>"
    s+="            <mi>m</mi>"
    s+="            <mo>&isin;</mo>"
    s+="            <mi>N</mi>"
    s+="        </mrow>"
    s+="    </munder>"
    s+="    <mrow>"
    s+="        <mrow>"
    s+="            <munder>"
    s+="                <mo>&sum;</mo>"
    s+="                <mrow>"
    s+="                    <mi>n</mi>"
    s+="                    <mo>&isin;</mo>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>N</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>m</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </munder>"
    s+="            <mrow>"
    s+="                <msub>"
    s+="                    <mrow>"
    s+="                        <mi>E</mi>"
    s+="                    </mrow>"
    s+="                    <mrow>"
    s+="                        <mi>e</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </mrow>"
    s+="            <mo>&middot;</mo>"
    s+="            <msub>"
    s+="                <mrow>"
    s+="                    <mi>A</mi>"
    s+="                </mrow>"
    s+="                <mrow>"
    s+="                    <mi>m</mi>"
    s+="                    <mi>n</mi>"
    s+="                </mrow>"
    s+="            </msub>"
    s+="        </mrow>"
    s+="    </mrow>"
    s+="    <mo>&middot;</mo>"
    s+="    <msub>"
    s+="        <mrow>"
    s+="            <mi>f</mi>"
    s+="        </mrow>"
    s+="        <mrow>"
    s+="            <mi>m</mi>"
    s+="            <mi>n</mi>"
    s+="        </mrow>"
    s+="    </msub>"
    s+="</math>"
    return s

def mathPowerFormulaIP():
    s = ""
    s+="<math>"
    s+="    <mrow>"
    s+="        <munder>"
    s+="            <mo>&sum;</mo>"
    s+="            <mrow>"
    s+="                <mi>i</mi>"
    s+="                <mo>&isin;</mo>"
    s+="                <mi>N</mi>"
    s+="            </mrow>"
    s+="        </munder>"
    s+="        <mrow>"
    s+="            <msub>"
    s+="                <mrow>"
    s+="                    <mi>E</mi>"
    s+="                </mrow>"
    s+="                <mrow>"
    s+="                    <mi>r</mi>"
    s+="                </mrow>"
    s+="            </msub>"
    s+="            <mo>&middot;</mo>"
    s+="            <mo>(</mo>"
    s+="                <mrow>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>&Delta;</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>i</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                    <mo>+</mo>"
    s+="                    <mrow>"
    s+="                        <munder>"
    s+="                            <mo>&sum;</mo>"
    s+="                            <mrow>"
    s+="                                <mi>i</mi>"
    s+="                                <mo>&isin;</mo>"
    s+="                                <mi>N</mi>"
    s+="                                <mo>:</mo>"
    s+="                                <mi>i</mi>"
    s+="                                <mo>&NotEqual;</mo>"
    s+="                                <mi>j</mi>"
    s+="                            </mrow>"
    s+="                        </munder>"
    s+="                        <mrow>"
    s+="                            <msub>"
    s+="                                <mrow>"
    s+="                                    <mi>C</mi>"
    s+="                                </mrow>"
    s+="                                <mrow>"
    s+="                                    <mi>i</mi>"
    s+="                                    <mi>j</mi>"
    s+="                                </mrow>"
    s+="                            </msub>"
    s+="                        </mrow>"
    s+="                    </mrow>"
    s+="                </mrow>"
    s+="            <mo>)</mo>"
    s+="        </mrow>"
    s+="    </mrow>"
    s+="</math>"
    return s

def mathPowerFormulaTransponders():
    s = ""
    s+="<math>"
    s+="    <mrow>"
    s+="        <munder>"
    s+="            <mo>&sum;</mo>"
    s+="            <mrow>"
    s+="                <mi>m</mi>"
    s+="                <mo>&isin;</mo>"
    s+="                <mi>N</mi>"
    s+="            </mrow>"
    s+="        </munder>"
    s+="        <mrow><mrow>"
    s+="            <munder>"
    s+="                <mo>&sum;</mo>"
    s+="                <mrow>"
    s+="                    <mi>n</mi>"
    s+="                    <mo>&isin;</mo>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>N</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>m</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </munder>"
    s+="            <mrow>"
    s+="                <msub>"
    s+="                    <mrow>"
    s+="                        <mi>E</mi>"
    s+="                    </mrow>"
    s+="                    <mrow>"
    s+="                        <mi>t</mi>"
    s+="                    </mrow>"
    s+="                </msub>"
    s+="            </mrow>"
    s+="        </mrow>"
    s+="        <mo>&middot;</mo>"
    s+="        <msub>"
    s+="            <mrow>"
    s+="                <mi>w</mi>"
    s+="            </mrow>"
    s+="            <mrow>"
    s+="                <mi>m</mi>"
    s+="                <mi>n</mi>"
    s+="            </mrow>"
    s+="        </msub>"
    s+="    </mrow>"
    s+="</mrow>"
    s+="</math>"
    return s

def mathPowerFormulaEDFA():
    s = ""
    s+="<math>"
    s+="<mrow>"
    s+="    <munder>"
    s+="        <mo>&sum;</mo>"
    s+="        <mrow>"
    s+="            <mi>m</mi>"
    s+="            <mo>&isin;</mo>"
    s+="            <mi>N</mi>"
    s+="        </mrow>"
    s+="    </munder>"
    s+="    <mrow>"
    s+="        <mrow>"
    s+="            <munder>"
    s+="                <mo>&sum;</mo>"
    s+="                <mrow>"
    s+="                    <mi>n</mi>"
    s+="                    <mo>&isin;</mo>"
    s+="                    <msub>"
    s+="                        <mrow>"
    s+="                            <mi>N</mi>"
    s+="                        </mrow>"
    s+="                        <mrow>"
    s+="                            <mi>m</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </munder>"
    s+="            <mrow>"
    s+="                <msub>"
    s+="                    <mrow>"
    s+="                        <mi>E</mi>"
    s+="                    </mrow>"
    s+="                    <mrow>"
    s+="                        <mi>e</mi>"
    s+="                        </mrow>"
    s+="                    </msub>"
    s+="                </mrow>"
    s+="            </mrow>"
    s+="            <mo>&middot;</mo>"
    s+="            <msub>"
    s+="                <mrow>"
    s+="                    <mi>A</mi>"
    s+="                </mrow>"
    s+="                <mrow>"
    s+="                    <mi>m</mi>"
    s+="                    <mi>n</mi>"
    s+="                </mrow>"
    s+="            </msub>"
    s+="        </mrow>"
    s+="    </mrow>"
    s+="    <mo>&middot;</mo>"
    s+="    <msub>"
    s+="        <mrow>"
    s+="            <mi>f</mi>"
    s+="        </mrow>"
    s+="        <mrow>"
    s+="            <mi>m</mi>"
    s+="            <mi>n</mi>"
    s+="        </mrow>"
    s+="    </msub>"
    s+="</math>"
    return s

def updateTotals(struct, key, val):
    if key in struct:  #add to total wavelengths
        tmp = struct.get(key)
        tmp += val
    else:
        tmp = val
    roundatdecimals(tmp,3)
    struct.update({key: tmp})

'''
def routeAllTrafficRequestsOverVirtualTopologyMultihopBypass(nodes, data, vt, vtl, vtfreecaps, maxGbpsPerWavelength, VTfinal, R, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection):
    #this function's parameter "data" refers to the traffic requests
    #this version is not using Queues!
    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    
    n = len(data)
    count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<table class='data'>")
        print("<tr><th colspan='7'>Routing traffic requests over the Virtual Topology <br>(a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes update</th><th>Current Virtual Topology</th></tr>")
        print ("<tr><th>Request</th><th>From</th><th>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th></tr>")
    #EOP

    # Traverse through all array elements
    for i in range(n):   #for each request
        
        remain = data[i][2]
    
        apo = nodes[data[i][0]]
        pros = nodes[data[i][1]]
        req=i+1

        graph_filename="VTpostReq"+str(req)+".html"

        while (remain>0): #while there are remaining Gb of the request to be routed
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("<td style='width: 50px; inline-size: 50px;'>Processing request ", req, "</td><td style='width: 50px; inline-size: 50px;'>from", apo, "("+str(data[i][0])+")", "</td><td style='width: 50px; inline-size: 50px;'>to", pros,"("+str(data[i][1])+")", "</td>")
                print ("<td>Remain",remain, "Gbps to be routed.</td>")
            #EOP

            graph_add_node(gr,data[i][0],apo,Ncolours)
            graph_add_node(gr,data[i][1],pros,Ncolours)
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("<td class='actions' style='font-size:0.5em'>")
            #EOP
            
            if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
                #EOP
                
                CapForTheLogicalLink=maxGbpsPerWavelength
                
                if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, req, data[i][0], data[i][1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTfinal, R, gr, VLIDs, dbConnection) == 0):
                    #added new link to route 40G successfully
                    remain = remain - CapForTheLogicalLink
                    #remain=numpy.round(remain, decimals=3, out=None)
                    remain = roundatdecimals(remain, 3)

                    # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                    TotalLightpaths[0] +=1

                    # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                    # if you want to add, just uncomment next line
                    # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, req, data[i][0], data[i][1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTfinal, R, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection) == 0):   #try to route it over existing paths of the virtual topology
                
                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    #remain=numpy.round(remain, decimals=3, out=None)

                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, req, data[i][0], data[i][1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTfinal, R, gr, VLIDs, dbConnection) == 0):
                        #added new link to route required capacity successfully
                        remain = remain - CapForTheLogicalLink
                        remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] +=1
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td>Free capacities list vTfreeCapacities vtFrCap=",vtfreecaps,"</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p>")
                print("</td></tr>")
                #print("<li>Links list vTL =",vtl)
                #print("<li>Links used for each request (s,d,type,capacity) R =",R)
            #EOP

        #SOP
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #after all requests show total graph
        print("</table>")
        #grFile = os.path.join(graph_path, graph_filename)
        #print("<div style='margin-left:auto;margin-right:auto;'>")
        #print("<br><br><a href='"+protocol+grFile+"' target='_blank'>"+graph_filename+"</a></div>")
        #print("<iframe src='"+protocol+grFile+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe>")
    #EOP
'''

def nsec2msec(t):
    return roundatdecimals( (t * 1e-6), 3 )

def copyDictionary(dict):
    cpdict = {}
    for key, value in dict.items():
        cpdict[key] = value
    return cpdict


def compare_lists(listA, listB):

    lAsort = sorted(listA)
    lBsort = sorted(listB)
    
    # Compare sorted lists
    return lAsort == lBsort


def printDifferencesOfDictionary2comparedtoDictionary1(dict1, dict2):
    print("<li>Dict1",dict1)
    print("<li>Dict2",dict2)
    
    print ("<table class='dictionary'>")
    print ("<tr><td>Justification</td>")
    print ("<td>Key</td>")
    print ("<td>Value</td>")
    for key2 in dict2:
        if key2 not in dict1:
            print ("<tr><td>New entry</td>")
            print ("<td>",key2,"</td>")
            print ("<td>",dict2[key2],"</td></tr>")
        elif key2 in dict1 and not compare_lists(dict1[key2], dict2[key2]):
                print ("<tr><td>Updated value</td>")
                print ("<td>",key2,"</td>")
                print ("<td>",dict2[key2],"</td></tr>")
        else:
            print ("<tr><td colspan='3'>Error! Not a new item, nor updated value?</td></tr>")
    for key1 in dict1:
            if key1 not in dict2:
                print ("<tr><td colspan='3'>Error! Removed item from the previous version of the virtual links dictionary?</td></tr>")

    print ("</table>")

def routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    
    startingStep = startingStep -1

    #this version uses Queues!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""

    graph_filename = ""
           
    #EOP
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    ###19-9-2024 create graph in the calling program and pass as parameter to the routing function, since the traffic requests might be served by more than one routing functions depending on the scheduling strategy
    ###s="Virtual topology graph after processing request "
    ###gr = graph_new(s, True)
    #EOP

    #n = len(data)
    n = len(Queue)
    #n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n #+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the single queue over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    #i0=0
    #i1=0
    currentrequest = 0
    step = 1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
    #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = QueueID

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        RequestTime = nsec2msec(startTReq - startRoutingOverVT)
        
        Qtime = RequestTime % 100.0
        
        '''
        if Qtime >= 0.0 and Qtime < 75.0:
            CurrentQueue="0"
        elif Qtime >= 75.0:
            CurrentQueue="1"
        '''

        if CurrentQueue==QueueID and currentrequest<n:
            treq = Queue[currentrequest] # treq = traffic request
            que=QueueID
            fromQueue=QueueID
            req=currentrequest
            currentrequest = currentrequest + 1
        
        '''
        elif CurrentQueue=="0" and i0>=n0:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1
        elif CurrentQueue=="1" and i1<n1:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1
        elif CurrentQueue=="1" and i1>=n1:
            treq = q0[i0]
            que=0
            fromQueue="0"
            i0 = i0 + 1
            req=i0
        else:
            print("<div>Error on Queue selection")
            exit(1)
        '''

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(startingStep+step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP
        
        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {startingStep+step:0d}</td><td>Processing queue {fromQueue:0d}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4d} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")
            
                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

            ##keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            #prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            #prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            #prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            #prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
                #EOP
                
                CapForTheLogicalLink = maxGbpsPerWavelength
                  
                if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                    
                    #if adding succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #added new link to route 40G successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                    TotalLightpaths[0] +=1

                    # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                    # if you want to add, just uncomment next line
                    # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    ##keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    #prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                        
                        #if adding succeded
                        RoutingOfRequestedTrafficStep += 1
                        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                        #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                # A not using vtfreecaps anymore 
                # print("<li>Free capacities list vTfreeCapacities",vtfreecaps)
                # printFreeCapacitiesAsTable(vtfreecaps)
                
                # B print latest addition, not new version of VirtualLinkIDs
                
                ###print("<li>Update of the Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkIDs, VirtualLinkIDs)
                
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # not printing new version printVLids(VirtualLinkIDs)

                ###print("<li>Update of the Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                                
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTReqs, VirtualLinkTReqs)

                ###print("<li>Update of the Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                #printVLTotals(VirtualLinkTotals)
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTotals, VirtualLinkTotals)

                ###print("<li>Update of the Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevReqRouteInfo, ReqRouteInfo)

                # C print all outcomes (dictionaries) on each step
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # printVLids(VirtualLinkIDs)

                # print("<li>Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                # printVLTReqs(VirtualLinkTReqs)
                
                # print("<li>Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                # printVLTotals(VirtualLinkTotals)

                # print("<li>Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                # printRequestRoutingInfoAsTable(ReqRouteInfo)

                print(GlobalStringOutcomes)

                GlobalStringOutcomes = ""

                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                #print("</td><td>",roundatdecimals((start_serve_treq_processtime * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serve_treq_processtime - start_serving_all_treqs_processtime) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess - start_time_of_all_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                print("<td>")
                #print("Since start serving all TReqs, For current TReq<br>")
                #print("Since start serving all TReqs, For current TReq<br>")
                print(f"Time of processing all requests {RequestTime:.3f},")
                print(f"Time of current queue's turn {Qtime:.3f}")
                #print(f"{nsec2msec(time_for_serving_current_Treq):.3f}")
                print("</td>")
                print("</tr>")
                #print("<li>Links list vTL =",vtl)
                #print("<li>Links used for each request (s,d,type,capacity) R =",R)
            #EOP

            #RoutingOfRequestedTrafficStep += 1

        #SOP    
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1

    # signaling process to stop
    #flag.set()  # Signal the worker to stop
    #process.join()
    #print("Process has stopped.")

    # terminating process
    #print(f"Sending SIGTERM to child process with PID: {process.pid}")
    ###os.kill(process.pid, signal.SIGTERM)
    
    #wait process to join the main program when it stops normally
    #process.join()
    #print("Child process terminated.")

    #SOP
    if (GlobalPrintOutEnabled==True) :
        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")
        #grFile = os.path.join(graph_path, graph_filename)
        #print("<div style='margin-left:auto;margin-right:auto;'>")
        #print("<br><br><a href='"+protocol+grFile+"' target='_blank'>"+graph_filename+"</a></div>")
        #print("<iframe src='"+protocol+grFile+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report
    #EOP

    return startingStep+step



def routeAllTrafficRequestsOfTwoQueuesOverVirtualTopologyMultihopBypass_Q0_75_Q1_25(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP
    
    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "0"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
                
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        Qtime = CurrentRequestTime % 100.0
        #if Qtime >= 0.0 and Qtime < 75.0:
        if Qtime < 75.0:
            CurrentQueue="0"
        #elif Qtime >= 75.0:
        else:
            CurrentQueue="1"
            Qtime -= 75.0 # to start the queue time from 0.0
        
        if CurrentQueue=="0" and i0<n0:
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            i0 = i0 + 1
            req=i0-1
        elif CurrentQueue=="0" and i0>=n0:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1-1
        elif CurrentQueue=="1" and i1<n1:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1-1
        elif CurrentQueue=="1" and i1>=n1:
            treq = q0[i0]
            que=0
            fromQueue="0"
            i0 = i0 + 1
            req=i0-1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP

        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d}" + "\n")
                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")
            
                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.5em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
                #EOP
                
                CapForTheLogicalLink = maxGbpsPerWavelength
                  
                if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                    
                    #if adding succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #added new link to route 40G successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                    TotalLightpaths[0] +=1

                    # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                    # if you want to add, just uncomment next line
                    # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):

                        #if adding succeded
                        RoutingOfRequestedTrafficStep += 1
                        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                        #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                # A not using vtfreecaps anymore 
                # print("<li>Free capacities list vTfreeCapacities",vtfreecaps)
                # printFreeCapacitiesAsTable(vtfreecaps)
                
                # B print latest addition, not new version of VirtualLinkIDs
                
                ###print("<li>Update of the Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkIDs, VirtualLinkIDs)
                
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # not printing new version printVLids(VirtualLinkIDs)

                ###print("<li>Update of the Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                                
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTReqs, VirtualLinkTReqs)

                ###print("<li>Update of the Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                #printVLTotals(VirtualLinkTotals)
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTotals, VirtualLinkTotals)

                ###print("<li>Update of the Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevReqRouteInfo, ReqRouteInfo)

                # C print all outcomes (dictionaries) on each step
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # printVLids(VirtualLinkIDs)

                # print("<li>Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                # printVLTReqs(VirtualLinkTReqs)
                
                # print("<li>Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                # printVLTotals(VirtualLinkTotals)

                # print("<li>Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                # printRequestRoutingInfoAsTable(ReqRouteInfo)

                print(GlobalStringOutcomes)

                GlobalStringOutcomes = ""

                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                #print("</td><td>",roundatdecimals((start_serve_treq_processtime * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serve_treq_processtime - start_serving_all_treqs_processtime) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess - start_time_of_all_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                print("<td>")
                #print("Since start serving all TReqs, For current TReq<br>")
                #print("Since start serving all TReqs, For current TReq<br>")

                print(f"All Requests processing time {CurrentRequestTime:.3f},")
                print(f"Current Queue processing time {Qtime:.3f}")
                #print(f"{nsec2msec(time_for_serving_current_Treq):.3f}")
                print("</td>")
                print("</tr>")
                #print("<li>Links list vTL =",vtl)
                #print("<li>Links used for each request (s,d,type,capacity) R =",R)

            #EOP

        '''
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        Qtime = CurrentRequestTime % 100.0
        #if Qtime >= 0.0 and Qtime < 75.0:
        if Qtime < 75.0:
            CurrentQueue="0"
        #elif Qtime >= 75.0:
        else:
            CurrentQueue="1"
            Qtime -= 75.0 # to start the queue time from 0.0
        '''

        #SOP    
        if (GlobalPrintOutEnabled==True) :

            #after serving current traffic request
            f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Time processing all TReqs {CurrentRequestTime:12.3f} ~ Queue time {Qtime:9.3f}\n")
        
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1

    # signaling process to stop
    #flag.set()  # Signal the worker to stop
    #process.join()
    #print("Process has stopped.")

    # terminating process
    #print(f"Sending SIGTERM to child process with PID: {process.pid}")
    ###os.kill(process.pid, signal.SIGTERM)
    
    #wait process to join the main program when it stops normally
    #process.join()
    #print("Child process terminated.")

    #SOP
    if (GlobalPrintOutEnabled==True) :

        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")
        #grFile = os.path.join(graph_path, graph_filename)
        #print("<div style='margin-left:auto;margin-right:auto;'>")
        #print("<br><br><a href='"+protocol+grFile+"' target='_blank'>"+graph_filename+"</a></div>")
        #print("<iframe src='"+protocol+grFile+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report

    #EOP



def routeAllTrafficRequestsOfTwoQueuesOverVirtualTopologyMultihopBypass_Q1nextQ0(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP
    
    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "1"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        #Qtime = CurrentRequestTime % 100.0
        Qtime = CurrentRequestTime

        if i1<n1:
            CurrentQueue="1"
        else:
            CurrentQueue="0"
        
        if CurrentQueue=="0":
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            req=i0
            i0 = i0 + 1
        elif CurrentQueue=="1":
            treq = q1[i1]
            que=1
            fromQueue="1"
            req=i1
            i1 = i1 + 1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP

        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d}" + "\n")
                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")
            
                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.5em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
                #EOP
                
                CapForTheLogicalLink = maxGbpsPerWavelength
                  
                if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                    
                    #if adding succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #added new link to route 40G successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                    TotalLightpaths[0] +=1

                    # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                    # if you want to add, just uncomment next line
                    # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):

                        #if adding succeded
                        RoutingOfRequestedTrafficStep += 1
                        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                        #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                # A not using vtfreecaps anymore 
                # print("<li>Free capacities list vTfreeCapacities",vtfreecaps)
                # printFreeCapacitiesAsTable(vtfreecaps)
                
                # B print latest addition, not new version of VirtualLinkIDs
                
                ###print("<li>Update of the Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkIDs, VirtualLinkIDs)
                
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # not printing new version printVLids(VirtualLinkIDs)

                ###print("<li>Update of the Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                                
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTReqs, VirtualLinkTReqs)

                ###print("<li>Update of the Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                #printVLTotals(VirtualLinkTotals)
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTotals, VirtualLinkTotals)

                ###print("<li>Update of the Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevReqRouteInfo, ReqRouteInfo)

                # C print all outcomes (dictionaries) on each step
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # printVLids(VirtualLinkIDs)

                # print("<li>Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                # printVLTReqs(VirtualLinkTReqs)
                
                # print("<li>Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                # printVLTotals(VirtualLinkTotals)

                # print("<li>Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                # printRequestRoutingInfoAsTable(ReqRouteInfo)

                print(GlobalStringOutcomes)

                GlobalStringOutcomes = ""

                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                #print("</td><td>",roundatdecimals((start_serve_treq_processtime * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serve_treq_processtime - start_serving_all_treqs_processtime) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess - start_time_of_all_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                print("<td>")
                #print("Since start serving all TReqs, For current TReq<br>")
                #print("Since start serving all TReqs, For current TReq<br>")

                print(f"All Requests processing time {CurrentRequestTime:.3f},")
                print(f"Current Queue processing time {Qtime:.3f}")
                #print(f"{nsec2msec(time_for_serving_current_Treq):.3f}")
                print("</td>")
                print("</tr>")
                #print("<li>Links list vTL =",vtl)
                #print("<li>Links used for each request (s,d,type,capacity) R =",R)

            #EOP

        '''
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        Qtime = CurrentRequestTime % 100.0
        #if Qtime >= 0.0 and Qtime < 75.0:
        if Qtime < 75.0:
            CurrentQueue="0"
        #elif Qtime >= 75.0:
        else:
            CurrentQueue="1"
            Qtime -= 75.0 # to start the queue time from 0.0
        '''

        #SOP    
        if (GlobalPrintOutEnabled==True) :

            #after serving current traffic request
            f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Time processing all TReqs {CurrentRequestTime:12.3f} ~ Queue time {Qtime:9.3f}\n")
        
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1

    # signaling process to stop
    #flag.set()  # Signal the worker to stop
    #process.join()
    #print("Process has stopped.")

    # terminating process
    #print(f"Sending SIGTERM to child process with PID: {process.pid}")
    ###os.kill(process.pid, signal.SIGTERM)
    
    #wait process to join the main program when it stops normally
    #process.join()
    #print("Child process terminated.")

    #SOP
    if (GlobalPrintOutEnabled==True) :

        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")
        #grFile = os.path.join(graph_path, graph_filename)
        #print("<div style='margin-left:auto;margin-right:auto;'>")
        #print("<br><br><a href='"+protocol+grFile+"' target='_blank'>"+graph_filename+"</a></div>")
        #print("<iframe src='"+protocol+grFile+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report

    #EOP






def routeAllTrafficRequestsOfTwoQueuesOverVirtualTopologyMultihopBypass_Q0nextQ1(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP
    
    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "0"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        #Qtime = CurrentRequestTime % 100.0
        Qtime = CurrentRequestTime

        if i0<n0:
            CurrentQueue="0"
        else:
            CurrentQueue="1"
        
        if CurrentQueue=="0":
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            req=i0
            i0 = i0 + 1
        elif CurrentQueue=="1":
            treq = q1[i1]
            que=1
            fromQueue="1"
            req=i1
            i1 = i1 + 1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP

        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d}" + "\n")
                #f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")
            
                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.5em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
                #EOP
                
                CapForTheLogicalLink = maxGbpsPerWavelength
                  
                if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                    
                    #if adding succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #added new link to route 40G successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                    TotalLightpaths[0] +=1

                    # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                    # if you want to add, just uncomment next line
                    # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):

                        #if adding succeded
                        RoutingOfRequestedTrafficStep += 1
                        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                        #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                # A not using vtfreecaps anymore 
                # print("<li>Free capacities list vTfreeCapacities",vtfreecaps)
                # printFreeCapacitiesAsTable(vtfreecaps)
                
                # B print latest addition, not new version of VirtualLinkIDs
                
                ###print("<li>Update of the Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkIDs, VirtualLinkIDs)
                
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # not printing new version printVLids(VirtualLinkIDs)

                ###print("<li>Update of the Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                                
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTReqs, VirtualLinkTReqs)

                ###print("<li>Update of the Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                #printVLTotals(VirtualLinkTotals)
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevVirtualLinkTotals, VirtualLinkTotals)

                ###print("<li>Update of the Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                ###printDifferencesOfDictionary2comparedtoDictionary1(prevReqRouteInfo, ReqRouteInfo)

                # C print all outcomes (dictionaries) on each step
                # print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
                # printVLids(VirtualLinkIDs)

                # print("<li>Traffic Requests for each Virtual Link = {(s,d,n):[(que,req,cap,type),...],...}")
                # printVLTReqs(VirtualLinkTReqs)
                
                # print("<li>Virtual Link Totals = {(s,d,n):[caputil, capfree, num_of_TReqs],...}")
                # printVLTotals(VirtualLinkTotals)

                # print("<li>Virtual Links per Request R = {(queue, request number): [(virtual link (s,d,n), type, capacity utilsed), ...], ...}")
                # printRequestRoutingInfoAsTable(ReqRouteInfo)

                print(GlobalStringOutcomes)

                GlobalStringOutcomes = ""

                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                #print("</td><td>",roundatdecimals((start_serve_treq_processtime * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serve_treq_processtime - start_serving_all_treqs_processtime) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                #print("</td><td>",roundatdecimals(((start_serving_current_treq_time_at_the_subprocess - start_time_of_all_at_the_subprocess) * 1e-6), 3),"msec</td>") # nsec to msec
                print("<td>")
                #print("Since start serving all TReqs, For current TReq<br>")
                #print("Since start serving all TReqs, For current TReq<br>")

                print(f"All Requests processing time {CurrentRequestTime:.3f},")
                print(f"Current Queue processing time {Qtime:.3f}")
                #print(f"{nsec2msec(time_for_serving_current_Treq):.3f}")
                print("</td>")
                print("</tr>")
                #print("<li>Links list vTL =",vtl)
                #print("<li>Links used for each request (s,d,type,capacity) R =",R)

            #EOP

        '''
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        Qtime = CurrentRequestTime % 100.0
        #if Qtime >= 0.0 and Qtime < 75.0:
        if Qtime < 75.0:
            CurrentQueue="0"
        #elif Qtime >= 75.0:
        else:
            CurrentQueue="1"
            Qtime -= 75.0 # to start the queue time from 0.0
        '''

        #SOP    
        if (GlobalPrintOutEnabled==True) :

            #after serving current traffic request
            f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Time processing all TReqs {CurrentRequestTime:12.3f} ~ Queue time {Qtime:9.3f}\n")
        
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1

    # signaling process to stop
    #flag.set()  # Signal the worker to stop
    #process.join()
    #print("Process has stopped.")

    # terminating process
    #print(f"Sending SIGTERM to child process with PID: {process.pid}")
    ###os.kill(process.pid, signal.SIGTERM)
    
    #wait process to join the main program when it stops normally
    #process.join()
    #print("Child process terminated.")

    #SOP
    if (GlobalPrintOutEnabled==True) :

        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")
        #grFile = os.path.join(graph_path, graph_filename)
        #print("<div style='margin-left:auto;margin-right:auto;'>")
        #print("<br><br><a href='"+protocol+grFile+"' target='_blank'>"+graph_filename+"</a></div>")
        #print("<iframe src='"+protocol+grFile+"' style='border:2px solid red;width:500px;height:500px;' title='"+graph_filename+"'></iframe>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report

    #EOP








def routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, queID, requestID, Ni,      Nj,      vt, vtl, vtfrcap,    requiredcap,          maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep): #, costs):
   #routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que,   req,       treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
    # this version uses queues
    # this version uses the new dictionary VirtualLinkTotals

    global GlobalPrintOutEnabled

    # Virtual topology's (VT) capacity logistics
    """
    vT={}   # VT = {node:[neighbour, ...], ...}
    vTL=[]   # VTL = [(tuple of source, destination of virtual link), ...]
    vTfreeCap={}   #VTFreeCap = {(tuple of source, destination of virtual link):[free capacity], ...}
    VTfinal={} # virtual topology for routing virtual links over physical topology
    """

    remaincap = requiredcap

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Looking for", requiredcap,"Gbps, to route the capacity requirement from", nodes[Ni], "to", nodes[Nj])
    #EOP

    #if it is the first request, thus VT is empty, then add nodes and the virtual (lightpath) link
    if (vt=={}):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<li>The virtual topology is empty, hence adding a new virtual link.")
        #EOP

        #<<< 9-9-2024 added 
        routOfReqTrffcStpVLseqNum = 0
        #>>>
        
        if (addNewVirtualLinkToTheVirtualTopology(nodes, queID, requestID, Ni, Nj, vt, vtl, vtfrcap, requiredcap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum) == 0):
            #added new link to route 40G successfully
            remaincap = roundatdecimals( (remaincap - requiredcap), 3)
            #remaincap=numpy.round(remaincap, decimals=3, out=None)
    else:
        #def find_shortest_path(graph, start, end, path=[])
        #print(find_shortest_path(vt,Ni,Nj))
        #print(find_path(vt,Ni,Nj))
       
        #minCostPath = getPathWithMinCost(vt,vtl,costs,Ni,Nj)

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<li>The virtual topology is NOT empty, hence looking for free capacity to groom.")
            print ("<li>Current virtual topology", vt,".")
            print ("<li>Required capacity", requiredcap,".")
        #EOP
        
        #2DO edo prepei na xrisimopoio ta nea dictionaries!
        #Done

        # εδώ αφήνω μόνο όσα virtual link έχουν ελεύθερο capacity
        #fcap = vtfrcap
        VLtotals = VirtualLinkTotals
        
        # Novelties
        # VTofVLwithonlyAdequateCapacity is a virtual topology where all virtual links have adequate free capacity to accomodate the capacity that is being seeked for possible traffic grooming.
        # VLofUniqueAdequateFreeCapacities is a list of the virtual links that have free capacity for the possible grooming and constitute the new virtual topology. Moreover, if more than one virtual links from the same source to the same destination exist and each has adequate free capacity to host the current traffic request, then the virtual link with the minimum adequate free capacity is selected to participate in this list for economy.
        VTofVLwithonlyAdequateCapacity, VLofUniqueAdequateFreeCapacities = create_a_VT_with_virtual_links_that_only_have_sufficient_free_capacity(VLtotals, requiredcap)

        #print ("<li>VTofVLwithonlyAdequateCapacity", VTofVLwithonlyAdequateCapacity)
        #print ("<li>VLofUniqueAdequateFreeCapacities", VLofUniqueAdequateFreeCapacities)

        #SOP
        if (GlobalPrintOutEnabled==True) :
            pass
            #print ("<li>Virtual topology containing only the virtual links with adequate free capacity. VT2 =", VTofVLwithonlyAdequateCapacity,".")
            #print("<li>Virtual Topology constituted only by Virtual Links that have adequate free capacity to accomodate the Traffic Request:",VTofVLwithonlyAdequateCapacity)
            #print("<li>List of Virtual Links that have adequate free capacity to accomodate the Traffic Request. If there are more than one Virtual Links per source, destination, then the one with the lowest adequate free capacity is included in this list:", VLofUniqueAdequateFreeCapacities)
            #there is only one virtual link per source destination (there is only one virtual link from each source to each destination)
            #print("<li>There is a unique virtual link with adequate free capacity for each source, destination pair:",uniqueSD(VLofUniqueAdequateFreeCapacities))
        #EOP

        # 2023 July: Since I have vt2 that every virtual link has adequate capacity to serve the traffic request capacity requirement.
        #            I am going to get just the shortest path and not all the paths to try them.
        # allpaths = find_all_paths(vt2,Ni,Nj)
        # shortestpath = find_shortest_path(vt2,Ni,Nj)
        
        #ftext = open("FindShortestPath"+nodes[Ni]+"-"+nodes[Nj]+".html", "w")
        #ftext.write("<ol>")
        #ftext.write("<li>Finding shortest path")
                
        ### allpaths = bfs_from_site(vt2,ftext,Ni,Nj)
        ### allpaths = find_shortest_path(vt2,ftext,Ni,Nj)
        if VTofVLwithonlyAdequateCapacity!={}: # if the virtual topology of virtual links that have free capacity is not empty, find the shortest path using BFS
            allpaths = find_shortest_path_using_bfs(VTofVLwithonlyAdequateCapacity,Ni,Nj)
        else:
        #    ftext.write("<li>Graph is empty</li>\n")
            allpaths = None
        #ftext.write("</ol>\n")
        #ftext.close()

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("</ol>")
            print ("<li>All paths", allpaths,".") #2DO > pairnei prota to pio syntomo?
                                                  #Done NAI  
        #EOP

        if allpaths==None:
            allpathslen = 0
        else:
            allpathslen = len(allpaths)

        requestrouted = False
        
        i=0   # counter to access all links of path 
        while (i < allpathslen) and (requestrouted == False):
        #for path in allpaths:   #for each path found      
            #path = allpaths[i]
            path = allpaths
            pathhasenoughfreecap = True # afou exw topologia opou ola ta link exoun enough free capacity

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>Processing path",path)
                print("<li>Path2links",path2links(path))
            #EOP
            
            ''' #edw elegxw to free capacity kathe virtual link alla den xreiazetai afou exw eikoniki topologia me kathe tis virtual link na exei free capacity
            for link in path2links(path):   #for each link of each path found
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Link", link)
                #EOP

                tlink = tuple(link)
                s, d = linkSrcDst(link)
                linkfreecap=getVirtualLinkFreeCapacity(vtl, vtfrcap,tlink)
                ###print("<li>Link",s,"&rarr;",d,"has free capacity",linkfreecap)
                
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Link",s,"&rarr;",d,"free capacity",linkfreecap)
                #EOP

                #check if free capacity in each and every one link of a path to accomodate request
                if ( not( requiredcap <= linkfreecap[0]) ):
                    pathhasenoughfreecap = False
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print ("<li>Not adequate free capacity on this link.") #2DO not using VT with free capacities properly!
                    #EOP
            '''

            #2DO edo prepei na kano tin allagi gia na ypologizei sosta ta synola traffic kathe virtual link
            #Done

            if (pathhasenoughfreecap == True):   #dromologise apo auto to path          # aka grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li><em>Traffic grooming</em>: Routing the required capacity via this path!")
                #EOP
                            
                # Count the number of used lightpaths (virtual links) 
                # One path in the virtual topology has many virtual links or lightpaths
                # Therefore, when there is grooming the number of reused lightpaths is incremented by the number of virtual links of the path in virtual topology
                
                LightpathReuses[0] = LightpathReuses[0] + len(path2links(path))

                for link in path2links(path):   #for each link of each path reused
                    if link not in ReUsedLightpaths:
                        ReUsedLightpaths.append(link)
                
                requestrouted = True
                remaincap = roundatdecimals( (remaincap - requiredcap), 3)
                #remaincap = numpy.round(remaincap, decimals=3, out=None)
                #print("<li>Remaining capacity for this request is",remaincap)

                #SOP
                if (GlobalPrintOutEnabled==True) :
                    #ypologise ti menei free gia kathe link tou path pou xrisimopoiithike telika
                    print("<li>Links of the path", path2links(path))
                #EOP
                
                #RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
                
                routOfReqTrffcStpVLseqNum = 0
                
                for link in path2links(path):   #for each link of each path found
                    #VTofVLwithonlyAdequateCapacity, VLofUniqueAdequateFreeCapacities
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<li>Subtract the utilised capacity from the Link's", link,"free capacity.")
                    #EOP
                    tlink = tuple(link)
                    s, d = linkSrcDst(link)
                    #linkfreecap=getVirtualLinkFreeCapacity(vtl, vtfrcap,tlink)
                    
                    #requiredcap
                    #vl = getVLfromSD(... ,s,d)
                    vls = find_keys_with_common_source_destination(VLofUniqueAdequateFreeCapacities, s, d)
                    #print("vls",vls)

                    if len(vls)>1:
                        error("More than a single virtual link for a single source destination found in the list of unique adequate free capacities virtual links",9)
                    
                    #Done now it updates the free capacity of the correct virtual link based on the virtual link id tuple (s,d,n) referred to also as (s,d,i)
                    vl = vls[0]
                    
                    updateVirtualLinkTReq(VirtualLinkTReqs,vl,queID,requestID,requiredcap,"Grm")
                    updateVirtualLinkTotals(VirtualLinkTReqs, VirtualLinkTotals, vl)

                    freecap = getVLfreecapacity(VirtualLinkTotals,vl)

                    graph_update_edge(gr,queID,requestID,s,d,freecap,maxGbpsPerWavelength,-1*requiredcap)

                    LinkFreeCap = updateVitualLinkFreeCapacity(vtfrcap, tlink, (-1*requiredcap))

                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(f"<li>Updated Virtual Link's ({vl[0]:d},{vl[1]:d},{vl[2]:d}) free capacity to {freecap:.3f}.")
                        updateVirtualLink2sqlite(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap)
                    #EOP
                    
                    appendPerRequestLinks(ReqRouteInfo,queID, requestID,vl,"Grm",requiredcap, routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum) #2 -> pou allou ginetai auto? Ginetai kai sto ###1 otan neo virtual link ("New") #append R with every link and capacity to fulfill the groomed request capacity
                    appendFinalVT(VTfinal,nodes,s,d,requiredcap,"Grm") 

                    #insert every link of the path to the routing table
                    virtlinkID = getVLIDwithfreecapacity(VLIDs,link[0], link[1])   # get the VLID for a virtual link from Ni to Nj that has free capacity.
                    
                    insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm", routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum)   # insert routing to sqlite table.
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<li>Insert routing of request over virtual links. QueueID:",queID,"RequestID:", requestID, "VirtualLinkID:", virtlinkID, "(src:", link[0], "dst:", link[1], "), Required Capacity:", requiredcap, "Free Capacity (on the graph):", freecap,"Free Capacity (on the corresponding array:)", LinkFreeCap[0], "Grooming: Yes (value==1).")
                        
                    #EOP
                
                    #RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber += 1
                    
                    routOfReqTrffcStpVLseqNum += 1                    

            i = i + 1   # increment counter to access all paths found 

        #SOP
        if (GlobalPrintOutEnabled==True) :
            if (requestrouted == True):
                print("<li>Request routed successfully over an existing path!")
            else:
                print("<li>Request not routed over existing paths, due to lack of free capacity on paths' links.")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Remaining capacity for this request is",remaincap)
    #EOP

    remaincap = roundatdecimals(remaincap,3) # remaincap=numpy.round(remaincap, decimals=3, out=None)
    return remaincap

def getVLfreecapacity(VirtualLinkTotals,vl):
    free=-1
    if vl in VirtualLinkTotals:
        free = VirtualLinkTotals[vl][1]
    return free                    

def CountLightpathsReusedReuses(VirtualLinkTotals):
    #Virtual Links Dictionary structure
    #Key                                    Value
    #source (s)	destination (d)	number (n)	cap utilised, cap free, num of traffic requests
    #e.g.
    #3	        1	            0	        40.0	      0.0	    1
    reused = 0 # how many virtual links were reused
    reuses = 0 # how many reuses of the virtual links
    for value in VirtualLinkTotals.values():
        if value[2]>1:
            reused +=1
            reuses +=value[2]-1
    return reused, reuses

def uniqueSD(VLofUniqueAdequateFreeCapacities):
    result = True
    dict = {}
    for key in VLofUniqueAdequateFreeCapacities.keys():
        s=key[0]
        d=key[1]
        if dict == {}:
            dict.update({(s,d):VLofUniqueAdequateFreeCapacities[key]})
        else:            
            if (s,d) in dict.keys():
                error("There are more than one VLs per s,d",9)
                result = False                
            else:
                dict.update({(s,d):VLofUniqueAdequateFreeCapacities[key]})
    return result
        

def demonstrate_how_to_access_the_items_of_a_dictionary():
    D = {}
    print("<p>D = ",D,"</p>")
    print("<ol>")
    for key in D.keys():
        print ("<li>key", key)
        print ("<li>key's value", D[key])
    for value in D.values():
        print ("<li>value", value)
    for item in D.items():
        print ("<li>item", item)
    print("</ol>")

def create_a_VT_with_virtual_links_that_only_have_sufficient_free_capacity(VirtualLinks, CapReq):
    # function to strip from VT virtual links with insufficient free capacity(vt)
    
    global GlobalPrintOutEnabled

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ('<li>Current list of virtual links to create a virtual topology of adequate capacity.')
        printVLdictionaryAsTable(VirtualLinks)
    #EOP

    # Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...} = {(3, 2, 0): [40.0, 0.0, 1], ...}

    #create new empty free capacities list
    newVLfreeCap = {}
    #VLsourcedestinations = {} # another dictionary that holds only the {(s,d):freecap,...} to find easily other virtual links with common s,d and keep the ones with lower free capacity
    #traverse all current free capacities list and copy to the new free capacities list only those that fullfil the capacity requirement
    for key in VirtualLinks.keys(): #key (s,d,i)
        value = VirtualLinks[key][1] #out of value [caputil, capfree, numoftrafreqs] just keep the capfree 
        if value>=CapReq:
            newVLfreeCap.update({key:[value]})
            #print("<li>added key ",key,"value",value,"to the new dictionary of virtual links with adequate free capacities.")
            
            #is there a key with common s,d ? (key[:2])
            #if yes, then compare their free capacities (values)
            s=key[0]
            d=key[1]
            commonSD = find_keys_with_common_source_destination(newVLfreeCap,s,d)
            
            if len(commonSD)>1: #if there are at least 2 VL with common s,d. Otherwise it will compare with itself
            

                k = getkeyofmaxfreecapacity(newVLfreeCap,commonSD)
                del newVLfreeCap[k]
            
    vtnew = convertVirtualLinksList2VirtualTopology(newVLfreeCap)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        
        print("<li>New VT only having VL with adequate free capacity required by the traffic request for possible grooming.")
        printVTdictionaryAsTable(vtnew)
        print("<li>New list of VL with adequate free capacity required by the traffic request for possible grooming.")
        printVLdictionaryAsTable(newVLfreeCap)
        
    #EOP

    return vtnew, newVLfreeCap

def getkeyofmaxfreecapacity(newVLfreeCap,commonSD):
    global GlobalPrintOutEnabled

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Getting VL with max free capacity among VLs with common source destination",newVLfreeCap)
        print("<li>List of VL ids with common source destination",commonSD)
    #EOP
    max = -1 * numpy.inf
    maxkey = None

    #SOP
    if (GlobalPrintOutEnabled==True) :
    #temp
        print("<table class='dictionary'>")
        print("<tr><td>s</td><td>d</td><td>i</td><td>freecap</td><td>equal free capacities</td></tr>")
    #EOP

    prevfreecap = 0

    for i in range(len(commonSD)):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            #temp
            print("<tr>","<td>",commonSD[i][0],"</td>","<td>",commonSD[i][1],"</td>","<td>",commonSD[i][2],"</td>","<td>",newVLfreeCap[commonSD[i]][0],"</td>")
        
            if prevfreecap == newVLfreeCap[commonSD[i]][0]:
                print("<td>YES</td>")
            print("</tr>")
        #EOP

        prevfreecap = newVLfreeCap[commonSD[i]][0]
        if newVLfreeCap[commonSD[i]][0] > max:
            max = newVLfreeCap[commonSD[i]]
            maxkey = commonSD[i]

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #temp
        print("</table>")
    #EOP
    
    return maxkey
        
def removeVL(dict,key):
    newdict = {}
    for k in dict:
        print("<li>current k=",k,",key to be removed=",key,".")
        if k != key:
            print("Adding to the dictionary {",k,",",dict[k],"}")
            newdict.update({k:dict[k]})
        else:
            print("Not adding to the dictionary {",k,",",dict[k],"}")
    return newdict

def find_keys_with_common_source_destination(data, src,dst):

    result = []
    for key in data.keys():
        if key[0]==src and key[1]==dst:
        #if key[:2] == prefix:
            result.append(key) #result.update({key:data[key]})
    return result

def keepVirtualLinksWithCommonSourceDestinationWithLowerFreeCapacity(newVLfreeCap):
    keys = list(newVLfreeCap.keys())
    for key in newVLfreeCap.keys():
        s = key[0]
        d = key[1]
        #if 
        #for item in keys:
        #    if s == item[0] and d == item[1]:
        #        if newVLfreeCap[key][1] < 


def  printVLids(dict):
    if len(dict)>0:
        longestvalue = len(max(dict.values(), key=len)) 
                
        print("<table class='dictionary'>")
        print("<tr><th colspan='2'>virtual link src,dst</th>")
        print(f"<th rowspan='2' colspan='{longestvalue:d}'>ID numbers</th>")
        print("</tr>")

        print("<tr>")
        print("<th rowspan='1'>source (s)</th>")
        print("<th rowspan='1'>destination (d)</th>")
        print("</tr>")
        
        for key in dict:
            print("<tr>")
            print("<td>",key[0],"</td>")
            print("<td>",key[1],"</td>")
            for data in dict[key]:
                print("<td>",data,"</td>")
            print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")
    
def printVLTReqs(dict):

    if len(dict)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='7'>Routing of Traffic Requests over Virtual Links</th></tr>")
        print("<tr><th colspan='7'>{(Virtal Link):[(Traffic Request 1, Traffic Request 2, ...)], ...}<br>")
        print("{(source, destination, number): [(queue, request, capacity required, type), ...], ...}</th>")
        print("</tr>")
        print("<tr><th colspan='3'>Virtual Link</th><th colspan='4'>Traffic Request</th></tr>")
        print("<tr><th>source</th><th>destination</th><th>number</th><th>queue</th><th>request</th><th>capacity required</th><th>type</th></tr>")

        for key in dict:
            numberoftrafficrequests = len(dict[key])
            print("<tr>")
            print(f"<td rowspan='{numberoftrafficrequests:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{numberoftrafficrequests:d}'>{key[1]:d}</td>")
            print(f"<td rowspan='{numberoftrafficrequests:d}'>{key[2]:d}</td>")
            i = 0
            while i < numberoftrafficrequests:
            #for i in range(len(dict[key])):
                print(f"<td>{dict[key][i][0]:d}</td>")
                print(f"<td>{dict[key][i][1]:d}</td>")
                print(f"<td>{dict[key][i][2]:.3f}</td>")
                print(f"<td>{dict[key][i][3]:s}</td>")
                if i == numberoftrafficrequests-1:
                    print("</tr><tr>")
                else:
                    print("</tr>")
                i += 1
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")

def printVLTotals(dict):
    if len(dict)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='3'>virtual link src,dst</th>")
        print("<th rowspan='2' colspan='3'>cap utilised, cap free, num of traffic requests</th>")
        print("</tr>")

        print("<tr>")
        print("<th rowspan='1'>source (s)</th>")
        print("<th rowspan='1'>destination (d)</th>")
        print("<th rowspan='1'>number (n)</th>")
        print("</tr>")
        
        for key in dict:
            print("<tr>")
            print("<td>",key[0],"</td>")
            print("<td>",key[1],"</td>")
            print("<td>",key[2],"</td>")
            for data in dict[key]:
                print(f"<td>{data:.3f}</td>")
            print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")


def printRoutingOfVirtualLinksOverWavelengthsAsTable(dict):

    if len(dict)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='7'>Routing of Virtual Link over the Physical Topology (wavelengths)</th></tr>")
        print("<tr><th colspan='7'>{(Virtal Link):[(WavelengthID 1, WavelengthID 2, ...)], ...}<br>")
        print("{(source, destination, number): [(source, destination, fiberID, wavelengthID), ...], ...}</th>")
        print("</tr>")
        print("<tr><th colspan='3'>Virtual Link</th><th colspan='4'>Wavelength ID</th></tr>")
        print("<tr><th>source</th><th>destination</th><th>number</th><th>source</th><th>destination</th><th>fiberID</th><th>wavelengthID</th></tr>")

        for key in dict:
            numberofphysicallinks = len(dict[key])
            print("<tr>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[1]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[2]:d}</td>")
            i = 0
            while i < numberofphysicallinks:
            #for i in range(len(dict[key])):
                print(f"<td rowspan='1'>{dict[key][i][0]:d}</td>")
                print(f"<td rowspan='1'>{dict[key][i][1]:d}</td>")
                print(f"<td rowspan='1'>{dict[key][i][2]:d}</td>")
                print(f"<td rowspan='1'>{dict[key][i][3]:d}</td>")
                if i == numberofphysicallinks-1:
                    print("</tr><tr>")
                else:
                    print("</tr>")
                
                i += 1
                
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")

def printRequestRoutingInfoAsTable(dict):
    if len(dict)>0:
        
        print("<table class='dictionary'>")
        #print("<tr><th colspan='2'>virtual link s,d</th>")
        #print("</tr>")

        print("<tr>")
        print("<th rowspan='1'>queue</th>")
        print("<th rowspan='1'>request</th>")
        print("<th rowspan='1'>(virtual link (s,d,n), type, capacity utilised, step of routing the requested capacity, step's virtual link sequence number)</th>")
        print("</tr>")
        
        for key in dict:
            valuelen = len(dict[key])
            print("<tr>")
            print(f"<td rowspan='{valuelen:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{valuelen:d}'>{key[1]:d}</td>")
            first = True
            for value in dict[key]:
                if not first:
                    print("<tr>")
                print("<td>",value,"</td>")
                if first:
                    print("</tr>")
                    first = False
                if not first:
                    print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")


'''
def FreeCapacitiesAsTable(dict):
    if len(dict)>0:
        
        print("<table class='dictionary'>")
        #print("<tr><th colspan='2'>virtual link s,d</th>")
        #print("</tr>")

        print("<tr>")
        print("<th rowspan='1'>queue</th>")
        print("<th rowspan='1'>request</th>")
        print("<th rowspan='1'>virtual link (s,d,i), type, capacity utilsed</th>")
        print("</tr>")
        
        for key in dict:
            valuelen = len(dict[key])
            print("<tr>")
            print(f"<td rowspan='{valuelen:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{valuelen:d}'>{key[1]:d}</td>")
            first = True
            for value in dict[key]:
                if not first:
                    print("<tr>")
                print("<td>",value,"</td>")
                if first:
                    print("</tr>")
                    first = False
                if not first:
                    print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")
'''

def printVLdictionaryAsTable(dict):
    if len(dict)>0:
        longestvalue = len(max(dict.values(), key=len)) 
        longestkey = len(max(dict.keys(), key=len))
        
        print("<table class='dictionary'>")
        print("<tr><th colspan='3'>virtual link id</th>")
        if longestvalue==1:
            print("<th rowspan='2'>free capacity</th>")
        elif longestvalue==3:
            print("<th rowspan='2'>utilised capacity</th>")
            print("<th rowspan='2'>free capacity</th>")
            print("<th rowspan='2'>number of traffic requests it servs</th>")
        print("</tr>")

        print("<tr>")
        print("<th rowspan='1'>source (s)</th>")
        print("<th rowspan='1'>destination (d)</th>")
        print("<th rowspan='1'>number of virtual link for (s,d)</th>")
        print("</tr>")
        
        for key in dict:
            print("<tr>")
            print("<td>",key[0],"</td>")
            print("<td>",key[1],"</td>")
            print("<td>",key[2],"</td>")
            for data in dict[key]:
                print("<td>",data,"</td>")
            print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")
    
def printVTdictionaryAsTable(dict):
    if len(dict)>0:

        longestvalue = len(max(dict.values(), key=len)) 
        
        print("<table class='dictionary'>")
        print("<tr><th>Source</th>")

        print(f"<th colspan='{longestvalue:d}'>Destinations</th></tr>")
        
        for key in dict:
            print("<tr>")
            print("<td>",key,"</td>")
            for data in dict[key]:
                print("<td>",data,"</td>")
            print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>") 



def convertVirtualLinksList2VirtualTopology(listVLs):

    M = list(listVLs.keys()) #get a list of [(s,d,i),...]

    vtc = {} #empty dictionary
    for i in range(len(M)): #each (s,d,i) in the list
        l = list(M[i]) #convert it to a list
        k = l[0] #get s
        v = l[1] #get d, 
                 #does not use i (virtual link sequence number from s to d)
        if k in vtc.keys(): #if key k is already in the dictionary
            tmp = vtc.get(k)
            tmp.append(v)   #append the d
        else:
            tmp = [v] #otherwise create a new value item for the key k 
        vtc.update({k:tmp}) #save the value for the key in the dictionary
        #print('<li>vtc',vtc)
    
    return vtc



def addNewVirtualLinkToTheVirtualTopology(nodes, que, req, Ni, Nj, vt, vtl, vtfrcap, cap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, VirtualLinkTotals, RoutReqTrfStp, RoutReqTrafficStpVLSeqNum, addEdgeWhenFreeCapacityOnly = True):
    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    # to add even the links that do not have free capacity to the graph, make last parameter False
    # def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, rq, Ni, Nj, vt, vtl, vtfrcap, cap, maxGbpsPerWavelength, VTfinal, R, gr, addEdgeWhenFreeCapacityOnly = False):
    # draw full edges $$$

    # Virtual topology's (VT) capacity logistics
    """
    vT={}   # VT = {node:[neighbour, ...], ...}
    vTL=[]   # VTL = [(tuple of source, destination of virtual link), ...]
    vTfreeCap={}   #VTFreeCap = {(tuple of source, destination of virtual link):[free capacity], ...}
    VTfinal={} # virtual topology for routing virtual links over physical topology
    """
        
    remaincap = cap

    LogicalLinkFreeCapacity=roundatdecimals((maxGbpsPerWavelength - cap), 3)
    
    t = tuple([Ni, Nj])

    GlobalVirtLinkID+=1 #id of the new virtual link by incrementing virtual link id i.e. create a new virtual link
    
    #VTobj.addNewVL(Ni, Nj)    
    newVL = addVirtualLink(VirtualLinkIDs, Ni, Nj)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>A new virtual link",newVL, "is created for queue",que,", request",req,", from", nodes[Ni], "to", nodes[Nj], "capacity requirement", cap,"Gbps, having free capacity",LogicalLinkFreeCapacity,"Gbps.")
    #EOP

    #updateVirtualLinkCapacity(VirtualLinkCap, newVL, cap, )
    updateVirtualLinkTReq(VirtualLinkTReq, newVL, que, req, cap, "New")
    updateVirtualLinkTotals(VirtualLinkTReq, VirtualLinkTotals, newVL)

    #now (2024-Aug) use the following 3 dictionaries to keep information related to routing
    #print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
    #printVLids(VirtualLinkIDs)
    #print("<li>Virtual Link Traffic Requests = {(s,d,i):[(que,req,cap,type),...],...}")
    #printVLTReqs(VirtualLinkTReq)
    #print("<li>Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...}")
    #printVLTotals(VirtualLinkTotals)
    
    insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    insertRoutingOfTrafficRequests2sqlite(dbConnection, que, req, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3), "New", RoutReqTrfStp, RoutReqTrafficStpVLSeqNum)

    appendVT(vt, Ni, Nj)       
    appendVTL(vtl, Ni, Nj)
    appendCapacities(vtfrcap,Ni,Nj,LogicalLinkFreeCapacity)
    
    appendPerRequestLinks(ReqRouteInfo,que,req,newVL,"New",cap, RoutReqTrfStp, RoutReqTrafficStpVLSeqNum) ###1 -> pou allou ginetai auto? Ginetai kai sto ###2 otan grooming ("Grm")
    appendFinalVT(VTfinal,nodes,Ni,Nj,cap,"New") #2DO auto tha ginetai pleon mesa sto appendPerRequestLinks gia na ginetai ekei kai h prosthesi tvn capacity ton grooming
                                                 #Done
    if (cap>0.0): #if there is capacity for the new virtual link then... (typical, since each new VL will have some capacity)
        appendVLIDs(VLIDs,Ni,Nj,GlobalVirtLinkID,cap) #create a virtual link id for each and every virtual (lightpath) link created.

    #SOP
    if (GlobalPrintOutEnabled==True) :
        if (addEdgeWhenFreeCapacityOnly == True):
            if (LogicalLinkFreeCapacity>0.0): #add graph edges only for free capacities > 0.0
                #graph_add_edge(gr,Ni,Nj,"rq:"+str(rq)+","+str(Ni)+"->"+str(Nj)+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
                graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
        else:
            #graph_add_edge(gr,Ni,Nj,"rq:"+str(rq)+","+str(Ni)+"->"+str(Nj)+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
            #graph_add_edge(gr,Ni,Nj,"req:"+str(req)+","+str(nodes[Ni])+"->"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
            graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
        
        """
        graph_add_edge(gr,Ni,Nj,"rq:"+str(rq)+","+str(Ni)+"&rarr;"+str(Nj)+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
        """
    #EOP
    
    remaincap = remaincap - cap
    #remaincap=numpy.round(remaincap, decimals=3, out=None)
    roundatdecimals(remaincap,3)
    #print("<li>Remaining capacity to be routed:",remaincap)

    return remaincap



def addVirtualLink(VLIDs, s, d):
    global GlobalStringOutcomes

    GlobalStringOutcomes += "<table class='dictionary'>"
    GlobalStringOutcomes += "<tr><th colspan='3'>Update of the Virtual Link IDs <br>{(s,d):[0,1,2,...],...}</th></tr>"
    GlobalStringOutcomes += "<tr><th>Justification</th><th>Key</th><th>Value</th></tr>"
    
    key = (s,d)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Adding a new virtual link from ", s,"to",d,".")
    #EOP
    
    if key in VLIDs:
        arrayIDs = VLIDs[key]
        id = max(arrayIDs) + 1
        arrayIDs.append(id)
        VLIDs.update({key:arrayIDs})

        GlobalStringOutcomes += "<tr><td>Update key value</td>"
    
    else:
        id=0
        arrayIDs = [id]
        VLIDs.update({key:arrayIDs})    
    
        GlobalStringOutcomes += "<tr><td>New entry</td>"
    
    GlobalStringOutcomes += f"<td>({s:d},{d:d})</td><td>["
    for i in range(len(arrayIDs)):
        GlobalStringOutcomes += str(arrayIDs[i])+","
    GlobalStringOutcomes = GlobalStringOutcomes[:-1]
    GlobalStringOutcomes += "]</td></tr>"
    GlobalStringOutcomes += "</table>"
    
    return (s,d,id)

'''
def updateVirtualLinkCapacity(VLCaps, vlidkey, utilcap, freecap):
    # virtual link capacities dictionary, virtual link id tuple (s, d, id), array of utilised capacity, free capacity
    if vlidkey in VLCaps:
        arrayCaps = VLCaps[vlidkey]
        c=arrayCaps[0]
        c = c + utilcap
        
        f=arrayCaps[1]
        f = f + freecap
        arrayCaps[1]=f
        
        VLCaps.update({vlidkey:arrayCaps})
    else:
        arrayCaps = [utilcap, freecap]
        VLCaps.update({vlidkey:arrayCaps})    
'''

def updateVirtualLinkTReq(VLTReqs, vlidkey, que, req, cap, type):
    
    # virtual link traffic requests dictionary, virtual link id tuple (s, d, id), array of (que, req, cap, type) tuples
    global maxGbpsPerWavelength
    limit = maxGbpsPerWavelength

    global GlobalStringOutcomes

    GlobalStringOutcomes += "<table class='dictionary'>"
    GlobalStringOutcomes += "<tr><th colspan='3'>Update of the Traffic Requests for each Virtual Link <br>{(s,d,n):[(que,req,cap,type),...],...}</th></tr>"
    GlobalStringOutcomes += "<tr><th>Justification</th><th>Key</th><th>Value</th></tr>"

    if vlidkey in VLTReqs:
        arrayTReqs = VLTReqs[vlidkey]
        arrayTReqs.append((que,req,cap,type))
        VLTReqs.update({vlidkey:arrayTReqs})
        
        GlobalStringOutcomes += "<tr><td>Update key value</td>"

        arrayTReqs = VLTReqs[vlidkey]
        sum = 0
        for item in arrayTReqs:
            sum = sum + item[2]
        if sum > limit:
            error("Error! More Gbps than the capacity of a single wavelength.",3)
            #exit(-1)
    else:
        if cap > limit:
            error("Error! More Gbps than the capacity of a single wavelength.",3)
            #exit(-1)
        arrayTReqs = [(que,req,cap,type)]
        VLTReqs.update({vlidkey:arrayTReqs})    

        GlobalStringOutcomes += "<tr><td>New entry</td>"
    
    #print ("<h1>vlidkey",vlidkey)
    #print("<h1>arrayTReqs",arrayTReqs)
    
    GlobalStringOutcomes += f"<td>({vlidkey[0]:d},{vlidkey[1]:d},{vlidkey[2]:d})</td><td>["
    for j in range(len(arrayTReqs)):
        GlobalStringOutcomes += f"({arrayTReqs[j][0]:d},{arrayTReqs[j][1]:d},{arrayTReqs[j][2]:.3f},'{arrayTReqs[j][3]:s}'),"
    GlobalStringOutcomes = GlobalStringOutcomes[:-1]
    GlobalStringOutcomes += "]</td></tr>"
    GlobalStringOutcomes += "</table>"
    

def error(description,code):
    global GlobalPrintOutEnabled

    txtLine = "<div class='error'>Error occurred! Error code:",code,". Description:",description,"</div>"
    #SOP
    if (GlobalPrintOutEnabled==True) :
        print(txtLine)
    #EOP

    #append the error log
    #errlog = open(experimentName+"_Errors.csv","w")
    #errlog.write()
    #errlog.close()

    #return(code)

    #exit(code)

def updateVirtualLinkTotals(VLTReqs, VLTotals, vlidkey):
    # virtual link traffic requests dictionary, virtual link id tuple (s, d, id), array of (que, req, cap, type) tuples
    global maxGbpsPerWavelength
    limit = maxGbpsPerWavelength

    global GlobalStringOutcomes

    GlobalStringOutcomes += "<table class='dictionary'>"
    GlobalStringOutcomes += "<tr><th colspan='3'>Update of the Virtual Link Totals <br>{(s,d,n):[caputil, capfree, num_of_TReqs],...}</th></tr>"
    GlobalStringOutcomes += "<tr><th>Justification</th><th>Key</th><th>Value</th></tr>"

    totalcap = 0.0
    totalfree = 0.0
    numtreqs = 0

    #print ("<h4>VL id key",vlidkey,"</h4>")

    if vlidkey in VLTReqs:
        arrayTReqs = VLTReqs[vlidkey]
        
        #print ("<h4>ArrayTReqs",arrayTReqs,"</h4>")

        for item in arrayTReqs:
            totalcap += item[2]
        totalfree = maxGbpsPerWavelength - totalcap
        numtreqs = len(arrayTReqs)      
        totalcap = roundatdecimals(totalcap, 3)
        totalfree = roundatdecimals(totalfree, 3)
        VLTotals.update({vlidkey:[totalcap, totalfree, numtreqs]})

        #print ("<h4>Updated VL ",vlidkey,"</h4>")
        #print ("<h4>Updated totalcap ",totalcap,"</h4>")
        #print ("<h4>Updated totalfree ",totalfree,"</h4>")
        #print ("<h4>Updated num of TReqs ",numtreqs,"</h4>")

        GlobalStringOutcomes += "<tr><td>Update key value</td>"

    else:
        error("Virtual link id not found.",201)
        #exit(-1)

        GlobalStringOutcomes += "<tr><td>Error! Virtual link ID not found!</td>"
    
    GlobalStringOutcomes += f"<td>({vlidkey[0]:d},{vlidkey[1]:d},{vlidkey[2]:d})</td><td>[{totalcap:.3f},{totalfree:.3f},{numtreqs:d}]</td></tr>"
    GlobalStringOutcomes += "</table>"

def routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass(VLs, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, dist, distEDFA,Cost, wavelengthIDs, LatRouterPort, LatTransponder, dbConnection):
    global GlobalPrintOutEnabled
    
    physicalLinks = [] # list to keep all physical links used to route virtual links on the physical topology
    RoutingOfVirtualLinksOverWavelengths = {}

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='data'>")
        print ("<tr><th colspan=14>Routing virtual (lightpath) links over the Physical Topology in the optical layer</th></tr>")
        print("<tr><th>Step</th><th>Virtual Link</th><th>Utilised capacity</th><th>Free capacity</th><th>Shortest path</th><th class='actions'>Physical Link(s)</th><th>Distance (km)</th><th>Wavelengths</th><th>Wavelength ID<br>(source,destination,fiber,wavelength)</th><th>Type</th><th>Node</th></tr>") # <th>Power for router port</th><th>Power for transponder</th></tr>") #<th>Power for EDFA(s)</th></tr>")
    #EOP

    virtlinkstep = 1 #count=1
    
    for vlink in VLs:   #for each virtual link
        start_vertex_str = vlink[0]
        end_vertex_str = vlink[1]
        sp = find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,start_vertex_str,end_vertex_str)

        SPnodes=len(sp)   
        rowspan = str(SPnodes)
        cap = vlink[3]

        vlSrc = nodenumber(N,vlink[0])
        vlDst = nodenumber(N,vlink[1])
        vlNum = vlink[2]
        virtlinkid=(vlSrc, vlDst, vlNum)

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr>")
            print("<td rowspan='"+rowspan+"'>",virtlinkstep,"</td>")   #<th>Virtual Link step number</th>
            print("<td rowspan='"+rowspan+"'>",vlink[0]+"&rarr;"+vlink[1]+"<br>("+str(nodenumber(N,vlink[0]))+","+str(nodenumber(N,vlink[1]))+","+str(vlink[2])+")</td>")   #<th>Virtual Link</th>
            print("<td rowspan='"+rowspan+"'>",vlink[3],"</td>")   #<th>Utilised capacity</th>
            print("<td rowspan='"+rowspan+"'>",roundatdecimals(maxGbpsPerWavelength-cap,3),"</td>")   #<th>Free capacity</th>
            print("<td rowspan='"+rowspan+"'>Shortest path: "+path2str(sp,N)) #print shortest path with nodes as 3 character tokens #<th>Shortest path</th>
            print ("<br><br>Shortest path: ",sp) #print shortest path with nodes as 3 character tokens
            print("</td>")
        #EOP

        wvl = 1
        physlinkid = linknumber(L, sp[0],sp[1])

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<td class='actions'>Link",physlinkid,": "+N[sp[0]]+"&rarr;"+N[sp[1]]+"</td>")   #<th class='actions'>Physical Link(s)</th>
            print("<td>",dist[physlinkid],"</td>") #<th>Distance (km)</th>
            print("<td>",wvl,"</td>")   #<th>Wavelengths</th>
        #EOP

        fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)
        plSrc = sp[0]
        plDst = sp[1]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<td>")
        #EOP

            #print(f"<td>({src:d},{dst:d},{fiberid:d},{waveid:d})")   #<th>Wavelength ID</th>
            #physicallinkid = (src, dst, fiberid, waveid)
            #addRoutingOfVirtualLinksOverPhysicalLinks(RoutingOfVirtualLinksOverPhysicalLinks, virtlinkid, physicallinkid)
            #print("<li>Virtual links' routing over the physical topology",RoutingOfVirtualLinksOverPhysicalLinks)
        physicallinkid = (plSrc, plDst, fiberid, waveid)
        addRoutingOfVirtualLinksOverPhysicalLinks(RoutingOfVirtualLinksOverWavelengths, virtlinkid, physicallinkid)
        
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("</td>")
            print("<td>Source</td>")   #<th>Type</th>
            print("<td>",N[sp[0]],"</td></tr>")   #<th>Node</th>
        #EOP

        if (SPnodes>2):         #if the physical path has more than one links
            PLtype = "First"
        else:                   #if the physical path has only one link
            PLtype = "Single"
        
        #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)

        if (fiberid!=-1) and (waveid!=-1):
            PhysicalLinkSource = L[physlinkid][0]
            PhysicalLinkCurrentSource = sp[0]
            PhysicalLinkCurrentDestination = sp[1]
            if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                PhysicalLinkDirection = "fwd" # forward
            else:
                PhysicalLinkDirection = "rev" # reverse

            #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
            #Done
            #2DO insertFiberWavelengthAssignments2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #Done and renamed function to insertRoutingVirtualLinksOverPhysicalTopology2sqlite()

            insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            
        updateTotals(Wmn, physlinkid, wvl)
        updateTotals(CUmn, physlinkid, roundatdecimals(cap,3))

        physicalLinks.append([sp[0],sp[1],vlink[2],roundatdecimals(maxGbpsPerWavelength-cap,3)])

        if (SPnodes>2): #if the path has more than one links
            z = 1
            while (z < SPnodes-1):   #for each physical link that serves the virtual link --> print the actions
                physlinkid = linknumber(L, sp[z],sp[z+1])
                noEr = 0.0
                noEe = 0.0
                doubleEt = 2*Et
                
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<tr><td class='actions'>Link",physlinkid,": "+N[sp[z]]+"&rarr;"+N[sp[z+1]]+"</td>")
                    print("<td>",dist[physlinkid],"</td><td>",wvl,"</td>")
                #EOP
                                    
                fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)
                    
                plSrc = sp[z]
                plDst = sp[z+1]

                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<td>")
                    #print(f"<td>({src:d},{dst:d},{fiberid:d},{waveid:d})")   #<th>Wavelength ID</th>
                #EOP

                physicallinkid = (plSrc, plDst, fiberid, waveid)
                    
                addRoutingOfVirtualLinksOverPhysicalLinks(RoutingOfVirtualLinksOverWavelengths, virtlinkid, physicallinkid)
                    
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    #print("<li>Virtual links' routing over the physical topology",RoutingOfVirtualLinksOverPhysicalLinks)
                    
                    print("</td>")

                    print("<td>Middle</td><td>",N[sp[z]],"</td></tr>")
                #EOP
                    
                if (z==SPnodes-2):      #if this is the last link of the physical path 
                    PLtype = "Last"
                else:                   #if the physical path has more links
                    PLtype = "Middle"
                
                #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)

                if (fiberid!=-1) and (waveid!=-1):
                    PhysicalLinkSource = L[physlinkid][0]
                    PhysicalLinkCurrentSource = sp[z]
                    PhysicalLinkCurrentDestination = sp[z+1]
                    if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                        PhysicalLinkDirection = "fwd" # forward
                    else:
                        PhysicalLinkDirection = "rev" # reverse

                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkstep, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
                    #Done
                    
                    insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                
                updateTotals(Wmn, physlinkid, wvl)
                updateTotals(CUmn, physlinkid, cap)
               
                physicalLinks.append([sp[z],sp[z+1],vlink[2],roundatdecimals(maxGbpsPerWavelength-cap,3)])

                z = z + 1

        noWvl = 0
        noCap = 0.0

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td class='actions'>-</td><td>-</td><td>",noWvl,"</td>")
            print("<td>no wavelength id</td>")
            print("<td>Destination</td><td>",N[sp[SPnodes-1]],"</td></tr>")
        #EOP

        updateTotals(Wmn, physlinkid, noWvl)
        updateTotals(CUmn, physlinkid, noCap)
    
        virtlinkstep += 1   #count = count + 1   # virtual links counter

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("</table>")
    #EOP

    #RoutingOfVirtualLinksOverPhysicalLinks

    return physicalLinks, RoutingOfVirtualLinksOverWavelengths

def addRoutingOfVirtualLinksOverPhysicalLinks(routingdict,VLid,PLid):
    if VLid in routingdict:
        val = routingdict[VLid]
        val.append(PLid)
        routingdict.update({VLid:val})
    else:
        routingdict.update({VLid:[PLid]})

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Appended the Physical Link:",PLid,"to the Virtual Link's",VLid,"routing over the physical topology.")
    #EOP



def routeAllRequestsOfOneQueueOverVirtualTopologyDirectBypass(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):

    startingStep = startingStep - 1

    #this version of Direct bypass uses a single Queue!
    #this version simulates execution time
    #Queue is the actual Queue data bearing data structure
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    ###19-9-2024 create graph in the calling program and pass as parameter to the routing function, since the traffic requests might be served by more than one routing functions depending on the scheduling strategy
    ###s="Virtual topology graph after processing request "
    ###gr = graph_new(s, True)
    #EOP
    
    #n = len(data)
    #n0 = len(q0)
    #n1 = len(q1)
    n = len(Queue)

    TotalNumberOfTrafficRequestsOnBothQueues = n #+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the single queue over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    
    #i0=0
    #i1=0
    currentrequest=0
    step = 1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        RequestTime = nsec2msec(startTReq - startRoutingOverVT)
        
        Qtime = RequestTime % 100.0
        
        CurrentQueue = QueueID
                
        if CurrentQueue==QueueID and currentrequest<n:
            treq = Queue[currentrequest] # treq = traffic request
            #que=0
            que=QueueID
            fromQueue=QueueID
            req=currentrequest
            currentrequest = currentrequest + 1
        
        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(startingStep+step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP

        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {startingStep+step:0d}</td><td>Processing queue {fromQueue:0d}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain:",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4d} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")

                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

            ##keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            #prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            #prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            #prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            #prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            #no if since this is direct bypass
            # if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            # ex if body from here 
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
            #EOP
            
            ###@@@>>> 29-08-2024

            # CapForTheLogicalLink = maxGbpsPerWavelength
            if remain >= maxGbpsPerWavelength:
                CapForTheLogicalLink = maxGbpsPerWavelength
            else:
                CapForTheLogicalLink = remain
                
            if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
            #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                
                #if adding succeded
                RoutingOfRequestedTrafficStep += 1
                RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                #added new link to route 40G successfully
                remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                
                # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                TotalLightpaths[0] +=1

                # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                # if you want to add, just uncomment next line
                # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")
            
            # ex if body to here 
            # endif
            #no else since this is direct bypass
            '''
            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                       #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1
            '''

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                print(GlobalStringOutcomes)
                GlobalStringOutcomes = ""
                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                print("<td>")
                print(f"Time of processing all requests {RequestTime:.3f},")
                print(f"Time of current queue's turn {Qtime:.3f}")
                print("</td>")
                print("</tr>")
            #EOP
            
            #RoutingOfRequestedTrafficStep += 1

        #SOP    
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report
    #EOP

    return startingStep+step



def routeAllRequestsOfTwoQueuesOverVirtualTopologyDirectBypass_Q0_75_Q1_25(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues for Direct Bypass!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP

    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "0"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
                
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        Qtime = CurrentRequestTime % 100.0
        #if Qtime >= 0.0 and Qtime < 75.0:
        if Qtime < 75.0:
            CurrentQueue="0"
        #elif Qtime >= 75.0:
        else:
            CurrentQueue="1"
            Qtime -= 75.0 # to start the queue time from 0.0
        
        if CurrentQueue=="0" and i0<n0:
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            i0 = i0 + 1
            req=i0-1
        elif CurrentQueue=="0" and i0>=n0:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1-1
        elif CurrentQueue=="1" and i1<n1:
            treq = q1[i1]
            que=1
            fromQueue="1"
            i1 = i1 + 1
            req=i1-1
        elif CurrentQueue=="1" and i1>=n1:
            treq = q0[i0]
            que=0
            fromQueue="0"
            i0 = i0 + 1
            req=i0-1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP
        
        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")

                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)

                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            #no if since this is direct bypass
            # if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            # ex if body from here 
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
            #EOP
                        
            ###@@@>>> 29-08-2024

            # CapForTheLogicalLink = maxGbpsPerWavelength
            if remain >= maxGbpsPerWavelength:
                CapForTheLogicalLink = maxGbpsPerWavelength
            else:
                CapForTheLogicalLink = remain

            if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
            #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):

                #if adding succeded
                RoutingOfRequestedTrafficStep += 1
                RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                #added new link to route 40G successfully
                remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                
                # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                TotalLightpaths[0] +=1

                # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                # if you want to add, just uncomment next line
                # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")
            
            # ex if body to here 
            # endif
            #no else since this is direct bypass
            '''
            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                       #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1
            '''

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                print(GlobalStringOutcomes)
                GlobalStringOutcomes = ""
                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                print("<td>")
                print(f"Time of processing all requests {CurrentRequestTime:.3f},")
                print(f"Time of current queue's turn {Qtime:.3f}")
                print("</td>")
                print("</tr>")
            #EOP
            
            #RoutingOfRequestedTrafficStep += 1

        #SOP    
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report
    #EOP




def routeAllRequestsOfTwoQueuesOverVirtualTopologyDirectBypass_Q0nextQ1(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues for Direct Bypass!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP

    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "0"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
                
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        #Qtime = CurrentRequestTime % 100.0
        Qtime = CurrentRequestTime

        if i0<n0:
            CurrentQueue="0"
        else:
            CurrentQueue="1"
        
        if CurrentQueue=="0":
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            req=i0
            i0 = i0 + 1
        elif CurrentQueue=="1":
            treq = q1[i1]
            que=1
            fromQueue="1"
            req=i1
            i1 = i1 + 1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP
        
        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")

                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)

                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            #no if since this is direct bypass
            # if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            # ex if body from here 
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
            #EOP
                        
            ###@@@>>> 29-08-2024

            # CapForTheLogicalLink = maxGbpsPerWavelength
            if remain >= maxGbpsPerWavelength:
                CapForTheLogicalLink = maxGbpsPerWavelength
            else:
                CapForTheLogicalLink = remain

            if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
            #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):

                #if adding succeded
                RoutingOfRequestedTrafficStep += 1
                RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                #added new link to route 40G successfully
                remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                
                # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                TotalLightpaths[0] +=1

                # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                # if you want to add, just uncomment next line
                # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")
            
            # ex if body to here 
            # endif
            #no else since this is direct bypass
            '''
            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                       #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1
            '''

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                print(GlobalStringOutcomes)
                GlobalStringOutcomes = ""
                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                print("<td>")
                print(f"Time of processing all requests {CurrentRequestTime:.3f},")
                print(f"Time of current queue's turn {Qtime:.3f}")
                print("</td>")
                print("</tr>")
            #EOP
            
            #RoutingOfRequestedTrafficStep += 1

        #SOP    
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report
    #EOP



def routeAllRequestsOfTwoQueuesOverVirtualTopologyDirectBypass_Q1nextQ0(nodes, q0, q1, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #this version uses Queues for Direct Bypass!
    #this version simulates execution time
    #this function's parameter "q0" refers to the traffic requests of the high priority "Video" queue
    #this function's parameter "q1" refers to the traffic requests of the low priority "Best Effort" queue

    global GlobalPrintOutEnabled
    global GlobalVirtLinkID
    global GlobalStringOutcomes

    GlobalStringOutcomes = ""
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
    s="Virtual topology graph after processing request "
    gr = graph_new(s, True)
    #EOP

    #n = len(data)
    n0 = len(q0)
    n1 = len(q1)
    TotalNumberOfTrafficRequestsOnBothQueues = n0+n1 # ex n
    #count=0

    GlobalVirtLinkID = 0

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #table routing traffic requests over virtual topology headings
        print("<table class='data'>")
        print("<tr><th colspan='10'>Routing traffic requests of the two queues (1: Video, high priority, and 2: Best Effort, low priority) over the Virtual Topology (a.k.a. Adding requests to the Virtual Topology)</th></tr>")
        print ("<tr><th>Step number</th><th>Queue</th><th>Request</th><th>From</th><th>To</th>")
        print ("<th>Required/Remain</th><th class='actions'>Actions</th><th>Outcomes</th>")
        print("<th>Current Virtual Topology</th><th>Current request processing start (msec)</th></tr>")
        #print ("<tr><th style='width: 50px; inline-size: 50px;'>Request</th><th style='width: 50px; inline-size: 50px;'>Queue</th><th style='width: 50px; inline-size: 50px;'>From</th><th style='width: 50px; inline-size: 50px;'>To</th><th>Required/Remain</th><th class='actions'>Actions</th><th>Free capacities</th><th>Current Virtual Topology</th><th>Time started serving TrReq (msec)</th><th>Time started serving after first TrReq (msec)</th><th>Time started serving TrReq at the subprocess (msec)</th><th>Time started serving after first TrReq at the subprocess (msec)</th></tr>")
    #EOP

    # Traverse through all array elements
    # edw prepei na pairnei apo tis 2 queues symfwna me to xronismo to shaper
    #for i in range(n):   #for each request
    i0=0
    i1=0
    step=1

    # Start the thread to alternate queues
    #thread = threading.Thread(target=alternateQueueSelection)
    #thread.daemon = True  # This ensures the thread will exit when the main program does
    #thread.start()

    startRoutingOverVT = time.process_time_ns()
    #startof_serving_current_TRreq_timestamp = 0.0
    #endof_serving_current_TRreq_timestamp = 0.0
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        #select path separator based on the host OS
        pathseparator = ""
        if platform.system() == 'Windows':
            pathseparator = "\\"
        elif platform.system() == 'Linux':
            pathseparator = "/"
        else:
            pathseparator = "/"

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'w')
    #EOP

    CurrentQueue = "1"

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startCurrentTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
                
        CurrentRequestTime = nsec2msec(startCurrentTReq - startRoutingOverVT)
        #Qtime = CurrentRequestTime % 100.0
        Qtime = CurrentRequestTime

        if i1<n1:
            CurrentQueue="1"
        else:
            CurrentQueue="0"
        
        if CurrentQueue=="0":
            treq = q0[i0] # treq = traffic request
            que=0
            fromQueue="0"
            req=i0
            i0 = i0 + 1
        elif CurrentQueue=="1":
            treq = q1[i1]
            que=1
            fromQueue="1"
            req=i1
            i1 = i1 + 1
        else:
            print("<div>Error on Queue selection")
            exit(1)

        remain = treq[2]
    
        apo = nodes[treq[0]]
        pros = nodes[treq[1]]

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graph_filename="VT_after_Step"+str(step)+"_Que"+str(que)+"_Req"+str(req)+".html"
        #EOP
        
        RoutingOfRequestedTrafficStep = 0
        RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
        
        while (remain>0.0): #while there are remaining Gb of the request to be routed
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<td style='width: 50px; inline-size: 50px;'>Step {step:0d}</td><td>Processing queue {fromQueue:s}</td><td>request {req:0d}</td><td style='width: 50px; inline-size: 50px;'>from {apo:s} ({treq[0]:0d})</td><td style='width: 50px; inline-size: 50px;'>to {pros:s} ({treq[1]:0d})</td>")
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4s} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")

                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)

                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

            #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
            prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
            prevVirtualLinkTReqs = copyDictionary(VirtualLinkTReqs)
            prevVirtualLinkTotals = copyDictionary(VirtualLinkTotals)
            prevReqRouteInfo = copyDictionary(ReqRouteInfo)

            #no if since this is direct bypass
            # if (remain >= maxGbpsPerWavelength):  #if the request is >=40Gbps
            # ex if body from here 
            
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>A new virtual link will be created since the requirement is >= 40 Gbps.")
            #EOP
                        
            ###@@@>>> 29-08-2024

            # CapForTheLogicalLink = maxGbpsPerWavelength
            if remain >= maxGbpsPerWavelength:
                CapForTheLogicalLink = maxGbpsPerWavelength
            else:
                CapForTheLogicalLink = remain

            if (addNewVirtualLinkToTheVirtualTopology(nodes, que, req,  treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
            #def addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):

                #if adding succeded
                RoutingOfRequestedTrafficStep += 1
                RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                #added new link to route 40G successfully
                remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                
                # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                TotalLightpaths[0] +=1

                # do not add a edge on the graph for 40 Gbps virtual (logical) links; we don't want the graph overcrowded
                # if you want to add, just uncomment next line
                # graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")
            
            # ex if body to here 
            # endif
            #no else since this is direct bypass
            '''
            else:   #if the request is <40Gbps attempt grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li>Since the requirement is < 40 Gbps then an attempt to route traffic over existing virtual links will be made")
                #EOP

                CapForTheLogicalLink=remain
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):   #try to route it over existing paths of the virtual topology
                    
                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                else:   #if it cannot be routed over existing paths of the virtual topology, then add a new virtual link for it
                    
                    #keep a copy of  the previous versions of the dictionaries to be able to only incremental updates of the content for shorter output
                    prevVirtualLinkIDs = copyDictionary(VirtualLinkIDs)
                                
                    if (addNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                       #defaddNewVirtualLinkToTheVirtualTopologyMultihopBypass(nodes, que, req, Ni,      Nj,      vt, vtl, vtfrcap,    cap,                  maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, addEdgeWhenFreeCapacityOnly = True):
                        #added new link to route required capacity successfully
                        remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                        #remain = remain - CapForTheLogicalLink
                        #remain=numpy.round(remain, decimals=3, out=None)

                        # prostithetai neo virtual link (lightpath) gia na dromologisi tin kinisi pou den mporese na ginei grooming
                        TotalLightpaths[0] += 1
            '''

            #endof_serving_current_TRreq_timestamp = time.process_time_ns()
            #time_for_serving_current_Treq = endof_serving_current_TRreq_timestamp - startof_serving_current_TRreq_timestamp

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("</td>")
                print("<td class='actions'>")
                print(GlobalStringOutcomes)
                GlobalStringOutcomes = ""
                print("</td>")
                print("<td>Virtual Topology vT =",vt)
                #print("<!--<iframe src='"+graph_filename+"' style='border:2px solid red;width:200px;height:200px;' title='"+graph_filename+"'></iframe>-->")   # not including graphs in the report, but only links to graphs
                print("<p><a href='"+graph_filename+"' target='_blank'>"+graph_filename+"</a></p></td>")
                print("<td>")
                print(f"Time of processing all requests {CurrentRequestTime:.3f},")
                print(f"Time of current queue's turn {Qtime:.3f}")
                print("</td>")
                print("</tr>")
            #EOP
            
            #RoutingOfRequestedTrafficStep += 1

        #SOP    
        if (GlobalPrintOutEnabled==True) :
            #after each request routing over virtual topology save graph phase
            graph_save(gr, graph_path, graph_filename)
            #add an iframe to show the virtual topology network graph
            #print("<iframe src='"+"VTpostReq"+str(r)+".html"+"'></iframe></td></tr>")
        #EOP
        step = step + 1
    
    #SOP
    if (GlobalPrintOutEnabled==True) :
        f.close()

        graph_save(gr, graph_path, "VirtualTopology.html")   # save virtual topology after last step as the final virtual topology graph.

        #after all requests show total graph
        print("</table>")

        visualiseVirtualTopology(graph_filename,(sys.argv[7]!="pdfout")) #if not output to pdf then draw graph in the report
    #EOP




def Log2path (p,f):
    outputPath = p
    now = datetime.now()
    newDirName= f+"_y"+str(now.year)+"_m"+str(now.month)+"_d"+str(now.day)+"_h"+str(now.hour)+"_m"+str(now.minute)+"_s"+str(now.second)+"_u"+str(now.microsecond)
    Path = os.path.join(outputPath, newDirName)
    os.mkdir(Path)
    f = f + ".html"
    FilePath = os.path.join(Path, f)
    #logging 
    stdoutOriginal=sys.stdout 
    ####sys.stdout = open(FilePath, "w")
    
    sys.stdout = open(FilePath, "a")
    #sys.stdout = open(".\direct.html", "w")
    return stdoutOriginal, sys.stdout, Path

def Log2pathCSV (p,f):
    outputPath = p
    now = datetime.now()
    newDirName= f+"_y"+str(now.year)+"_m"+str(now.month)+"_d"+str(now.day)+"_h"+str(now.hour)+"_m"+str(now.minute)+"_s"+str(now.second)+"_u"+str(now.microsecond)
    Path = os.path.join(outputPath, newDirName)
    os.mkdir(Path)
    f = f + ".csv"
    FilePath = os.path.join(Path, f)
    #logging 
    stdoutOriginal=sys.stdout 
    sys.stdout = open(FilePath, "a")
    return stdoutOriginal, sys.stdout, Path

def removeNewLine(s):
    out = ""
    for c in s:
        if ( (c != "\n") and (c != "\r") ):
            out = out + c
    return out

def readConfig(file):
    '''
    name = "ShnTckrFullPrintOut" 
    description = "Shen Tucker Multihop and Direct bypass. Printing a full report"
    version = "115"
    runs = 1
    X = ["0","1","2","3","4","5"]
    nets = [
        "N4L5_GRNetSubnet.txt",
        "N6L7_GRNetSubnet.txt",
        "N6L8_ShnTckr_a.txt",
        "N8L9_GRNetSubnet.txt",
        "N8L11_Beletsioti.txt",
        "N10L10_GRNetSubnet.txt",
        "N10L12_GRNetSubnetMesh.txt",
        "N12L13_GRNetSubnet.txt",
        "N14L21_ShnTckr_b.txt",
        "N14L22_DT.txt",
        "N24L28_GRNet.txt",
        "N24L43_ShnTckr_c.txt"
    ]
    '''
    '''
    [Name]
    ShnTckrFullPrintOut
    [Description]
    Shen Tucker Multihop and Direct bypass. Printing a full report
    [Version]
    116
    [Runs]
    1
    [X]
    0, 1, 2, 3, 4, 5
    [Nets_start]
    N4L5_GRNetSubnet.txt
    N6L7_GRNetSubnet.txt
    N6L8_ShnTckr_a.txt
    N8L9_GRNetSubnet.txt
    N8L11_Beletsioti.txt
    N10L10_GRNetSubnet.txt
    N10L12_GRNetSubnetMesh.txt
    N12L13_GRNetSubnet.txt
    N14L21_ShnTckr_b.txt
    N14L22_DT.txt
    N24L28_GRNet.txt
    N24L43_ShnTckr_c.txt
    [Nets_end]
    '''

    X=[]
    nets=[]
    printout = ""
    keepeveryNreport = ""
    lamdagensaveload = ""
    lamdafile = ""
    name = ""
    description = ""
    version = ""
    runs = ""
    pdfout = ""
    numberofqueues = ""
    computername = ""
    progfolder = ""
    distribution = ""
    EndOfConfig = ""

    fin = open(file,"r")

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Name]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        name = nextLine
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Description]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        description = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Version]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        version = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Runs]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        runs = int(nextLine)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[X]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine);
        X = nextLine.split(',')

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Nets_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[Nets_end]"):
            #nextLine = removeNewLine(nextLine); 
            nets.append(nextLine)
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Printout]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        printout = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[KeepEveryNthReport]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        keepeveryNreport = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Lamda]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        lamdagensaveload = nextLine
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[LamdaTextFile]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        lamdafile = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[PDFout]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        pdfout = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Queues]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        numberofqueues = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[ComputerName]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        computername = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[ProgramFolder]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        progfolder = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Distribution]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        distribution = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Strategy]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        strategy = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[EndOfConfig]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        EndOfConfig = nextLine

    fin.close()
    
    return name, description, version, runs, X, nets, printout, int(keepeveryNreport), lamdagensaveload, lamdafile, pdfout, numberofqueues, computername, progfolder, distribution, strategy
           

def readData(file):
    N = []
    L = []
    Nm = {}
    Dist = []
    netName = ""
    #inLine = 0
    fin = open(file,"r")
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[Name]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        netName = nextLine
        #print ("netName",netName)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[N]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine);
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        N = nextLine.split(',')
        #print ("N",N)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine);
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[L]"):
        nextLine = fin.readline();
        nextLine = removeNewLine(nextLine);
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        temp = nextLine.split(' ')
        for item in temp:
            itemList = item.split(',')
            L.append(list(map(int, itemList)))
        #print ("L",L)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[Nm]"):
        nextLine = fin.readline();
        nextLine = removeNewLine(nextLine);
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        temp = nextLine.split(' ')
        times=[]
        timesNum=[]
        for item in temp:
            itemList = item.split(':')
            klidi = int(itemList[0])
            #print('klidi',klidi)
            times = itemList[1]
            #print('times',times)
            times = times.split(',')
            times = list(map(int, times))
            #print('times',times)
            Nm.update({klidi:times})
        #print ("Nm",Nm)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine);
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[Dist]"):
        nextLine = fin.readline();
        nextLine = removeNewLine(nextLine);
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        tmp = nextLine.split(',')
        Dist = list(map(float, tmp))
        #print ("Dist",Dist)
    fin.close()
    return netName, N, L, Nm, Dist

def removeTempFiles(dir, pattern):    
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))

def accumulatePowerParameters(struct, key, val):
    if key in struct: 
        tmp = struct.get(key)
        tmp += val
    else:
        tmp = val
    roundatdecimals(tmp,3)
    struct.update({key: tmp})

def printDi(struct, nodes, sigmalamda):
    print ("<table class='table1c'>")
    print ("<tr><th colspan=3>&Sigma;&lambda;<sup>id</sup>: Traffic data from low end routers at node i in Gbps</th></tr>")
    print ("<tr><th>Node</th><th>Data in Gbps</th><th>&Delta;<sub>i</sub></th></tr>")
    keys = list(struct.keys())
    for key in keys:
        print("<tr><td>",nodes[key],"</td><td>",roundatdecimals(sigmalamda.get(key),3), "</td><td>",roundatdecimals(struct.get(key),0), "</td></tr>")
    print ("</table>")

def printDiPerQueue(que, struct, nodes, sigmalamda):
    print ("<table class='table1c'>")
    print ("<tr><th colspan=3>&Sigma;&lambda;<sup>id</sup>: Traffic data from low end routers at node i in Gbps for Queue:",que,"</th></tr>")
    print ("<tr><th>Node</th><th>Data in Gbps</th><th>&Delta;<sub>i</sub></th></tr>")
    keys = list(struct.keys())
    for key in keys:
        print("<tr><td>",nodes[key],"</td><td>",roundatdecimals(sigmalamda.get(key),3), "</td><td>",roundatdecimals(struct.get(key),0), "</td></tr>")
    print ("</table>")

def printCij(struct, nodes):
    # print Cij
    print ("<table class='table1c'>")
    print ("<tr><th colspan=2>Cij: number of wavelength channels on the virtual topology between node pair (i,j)</th></tr>")
    print ("<tr><th>Virtual link</th><th>number of wavelengths</th></tr>")
    keys = list(struct.keys())
    for key in keys:
        #print ("key",key)
        print("<tr><td>",nodes[key[0]],"&rarr;",nodes[key[1]],"</td><td>",struct.get(key),"</td></tr>")
    print ("</table>")

def printSigmaCij(struct, nodes):
    print ("<table class='table1c'>")
    print ("<tr><th colspan=2>&sum; C<sub>ij</sub>: number of wavelength channels on the virtual topology starting from node i</th></tr>")
    print ("<tr><th>Node</th><th>number of wavelengths</th></tr>")
    keys = list(struct.keys())
    for key in keys:
        print("<tr><td>",nodes[key],"</td><td>",struct.get(key),"</td></tr>")
    print ("</table>")

def initialiseSet(struct,L,values):
    if (len(values)==0):
        for physicalLink in L:
            #print("physicalLink",physicalLink)
            #key = (physicalLink[0],physicalLink[1]) # if keys were (source,destination) a.k.a. (m,n)
            key = linknumber(L,physicalLink[0],physicalLink[1]) # the link id number (e.g. 0, 1, 2, etc.) is considered the key 
            struct.update({key: 0.0})
    else:
        for i in range(len(L)):
            #key = (L[i][0],L[i][1]) # if keys were (source,destination) a.k.a. (m,n)
            key = i 
            struct.update({key: values[i]})

#def initialiseFiberids(fiberids,L):
    """
    # fiberids: dictionary of fiber ids for each link
    # fiberids = {0:0, 1:0, ...}
    # fiberids = {<linkid>:<fibers count for this link>, ...}
    for i in range(len(L)):
        fiberids.update({i: -1})
    """

#def assignFiberid(fiberIDs,linkid):
    """
    # maxFibersPerLink = -1       #no limit on the total number of fibers on each physical link
    # maxFibersPerLink not considered yet as a limit!

    if linkid in fiberIDs:
        count = fiberIDs.get(linkid)
        count += 1
        fiberIDs.update({linkid:count})
        return count
    else:
        print("assignFiberid Error: LinkID",linkid,"does not exist")
        return -1
    """

#def getmaxFiberidForLink(fiberIDs,linkid):
    """
    if linkid in fiberIDs:
        fiberid = fiberIDs.get(linkid)
        return fiberid
    else:
        print("getmaxFiberidForLink Error: LinkID",linkid,"does not exist")
        return -1
    """

def initialiseWavelegthids(wavelegthids,L):
    # wavelengthids: dictionary of wavelgth ids for each fiber of each link 
    # that keeps the IDs of wavelength per fiber per link (linkids, fiberids, wavelengthids are zero based)
    # wavelengthids = {0:{0:16, 1:1}, 1:{0:3}, ...} when the fiber reaches the maxWavelengthsPerFiber, a new fiber is utilised
    # wavelengthids = {<linkid>:{<fiberid>:<wavelengths count for this fiber of the link>, ...}, ...}
    for i in range(len(L)):
        wavelegthids.update({i: {0:-1}})

def assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, linkid):
    # maxWavelengthsPerFiber = 16 # max 16 wavelengths are multiplexed in each fiber
    # every 16 wavelengths a new fiber is assigned to the link

    if linkid in wavelengthIDs:
        fibers = wavelengthIDs.get(linkid)
        #assignFiberid(fibers,linkid)
        #print("fibers",fibers)
        #numberoffibers = len(fibers.keys())-1
        #print("numberoffibers",numberoffibers)
        
        #getting the last key of the dictionary
        templist = list(fibers.keys())
        lastkey = templist[-1]

        #print("lastkey",lastkey)
        wavescount = fibers.get(lastkey)
        #print("wavescount",wavescount)
        wavescount +=1
        if ( wavescount > (maxWavelengthsPerFiber-1) ):
            lastkey += 1
            wavescount = 0
        fibers.update({lastkey:wavescount})
        #print("returning for linkid",linkid,"fiberid",lastkey,"waveid",wavescount)
        return lastkey, wavescount 
    else:
        print("assignWavelengthid Error: LinkID",linkid,"does not exist")
        return -1, -1

def printAmn(struct, nodes, links):
    print ("<table class='table1c'>")
    print ("<tr><th colspan=2>Amn: Number of EDFAs that should be deployed on each fiber of physical link (m,n)</th></tr>")
    print ("<tr><th>Physical link</th><th>number of EDFAs A<sub>mn</sub></th></tr>")
    keys = list(struct.keys())
    for key in keys:
        #print ("<li>key",links[key])
        link = links[key]
        print("<tr><td>",nodes[link[0]],"&rarr;",nodes[link[1]],"</td><td>",struct.get(key),"</td></tr>")
    print ("</table>")

def calculateTotalCapacity(R):
    sum = 0.0
    for rq in R:
        sum += rq[2]
    return sum

'''
def NotUsed_selectQueue(interval1, interval2):
    while True:
        t1=time.process_time_ns()
        time.sleep(interval1)
        t2=time.process_time_ns()
        GlobalQ = 0
        print("queue 0 selected for ",t2-t1,"nsec")
        t1=time.process_time_ns()
        time.sleep(interval2)
        t2=time.process_time_ns()
        GlobalQ = 1
        print("queue 1 selected for ",t2-t1,"nsec")

def NotUsed_selectQueue_ForUseWith_testingTAS_py(shared_array):
    """Function to run in the separate process."""
    """Process modifies elements in the shared array."""
    
    timestamp = time.time()

    appDir = "C:\\SimLight"
    stdoutOriginal, sys.stdout, graphsPath = Log2pathCSV(appDir, "SelectQueueProcessStart")
    
    print(f"{shared_array[3]:.0f}; Process selectQueue in {__name__:s} is running at; X; {timestamp:.9f}; X")
    
    sys.stdout.close()
    sys.stdout=stdoutOriginal
    
    #select Queue 0 for during the next t0 seconds
    t0 = shared_array[0]
    #select Queue 1 for during the next t1 seconds
    t1 = shared_array[1]

    while True:
        # select Queue 0
        shared_array[2] = 0.0
        time.sleep(t0)

        # select Queue 1
        shared_array[2] = 1.0
        time.sleep(t1)

def NotUsed_activateTimeAwareShaper_ForUseWith_testingTAS_py(id):
    
    # Create a shared array of integers (change 'd' for other data types)
    shared_array = multiprocessing.Array('d', range(4))
    # shared_array[0] = Time for Queue 0 selection
    # shared_array[1] = Time for Queue 1 selection
    # shared_array[2] = Currently selected Queue
    # shared_array[3] = just a number (afxon arithmos)
    
    shared_array[0] = 0.7
    shared_array[1] = 0.3
    shared_array[2] = 0.0 
    shared_array[3] = id # just a number (afxon arithmos)

    # Create and start the process
    process = multiprocessing.Process(target=selectQueue, args=(shared_array,))
    process.start()

    start_time = time.time()

    print("ID; Line; Queue; Timestamp; Elapsed time (sec)")
    
    # You can do other things in the main program here
    for i in range(1000000):
        #time.sleep(0.2)  # Simulate some main program work
        
        # Access the modified array from shared memory
        # print("Modified array:", shared_array[:])

        Queue = shared_array[2]
        
        timestamp = time.time()
        elapsedTime = timestamp - start_time
        # start_time = current_time
    
        #print("Main program Jumpball=",Jumpball)
        print(f"{id:4d}, {i:9d}; {Queue:.0f}; {timestamp:.9f}; {elapsedTime:.9f}")
        # end for
        # pass  # Do some time-consuming operations here        

    return process

def NotUsed_activateTimeAwareShaper(TimeForHighPriorityQueue, TimeForLowPriorityQueue):
    
    # Create a shared array of integers (change 'd' for other data types)
    shared_array = multiprocessing.Array('d', range(3))
    # shared_array[0] = Time for Queue 0 selection
    # shared_array[1] = Time for Queue 1 selection
    # shared_array[2] = Currently selected Queue
        
    shared_array[0] = TimeForHighPriorityQueue
    shared_array[1] = TimeForLowPriorityQueue
    shared_array[2] = 0.0 

    # Create and start the process
    process = multiprocessing.Process(target=selectQueue, args=(shared_array,))
    process.start()

    start_time = time.time()

    print("ID; Line; Queue; Timestamp; Elapsed time (sec)")
    
    # You can do other things in the main program here
    for i in range(1000000):
        #time.sleep(0.2)  # Simulate some main program work
        
        # Access the modified array from shared memory
        # print("Modified array:", shared_array[:])

        Queue = shared_array[2]
        
        timestamp = time.time()
        elapsedTime = timestamp - start_time
        # start_time = current_time
    
        #print("Main program Jumpball=",Jumpball)
        print(f"{id:4d}, {i:9d}; {Queue:.0f}; {timestamp:.9f}; {elapsedTime:.9f}")
        # end for
        # pass  # Do some time-consuming operations here        

    return process

def NotWorking_selectQueue(queue_selection_process_shared_array):  
    """Function to run in the separate process."""
    """Process modifies elements in the shared array."""

    appDir = "C:\\SimLight"
    stdoutOriginal, sys.stdout, graphsPath = Log2pathCSV(appDir, "SelectQueueProcessStart")

    #timestamp = time.time()

    #appDir = "C:\\SimLight"
    #stdoutOriginal, sys.stdout, graphsPath = Log2pathCSV(appDir, "SelectQueueProcessStart")
    
    #print(f"{shared_array[3]:.0f}; Process selectQueue in {__name__:s} is running at; X; {timestamp:.9f}; X")
    
    #sys.stdout.close()
    #sys.stdout=stdoutOriginal
    
    #select Queue 0 for during the next t0 seconds
    t0 = queue_selection_process_shared_array[0]
    #select Queue 1 for during the next t1 seconds
    t1 = queue_selection_process_shared_array[1]
    print ("<p>t0=",t0)
    print ("<p>t1=",t1)
    while True:
        # select Queue 0
        queue_selection_process_shared_array[2] = 0.0
        print("<p>queue=",queue_selection_process_shared_array[2])
        time.sleep(t0)

        # select Queue 1
        queue_selection_process_shared_array[2] = 1.0
        print("<p>queue=",queue_selection_process_shared_array[2])
        time.sleep(t1)

    sys.stdout.close()
    sys.stdout=stdoutOriginal

def NotUsed_terminateTimeAwareShaper(p):
    # Wait for the time_counter process to finish (optional)
    #process.join()
    p.terminate()
'''

def generateTrafficRequests(dbConnection, N, graphsPath, X, xi, Queuelabel, queueID, distribution): #, startReqID):

    ### generate and save lamda matrix traffic request values for the video queue

    requests=[] # the original requests
    #decoratedrequests=[] # the requests extended by an extra field about the priority class (0, 1, 2) 
                        # used for sorting by class ascending and then by traffic demand descending
    lamda=[]
    rqsts=[]

    # save lamda to text file
    if (sys.argv[5]=="gensave"):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan='"+str(len(N))+"' style='background:orange;'>Generate and save lamda matrix traffic requests to the",sys.argv[6],"text file</th></tr>")
            print ("<tr><th colspan=",len(N),">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi])
            
            if distribution=="Poisson":
                #Poisson distribution
                print ("<br><em style='font-size:0.8em'>The traffic demand between each node pair is random following a Poisson distribution around a mean traffic data amount,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gbps, ")
                print ("the actual demand between a node pair is generated by a random function distributed following the Poisson process.</em></th></tr>")
            elif distribution == "Uniform":
                #Uniform distribution
                print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random with a uniform distribution within a certain range,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, ")
                print ("the actual demand between a node pair is generated by a random function uniformly distributed within the range [10,2X-10] Gb/s.</em></th></tr>")
            
        #EOP

        for x in range(len(N)):
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<tr>")
            #EOP
            for y in range(len(N)):
                if (x!=y):
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<td>")
                    #EOP
                    rnd=1 #rnd=numpy.random.randint(0, 10) #0 to 10 requests per virtual link, randomly
                        #originally I have created a version that the total traffic demand for a node pair might be the aggregation (sum) of a random number (up to 10) of sub-demands from regional routers
                    
                    if distribution=="Poisson":
                        #Poisson distribution
                        rqsts=generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(X[xi], 1) #if number greater than 1, it can be considered the grooming of Chatterjee et al.
                    elif distribution == "Uniform":
                        #Uniform ditribution
                        rqsts=generateUniformlyDistributedTrafficRequestValues(X[xi], 1) # X = [20, 40, 60, 80, 100, 120], one request
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(" m=",x,"n=",y)
                    #EOP

                    #add random class for each traffic request (0, 1, 2)
                    for i in range(len(rqsts)):
                        #trafficclass = randrange(3)
                        requests.append([x, y, rqsts[i]])
                        #decoratedrequests.append([x, y, rqsts[i], trafficclass])
                        #requests.append([x, y, rqsts[i]])
                    l=calculateLamdaMatrixSums(rqsts) #lamda is the sum of all requests for the same pair of nodes #can be considered the grooming of Chatterjee et al.
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("</td>")
                    #EOP
                else:
                    l=0
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<td>diagonal, no traffic for","m=",x,"n=",y,"</td>")
                    #EOP
                lamda.append([x, y, l])
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("</tr>")
            #EOP
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("</table>")
        #EOP

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan="+str(len(N)+1)+">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi])
            print ("<tr><td></td>")
            for i in range(len(N)):
                print("<td>%9s</td>" % N[i], end=" ")
            print("</tr>")
            for x in range(len(N)):
                print("<tr>")
                print ("<td>",N[x], "</td>", end="")
                for y in range(len(N)):
                    a=len(lamda)
                    print("<td>%9.3f</td>" % (lamda[x*len(N)+y][2]), end=" ")
                print("</tr>")
            print ("</table>")
        #EOP

        fout = open(sys.argv[6],"a")
                        # prefer to write lamda to the output text file since requests do not include the 0.0 capacity for nodes where i==Nj
        for r in lamda: #lamda include the 0.0 capacity for nodes where i==j
            #fout.write(str(r[0])+","+str(r[1])+","+"{:0.3f}".format(r[2])+"\n")
            fout.write(Queuelabel+","+str(r[0])+","+str(r[1])+","+"{:0.3f}".format(r[2])+"\n")
        fout.close()

    elif (sys.argv[5]=="load"):   # load lamda from text file NEW reads the queue labels
        fin = open(sys.argv[6],"r")
        lamda = []
        requests = []
        nextLine = fin.readline();
        while (nextLine!=""):
            temp = nextLine.split(',');
            if (temp[0] == Queuelabel):
                lamda.append([int(temp[1]),int(temp[2]),float(temp[3])])   # the input text file has the lamda matrix which includes the 0.0 capacity for nodes where i==j    
                if int(temp[1]) != int(temp[2]):                           # requests do not include the 0.0 capacity for nodes where i==j, hence remove 0.0 capacity where i==j
                    requests.append([int(temp[1]),int(temp[2]),float(temp[3])])
            nextLine = fin.readline();
    
        ''' OLD does not read the traffic reqquests file with queue labels
        elif (sys.argv[5]=="load"):   # load lamda from text file
            fin = open(sys.argv[6],"r")
            lamda = []
            requests = []
            nextLine = fin.readline();
            while (nextLine!=""):
                temp = nextLine.split(',');
                lamda.append([int(temp[0]),int(temp[1]),float(temp[2])])   # the input text file has the lamda matrix which includes the 0.0 capacity for nodes where i==j    
                if int(temp[0]) != int(temp[1]):                           # requests do not include the 0.0 capacity for nodes where i==j, hence remove 0.0 capacity where i==j
                    requests.append([int(temp[0]),int(temp[1]),float(temp[2])])
                nextLine = fin.readline();
        ''' 
        
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th style='background:cyan;'>Loaded lamda matrix traffic requests from the",sys.argv[6],"text file</th></tr>")
            print ("</table>")
        #EOP

        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan="+str(len(N)+1)+">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi])
            print ("<tr><td></td>")
            for i in range(len(N)):
                print("<td>%9s</td>" % N[i], end=" ")
            print("</tr>")
        
            for x in range(len(N)):
                print("<tr>")
                print ("<td>",N[x], "</td>", end="")
                for y in range(len(N)):
                    a=len(lamda)
                    if (x==y):
                        print("<td>%9.3f</td>" % (0.0), end=" ")
                    else:
                        print("<td>%9.3f</td>" % (lamda[x*len(N)+y][2]), end=" ") #error out of range when load #2DO
                print("</tr>")
            print ("</table>")
        #EOP

    sortTrafficRequestsDescending(requests) #the original sort order according to the Shen Tucker paper
    #sortTrafficRequestsAscending(requests)
    #sortDecoratedTrafficRequestsClassAscendingTrafficDemandDescending(decoratedrequests)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        printTrafficRequests(requests,N,"For the "+Queuelabel+" Queue.")
        #nextReqID = saveTrafficRequests2sqlite(dbConnection, requests, N, graphsPath, Queuelabel, queueID) #, startReqID)
        #saveTrafficRequests2sqlite(dbConnection, requests, N, graphsPath, Queuelabel, queueID)
        #saveTrafficRequests2csv(requests,N,graphsPath)
    #EOP

    saveTrafficRequests2sqlite(dbConnection, requests, N, graphsPath, Queuelabel, queueID)

    return requests #, nextReqID

def AggregateRequestsTraffic(N, queueVideo, queueBestEffort):

    aggregatedTraffic = []

    for qVitem in queueVideo:
        for qBEitem in queueBestEffort:
            if ( (qBEitem[0] == qVitem[0]) and (qBEitem[1] == qVitem[1]) ):
                aggregatedTraffic.append([qBEitem[0], qBEitem[1], (qBEitem[2]+qVitem[2])])

    return  aggregatedTraffic


def removeTree(path):
    
    import os
    import glob

    #select path separator based on the host OS
    pathseparator = ""
    if platform.system() == 'Windows':
        #pathseparator = "\\"
        files = glob.glob(path+"\\*.*", recursive=True)
    elif platform.system() == 'Linux':
        #pathseparator = "/"
        files = glob.glob(path+"/*", recursive=True)
    else:
        #pathseparator = "/"
        files = glob.glob(path+"/*", recursive=True)

    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            #print("Error: %s : %s" % (f, e.strerror))
            error(e.strerror, f)

    try:
        os.rmdir(path)
    except OSError as e:
        print("Error: %s : %s" % (path, e.strerror))
        error(e.strerror, path)
