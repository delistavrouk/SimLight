# -*- coding: utf-8 -*-

# Konstantinos Delistavrou 2021, 2022, 2023, 2024, 2025
# Library of subroutines for SimLight IpoWDM RWA simulator

protocol = "File:///"
#protocol = "http://"

# SOP: Start of printout
# EOP: End of printout

#2DO : elaboration needed
#Done : elaboration completed
#>>> : elaboration priority
#Novelties

CurrentRunUUID = 0

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
#EOP
'''

import numpy   # NumPy library used for calculations
import random
import sys
import os
#import shutil
import re
#import glob
import threading
import time
#import queue
#import multiprocessing
#from multiprocessing import Process, Value, Array, Pipe
#import asyncio
#import signal
import operator
import sqlite3
from datetime import datetime
#from codeClassVT import *
import platform
import numpy as np
from scipy.stats import poisson
from pyvis.network import Network   # https://pyvis.readthedocs.io/en/latest/install.html   # network visualisation https://pyvis.readthedocs.io/en/latest/tutorial.html
import shutil



class Dijkstra:
#source: https://stackoverflow.com/questions/22897209/dijkstras-algorithm-in-python

    def __init__(self, vertices, graph):
        self.vertices = vertices  # ("A", "B", "C" ...)
        self.graph = graph  # {"A": {"B": 1}, "B": {"A": 3, "C": 5} ...}

    def find_route(self, start, end):
        unvisited = {n: float("inf") for n in self.vertices}
        #print("unvisited",unvisited)
        unvisited[start] = 0  # set start vertex to 0
        visited = {}  # list of all visited nodes
        parents = {}  # predecessors
        while unvisited:
            min_vertex = min(unvisited, key=unvisited.get)  # get smallest distance
            for neighbour, _ in self.graph.get(min_vertex, {}).items():
                if neighbour in visited:
                    continue
                new_distance = unvisited[min_vertex] + self.graph[min_vertex].get(neighbour, float("inf"))
                if new_distance < unvisited[neighbour]:
                    unvisited[neighbour] = new_distance
                    parents[neighbour] = min_vertex
            visited[min_vertex] = unvisited[min_vertex]
            unvisited.pop(min_vertex)
            if min_vertex == end:
                break
        return parents, visited

    @staticmethod
    def generate_path(parents, start, end):
        path = [end]
        while True:
            key = parents[path[0]]
            path.insert(0, key)
            if key == start:
                break
        return path

def SetGlobalCurrentRunUUID(value):
    global CurrentRunUUID
    CurrentRunUUID = value

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

def SetGlobalLimitsVirtualGpW(maxFpL,maxWpF,maxGpW,virtGpW,b,maxFiC,maxLiC):
    global maxFibersPerLink
    global maxWavelengthsPerFiber
    global maxGbpsPerWavelength
    global virtualGbpsPerWavelength
    global B
    global maxGbpsPerWavelength
    global maxFiberCapacity
    global maxLinkCapacity

    maxFibersPerLink         = maxFpL
    maxWavelengthsPerFiber   = maxWpF
    maxGbpsPerWavelength     = maxGpW
    virtualGbpsPerWavelength = virtGpW
    B                        = b
    maxFiberCapacity         = maxFiC
    maxLinkCapacity          = maxLiC

def find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,start_vertex_str,end_vertex_str):
    global GlobalPrintOutEnabled

    input_vertices = Nt
    input_graph = NmC
    start_vertex = start_vertex_str
    end_vertex = end_vertex_str
    dijkstra = Dijkstra(input_vertices, input_graph)
    p, v = dijkstra.find_route(start_vertex, end_vertex)
    se = dijkstra.generate_path(p, start_vertex, end_vertex)
    #SOP
    #if (GlobalPrintOutEnabled==True) :
        #print("<li>Distance from node",start_vertex, "to node",end_vertex, "is:", v[end_vertex])
        #print("<li>Path from %s to %s is: %s" % (start_vertex, end_vertex, " &rarr; ".join(se)))
    #EOP

    pth=[]
    for i in range(len(se)):
        pth.append(nodenumber(N,se[i]))
    
    #SOP
    #if (GlobalPrintOutEnabled==True) :
        #print("<li>Path is",pth)
    #EOP

    return pth

def randomcolor(x):
    # generate a random color to use for the network graph visualisation
    # random color https://www.pythonpool.com/python-random-color/
    #              https://stackoverflow.com/questions/5796238/python-convert-decimal-to-hex
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
    # more on graph edges
    # https://pyvis.readthedocs.io/en/latest/tutorial.html#edges
    # https://visjs.github.io/vis-network/docs/network/edges.html

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


def graph_export_to_graphml(gr, path, name):
    print ("<h1>the source of the graph=",gr,"</h1>")
    pyvis_to_graphml(gr, filename="graph.graphml")


def pyvis_to_graphml(pyvis_net, filename="graph.graphml"):
    import networkx as nx

    G = nx.Graph()

    # Rebuild nodes
    for node in pyvis_net.nodes:
        node_id = node.get("id")
        if node_id is None:
            continue
        attrs = {k: v for k, v in node.items() if k != "id"}
        G.add_node(node_id, **attrs)

    # Rebuild edges
    for edge in pyvis_net.edges:
        source = edge.get("from")
        target = edge.get("to")
        if source is None or target is None:
            continue
        attrs = {k: v for k, v in edge.items() if k not in ("from", "to")}
        G.add_edge(source, target, **attrs)

    # Clean up attributes for GraphML compatibility
    for _, data in G.nodes(data=True):
        for key in list(data):
            if not isinstance(data[key], (str, int, float, bool)):
                del data[key]

    for _, _, data in G.edges(data=True):
        for key in list(data):
            if not isinstance(data[key], (str, int, float, bool)):
                del data[key]

    # Export to GraphML
    nx.write_graphml(G, filename)
    print(f"GraphML file saved as: {filename}")


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
    # Visualise network graph 
    # https://pyvis.readthedocs.io/en/latest/documentation.html
    # https://www.askpython.com/python/examples/customizing-pyvis-interactive-network-graphs
    # https://towardsdatascience.com/pyvis-visualize-interactive-network-graphs-in-python-77e059791f01
    
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
    #graph_export_to_graphml(net, grpath, 'PhysicalTopology.graphml')
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


def linkIDtoSrcDst(L, link):
    # Return the source and destination of a link, given its link number
    return L[link][0], L[link][1]

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
    sep = ","
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
    # -2 to order by the 3rd item, descending
    # data.sort(key = operator.itemgetter(-2)) #DOES NOT WORK - NEEDS FURTHER EXPLORATION - DISCARDED

    # Python Bubble Sort implementation
    # Source https://www.geeksforgeeks.org/bubble-sort/
    # Sort according to the 3rd item of each triplet which corresponds to the requested Gbps [m,n,req]

    n = len(data)
 
    # Traverse through all array elements
    for i in range(n):
 
        # Last i elements are already in place
        #for j in range(0, n-i-1):
        for j in range(0, n-1):
 
            # traverse the array from 0 to n-i-1
            # Swap if the element found is less than the next element
            if data[j][2] < data[j+1][2] :
                data[j], data[j+1] = data[j+1], data[j]

def sortDecoratedTrafficRequestsClassAscendingTrafficDemandDescending(data):
    # Sort according to the 3rd item of each triplet which corresponds to the requested Gbps [m,n,req,class]
    # order ascending by the 4th field (index 3), that is the class
    # and then order descending (minus sign) by the 3rd field (index 2), that is the capacity amount requested 
    # https://stackoverflow.com/questions/4233476/sort-a-list-by-multiple-attributes

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

def connecttoSQLiteDB(path):
    # 20-9-2025
    
    try:
        conn = sqlite3.connect(path)
        print(f"Connected to database: {path}")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def createSQLiteDB_withoutBlocking(path):
    #source: https://www.sqlite.org/docs.html
    #        https://www.geeksforgeeks.org/python-sqlite-connecting-to-database/?ref=next_article 

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
                HopSeqNum integer NOT NULL,
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
                RoutingVirtualLinksOverPhysicalTopology.HopSeqNum as routeVLoverPT_HopSeqNum,                 
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
                RoutingVirtualLinksOverPhysicalTopology.HopSeqNum as rtVLoverPTHopSeqNum,
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
            routeVLoverPT_HopSeqNum
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

        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfThreadOfTrafficRequest (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    routeTReqOverVTroutingStep integer NOT NULL,
                    NumberOfLightpathHops integer NOT NULL,
                    LatIP real NOT NULL,
                    LatTransp real NOT NULL,
                    LatEDFA real NOT NULL,
                    LatFibLen real NOT NULL,
                    ThreadLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfTrafficRequest (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    TrafficRequestLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        #13-10-2025
        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfTrafficRequestTemp (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    TrafficRequestLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
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


def createSQLiteDB(path, dbName):
    #source: https://www.sqlite.org/docs.html
    #        https://www.geeksforgeeks.org/python-sqlite-connecting-to-database/?ref=next_article 

    db_filename=dbName
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
                result text NOT NULL,
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
                result text NOT NULL,
                PRIMARY KEY (src, dst, num)
            );
        ''')

        sqliteConnection.execute('''
            CREATE TABLE IF NOT EXISTS RunID (
                uuid text NOT NULL,
                PRIMARY KEY (uuid)
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
                result text NOT NULL,
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
                HopSeqNum integer NOT NULL,
                NumberOfHops integer NOT NULL,
                ShortestpathAsInt text NOT NULL,
                ShortestpathAsStr text NOT NULL, 
                PhysicalLinkDirection text NOT NULL,
                PhysicalLinkCurrentSource integer NOT NULL,
                PhysicalLinkCurrentDestination integer NOT NULL,
                LatIP real NOT NULL,
                LatTransp real NOT NULL,
                result text NOT NULL,
                PRIMARY KEY (vlsrc, vldst,vlnum, plsrc, pldst, fiberid, waveid),
                FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num),
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
                TrafficRequests.result as TReqResult,                                 
            
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
                RoutingTrafficRequestsOverVirtualTopology.result as routeTReqOverVTresult,
                            
                VirtualLinks.src as VLsrc,
                VirtualLinks.dst as VLdst,
                VirtualLinks.num as VLnum,
                VirtualLinks.caputil as VLcaputil,
                VirtualLinks.capfree as VLcapfree,
                VirtualLinks.result as VLresult,
            
                RoutingVirtualLinksOverPhysicalTopology.vlsrc as routeVLoverPT_VLsrc,
                RoutingVirtualLinksOverPhysicalTopology.vldst as routeVLoverPT_VLdst,
                RoutingVirtualLinksOverPhysicalTopology.vlnum as routeVLoverPT_VLnum,
                RoutingVirtualLinksOverPhysicalTopology.plsrc as routeVLoverPT_PLsrc,
                RoutingVirtualLinksOverPhysicalTopology.pldst as routeVLoverPT_PLdst,
                RoutingVirtualLinksOverPhysicalTopology.fiberid as routeVLoverPT_fiberID,
                RoutingVirtualLinksOverPhysicalTopology.waveid as routeVLoverPT_waveID,
                RoutingVirtualLinksOverPhysicalTopology.type as routeVLoverPT_type,
                RoutingVirtualLinksOverPhysicalTopology.HopSeqNum as routeVLoverPT_HopSeqNum,                 
                RoutingVirtualLinksOverPhysicalTopology.NumberOfHops as routeVLoverPT_NumOfHops,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsInt as routeVLoverPT_shPathAsInt,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsStr  as routeVLoverPT_shPathAsStr,
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkDirection as routeVLoverPT_PLdir, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentSource as routeVLoverPT_currSrc, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentDestination as routeVLoverPT_currDest,
                RoutingVirtualLinksOverPhysicalTopology.LatIP as routeVLoverPT_LatIP,
                RoutingVirtualLinksOverPhysicalTopology.LatTransp as routeVLoverPT_LatTransp,
                RoutingVirtualLinksOverPhysicalTopology.result as routeVLoverPT_result,
            
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
                TrafficRequests.result as TReqResult,

                VirtualLinks.src as VLsrc,
                VirtualLinks.dst as VLdst,
                VirtualLinks.num as VLnum,
                VirtualLinks.caputil as VLcaputil,
                VirtualLinks.capfree as VLcapfree,
                VirtualLinks.result as VLresult,
                RoutingTrafficRequestsOverVirtualTopology.type as rtTRoverVT_type,
                RoutingTrafficRequestsOverVirtualTopology.routingStep as rtTRoverVTroutingStep,
                RoutingTrafficRequestsOverVirtualTopology.routStepVLseqnum as rtTRoverVTroutStpVLseqnum,
                RoutingTrafficRequestsOverVirtualTopology.result as rtTRoverVT_result,
                                 
                PhysicalLinks.src as PLsrc,
                PhysicalLinks.dst as PLdst,
                PhysicalLinks.dist as PLdistance,
                PhysicalLinks.LatEDFAs as PLlatEDFA,
                PhysicalLinks.LatFibLen as PLlatFibLen,
            
                RoutingVirtualLinksOverPhysicalTopology.fiberid as rtVLoverPTfiberID,
                RoutingVirtualLinksOverPhysicalTopology.waveid as rtVLoverPTwaveID,
                RoutingVirtualLinksOverPhysicalTopology.type as rtVLoverPTtype,
                RoutingVirtualLinksOverPhysicalTopology.HopSeqNum as rtVLoverPTHopSeqNum,
                RoutingVirtualLinksOverPhysicalTopology.NumberOfHops as rtVLoverPTnumOfHops,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsInt as rtVLoverPTshrtPathAsInt,
                RoutingVirtualLinksOverPhysicalTopology.ShortestpathAsStr  as rtVLoverPTshrtPathAsStr,
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkDirection as rtVLoverPTphysLinkDir, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentSource as rtVLoverPTcurrSrc, 
                RoutingVirtualLinksOverPhysicalTopology.PhysicalLinkCurrentDestination as rtVLoverPTcurrDst,
                RoutingVirtualLinksOverPhysicalTopology.LatIP as rtVLoverPTlatIP,
                RoutingVirtualLinksOverPhysicalTopology.LatTransp as rtVLoverPTlatTranspndr,
                RoutingVirtualLinksOverPhysicalTopology.result as rtVLoverPT_result
            
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
            routeVLoverPT_HopSeqNum
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

        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfThreadOfTrafficRequest (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    routeTReqOverVTroutingStep integer NOT NULL,
                    NumberOfLightpathHops integer NOT NULL,
                    LatIP real NOT NULL,
                    LatTransp real NOT NULL,
                    LatEDFA real NOT NULL,
                    LatFibLen real NOT NULL,
                    ThreadLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        #13-10-2025
        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfThreadOfTrafficRequestTemp (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    routeTReqOverVTroutingStep integer NOT NULL,
                    NumberOfLightpathHops integer NOT NULL,
                    LatIP real NOT NULL,
                    LatTransp real NOT NULL,
                    LatEDFA real NOT NULL,
                    LatFibLen real NOT NULL,
                    ThreadLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        #13-10-2025
        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfThreadOfTrafficRequestTemp (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    routeTReqOverVTroutingStep integer NOT NULL,
                    NumberOfLightpathHops integer NOT NULL,
                    LatIP real NOT NULL,
                    LatTransp real NOT NULL,
                    LatEDFA real NOT NULL,
                    LatFibLen real NOT NULL,
                    ThreadLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfTrafficRequest (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    TrafficRequestLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
        ''')

        #13-10-2025
        sqliteConnection.execute('''
                CREATE TABLE IF NOT EXISTS LatencyOfTrafficRequestTemp (
                    TReqQueNum integer NOT NULL,
                    TReqReqNum integer NOT NULL,
                    TrafficRequestLatency real NOT NULL,
                                    
                    PRIMARY KEY (TReqQueNum, TReqReqNum),
                    FOREIGN key (TReqQueNum, TReqReqNum) REFERENCES TrafficRequests (quenum, num)
                );
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



def insertRoutingVirtualLinksOverPhysicalTopology2sqlite(sqliteConnection, vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, type, hopseqnum, numHops, shPathAsInt, shPathAsStr, plDirection, plCurrentSource, plCurrentDestination, LatIP, LatTransp):
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
            sql += "(vlsrc,vldst,vlnum,plsrc,pldst,fiberid,waveid,type,HopSeqNum,NumberOfHops,ShortestpathAsInt,ShortestpathAsStr,PhysicalLinkDirection,PhysicalLinkCurrentSource,PhysicalLinkCurrentDestination,LatIP,LatTransp,result) "
            sql += "VALUES (%d, %d, %d, %d, %d, %d, %d, '%s', %d, %d, '%s', '%s', '%s', %d, %d, %.3f, %.3f,'%s');" % (vlsrc, vldst, vlnum, plSource, plDestination, fiberid, waveid, type, hopseqnum, numHops, shPathAsInt, shPathAsStr, plDirection, plCurrentSource, plCurrentDestination, LatIP, LatTransp,'ok')

            # source https://developer.mozilla.org/en-US/docs/Web/CSS/list-style-type
            #        https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references
            #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

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

# 3-9-2025 
def getRevisitsFromSQLite(sqliteConnection):
    sql = f"SELECT src, dst FROM TrafficRequests;"
    cursor = sqliteConnection.execute(sql)
    
    dataset = cursor.fetchall() 
    for row in dataset: 
        print("<li>",row) 
    sqliteConnection.commit()
    #print(f"<li style='list-style-type: circle;'>PhysicalLinks having source={plsrc:d} and destination={pldst:d}: {len(dataset):d}.")
    #return len(dataset)


# get totals from DB

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
        value = numpy.ceil(row[1] / B) if B > 0 else 0 # 5-10-2025 prevent division by zero
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

    #print (f"<li>&Sigma;C<sub>ij</sub> for queue {quenum:d} ",dict)

    # mathml editor https://visualmatheditor.equatheque.net/
    #        editor https://www.tutorialspoint.com/online_mathml_editor.php
    #        fundamentals https://www.w3.org/TR/MathML2/chapter2.html
    #        from MS Word https://stackoverflow.com/questions/23737171/copy-equations-from-word-in-mathml-format

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
        value = numpy.ceil(row[4] / WavelengthsPerFiber) if WavelengthsPerFiber > 0 else 0 # 5-10-2025 prevent division by zero
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


#5-10-2025
def updateVirtualLink2sqliteForHeaviestHottestFirstAndComparison(sqliteConnection, vl, utilcap, freecap, tag):
    
    try:
        sql = f"UPDATE VirtualLinks SET caputil = {utilcap:.3f}, capfree = {freecap:.3f}, result = '{tag:s}' WHERE src = {vl[0]:0d} AND dst = {vl[1]:0d} AND num = {vl[2]:0d};"

        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)
        sqliteConnection.commit()

    except sqlite3.Error as err:
        #print('<div class="error">Error occurred during INSERT INTO VirtualLinks - ', err,"</div>")
        error("Error occurred during UPDATE VirtualLinks. "+err.sqlite_errorname,err.sqlite_errorcode)



# 5-10-2025
def insertVirtualLinkLightPaths2sqliteForHeaviestHottestAndComparison(sqliteConnection, src, dst, num, caputil, capfree, tag):
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    try:
        sql = "INSERT INTO VirtualLinks (src, dst, num, caputil, capfree, result) VALUES (%d, %d, %d, %.3f, %.3f,'%s');" % (src, dst, num, caputil, capfree, tag)

        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)
        sqliteConnection.commit()

    except sqlite3.Error as err:
        #print('<div class="error">Error occurred during INSERT INTO VirtualLinks - ', err,"</div>")
        error("Error occurred during INSERT INTO VirtualLinks. "+err.sqlite_errorname,err.sqlite_errorcode)


def insertVirtualLinkLightPaths2sqlite(sqliteConnection, src, dst, num, caputil, capfree):
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    try:
        sql = "INSERT INTO VirtualLinks (src, dst, num, caputil, capfree, result) VALUES (%d, %d, %d, %.3f, %.3f,'%s');" % (src, dst, num, caputil, capfree, 'ok')

        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)
        sqliteConnection.commit()

    except sqlite3.Error as err:
        #print('<div class="error">Error occurred during INSERT INTO VirtualLinks - ', err,"</div>")
        error("Error occurred during INSERT INTO VirtualLinks. "+err.sqlite_errorname,err.sqlite_errorcode)

"""
# 5-10-2025
def insertRoutingOfTrafficRequests2sqliteForHeaviestHottestAndComparison(sqliteConnection, que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum, tag):

    #insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm")   # insert routing to sqlite table.
    try:
        sql =  "INSERT INTO RoutingTrafficRequestsOverVirtualTopology "
        sql += "(reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, type, routingStep, routStepVLseqnum, result) "
        sql += "VALUES (%d, %d, %d, %d, %d, %.3f, %.3f, '%s', %d, %d, '%s');" % (que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum, tag)
        
        ###17-9-2024 
        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)

        sqliteConnection.commit()

        ###17-9-2024 
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
"""

def insertRoutingOfTrafficRequests2sqlite(sqliteConnection, que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum):
    #insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm")   # insert routing to sqlite table.
    try:
        sql =  "INSERT INTO RoutingTrafficRequestsOverVirtualTopology "
        sql += "(reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, type, routingStep, routStepVLseqnum, result) "
        sql += "VALUES (%d, %d, %d, %d, %d, %.3f, %.3f, '%s', %d, %d, '%s');" % (que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum, 'ok')
        
        ###17-9-2024 
        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)

        sqliteConnection.commit()

        ###17-9-2024 
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




#5-10-2025
def insertRoutingOfTrafficRequests2sqliteForHeaviestHottestAndComparison(sqliteConnection, que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum, tag):
    #insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm")   # insert routing to sqlite table.
    try:
        sql =  "INSERT INTO RoutingTrafficRequestsOverVirtualTopology "
        sql += "(reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, type, routingStep, routStepVLseqnum, result) "
        sql += "VALUES (%d, %d, %d, %d, %d, %.3f, %.3f, '%s', %d, %d, '%s');" % (que, request, vlsrc, vldst, vlnum, utilcap, freecap, type, routingReqTrfStep, routReqTrfStpVLseqNum, tag) # tag is used to be able to track changes and rollback later when G1 or G2 is selected
        
        ###17-9-2024 
        #print("<li style='list-style-type: square;'>SQL query = ",sql,"</li>")

        sqliteConnection.execute(sql)

        sqliteConnection.commit()

        ###17-9-2024 
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




def saveUUID2sqlite(sqliteConnection, uuid):
    sql = "INSERT INTO RunID (uuid) VALUES ('%s');" % (uuid)

    try:
        sqliteConnection.execute(sql)    
        sqliteConnection.commit()
   
    except sqlite3.Error as err:
        #print('<div class="error">Error occurred - ', error,"</div>")
        error("Error during instertion to RunID table. "+err.sqlite_errorname, err.sqlite_errorcode)





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
            LatEDFAs = LatEDFA * (numpy.ceil(Dist[i] / EDFAdist - 1.0) + 2) if EDFAdist > 0 else 0 # 5-10-2025 prevent division by zero
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
            sql = "INSERT INTO TrafficRequests (quenum, num, src, dst, cap, result) VALUES (%d, %d, %d, %d, %.3f, '%s');" % (QueueID, reqID, TReqs[reqID][0], TReqs[reqID][1], TReqs[reqID][2],'ok')

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



def getLatencyForAllTrafficRequests():
# 19-9-2025 >>> this calculates the average per concurrent virtual link (lightpath) of a traffic request and shows the average latency of all the concurrent virtual links (routing steps) of a traffic request
    """
    SELECT 
    TReqQueNum, 
    TReqReqNum,
    MIN(TReqSrc)       AS TReqSrc,     -- or MAX(), depends on logic
    MIN(TReqDst)       AS TReqDst,
    SUM(routeTReqOverVTutilCap) AS SumUtilCap,
    AVG(TotalLatency)  AS AvgLatency
FROM (
    SELECT 
        TReqQueNum, 
        TReqReqNum,
        TReqSrc,
        TReqDst,
        routeTReqOverVTutilCap,
        routeTReqOverVTroutingStep,	
        routeTReqOverVTtype,
        SUM(routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) AS TotalLatency
    FROM route_traffic_requests_over_virtual_and_physical_topology
    GROUP BY
        TReqQueNum, 
        TReqReqNum,	
        TReqSrc,
        TReqDst,
        routeTReqOverVTutilCap,
        routeTReqOverVTroutingStep,
        routeTReqOverVTtype
) AS innerq
GROUP BY 
    TReqQueNum, 
    TReqReqNum
ORDER BY 
    TReqQueNum, 
    TReqReqNum;

    """

#the following uses the old latency formula for published measurements
def saveLatencyPerTrafficRequestToDatabase_according_to_the_old_latency_formula(sqliteConnection):

    # 20-9-2025 >>> $$$

    # SQL clause 1: aggregate latency per queue and type of routing {all/new/grm} according to the current Latency formula
    '''
    sql1 = """
        SELECT avg(TotalLatency) as avgLat, min(TotalLatency) as minLat, max(TotalLatency) as maxLat   
        FROM (	SELECT                                                                                 
        TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep,	routeTReqOverVTtype,                   
        sum (routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) as TotalLatency 
        FROM (select * from route_traffic_requests_over_virtual_and_physical_topology                 
        order by TReqQueNum,                                                                          
        TReqReqNum)                                                                                   
        WHERE                                                                                         
        TReqQueNum like '{Q:s}'                   <<< need to set the queue parameter
        AND routeTReqOverVTtype like '{Type:s}'   <<< need to set the routing parameter                      
        group by                                                                                      
        TReqQueNum, TReqReqNum,	routeTReqOverVTroutingStep                                         
        order by                                                                                       
        TReqQueNum ASC,	TReqReqNum ASC);
    """
    '''

    # SQL clause 2: aggregate latency per traffic request's routing step (concurrent transmission step) according to the current Latency formula 
    '''
    sql2 = """
        SELECT 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep,
            routeTReqOverVTtype,
            SUM(routeVLoverPT_LatIP + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) AS TotalLatency
        FROM route_traffic_requests_over_virtual_and_physical_topology
        GROUP BY 
            TReqQueNum, 
            TReqReqNum, 
            routeTReqOverVTroutingStep, 
            routeTReqOverVTtype
        ORDER BY 
            TReqQueNum ASC, 
            TReqReqNum ASC;
    """
    '''

    # SQL clause 3: aggregate latency per traffic request according to the current Latency formula 
    sql3 = """
        CREATE TABLE IF NOT EXISTS LatencyPerTrafficRequestAccordingToTheOldFormula AS
        select TReqQueNum, TReqReqNum, avg(TotalLatency) as TotalLatency
        from (SELECT 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep,
            routeTReqOverVTtype,
            SUM(routeVLoverPT_LatIP*2 + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) AS TotalLatency
        FROM route_traffic_requests_over_virtual_and_physical_topology
        GROUP BY 
            TReqQueNum, 
            TReqReqNum, 
            routeTReqOverVTroutingStep, 
            routeTReqOverVTtype
        ORDER BY 
            TReqQueNum ASC, 
            TReqReqNum ASC)
        Group By TReqQueNum, TReqReqNum
        Order By TReqQueNum ASC, TReqReqNum ASC;
    """

    cursor = sqliteConnection.execute(sql3)
    sqliteConnection.commit()


#13-10-2025 for latency cap calculation
#the following uses the old latency formula for published measurements
def calculateLatencyPerTrafficRequestTempDatabase_according_to_the_old_latency_formula(sqliteConnection):

    #13-10-2025 Temp means for latency cap 
    # SQL clause 3: aggregate latency per traffic request according to the current Latency formula 
    sql3 = """
        CREATE TABLE IF NOT EXISTS LatencyPerTrafficRequestAccordingToTheOldFormulaTemp AS
        select TReqQueNum, TReqReqNum, avg(TotalLatency)
        from (SELECT 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep,
            routeTReqOverVTtype,
            SUM(routeVLoverPT_LatIP*2 + routeVLoverPT_LatTransp + PLlatEDFA + PLlatFibLen) AS TotalLatency
        FROM route_traffic_requests_over_virtual_and_physical_topology
        GROUP BY 
            TReqQueNum, 
            TReqReqNum, 
            routeTReqOverVTroutingStep, 
            routeTReqOverVTtype
        ORDER BY 
            TReqQueNum ASC, 
            TReqReqNum ASC)
        Group By TReqQueNum, TReqReqNum
        Order By TReqQueNum ASC, TReqReqNum ASC;
    """

    cursor = sqliteConnection.execute(sql3)
    sqliteConnection.commit()


#13-10-2025 for latency cap
#the following uses the updated latency formula for future measurements
def calculateLatencyPerTrafficRequestTempDatabase(sqliteConnection):
    # 20-9-2025 >>> 
    
   

    sql="""
        SELECT 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep as ConcurrentRouteID,
            MAX(routeTReqOverVTroutStepVLseqnum)+1 AS numberOfLightpathHops_H_sd_mn
        FROM route_traffic_requests_over_virtual_and_physical_topology AS WaveLengthAssignments
        GROUP BY 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep
        ORDER BY 
            TReqQueNum ASC, 
            TReqReqNum ASC;
        """

    cursor = sqliteConnection.execute(sql)
    sqliteConnection.commit()
    
    dataset1 = cursor.fetchall() 
    for row in dataset1: 
        Q = row[0]
        R = row[1]
        C = row[2]
        H = row[3]
        #print (f"<li>queue:{Q:0d}, request:{R:0d}, concurrentRouteID:{C:0d}, numberOfLightpathHops:{H:0d}")
        sql = f"""
                SELECT                                                                                  
                        TReqQueNum,
                        TReqReqNum,
                        routeTReqOverVTroutingStep,
                        routeTReqOverVTroutStepVLseqnum,
                        routeVLoverPT_NumOfHops,
                        routeVLoverPT_LatIP,
                        routeVLoverPT_LatTransp,
                        PLlatEDFA,
                        PLlatFibLen
                FROM route_traffic_requests_over_virtual_and_physical_topology
                where
                            TReqQueNum = {Q:d}
                        and TReqReqNum = {R:d}
                        and routeTReqOverVTroutingStep = {C:d}
                order by                                                                                       
                TReqQueNum ASC,	TReqReqNum ASC, routeTReqOverVTroutingStep ASC, routeTReqOverVTroutStepVLseqnum ASC
              """
        cursor = sqliteConnection.execute(sql)
        sqliteConnection.commit()

        LatIP = 0.0
        LatTransp = 0.0
        LatWDM = 0.0
        LatEDFA = 0.0
        LatFibLen = 0.0

        dataset2 = cursor.fetchall() 
        for row in dataset2: 
            Que = row[0]
            Req = row[1]
            Rou = row[2]
            Seq = row[3]
            phH = row[4]
            L_r = row[5]
            L_t = row[6]
            L_e = row[7]
            L_f = row[8]
            #print (f"<li>queue:{Que:0d}, request:{Req:0d}, concurrentRouteID:{Rou:0d}, lightpathID:{Seq:0d}, numberOfPhysicalLinkHops:{phH:0d}, LatencyRouterPort:{L_r:0.3f}, LatencyTransponder:{L_t:0.3f}, LatencyEDFAs:{L_e:0.3f}, LatencyPropagation:{L_f:0.3f}")

            LatEDFA += L_e
            LatFibLen += L_f

        #end_for

        LatIP = 2*(H+1)*L_r
        LatTransp = 2*H*L_t
                
        LatWDM = LatTransp+LatEDFA+LatFibLen
        LatThread = LatIP + LatWDM

        sqliteConnection.execute(f'''INSERT INTO LatencyOfThreadOfTrafficRequestTemp (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep, NumberOfLightpathHops, LatIP, LatTransp, LatEDFA, LatFibLen, ThreadLatency)
                                     VALUES ({Q:d}, {R:d}, {C:d}, {H:d}, {LatIP:0.3f}, {LatTransp:0.3f}, {LatEDFA:0.3f}, {LatFibLen:0.3f}, {LatThread:0.3f});''')
        sqliteConnection.commit()

    #end_for
    
    # save latency per traffic request for all requests to the database
    
    sqliteConnection.execute('''
        INSERT INTO LatencyOfTrafficRequestTemp (
            TReqQueNum,
            TReqReqNum,
            TrafficRequestLatency
        ) 
        SELECT 
            TReqQueNum,
            TReqReqNum,
            AVG(ThreadLatency) AS avg_latency
        FROM LatencyOfThreadOfTrafficRequestTemp
        GROUP BY 
            TReqQueNum,
            TReqReqNum
        ORDER BY 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep;
    ''')
    sqliteConnection.commit()



#the following uses the updated latency formula for future measurements
def saveLatencyPerTrafficRequestToDatabase(sqliteConnection):
    # 20-9-2025 >>> 
    
   

    sql="""
        SELECT 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep as ConcurrentRouteID,
            MAX(routeTReqOverVTroutStepVLseqnum)+1 AS numberOfLightpathHops_H_sd_mn
        FROM route_traffic_requests_over_virtual_and_physical_topology AS WaveLengthAssignments
        GROUP BY 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep
        ORDER BY 
            TReqQueNum ASC, 
            TReqReqNum ASC;
        """

    cursor = sqliteConnection.execute(sql)
    sqliteConnection.commit()
    
    dataset1 = cursor.fetchall() 
    for row in dataset1: 
        Q = row[0]
        R = row[1]
        C = row[2]
        H = row[3]
        #print (f"<li>queue:{Q:0d}, request:{R:0d}, concurrentRouteID:{C:0d}, numberOfLightpathHops:{H:0d}")
        sql = f"""
                SELECT                                                                                  
                        TReqQueNum,
                        TReqReqNum,
                        routeTReqOverVTroutingStep,
                        routeTReqOverVTroutStepVLseqnum,
                        routeVLoverPT_NumOfHops,
                        routeVLoverPT_LatIP,
                        routeVLoverPT_LatTransp,
                        PLlatEDFA,
                        PLlatFibLen
                FROM route_traffic_requests_over_virtual_and_physical_topology
                where
                            TReqQueNum = {Q:d}
                        and TReqReqNum = {R:d}
                        and routeTReqOverVTroutingStep = {C:d}
                order by                                                                                       
                TReqQueNum ASC,	TReqReqNum ASC, routeTReqOverVTroutingStep ASC, routeTReqOverVTroutStepVLseqnum ASC
              """
        cursor = sqliteConnection.execute(sql)
        sqliteConnection.commit()

        LatIP = 0.0
        LatTransp = 0.0
        LatWDM = 0.0
        LatEDFA = 0.0
        LatFibLen = 0.0

        dataset2 = cursor.fetchall() 
        for row in dataset2: 
            Que = row[0]
            Req = row[1]
            Rou = row[2]
            Seq = row[3]
            phH = row[4]
            L_r = row[5]
            L_t = row[6]
            L_e = row[7]
            L_f = row[8]
            #print (f"<li>queue:{Que:0d}, request:{Req:0d}, concurrentRouteID:{Rou:0d}, lightpathID:{Seq:0d}, numberOfPhysicalLinkHops:{phH:0d}, LatencyRouterPort:{L_r:0.3f}, LatencyTransponder:{L_t:0.3f}, LatencyEDFAs:{L_e:0.3f}, LatencyPropagation:{L_f:0.3f}")

            LatEDFA += L_e
            LatFibLen += L_f

        #end_for

        LatIP = 2*(H+1)*L_r
        LatTransp = 2*H*L_t
                
        LatWDM = LatTransp+LatEDFA+LatFibLen
        LatThread = LatIP + LatWDM

        sqliteConnection.execute(f'''INSERT INTO LatencyOfThreadOfTrafficRequest (TReqQueNum, TReqReqNum, routeTReqOverVTroutingStep, NumberOfLightpathHops, LatIP, LatTransp, LatEDFA, LatFibLen, ThreadLatency)
                                     VALUES ({Q:d}, {R:d}, {C:d}, {H:d}, {LatIP:0.3f}, {LatTransp:0.3f}, {LatEDFA:0.3f}, {LatFibLen:0.3f}, {LatThread:0.3f});''')
        sqliteConnection.commit()

    #end_for
    
    # save latency per traffic request for all requests to the database
    
    sqliteConnection.execute('''
        INSERT INTO LatencyOfTrafficRequest (
            TReqQueNum,
            TReqReqNum,
            TrafficRequestLatency
        ) 
        SELECT 
            TReqQueNum,
            TReqReqNum,
            AVG(ThreadLatency) AS avg_latency
        FROM LatencyOfThreadOfTrafficRequest
        GROUP BY 
            TReqQueNum,
            TReqReqNum
        ORDER BY 
            TReqQueNum,
            TReqReqNum,
            routeTReqOverVTroutingStep;
    ''')
    sqliteConnection.commit()





def getLatencyStatsPerTrafficRequest(sqliteConnection, Q, Type):

    # 19-9-2025 >>> this falsely calculates one Lt and 2 Lr for each physical link even if there is no virtual link (lightpath) hop.
    # resulting to either more or less latency
    
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



# def EvaluateLatencyPerQueue() below does evaluate Latency (the wrong way, cummulative)
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





'''
def saveTrafficRequests2mysql(data, nodes):
    #source: https://realpython.com/python-mysql/
    #source: https://www.w3schools.com/python/python_mysql_getstarted.asp
    
    import mysql.connector # type: ignore
    now = datetime.now()
    timestamp = "y"+str(now.year)+"_m"+str(now.month)+"_d"+str(now.day)+"_h"+str(now.hour)+"_m"+str(now.minute)+"_s"+str(now.second)+"_u"+str(now.microsecond)
    mydb = mysql.connector.connect(
        host="localhost",
        user="lightuser",
        password="Success2024!",
        database="lightbase"
    )
    mycursor = mydb.cursor()
    n = len(data)
    count=0
    # Traverse through all array elements
    for i in range(n):
        count+=1
        sql = "INSERT INTO trafficrequest (reqid, src, dst, reqcap) VALUES (%d, %d, %d, %.3f)" % (count, data[i][0], data[i][1], data[i][2])
        mycursor.execute(sql)
    mydb.commit()
'''



def there_is_a_value_out_of_range(data_list, min_val, max_val):
    for value in data_list:
        if (value < min_val) or (value > max_val):
            return True;
    return False;

def poisson_range(mu, low, high, size=1):

    if low > high:
        raise ValueError("low must be less than or equal to high")

    if low < 0:
        raise ValueError("low must be non-negative")

    if not isinstance(size, int) or size <= 0:
        raise ValueError("size must be a positive integer")

    results = []
    while len(results) < size:
        samples = poisson.rvs(mu, size=size * 2) #Generate more than needed, to account for discards
        valid_samples = samples[(samples >= low) & (samples <= high)]
        results.extend(valid_samples)

    return np.array(results[:size])


def generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(apo, mexri, X, megethos):

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html#scipy.stats.poisson
    # https://www.statology.org/poisson-distribution-python/
        
    #gen_data = poisson.rvs(mu=X, size=megethos*2) #generate double size to keep valid
    
    data = poisson_range(X, apo, mexri, megethos)

    while there_is_a_value_out_of_range(data, apo, mexri):
        data = poisson.rvs(mu=X, size=megethos)

    return data


def generateUniformlyDistributedTrafficRequestValues(apo, mexri, X, megethos):
    import scipy.stats as stats

    # https://numpy.org/doc/stable/reference/random/index.html#random-quick-start
    # https://mathworld.wolfram.com/UniformDistribution.html
    # Do this (new version)
    #from numpy.random import default_rng
    
    #rng = default_rng()
    #data = rng.uniform(low=10.0, high=2.0*x-10.0, size=num)
    #data = rng.uniform(low=range_from, high=range_to, size=num)
    #data = np.random.uniform(range_from, range_to, size)

    #https://www.w3schools.com/python/numpy/numpy_random_uniform.asp
    #https://numpy.org/doc/stable/reference/random/generated/numpy.random.uniform.html
    #data=numpy.random.uniform(low=10.0, high=2.0*x-10.0, size=num)
        
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html#scipy.stats.poisson
    # https://www.statology.org/poisson-distribution-python/
        
    klimaka = mexri - apo

    data = stats.uniform.rvs(loc=apo, scale=klimaka, size=megethos)
    
    while there_is_a_value_out_of_range(data, apo, mexri):
        data = stats.uniform.rvs(loc=apo, scale=klimaka, size=megethos)

    roundata = []
    for val in data:
        roundata.append(roundatdecimals(val, 3))

    #rnd=1 #assuming one (1) request per virtual link i.e. that all the traffic of a traffic request comes from one source and not multiple sources so that the traffic is the aggregation of all these sources
    #rnd may be: rnd=numpy.random.randint(0, 10) #no requests to e.g. 10 requests per virtual link, randomly
    #noprintout#print (rnd,"random traffic amount",data,end=" for ")
    return roundata

def graphDistribution(N, a, b, lambda_param, data, distrib, filepath):
    import matplotlib.pyplot as plt
    # Parameters
    #lambda_param = 5  # Mean of Poisson distribution
    #a, b = 2, 10      # Range of interest
    #sample_size = 1000

    # Generate Poisson-distributed values within [a, b]
    #poisson_values = generate_poisson_in_range(lambda_param, a, b, 24 * 24 - 24)

    #print("poisson_values")
    #print(poisson_values)
    #print("data")
    #print(data)

    # Plot histogram
    #plt.hist(poisson_values, bins=range(a, b+2), edgecolor='black', alpha=0.7)
    
    #2-10-2025
    numberOfBins = numpy.linspace(a, b, len(N)*len(N)-len(N)) #all possible links without self-loops
    
    # this works for integer a, b
    # plt.hist(data, bins=range(a, b+2), edgecolor='black', alpha=0.7)

    # So, this works for float a, b
    # bins = numpy.linspace(a, b, 30)  # 30 equally spaced bins between a and b
    # plt.hist(data, bins=bins, edgecolor='black', alpha=0.7)
    
    # OR this works for float a, b
    # plt.hist(data, bins=np.arange(a, b + step, step), edgecolor='black', alpha=0.7)

    # OR this works for float a, b
    plt.hist(data, bins=numberOfBins, range=(a, b), edgecolor='black', alpha=0.7)

    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(f'Histogram of {len(data)} values {distrib} distributed with mean X={lambda_param} in range [{a}, {b}]')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(filepath, format = 'png', bbox_inches='tight',dpi=300)
    #plt.show(block=False)
    #plt.pause(1)
    plt.close()
    



def find_path(graph, start, end, path=[]):
    # source https://www.python.org/doc/essays/graphs/

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

"""
def find_all_paths(graph, start, end, path=[]):
    #source https://www.python.org/doc/essays/graphs/

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
"""

def find_shortest_path_using_bfs(graph, src, dst):
    # def bfs_shortest_path(graph, start, goal):

    from collections import deque

    # sources 
    # https://docs.python.org/3/library/collections.html#collections.deque
    # https://www.almabetter.com/bytes/cheat-sheet/dsa
    # https://www.educative.io/answers/how-to-implement-a-breadth-first-search-in-python
    # https://favtutor.com/blogs/breadth-first-search-python
    # https://stackabuse.com/courses/graphs-in-python-theory-and-implementation/lessons/breadth-first-search-bfs-algorithm/
    # https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/ 
    
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

'''
def find_all_paths_using_bfs(graph, src, dst):
    """
    Finds all paths from source to destination using breadth-first search.

    Args:
        graph: A dictionary representing the graph, where keys are vertices and
               values are lists of their neighbors.
        src: The source vertex.
        dst: The destination vertex.

    Returns:
        A list of lists, where each inner list represents a path from src to dst.
    """
    from collections import deque
    queue = deque([(src, [src])])
    all_paths = []
    visited = set()  # Track visited nodes to prevent cycles in already explored paths.

    while queue:
        vertex, path = queue.popleft()

        if vertex == dst:
            all_paths.append(path)
            # Do NOT return here. Continue to find other paths.
        if vertex not in visited or vertex == src: #allow the source to be visited multiple times
            if vertex != src:
                visited.add(vertex)

            for neighbor in graph.get(vertex, []):
                queue.append((neighbor, path + [neighbor]))

    return all_paths
'''


def find_all_simple_paths_bfs(graph, src, dst):
    from collections import deque

    """
    Finds all SIMPLE paths from source to destination using breadth-first search.

    Args:
        graph: A dictionary representing the graph, where keys are vertices and
               values are lists of their neighbors.
        src: The source vertex.
        dst: The destination vertex.

    Returns:
        A list of lists, where each inner list represents a simple path from src to dst.
    """
    queue = deque([(src, [src])])
    all_simple_paths = []

    while queue:
        vertex, path = queue.popleft()

        if vertex == dst:
            all_simple_paths.append(path)
            continue  # Continue to find other simple paths

        for neighbor in graph.get(vertex, []):
            if neighbor not in path:  # Ensure no repeated nodes in the current path
                queue.append((neighbor, path + [neighbor]))

    #return all_simple_paths
    return sorted(all_simple_paths, key=len)


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

"""
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
"""

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


"""
def roundatdecimals(val, dec):
    if numpy.isnan(val):
        error("The value is not a number",555)
        return -1
    if isinstance(val, str):
        val = float(val)
    return numpy.round(val, decimals=dec, out=None)
"""



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

def htmlhead(title, lenQs, distribution):
    #heading for html output
    # CSS info found at http://www.w3schools.com
    # source for HTML character entities https://html.spec.whatwg.org/multipage/named-characters.html#named-character-references
    
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
        print("<h2><em>"+title+" Routing and Wavelength Assignment algorithm for traffic requests on ")
        print(f"{('a single queue' if lenQs==1 else (str(lenQs)+' queues')):s}");
        print(", having the requested capacities randomised by following a "+distribution+" distribution process.</em></h2>")
        print("<h3 style='text-align:center'>Implementation by <em>Konstantinos Delistavrou</em> &copy; 2021-2025</h3><hr>")
    #EOP

def mathPowerFormula():
    # https://fred-wang.github.io/MathFonts/mozilla_mathml_test/
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
    # https://fred-wang.github.io/MathFonts/mozilla_mathml_test/
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
    # https://fred-wang.github.io/MathFonts/mozilla_mathml_test/
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
    # https://fred-wang.github.io/MathFonts/mozilla_mathml_test/
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

def updateTotals(struct, key, val): #function that updates totals in a dictionary
    # struct is the dictionary
    # key is the key of the dictionary
    # val is the value to be added to the total of the key
    if key in struct:   #if the key exists in the structure then accumulate
        tmp = struct.get(key)
        tmp += val
    else:               #if the key does not exist in the structure then create it
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



def routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypassWithForceGrooming(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):

    # 6-4-2025
    

    page =  f"""
                <table class='data' style='border-collapse: collapse; width: 100%; background-color: lightcoral;'>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>startingStep</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{startingStep}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>gr</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{gr}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>nodes</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{nodes}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>Queue</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{Queue}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>QueueID</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{QueueID}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>vt</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{vt}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>vtl</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{vtl}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>vtfreecaps</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{vtfreecaps}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>maxGbpsPerWavelength</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{maxGbpsPerWavelength}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>VTFinal</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{VTFinal}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>ReqRouteInfo</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{ReqRouteInfo}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>graph_path</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{graph_path}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>Ncolours</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{Ncolours}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>ReUsedLightpaths</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{ReUsedLightpaths}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>LightpathReuses</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{LightpathReuses}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>TotalLightpaths</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{TotalLightpaths}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>VLIDs</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{VLIDs}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>dbConnection</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{dbConnection}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>VirtualLinkIDs</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{VirtualLinkIDs}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>VirtualLinkTReqs</th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{VirtualLinkTReqs}</td></tr>
                <tr><th style='background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; text-align: left;'>VirtualLinkTotals   </th><td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{VirtualLinkTotals   }</td></tr>
                </table>
            """

    print(f"<div>{page}</div>")

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
    numOfReqs = len(Queue)
    #n1 = len(q1)
    #TotalNumberOfTrafficRequestsOnBothQueues = n #+n1 # ex n
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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
    #EOP

    CurrentQueue = QueueID

    while step <= numOfReqs: # TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        # Solution D with simulation time estimated/approximated
        #CurrentQueue = QueueVideoTurn(0.75) # this works! using random parameter with probability 0.75

        startTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        RequestTime = nsec2msec(startTReq - startRoutingOverVT)
        
        Qtime = RequestTime % 100.0
                
        if CurrentQueue==QueueID and currentrequest<numOfReqs:
            treq = Queue[currentrequest] # treq = traffic request
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
                
                # Try to route it over existing paths of the virtual topology that have adequate free capacity with the classic MultiHop Bypass
                if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   
                
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)
                    
                    #graph_add_edge(gr,data[i][0],data[i][1],str(CapForTheLogicalLink),"free:0")

                # else, if it cannot be routed over existing paths of the virtual topology that have all the required capacity, then
                # try to route it over existing paths of the virtual topology that have less free capacity than the required by breaking the required capacity into smaller chunks
                elif (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypassForceGrooming(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):
                    #6-4-2025 
                
                    #if routing succeded
                    RoutingOfRequestedTrafficStep += 1
                    RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0

                    #routed the required capacity successfully
                    remain = roundatdecimals( (remain - CapForTheLogicalLink), 3)

                #if it cannot be routed over existing paths of the virtual topology , then add a new virtual link for it
                elif (addNewVirtualLinkToTheVirtualTopology(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber) == 0):
                        
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
                else:
                    print(f"<li>Warning! The remainder {remain} Gbps of the traffic demand could not be routed over the virtual topology!")
                    error("The remaining required capacity could not be routed over the virtual topology!",111)

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





def routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    
    #6-9-2025 this is the original version of the subroutine, used in multihop bypass

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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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







def routeAllTrafficRequestsOfOneQueueOverVirtualTopologyHeaviestFirstAndComparison(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):
    #traffic requests einai to Queue
    #30-9-2025


    #6-9-2025 this is the original version of the subroutine, used in multihop bypass

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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
    #EOP

    CurrentQueue = QueueID

    while step <= TotalNumberOfTrafficRequestsOnBothQueues: # process all traffic requests from all queues
                
        startTReq = time.process_time_ns() # count the time per traffic request, not for each lightpath of the traffic request

        #time_from_start = startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp

        #select queue based on time passed (simulation time, not system time)
        #ReqTime = abs(startof_serving_current_TRreq_timestamp - startof_serving_all_TRreqs_timestamp)
        RequestTime = nsec2msec(startTReq - startRoutingOverVT)
        
        Qtime = RequestTime % 100.0

        if CurrentQueue==QueueID and currentrequest<n:
            treq = Queue[currentrequest] # treq = traffic request
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
                print ("<td>Remain",remain,"Gbps to be routed.</td>")

                f.write(f"Que {fromQueue:4d} ~ Req {req:4d} ~ Remain Gbps {remain:10.3f}\n")
            
                graph_add_node(gr,treq[0],apo,Ncolours)
                graph_add_node(gr,treq[1],pros,Ncolours)
            
                #print ("<td class='actions' style='font-size:0.8em'>")
                print ("<td class='actions'>")
            #EOP

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







def routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass_checkingForRevisits_usedbyHybridBypass(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, N, Nt, NmC):
    
    #6-9-2025 this is the new version of the subroutine for Hybrid Bypass, where I check for revisits
    # >>>>>>> on this routine I have to perform the wavelength assignment for each routing of a traffic request over a virtual link and check for no revisits in case of traffic grooming before I move to the next traffic request
    # >>>>>>> in order not to modify a lot the code, temporarily I will intervene only in case of traffic grooming to perform the wavelength assignment only to check for revisits and repeat the routing of the traffic request only in case of revisit
    #2DO >>>> at some point a redesign of the data structures and parameters must take place to avoid data redundancy (πλεονασμός δεδομένων)

    startingStep = startingStep -1
    
    # 12-10-2025 count paths with revisits
    numberOfPathsWithRevisitWhichRoutedDirectly = 0

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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                
                # 6-9-2025 this is the point that this routine for Hybrid Bypass routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass_checkingForRevisits_usedbyHybridBypass()
                #          differs from the regular routeAllTrafficRequestsOfOneQueueOverVirtualTopologyMultihopBypass()
                #          on this one the following routine also checks for revisits
                
                # for MultiHop Bypass: if (routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
                
                # new, for Hybrid Bypass:
                
                #12-10-2025
                returnedremainingcapacity, numPathsAbortedDueToRevisit = routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass_checkforRevisits(nodes, que, req, treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep, N, Nt, NmC)
                numberOfPathsWithRevisitWhichRoutedDirectly += numPathsAbortedDueToRevisit
                if (returnedremainingcapacity == 0):   
                    
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

    return startingStep+step, numberOfPathsWithRevisitWhichRoutedDirectly




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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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








#6-4-2025 

#Boithitikes functions

def get_virtual_link_ids(virtual_link_ids_dict, source_dest_tuple):
    """
    Retrieves the array of virtual link IDs for a given (source, destination) tuple.

    Args:
    virtual_link_ids_dict: A dictionary where keys are (source, destination) tuples
                            and values are lists of virtual link IDs.
    source_dest_tuple: The (source, destination) tuple for which to retrieve the IDs.

    Returns:
    The list of virtual link IDs associated with the tuple, or None if the tuple
    is not found in the dictionary.
    """
    if source_dest_tuple in virtual_link_ids_dict:
        return virtual_link_ids_dict[source_dest_tuple]
    else:
        return None




#πρεπει να βρω πρωτα όλες τις διαδρομές από την πηγή στον προορισμό
#ταξινομώ ως προς τη συντομότερη με τη μεγαλύτερη διαθέσιμο χωρητικότητα
# μετα να βρω τη μεγιστη ελευθερη χωρητικοτητα για αυτη τη διαδρομη
#μετα να αναθεσω την κινηση που χωρα στη διαδρομη αυτη
#μετα να αφαιρεσω την κινηση που περασε απο τη διαδρομη απο την ζητουμενη κινηση
#μετα να επαναλαβω οσο υπαρχει ζητουμενη κινηση, μεχρι να μηδενιστει η ζητουμενη κινηση
def routeOneVirtualLinkOverTheVirtualTopologyMultihopBypassForceGrooming(nodes, queID, requestID, Ni,      Nj,      vt, vtl, vtfrcap,    requiredcap,          maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep): #, costs):
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
        #
        
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
            print ("<li>The virtual topology is NOT empty, hence looking for free capacity to groom. Trying to force traffic grooming by splitting remaining traffic demand to smaller chunks.")
            print ("<li>Current virtual topology", vt,".")
            print ("<li>Required capacity", requiredcap,".")
            print (f"<li>All paths from source {Ni} to destination {Nj} sorted by path length ascending:")
        #EOP

        allpaths = find_all_simple_paths_bfs(vt, Ni, Nj)

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<li>",allpaths) # ola ta paths apo src pros dst
        #EOP

        for path in allpaths: # gia kathe path
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print("<li>Examining virtual path",path)
            #EOP
            pathmaxfreecapacity = 0   #estw to free capacity tou path
            links = path2links(path) # metatrepw to path se links
            for linkarray in links:  # gia kathe link
                #print ("<li>Link array",linkarray)
                linktuple = tuple(linkarray)     # metatrepw to [s,d] se (s,d) gia na psaksw se VirtLinkIDs
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print ("<li>Examining link",linkarray)
                #EOP
                IDs = VirtualLinkIDs[linktuple] # get link IDs [0, 1, 2, ...] for the (source,dest) tuple
                for id in range(len(IDs)): #gia kathe link ID ftiaxnw to tuple to virt link (s, d, num(or id)) gia na psaksw sto virtual link totals
                    x = [] 
                    x.append(linkarray[0])
                    x.append(linkarray[1])
                    x.append(id)
                    t = tuple(x)
                    vlfreecap = VirtualLinkTotals[t][1] # briskw to free capacity tou virt link [caputilised(0), capfree(1), numofTReqs(2)] 
                    if vlfreecap > 0:
                        if pathmaxfreecapacity == 0:
                            pathmaxfreecapacity = vlfreecap 
                        elif vlfreecap < pathmaxfreecapacity:
                            pathmaxfreecapacity = vlfreecap 
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print (f"<li>Link with ID {t} has free capacity {vlfreecap}.")
                    #EOP
            #SOP
            if (GlobalPrintOutEnabled==True) :
                print (f"<li>Virtual path {path} has free capacity {pathmaxfreecapacity}.")
            #EOP
            

            # από εδώ να ελέγξω! 6-4-2025
            

            #edw an to path exei free capacity > 0 tote tha ginei grooming 
            if (pathmaxfreecapacity > 0):   #dromologise apo auto to path, a.k.a. grooming
                #SOP
                if (GlobalPrintOutEnabled==True) :
                    print("<li><em>Forced traffic grooming</em>: Routing part of the required capacity via this path!")
                #EOP
                            
                # Count the number of used lightpaths (virtual links) 
                # One path in the virtual topology has many virtual links or lightpaths
                # Therefore, when there is grooming the number of reused lightpaths is incremented by the number of virtual links of the path in virtual topology
                
                LightpathReuses[0] = LightpathReuses[0] + len(links)
                #LightpathReuses[0] = LightpathReuses[0] + len(path2links(path))

                for link in links: #path2links(path):   #for each link of each path reused
                    if link not in ReUsedLightpaths:
                        ReUsedLightpaths.append(link)
                
                #requestrouted = True
                #6-4-2025 #remaincap = roundatdecimals( (remaincap - requiredcap), 3)
                print(f"<li>Required {remaincap} Gbps to be traffic groomed.")
                print(f"<li>Groomed {pathmaxfreecapacity} Gbps.")
                remaincap = roundatdecimals( (remaincap - pathmaxfreecapacity), 3)
                print(f"<li>Remain {remaincap} Gbps to be traffic groomed.")
                

                #remaincap = numpy.round(remaincap, decimals=3, out=None)
                #print("<li>Remaining capacity for this request is",remaincap)

                #SOP
                if (GlobalPrintOutEnabled==True) :
                    #ypologise ti menei free gia kathe link tou path pou xrisimopoiithike telika
                    print("<li>Virtual links of the virtual path", links)
                #EOP
                
                #RoutingOfRequestedTrafficStepVirtualLinkSequenceNumber = 0
                
                routOfReqTrffcStpVLseqNum = 0
                
                for link in links: #path2links(path):   #for each link of each path found
                    #VTofVLwithonlyAdequateCapacity, VLofUniqueAdequateFreeCapacities
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<li>Subtract the utilised capacity from the Link's", links,"free capacity.")
                    #EOP
                    tlink = tuple(link)
                    s, d = linkSrcDst(L, link)
                    #linkfreecap=getVirtualLinkFreeCapacity(vtl, vtfrcap,tlink)
                    
                    #requiredcap
                    #vl = getVLfromSD(... ,s,d)
                    
                    vls = links #6-4-2025 #find_keys_with_common_source_destination(VLofUniqueAdequateFreeCapacities, s, d)
                    
                    '''
                    #6-4-2025 #
                    if len(vls)>1:
                        error("More than a single virtual link for a single source destination found in the list of unique adequate free capacities virtual links",9)
                    '''

                    #Done now it updates the free capacity of the correct virtual link based on the virtual link id tuple (s,d,n) referred to also as (s,d,i)
                    vl = vls[0]
                    
                    print("<li>Update the free capacity by subtracting the utilised capacity from the Link's", links,"free capacity.")
                    
                    updateVirtualLinkTReq(VirtualLinkTReqs,vl,queID,requestID,requiredcap,"Grm")
                    updateVirtualLinkTotals(VirtualLinkTReqs, VirtualLinkTotals, vl)

                    freecap = getVLfreecapacity(VirtualLinkTotals,vl)

                    graph_update_edge(gr,queID,requestID,s,d,freecap,maxGbpsPerWavelength,-1*requiredcap)

                    LinkFreeCap = updateVitualLinkFreeCapacity(vtfrcap, tlink, (-1*requiredcap))

                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(f"<li>Updated Virtual Link's ({vl[0]:d},{vl[1]:d},{vl[2]:d}) free capacity to {freecap:.3f}.")
                    #EOP

                    updateVirtualLink2sqlite(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap)
                    
                    
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
            if remaincap == 0:
                break

            #6-4-2025 #i = i + 1   # increment counter to access all paths found 

        #SOP
        if (GlobalPrintOutEnabled==True) :
            #6-4-2025 #if (requestrouted == True):
            if (remaincap==0):
                print("<li>Request routed successfully over multiple existing paths!")
            else:
                print("<li>Request not routed over existing paths, due to lack of free capacity on paths' links.")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Remaining capacity for this request is",remaincap)
    #EOP

    remaincap = roundatdecimals(remaincap,3) # remaincap=numpy.round(remaincap, decimals=3, out=None)
    return remaincap



# 30-9-2025 Used for Lee & Rhee Heaviest / Hottest first and comparison implementation
#def routeOneVirtualLinkOverTheVirtualTopologyWithTrafficGroomingForHeaviestHottestAndComparison(nodes, queID, requestID, Ni, Nj, vt, vtl, vtfrcap, requiredcap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep):
#5-10-2025 tag marks temporary update and insertion to keep final virtual topology data later after selection of G1 or G2
def routeOneVirtualLinkOverTheVirtualTopologyWithTrafficGroomingForHeaviestHottestAndComparison(nodes, queID, requestID, Ni, Nj, vt, vtl, vtfrcap, requiredcap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep, tag):
    # the original function taken from multihop bypass and modified had also graphs, this one does not
    # def routeOneVirtualLinkOverTheVirtualTopologyWithTrafficGrooming(nodes, queID, requestID, Ni,      Nj,      vt, vtl, vtfrcap,    requiredcap,          maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep): #, costs):

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
        #this is not like multihop bypass, here we do not add a new virtual link if the VT is empty
        #we just return the required capacity as remaining capacity to be routed

        return remaincap
    
        '''
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<li>The virtual topology is empty, hence adding a new virtual link.")
        #EOP

        #<<< 9-9-2024 added 
        routOfReqTrffcStpVLseqNum = 0
        
        
        if (addNewVirtualLinkToTheVirtualTopologyNoGraphs(nodes, queID, requestID, Ni, Nj, vt, vtl, vtfrcap, requiredcap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum) == 0):
            #added new link to route 40G successfully
            remaincap = roundatdecimals( (remaincap - requiredcap), 3)
            #remaincap=numpy.round(remaincap, decimals=3, out=None)
        '''
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

            if (pathhasenoughfreecap == True):   #dromologise apo auto to path   # aka traffic grooming
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

                    #30-9-2025 #graph_update_edge(gr,queID,requestID,s,d,freecap,maxGbpsPerWavelength,-1*requiredcap)

                    LinkFreeCap = updateVitualLinkFreeCapacity(vtfrcap, tlink, (-1*requiredcap))

                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(f"<li>Updated Virtual Link's ({vl[0]:d},{vl[1]:d},{vl[2]:d}) free capacity to {freecap:.3f}.")
                    #EOP

                    #updateVirtualLink2sqlite(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap)
                    updateVirtualLink2sqliteForHeaviestHottestFirstAndComparison(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap, tag) #G1 since traffic grooming
                    
                    appendPerRequestLinks(ReqRouteInfo,queID, requestID,vl,"Grm",requiredcap, routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum) #2 -> pou allou ginetai auto? Ginetai kai sto ###1 otan neo virtual link ("New") #append R with every link and capacity to fulfill the groomed request capacity
                    appendFinalVT(VTfinal,nodes,s,d,requiredcap,"Grm") 

                    #insert every link of the path to the routing table
                    virtlinkID = getVLIDwithfreecapacity(VLIDs,link[0], link[1])   # get the VLID for a virtual link from Ni to Nj that has free capacity.
                    
                    #5-10-2025 insert with temporary tag "G1" for Heaviest / Hottest and Comparison implementation since this is traffic grooming
                    #insertRoutingOfTrafficRequests2sqlite(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm", routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum)   # insert routing to sqlite table.
                    insertRoutingOfTrafficRequests2sqliteForHeaviestHottestAndComparison(dbConnection, queID, requestID, vl[0],vl[1],vl[2], requiredcap, freecap, "Grm", routingOfReqTrafficStep, routOfReqTrffcStpVLseqNum, tag) #G1 since traffic grooming


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

            if (pathhasenoughfreecap == True):   #dromologise apo auto to path   # aka traffic grooming
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
                    #EOP

                    updateVirtualLink2sqlite(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap)
                    
                    
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



#6-9-2025
def routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass_checkforRevisits(nodes, queID, requestID, Ni, Nj, vt, vtl, vtfrcap, requiredcap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection,VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, routingOfReqTrafficStep, N, Nt, NmC):
   #routeOneVirtualLinkOverTheVirtualTopologyMultihopBypass(nodes, que,   req,       treq[0], treq[1], vt, vtl, vtfreecaps, CapForTheLogicalLink, maxGbpsPerWavelength, VTFinal, ReqRouteInfo, gr, ReUsedLightpaths, LightpathReuses, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals, RoutingOfRequestedTrafficStep) == 0):   #try to route it over existing paths of the virtual topology
    # this version uses queues
    # this version uses the new dictionary VirtualLinkTotals

    global GlobalPrintOutEnabled

    revisits = False
    
    #12-10-2025 count paths with revisits
    numberOfPathsWithRevisitWhichRoutedDirectly = 0

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
        # VLofUniqueAdequateFreeCapacities is a list of the virtual links that have free capacity for the possible grooming and constitute the new virtual topology. 
        # Moreover, if more than one virtual links from the same source to the same destination exist and each has adequate free capacity to host the current traffic request, 
        # then the virtual link with the minimum adequate free capacity is selected to participate in this list for economy.
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

            if (pathhasenoughfreecap == True):   #if enough free capacity 

                # 6-9-2025 here I must do the Wavelength assignment for each virtual link of the virtual path and check for revisits
                #>>>
                #8-9-2025 EDW elegxw giarevisit an to virtual path den exei 2 nodes, ara perissotera, ara to virtual path apoteleitai apo perissotera virtual links ara exei noima na elenxw gia revisit afou tha dimiourgithei pysical path pou isws exei revisits afou gia ena virtual link den prokyptei physical path me revisits
                
                print ("<li>The length of the virtual path is ",len(path),".")
                if (len(path) == 2):
                    revisits = False #for a virtual path of a single virtual link (2 nodes) the Dijkstra algorithm will output a shortest physical path without node revisits
                    print ("<li>The virtual path has a single virtual link and so not checked for revisits since the shortest path algorithm will output a physical path without node revisits.")
                else:
                    print ("<li>The virtual path has more than one virtual links and so it will be checked for revisits.")
                    revisits = VirtualPathLeadsToRevisitsOnPhysicalTopology(path, N, Nt, NmC)   # EDW elegxw gia revisits

                if (revisits == False):   # if there are no revisits then keep routing and route traffic via this path   
                
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
                    print("<li>Remaining capacity for this request is",remaincap)

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
                        #EOP

                        updateVirtualLink2sqlite(dbConnection, vl, maxGbpsPerWavelength-freecap, freecap)
                        
                    
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
                        
                else:
                    numberOfPathsWithRevisitWhichRoutedDirectly += 1
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print("<li>Despite traffic grooming could be realised, this virtual path leads to revisits on the physical topology, hence aborted.")
                    #EOP
                    
                    i = allpathslen # trick to stop iteration for all virtual links in case of revisits

            i = i + 1   # increment counter to access all paths found 

        #SOP
        if (GlobalPrintOutEnabled==True) :
            if (requestrouted == True):
                print("<li>Request routed successfully over an existing path!")
            else:
                if revisits:
                    print("<li>Despite the existance of available capacity on current vairtual paths, the request was not routed over them since this would lead to node revisits on the physical layer.")
                else:
                    print("<li>Request not routed over existing paths, due to lack of free capacity on paths' links.")
        #EOP

        #if (requestrouted == True): # 6-9-2025 elegxw gia revisits pio panw, oxi edw  --> elwgxw prin theorisw to request oti exei ginei routed! #OLD comment: if request routed then I will check for revisits
        #    pass                     

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<li>Remaining capacity for this request is",remaincap)
    #EOP

    remaincap = roundatdecimals(remaincap,3) # remaincap=numpy.round(remaincap, decimals=3, out=None)

    # 12-10-2025 not only return the remaining capacity as a indication of successful routing (if it is 0) but also return the number of paths that could not use traffic grooming due to revisits
    return remaincap, numberOfPathsWithRevisitWhichRoutedDirectly





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
            #commonSD = find_keys_with_common_source_destination(newVLfreeCap,key[0:2]) # https://www.geeksforgeeks.org/python-minimum-value-keys-in-dictionary/
            if len(commonSD)>1: #if there are at least 2 VL with common s,d. Otherwise it will compare with itself
                #print("<li>virtual links with common source destination ",commonSD)
                
                #minfreecap = min(newVLfreeCap.values())
                #minfreecapKey = [k for k in newVLfreeCap if newVLfreeCap[k] == minfreecap]
                #minfreecap = min(commonSD.values())
                #minfreecapKey = [k for k in commonSD if commonSD[k] == minfreecap]
                #print("<li>minimum free capacity among common source destination is {",minfreecapKey,":",minfreecap,"}")
                
                #maxfreecap = max(newVLfreeCap.values())
                #maxfreecapKey = [k for k in newVLfreeCap if newVLfreeCap[k] == maxfreecap]
                #maxfreecap = max(commonSD.values())
                #maxfreecapKey = [k for k in commonSD if commonSD[k] == maxfreecap]
                #print("<li>maximum free capacity among common source destination is {",maxfreecapKey,":",maxfreecap,"}")
                #kleidi = maxfreecapKey
                #newVLfreeCap.pop(kleidi,None)
                #del newVLfreeCap[kleidi]

                k = getkeyofmaxfreecapacity(newVLfreeCap,commonSD)
                del newVLfreeCap[k]
                #verynewVLfreeCap = removeVL(newVLfreeCap,maxfreecapKey)
                #del newVLfreeCap
                #newVLfreeCap = verynewVLfreeCap
                
                #print("<li>Current temp list of VL free capacities",newVLfreeCap)
                
            #add the freecap to the other dictionary of (s,d):freecap
            #VLsdKey = (key[0],key[1])
            #VLsourcedestinations.update({VLsdKey:value}) # add free capacity to the other dictionary
            #for k in VLsourcedestinations.keys():
            #    if VLsourcedestinations[k] < 
            #commonSD = find_keys_with_common_source_destination(newVLfreeCap,key[:2])
    
    #newVLfreeCap = keepVirtualLinksWithCommonSourceDestinationWithLowerFreeCapacity(newVLfreeCap)

    #create a new complementary virtual topology and add nodes only for the links that have adequate free capacity
    #vtnew = appenddictionaryvalueslist(newVTfreeCap)
    vtnew = convertVirtualLinksList2VirtualTopology(newVLfreeCap)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        #print ('<li>New list of virtual links with adequate Free Capacities only = ',newVLfreeCap)
        # New list of virtual links with adequate Free Capacities only = {(1, 0): [14.0], ...}
        print("<li>New VT only having VL with adequate free capacity required by the traffic request for possible grooming.")
        printVTdictionaryAsTable(vtnew)
        print("<li>New list of VL with adequate free capacity required by the traffic request for possible grooming.")
        printVLdictionaryAsTable(newVLfreeCap)
        #print ('<li>New VT with links of adequate free Capacity = ',vtnew)
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
#def find_keys_with_common_source_destination(data, prefix):
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


def printVLids(dict):
    if len(dict)>0:
        longestvalue = len(max(dict.values(), key=len)) # find the longest value in a dictionary - source: https://stackoverflow.com/questions/23554249/how-to-print-the-longest-dictionary-value
        #longestkey = len(max(dict.keys(), key=len)) # find the longest key in a dictionary
        
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


def printRoutingOfVirtualLinksOverWavelengthsWithLimitResultsAsTable_Copy(dict1, dict2):

    if len(dict1)>0 and len(dict2)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='8'>Routing of Virtual Link over the Physical Topology (wavelengths) WITH Result</th></tr>")
        print("<tr><th colspan='8'>{(Virtal Link):[(WavelengthID 1, WavelengthID 2, ...),RESULT], ...}<br>")
        print("{(source, destination, number): [(source, destination, fiberID, wavelengthID), ...], ...}</th>")
        print("</tr>")
        print("<tr><th colspan='3'>Virtual Link</th><th colspan='5'>Wavelength ID, RESULT</th></tr>")
        print("<tr><th>source</th><th>destination</th><th>number</th><th>source</th><th>destination</th><th>fiberID</th><th>wavelengthID</th><th>Result</th></tr>")

        for key in dict1:
            numberofphysicallinks = len(dict1[key][0])
            print("<tr>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[1]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[2]:d}</td>")

            i = 0
            while i < numberofphysicallinks:
                print("<td rowspan='1'>",dict1[key][0][i][0],"</td>")
                print("<td rowspan='1'>",dict1[key][0][i][1],"</td>")
                print("<td rowspan='1'>",dict1[key][0][i][2],"</td>")
                print("<td rowspan='1'>",dict1[key][0][i][3],"</td>") #from 1st dictionary (routings)
                print("<td rowspan='1'>",dict2[key],"</td>")    #from 1st dictionary (results)
                
                if i == numberofphysicallinks-1:
                    print("</tr><tr>")
                else:
                    print("</tr>")
                
                i += 1
                
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")


def printRoutingOfVirtualLinksOverWavelengthsWithLimitResultsAsTable(dict1, dict2):

    dict1 = normalize_dict(dict1)

    if len(dict1)>0 and len(dict2)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='8'>Routing of Virtual Link over the Physical Topology (wavelengths) WITH Result</th></tr>")
        print("<tr><th colspan='8'>{(Virtal Link):[(WavelengthID 1, WavelengthID 2, ...),RESULT], ...}<br>")
        print("{(source, destination, number): [(source, destination, fiberID, wavelengthID), ...], ...}</th>")
        print("</tr>")
        print("<tr><th colspan='3'>Virtual Link</th><th colspan='5'>Wavelength ID, RESULT</th></tr>")
        print("<tr><th>source</th><th>destination</th><th>number</th><th>source</th><th>destination</th><th>fiberID</th><th>wavelengthID</th><th>Result</th></tr>")

        for key in dict1:
            numberofphysicallinks = len(dict1[key])
            print("<tr>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[1]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[2]:d}</td>")

            i = 0
            while i < numberofphysicallinks:
                print("<td rowspan='1'>",dict1[key][i][0],"</td>")
                print("<td rowspan='1'>",dict1[key][i][1],"</td>")
                print("<td rowspan='1'>",dict1[key][i][2],"</td>")
                print("<td rowspan='1'>",dict1[key][i][3],"</td>") #from 1st dictionary (routings)
                print("<td rowspan='1'>",dict2[key],"</td>")    #from 1st dictionary (results)
                
                if i == numberofphysicallinks-1:
                    print("</tr><tr>")
                else:
                    print("</tr>")
                
                i += 1
                
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>")




def printRoutingOfVirtualLinksOverWavelengthsWithLimitResultsAsTableForHeaviestHottestFirstAndComparison(dict1, dict2):

    dict1 = normalize_dict(dict1)

    if len(dict1)>0 and len(dict2)>0:
        print("<table class='dictionary'>")
        print("<tr><th colspan='8'>Routing of Virtual Link over the Physical Topology (wavelengths) WITH Result</th></tr>")
        print("<tr><th colspan='8'>{(Virtal Link):[(WavelengthID 1, WavelengthID 2, ...),RESULT], ...}<br>")
        print("{(source, destination, number): [(source, destination, fiberID, wavelengthID), ...], ...}</th>")
        print("</tr>")
        print("<tr><th colspan='3'>Virtual Link</th><th colspan='5'>Wavelength ID, RESULT</th></tr>")
        print("<tr><th>source</th><th>destination</th><th>number</th><th>source</th><th>destination</th><th>fiberID</th><th>wavelengthID</th><th>Result</th></tr>")

        for key in dict1:
            numberofphysicallinks = len(dict1[key])
            print("<tr>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[0]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[1]:d}</td>")
            print(f"<td rowspan='{numberofphysicallinks:d}'>{key[2]:d}</td>")

            i = 0
            while i < numberofphysicallinks:
                print("<td rowspan='1'>",dict1[key][i][0],"</td>")
                print("<td rowspan='1'>",dict1[key][i][1],"</td>")
                print("<td rowspan='1'>",dict1[key][i][2],"</td>")
                print("<td rowspan='1'>",dict1[key][i][3],"</td>") #from 1st dictionary (routings)
                print("<td rowspan='1'>",dict2[key],"</td>")    #from 1st dictionary (results)
                
                if i == numberofphysicallinks-1:
                    print("</tr><tr>")
                else:
                    print("</tr>")
                
                i += 1
                
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
        longestvalue = len(max(dict.values(), key=len)) # https://stackoverflow.com/questions/23554249/how-to-print-the-longest-dictionary-value
        longestkey = len(max(dict.keys(), key=len))
        #first_key = list(dict)[0]
        #keylen = len(first_key)
        #value = dict[first_key]

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

        longestvalue = len(max(dict.values(), key=len)) # https://stackoverflow.com/questions/23554249/how-to-print-the-longest-dictionary-value
        #longestkey = len(max(dict.keys(), key=len))

        #first_key = list(dict)[0]
        #value = dict[first_key]
        
        print("<table class='dictionary'>")
        print("<tr><th>Source</th>")
        #cols = len(value)
        #print(f"<th colspan='{cols:d}'>Destinations</th></tr>")
        print(f"<th colspan='{longestvalue:d}'>Destinations</th></tr>")
        
        for key in dict:
            print("<tr>")
            print("<td>",key,"</td>")
            for data in dict[key]:
                print("<td>",data,"</td>")
            print("</tr>")
        print("</table>")
    else:
        print("<table class='dictionary'><tr><th>&emptyset;</th></tr></table>") # https://dev.w3.org/html5/spec-LC/named-character-references.html



def convertVirtualLinksList2VirtualTopology(listVLs):
    # gets keys (s,d,i) and converts to {s: [d,...],...}
    #print ('<ol><li>In appenddictionaryvalueslist',newVTfreeCap)
    #Shen & Tucker care about power but I need to be deterministic about the resources utilised since I want to monitor all the path of the information
    
    #print("<li>Convert virtual links with adequate capacity to virtual topology of virtual links with adequate capacity")
    #print("<li>Since I have more than one queues, if it happens to have more than one virtual link with adequate capacity from the same source to the same destination, then I will use the virtual link with the lower free capacity for economy (anyway the input list has only virtual links with adequate capacity, hence there is no worry to select a virtual link that does not have enough free capacity.)")
    #print("<li>List of virtual links with adequate free capacity listVLs",listVLs)

    M = list(listVLs.keys()) #get a list of [(s,d,i),...]
    #print("<li>keys of the list",M)
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


# 30-9-2025 Used for Lee & Rhee Heaviest first and comparison implementation
#5-10-2025 tag marks temporary update and insertion to keep final virtual topology data later after selection of G1 or G2
def addNewVirtualLinkToTheVirtualTopologyWithoutGroomingDirectBypassRoutingForHeaviestHottestAndComparison(nodes, que, req, Ni, Nj, vt, vtl, vtfrcap, cap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, VirtualLinkTotals, RoutReqTrfStp, RoutReqTrafficStpVLSeqNum, tag, addEdgeWhenFreeCapacityOnly = True):
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

    #now (2024-Aug) I use the following 3 dictionaries to keep information related to routing
    #print("<li>Virtual Link IDs = {(s,d):[0,1,2,...],...}")
    #printVLids(VirtualLinkIDs)
    #print("<li>Virtual Link Traffic Requests = {(s,d,i):[(que,req,cap,type),...],...}")
    #printVLTReqs(VirtualLinkTReq)
    #print("<li>Virtual Link Totals = {(s,d,i):[caputil, capfree, num_of_TReqs],...}")
    #printVLTotals(VirtualLinkTotals)
    
    #5-10-2025
    #insertVirtualLinkLightPaths2sqlite(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3))
    insertVirtualLinkLightPaths2sqliteForHeaviestHottestAndComparison(dbConnection, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3), tag)

    #insertRoutingOfTrafficRequests2sqlite(dbConnection, que, req, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3), "New", RoutReqTrfStp, RoutReqTrafficStpVLSeqNum)
    insertRoutingOfTrafficRequests2sqliteForHeaviestHottestAndComparison(dbConnection, que, req, newVL[0], newVL[1], newVL[2], cap, roundatdecimals((maxGbpsPerWavelength - cap),3), "New", RoutReqTrfStp, RoutReqTrafficStpVLSeqNum, tag)

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
                pass
                #graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
        else:
            pass
            #graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
    #EOP
    
    remaincap = remaincap - cap
    #remaincap=numpy.round(remaincap, decimals=3, out=None)
    roundatdecimals(remaincap,3)
    #print("<li>Remaining capacity to be routed:",remaincap)

    return remaincap



# 30-9-2025 Used for Lee & Rhee Heaviest first and comparison implementation
def addNewVirtualLinkToTheVirtualTopologyNoGraphs(nodes, que, req, Ni, Nj, vt, vtl, vtfrcap, cap, maxGbpsPerWavelength, VTfinal, ReqRouteInfo, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReq, VirtualLinkTotals, RoutReqTrfStp, RoutReqTrafficStpVLSeqNum, addEdgeWhenFreeCapacityOnly = True):
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

    #now (2024-Aug) I use the following 3 dictionaries to keep information related to routing
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
                pass
                #graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
        else:
            pass
            #graph_add_edge(gr,Ni,Nj,"que"+str(que)+",req:"+str(req)+","+str(nodes[Ni])+"&rarr;"+str(nodes[Nj])+",cp:"+str(cap)+",fr:"+str(LogicalLinkFreeCapacity), "fr:"+str(LogicalLinkFreeCapacity))
    #EOP
    
    remaincap = remaincap - cap
    #remaincap=numpy.round(remaincap, decimals=3, out=None)
    roundatdecimals(remaincap,3)
    #print("<li>Remaining capacity to be routed:",remaincap)

    return remaincap






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

    #now (2024-Aug) I use the following 3 dictionaries to keep information related to routing
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







# 22-9-2025 new route Virtual Links Over Physical Topology Common for Hybrid Direct Multi-hop With Limited Fibers WaveLength Continuity
# THE ORIGINAL IDEA WAS TO INTERLACE THE CALCULATION OF BLOCKINGS DURING THE ROUTING OF VIRTUAL LINKS OVER THE PHYSICAL TOPOLOGY AND THE ASSIGNMENT OF WAVELENGTHS
# NOT USED
def routeVirtualLinksOverPhysicalTopologyNewCommonforHybridDirectMultiHopWithLimitedFibersWaveLengthContinuity(VLs, N, Nt, NetworkWavelengthsMap, maxGbpsPerWavelength, maxWavelengthsPerFiber, maxFibersPerLink, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, dist, HasWavConv, distEDFA,Cost, wavelengthIDs, LatRouterPort, LatTransponder, dbConnection):
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

    # Τα VL έχουν δημιουργηθεί εξυπηρετώντας πρώτα τα TReq με το μεγαλύτερο demand. Άρα, τα πρώτα VL αφορούν TReq με μεγαλύτερο traffic.
    # Προς το παρόν (23-9-2025) το αφήνω έτσι. Μια άλλη λογική είναι να αναδιατάξω τα VL ώστε να εξυπηρετηθούν πρώτα αυτά που εξυπηρετούν μεγαλύτερο πλήθος από TReq.

    dataForAllVLsRouting = {}

    for vlink in VLs:   #for each virtual link of the VT
        dataForCurrentVL = {}

        start_vertex_str = vlink[0]
        end_vertex_str = vlink[1]

        ShortestPath = find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,start_vertex_str,end_vertex_str) #σε επόμενη φάση μπορεί αν αποτυγχάνει λόγω wavelngth continuity constraint, θα μπορεί να βρεθεί το αμέσως μεγαλύτερο path για να γίνει προσπάθεια δρομολόγησης
        
        #temp
        sp = ShortestPath

        SPnodes=len(ShortestPath)   #length of the shortest path
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

        #23-9-2025
        #old fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid) #OLD
        #@@@
        #24-9-2025

        print("</table")

        #^^^^^^^^^24-9-2025
        #!!!!!!!!!!!!!!!!!!!!!!

        dataForCurrentVL["ShortestPath"]=ShortestPath
        dataForCurrentVL["virtlinkid"]=virtlinkid

        WavAssignSuccess, reason, linkID, fiberID, waveID = assignWavelengthChannelsConsideringLimits(NetworkWavelengthsMap, L, HasWavConv, ShortestPath, virtlinkid)
        
        #24-9-2025
        # palia epestrefa kathe fora fiberid kai waveid giati den ypirxe periorismos 
        # twra prepei na balw periorismo giati isws ginei block to virtual link kai ara kai to request
        
        print ("<p>Routine: routeVirtualLinksOverPhysicalTopologyNewCommonforHybridDirectMultiHopWithLimitedFibersWaveLengthContinuity()")

        print ("<p><li>wavelength Assignment Result:",WavAssignSuccess)
       
        print_reservations(NetworkWavelengthsMap, L)

        #>>> 25-9-2025 edw prepei na pairnw tin apofasi block H oxi
        #              an den einai block krataw oli tin pliroforia pou xreiazomai gia na typoso kai na ypologisw meta
        #                                 katopin synexizv me to epomeno,
        #              an einai block prepei na simeiwsw to VL ws block
        #                             na brw to TReq kai na to markarw ws block
        #                             na afairesw ola ta VL pou exoun traffic mono apo auto to TReq

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
        
        #prepei na dw ti tha kanw me ta fiberid waveid
        
        """
        24-9-2025
        isws exei ginei assignment 
        isws omws exei ginei block!
        ara prepei na ta problepw!
        """
        #fiberid, waveid = 0, 0

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

        #5-9-2025 Physical hop sequence number aka PhyHopSeqNum is the sequence number of the hop the transmission for a Virtual Link follows
        PhyHopSeqNum = 0
        
        #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid) den xreiazetai pleon

        if (fiberid!=-1) and (waveid!=-1):
            PhysicalLinkSource = L[physlinkid][0]
            PhysicalLinkCurrentSource = sp[0]
            PhysicalLinkCurrentDestination = sp[1]
            if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                PhysicalLinkDirection = "fwd" # forward #forward transmission direction on the physical link for the current transmission of traffic 
            else:
                PhysicalLinkDirection = "rev" # reverse #reverse transmission direction on the physical link for the current transmission of traffic 

            #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
            #Done
            #2DO insertFiberWavelengthAssignments2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #Done and renamed function to insertRoutingVirtualLinksOverPhysicalTopology2sqlite()

            ### 20-9-2025 will not insert 2*router port latency because the way the latency is calculated has changed insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
            
        updateTotals(Wmn, physlinkid, wvl)
        updateTotals(CUmn, physlinkid, roundatdecimals(cap,3))

        #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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
                                    
                #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)
                #24-9-2025 prepei na dw ti tha kanw me ta fiberid kai waveid
                WavAssignSuccess, linkID, fiberID, waveID = assignWavelengthChannelsConsideringLimits(NetworkWavelengthsMap, L, HasWavConv, ShortestPath)
                    
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
                    
                    PhyHopSeqNum += 1 # increment the physical hop sequence number

                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #20-9-2025 not 2*router port latency any more insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
                
                updateTotals(Wmn, physlinkid, wvl)
                updateTotals(CUmn, physlinkid, cap)
               
                #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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

    print ("<li>Physical Links", physicalLinks)
    print ("<li>Routing Of Virtual Links Over Wavelengths", RoutingOfVirtualLinksOverWavelengths)

    return physicalLinks, RoutingOfVirtualLinksOverWavelengths


#<24-9-2025 replace def routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass() with older version - this might be corrupted>
"""
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

        #5-9-2025 Physical hop sequence number aka PhyHopSeqNum is the sequence number of the hop the transmission for a Virtual Link follows
        PhyHopSeqNum = 0
        
        #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)

        if (fiberid!=-1) and (waveid!=-1):
            PhysicalLinkSource = L[physlinkid][0]
            PhysicalLinkCurrentSource = sp[0]
            PhysicalLinkCurrentDestination = sp[1]
            if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                PhysicalLinkDirection = "fwd" # forward #forward transmission direction on the physical link for the current transmission of traffic 
            else:
                PhysicalLinkDirection = "rev" # reverse #reverse transmission direction on the physical link for the current transmission of traffic 

            #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
            #Done
            #2DO insertFiberWavelengthAssignments2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #Done and renamed function to insertRoutingVirtualLinksOverPhysicalTopology2sqlite()

            ### 20-9-2025 will not insert 2*router port latency because the way the latency is calculated has changed insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
            
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
                    
                    PhyHopSeqNum += 1 # increment the physical hop sequence number

                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #20-9-2025 not 2*router port latency any more insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
                
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
"""
#</24-9-2025 replace def routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass() with older version - this might be corrupted>

#<24-9-2025 routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass() restored from previous date
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

        #5-9-2025 Physical hop sequence number aka PhyHopSeqNum is the sequence number of the hop the transmission for a Virtual Link follows
        PhyHopSeqNum = 0
        
        #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)

        if (fiberid!=-1) and (waveid!=-1):
            PhysicalLinkSource = L[physlinkid][0]
            PhysicalLinkCurrentSource = sp[0]
            PhysicalLinkCurrentDestination = sp[1]
            if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                PhysicalLinkDirection = "fwd" # forward #forward transmission direction on the physical link for the current transmission of traffic 
            else:
                PhysicalLinkDirection = "rev" # reverse #reverse transmission direction on the physical link for the current transmission of traffic 

            #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
            #Done
            #2DO insertFiberWavelengthAssignments2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #Done and renamed function to insertRoutingVirtualLinksOverPhysicalTopology2sqlite()

            ### 20-9-2025 will not insert 2*router port latency because the way the latency is calculated has changed insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
            
        updateTotals(Wmn, physlinkid, wvl)
        updateTotals(CUmn, physlinkid, roundatdecimals(cap,3))

        #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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
                    
                    PhyHopSeqNum += 1 # increment the physical hop sequence number

                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #20-9-2025 not 2*router port latency any more insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
                
                updateTotals(Wmn, physlinkid, wvl)
                updateTotals(CUmn, physlinkid, cap)
               
                #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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





#<5-10-2025 routeVirtualLinksOverPhysicalTopologyCommonforMultiAndDirectBypass() restored from previous date
#    routeVirtualLinksOverPhysicalTopologyForHeaviestHottestAndComparison(G1VT, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, Dist, EDFAdist, Dist, wavelegthids, LatRouterPort, LatTransponder)
#def routeVirtualLinksOverPhysicalTopologyForHeaviestHottestAndComparison(VLs, virtualtopology, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, dist, distEDFA,Cost, wavelengthIDs, LatRouterPort, LatTransponder):
def routeVirtualLinksOverPhysicalTopologyForHeaviestHottestAndComparison(VLs, N, Nt, maxGbpsPerWavelength, maxWavelengthsPerFiber, Er, Et, Ee, Wmn, CUmn, fmn, Em, Nm, NmC, L, dist, distEDFA,Cost, wavelengthIDs, LatRouterPort, LatTransponder):
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

        #5-9-2025 Physical hop sequence number aka PhyHopSeqNum is the sequence number of the hop the transmission for a Virtual Link follows
        PhyHopSeqNum = 0
        
        #fiberid,waveid = assignWavelengthid(maxWavelengthsPerFiber, wavelengthIDs, physlinkid)

        if (fiberid!=-1) and (waveid!=-1):
            PhysicalLinkSource = L[physlinkid][0]
            PhysicalLinkCurrentSource = sp[0]
            PhysicalLinkCurrentDestination = sp[1]
            if (PhysicalLinkCurrentSource == PhysicalLinkSource):
                PhysicalLinkDirection = "fwd" # forward #forward transmission direction on the physical link for the current transmission of traffic 
            else:
                PhysicalLinkDirection = "rev" # reverse #reverse transmission direction on the physical link for the current transmission of traffic 

            #2DO use virtual link id (s,d,n) instead virtuallink step to save in DB
            #Done
            #2DO insertFiberWavelengthAssignments2sqlite(dbConnection, physlinkid,fiberid,waveid,virtlinkid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #Done and renamed function to insertRoutingVirtualLinksOverPhysicalTopology2sqlite()

            ### 20-9-2025 will not insert 2*router port latency because the way the latency is calculated has changed insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
            #5-10-2025 no insert to DB 
            #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
            
        updateTotals(Wmn, physlinkid, wvl)
        updateTotals(CUmn, physlinkid, roundatdecimals(cap,3))

        #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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
                    
                    PhyHopSeqNum += 1 # increment the physical hop sequence number

                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #20-9-2025 not 2*router port latency any more insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, 2*LatRouterPort, LatTransponder)
                    #5-10-2025 no insert to DB 
                    #insertRoutingVirtualLinksOverPhysicalTopology2sqlite(dbConnection, vlSrc, vlDst, vlNum, plSrc, plDst, fiberid, waveid, PLtype, PhyHopSeqNum, len(sp)-1, sp, path2str(sp,N), PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatRouterPort, LatTransponder)
                
                updateTotals(Wmn, physlinkid, wvl)
                updateTotals(CUmn, physlinkid, cap)
               
                #25-9-2025 the following are the physicalLinks [src,dst,fiber,free capacity]
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



def routeAllRequestsOfOneQueueOverVirtualTopologyDirectBypassWithVirtualGbpsPerWavelength(startingStep, gr, nodes, Queue, QueueID, vt,vtl,vtfreecaps, maxGbpsPerWavelength, virtualGbpsPerWavelength, VTFinal, ReqRouteInfo, graph_path, Ncolours, ReUsedLightpaths, LightpathReuses, TotalLightpaths, VLIDs, dbConnection, VirtualLinkIDs, VirtualLinkTReqs, VirtualLinkTotals):

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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                print("<li>A new virtual link will be created since Direct Bypass is applied.")
            #EOP
            
            # 29-08-2024

            # CapForTheLogicalLink = maxGbpsPerWavelength
            #if remain >= maxGbpsPerWavelength:      ### 30-03-2025 programming the virtual wavelength capacity
            if remain >= virtualGbpsPerWavelength:   ### 30-03-2025 programming the virtual wavelength capacity
                #CapForTheLogicalLink = maxGbpsPerWavelength
                CapForTheLogicalLink = virtualGbpsPerWavelength
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
        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                print("<li>A new virtual link will be created since the requirement is routed using Direct Bypass.")
            #EOP
            
            # 29-08-2024

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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                        
            # 29-08-2024

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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                        
            # 29-08-2024

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

        f = open(graph_path+pathseparator+'QueuesServingPattern_methodAthreads.txt', 'a')
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
                        
            # 29-08-2024

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
    X=[]
    nets=[]
    runConfigs = []
    distributions = []
    printout = ""
    keepeveryNreport = ""
    lamdagensaveload = ""
    lamdafile = ""
    name = ""
    description = ""
    version = ""
    runs = 0
    pdfout = ""
    numberofqueues = ""
    computername = ""
    progfolder = ""

    fin = open(file,"r")

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    while (nextLine!="[Config_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 

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
        keepeveryNreport = int(keepeveryNreport)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Lambda]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        lamdagensaveload = nextLine
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[LambdaTextFile]"):
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
    if (nextLine=="[RunConfigurations(Program,Strategy,Queues)_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[RunConfigurations(Program,Strategy,Queues)_end]"):
            runConfigs.append(nextLine.split(','))
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

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
    if (nextLine=="[Distributions_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[Distributions_end]"):
            #nextLine = removeNewLine(nextLine); 
            distributions.append(nextLine)
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Config_end]"):
        fin.close()
    
    return name, description, version, runs, X, nets, printout, keepeveryNreport, lamdagensaveload, lamdafile, pdfout, numberofqueues, computername, progfolder, distributions, runConfigs
           

def setTextCaptions(LatencyTimeUnit4csv):
    #LatencyTimeUnit4csv = 'micro'+"sec"  #microseconds

    txtCaptions = ""
    txtCaptions += "UUIDofRun;"
    txtCaptions += "Timestamp;"
    txtCaptions += "Computer(name);"
    txtCaptions += "ProgramFolder(path);"
    txtCaptions += "Algorithm(name);"
    txtCaptions += "Queues(num);"
    txtCaptions += "SchedulingStrategy(name);"
    txtCaptions += "Experiment(name);"
    txtCaptions += "Network(name);"
    txtCaptions += "Nodes(num);"
    txtCaptions += "Links(num);"
    txtCaptions += "X(Gbps);"
    txtCaptions += "Distribution(name);"
    txtCaptions += "TotalCapacityProcessed(Gbps);"
    txtCaptions += "PowerIPRouters(kWatt);"
    txtCaptions += "PowerWDMTransponders(kWatt);"
    txtCaptions += "PowerEDFAs(kWatt);"
    txtCaptions += "PowerTotal(kWatt);"
    txtCaptions += "ProcessTime(sec);"
    txtCaptions += "TotalLightpaths(num);"
    txtCaptions += "ReusedLightpaths(num);"
    txtCaptions += "ReusedLightpaths(%);"
    txtCaptions += "AverageLightpathReuses(num);"
    txtCaptions += "AverageWavelengthsUtilisation(%);"
    txtCaptions += "AverageFiberLinksUtilisation(%);"
    txtCaptions += "TrReq_AvgLat_AllQs_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_AllQs_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_AllQs_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_AllQs_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_AllQs_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_AllQs_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_AllQs_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_AllQs_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_AllQs_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(HP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(HP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(HP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(HP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(HP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(HP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(HP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(HP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(HP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(LP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(LP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(LP)_AnyTypeRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(LP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(LP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(LP)_NewVLRoutingOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_AvgLat_Q(LP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MinLat_Q(LP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "TrReq_MaxLat_Q(LP)_GrmOverVT("+LatencyTimeUnit4csv+");"
    txtCaptions += "Limitations;"
    txtCaptions += "MaxFibersPerLink(num);"
    txtCaptions += "MaxWavelengthsPerFiber(num);"
    txtCaptions += "MaxGbpsPerWavelength(Gbps);"
    txtCaptions += "Latency_Router_port("+LatencyTimeUnit4csv+");"
    txtCaptions += "Latency_Transponder("+LatencyTimeUnit4csv+");"
    txtCaptions += "Traffic_QueueHP(%);"
    txtCaptions += "Traffic_QueueLP(%);"

    txtCaptions += "PassLPs(VLs)(num);"
    txtCaptions += "BlockedLPs(VLs)(num);"
    txtCaptions += "PassLPs(VLs)(%);"
    txtCaptions += "BlockedLPs(VLs)(%);"

    txtCaptions += "PassTRs(num);"
    txtCaptions += "BlockedTRs(num);"
    txtCaptions += "PassTRs(%);"
    txtCaptions += "BlockedTRs(%);"

    
    
    txtCaptions += "Node_Revisits(boolean);"
    txtCaptions += "Paths_With_Revisits_Which_Routed_Directly(num);"

    txtCaptions += "LightpathsCheckedForHardLatencyCap(num);"

    txtCaptions += "LightpathsBlockedByHardLatencyCapOn_Q_HP(num);"
    txtCaptions += "LightpathsBlockedByHardLatencyCapOn_Q_LP(num);"

    

    txtCaptions += "\n"
    
    return txtCaptions



def readConfigNew(file):
    cfgName = ""
    cfgDescription = ""
    cfgVersion = ""
    cfgRuns = 0
    cfgX = []
    cfgNets=[]
    cfgPrintout = ""
    cfgKeepEveryNthReport = 0
    cfgLamdagensaveload = ""
    cfgLamdaFile = ""
    cfgPdfOut = ""
    cfgRunConfigs = []
    cfgComputerName = ""
    cfgProgFolder = ""
    cfgDistributions = []    
    cfgLimitConfigs = []
    cfgLatencyComponent = []
    cfgQHPpercentTrafficSplit = []
    cfgCheckForRevisits = ""
    cfgHardLatencyCap_Q_HP = 0.0
    cfgHardLatencyCap_Q_LP = 0.0
    
    #numberofqueues = ""

    fin = open(file,"r")

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    while (nextLine!="[Config_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine);     
    if (nextLine=="[Name]"):
        nextLine = fin.readline();  
        nextLine = removeNewLine(nextLine); 
        cfgName = nextLine
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Description]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgDescription = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Version]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgVersion = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Runs]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgRuns = int(nextLine)

    while (nextLine!="[Xi where X={2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 400, 640, 960, 1280}]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 

    #nextLine = fin.readline(); 
    #nextLine = removeNewLine(nextLine); 
    #if (nextLine=="[Xi where X={2, 4, 6, 8, 10, 15, 20, 30, 40, 50, 60, 80, 100, 120, 160, 200, 320, 640, 960, 1280}]"):
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine);
    cfgX = nextLine.split(',')

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Nets_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[Nets_end]"):
            cfgNets.append(nextLine)
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Printout]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgPrintout = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[KeepEveryNthReport]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgKeepEveryNthReport = int(nextLine) 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Lambda]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgLamdagensaveload = nextLine
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[LambdaTextFile]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgLamdaFile = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[PDFout]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgPdfOut = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[RunConfigurations(Program,Queues,Strategy)_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[RunConfigurations(Program,Queues,Strategy)_end]"):
            cfgRunConfigs.append(nextLine.split(','))
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[ComputerName]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgComputerName = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[ProgramFolder]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgProgFolder = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Distributions_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[Distributions_end]"):
            #nextLine = removeNewLine(nextLine); 
            cfgDistributions.append(nextLine)
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[LimitConfig(FibersPerLink, WavelengthsPerFiber, WavelengthCapacity)_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[LimitConfig(FibersPerLink, WavelengthsPerFiber, WavelengthCapacity)_end]"):
            cfgLimitConfigs.append(nextLine.split(','))
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[LatencyComponentConfig(LRouterport,LTransponder)_start]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        while (nextLine!="[LatencyComponentConfig(LRouterport,LTransponder)_end]"):
            cfgLatencyComponent.append(nextLine.split(','))
            nextLine = fin.readline();
            nextLine = removeNewLine(nextLine); 

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[QHP_percent_of_traffic_split]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine);
        cfgQHPpercentTrafficSplit = nextLine.split(',')

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[CheckForRevisits]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgCheckForRevisits = nextLine

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[HardLatencyCap_Q_HP microsec]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgHardLatencyCap_Q_HP = float(nextLine)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[HardLatencyCap_Q_LP microsec]"):
        nextLine = fin.readline(); 
        nextLine = removeNewLine(nextLine); 
        cfgHardLatencyCap_Q_LP = float(nextLine)

    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine); 
    if (nextLine=="[Config_end]"):
        fin.close()
    
    return cfgName, cfgDescription, cfgVersion, cfgRuns, cfgX, cfgNets, cfgPrintout, cfgKeepEveryNthReport, cfgLamdagensaveload, cfgLamdaFile, cfgPdfOut, cfgRunConfigs, cfgComputerName, cfgProgFolder, cfgDistributions, cfgLimitConfigs, cfgLatencyComponent, cfgQHPpercentTrafficSplit, cfgCheckForRevisits, cfgHardLatencyCap_Q_HP, cfgHardLatencyCap_Q_LP

    

def readData(file): #read network data from text file
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
    
    nextLine = fin.readline(); 
    nextLine = removeNewLine(nextLine);
    #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
    if (nextLine=="[HasWavConv]"):
        nextLine = fin.readline();
        nextLine = removeNewLine(nextLine);
        #inLine = inLine + 1; print("Read line ",inLine,":"+nextLine+".")
        tmp = nextLine.split(',')
        HasWavConv = list(map(float, tmp))
        #print ("Dist",Dist)

    fin.close()

    return netName, N, L, Nm, Dist, HasWavConv



def removeTempFiles(dir, pattern):
    #https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern

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






























#<25-9-2025> calculation of traffic blocking due to criteria: limited fibers per link, wavelength continuity constraint

def decideLimitations(N, HasWavConv, maxFibersPerLink):
    NumOfWavConv = 0
    
    #WavConvInAllNodes = 1
    #for hwc in HasWavConv:
    #    WavConvInAllNodes *= hwc
    
    if maxFibersPerLink<=0:
        return "NoBlocking"
    else:
        WavConv = 1
        for hwc in HasWavConv:
            WavConv *= hwc
        if WavConv == 1:
            return "NumFibers"
        elif WavConv == 0:
            return "WavContinuity"



def blockTrafficAccordingToCriteria(L, RoutingOfVirtualLinksOverWavelengths, criterion, HasWavConv):
    """
    NetworkWavelengthsMap
    Network
    [	
        Lnk [	 W   W   W   W   W   W   W   W   W   W   W   W   W   W   W   W
            Fbr ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''], 	
            Fbr	['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']	
        ],
        Lnk [	 W	 W   W   ...                                             W
            Fbr	['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''], 	
            Fbr	['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']	
        ],
        ...
        Lnk [    W	 W   W   ...                                             W
            Fbr	['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''], 	
            Fbr	['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']	
        ]	
    ]
    """
    """
    NetworkWavelengthsMap = [] # 3D matrix (link, fiber, wavelength channel) to keep information about wavelength channels assignment for the whole network) 
                            # I assume that each link has the same amount of fibers per link and each fiber has the same amount of wavelength channels per fiber
    for linkID in range(len(L)):
        LinkFibersMap = []
        for fiberID in range(maxFibersPerLink):
            FiberWavelegthsMap = []
            for wavelengthID in range(maxWavelengthsPerFiber):
                FiberWavelegthsMap.append("")
            LinkFibersMap.append(FiberWavelegthsMap)
        NetworkWavelengthsMap.append(LinkFibersMap)
    #print("<li>",NetworkWavelengthsMap)
    """

    print("<li><em>Will calculate blocking according to the criterion:",criterion)

    NetworkWavelengthsMap = [[["" for _ in range(maxWavelengthsPerFiber)] for _ in range(maxFibersPerLink)] for _ in range(len(L))]

    newRoutingWithLimits, resultRouting = assignWavelengthChannelsConsideringLimits_FollowingWavelengthsAssignment(L, RoutingOfVirtualLinksOverWavelengths, NetworkWavelengthsMap, criterion, HasWavConv)
    
    print_reservations(NetworkWavelengthsMap, L)
    
    return newRoutingWithLimits, resultRouting, NetworkWavelengthsMap


#</25-9-2025>

""" 
#<24-9-2025>
def linknumber(data, m, n):
    # Return the number of a link, given its source and destination nodes
    
    for i in range(len(data)):
        if ( (data[i][0]==m) and (data[i][1]==n) ) or ( (data[i][0]==n) and (data[i][1]==m) ):
            return i
    return None
"""

def find_the_same_free_wavelength_for_lightpath(link_ids, netmap):
    """Find a single wavelength index free on *all* links (but fibers may differ)."""
    num_fibers = len(netmap[0])
    num_wavelengths = len(netmap[0][0])
    for w in range(num_wavelengths):
        Found = True
        for link in link_ids:
            if not any(netmap[link][fiber][w] == '' for fiber in range(num_fibers)):
                Found = False
                break
        if Found:
            return w
    return None

def find_free_wavelength_same(link_ids, netmap):
    """Find a single wavelength index free on *all* links (but fibers may differ)."""
    num_fibers = len(netmap[0])
    num_wavelengths = len(netmap[0][0])
    for w in range(num_wavelengths):
        ok = True
        for link_id in link_ids:
            if not any(netmap[link_id][fiber][w] == '' for fiber in range(num_fibers)):
                ok = False
                break
        if ok:
            return w
    return None

def reserve_fiber(link, wavelength, VLtag, L):
    """Reserve a given wavelength on one fiber (any free fiber)."""
    print("<li>try to reserve the wavelength",wavelength,"on any fiber of link", link)
    for fiber in range(len(L[link])):
        if L[link][fiber][wavelength] == '':
            L[link][fiber][wavelength] = VLtag
            print("<li>found fiber", fiber)
            return fiber
    return None

def find_any_free_wavelengths_along_the_path(link_ids, path, path_tag, netmap):
    """Reserve any wavelength on any free fiber of the path."""
    num_fibers = len(netmap[0])
    num_wavelengths = len(netmap[0][0])
    for linkid in link_ids: 
        for fiber in range(num_fibers):
            for wavelength in range(num_wavelengths):
                if netmap[linkid][fiber][wavelength] == '':
                    netmap[linkid][fiber][wavelength] = path_tag
                    print("<li>found fiber", fiber)
                    return True
    return False


def find_any_free_wavelength(linkid, VLtag, netmap):
    """Reserve any wavelength on any free fiber of the given link."""
    num_fibers = len(netmap[0])
    num_wavelengths = len(netmap[0][0])
    
    for fiber in range(num_fibers):
        for wavelength in range(num_wavelengths):
            if netmap[linkid][fiber][wavelength] == '':
                netmap[linkid][fiber][wavelength] = VLtag
                print("<li>found wavelength",wavelength,"on fiber", fiber)
                return fiber, wavelength
    return None, None


def release_fiber(link, fiber, wavelength, netmap):
    print("<li>release link", link,"fiber",fiber,"wavelength",wavelength)
    netmap[link][fiber][wavelength] = ''


def vlIDtoTag(vlid):
    return f"({','.join(map(str, vlid))})"


#reserve wavelength for a single lightpath
def reserveWavelengthForLightpath(L, vlid, lightPath, NetworkWavelengthsMap, criterion, HasWavConv):

    #"WavConvEverywhere-BlockingDueToLimitedFibers"         --> "numFibers"
    #"NoWavConv-BlockingDueToWavelengthContinuity"          --> "FullWavContinuity"
    #"WavConvInSomeNodes-BlockingDueToWavelengthContinuity" --> "PartialWavContinuity"

    print("<hr><li><em>Trying to reserve wavelength(s) for lightpath:",lightPath,"of VL with id:",vlid)

    # build link sequence from path
    linkIDs = []
    LinkHasWavConv = {}

    for link in lightPath:  
        src = link[0]
        dst = link[1]

        linkID = linknumber(L, src, dst)
        if linkID is None:
            return [(None, None, None, "InvalidPath")]
        
        linkIDs.append(linkID)

        if (HasWavConv[src]==1) and (HasWavConv[dst]==1):
            LinkHasWavConv[linkID]=1
        else:
            LinkHasWavConv[linkID]=0

    # pros to paron an ena physical hop tou lightpath den ypostirizei wav-conv tote olo to lightpath den to ypostirizei kai efarmozetai wav-cont-constraint.
    # sto mellon to wav-cont-constraint tha mporei na epibaletai mono sta hops pou den ypostirizoun wav-conv

    PathWavConv = 1
    for k in LinkHasWavConv.keys():
        PathWavConv *= LinkHasWavConv[k]
    
    if PathWavConv == 1:
        print ("<li>The whole lightpath (all nodes) supports wavelength conversion, hence no wavelength continuity constraint, just limited fibers per link")
        criterion = "NumFibers"
    elif PathWavConv == 0:
        print ("<li>The whole lightpath (some or all nodes) does not support wavelength conversion, hence wavelength continuity constraint applies")
        criterion = "WavContinuity"

    reservations = []  # keep track for rollback
    VLidTag = f"({','.join(map(str, vlid))})"
    
    returnValue = []

    if criterion == "WavContinuity":

        w = find_the_same_free_wavelength_for_lightpath(linkIDs, NetworkWavelengthsMap)
        
        print("<li>candidate wavelength", w)
        if w is None:            
            return [(None, None, None, "path with wavelength continuity constraint (no conversion) - unavailable wavelength with the same channel number")]
            
        for link_id in linkIDs:
            fiber = reserve_fiber(link_id, w, VLidTag, NetworkWavelengthsMap)
            print("<li>reserved fiber", fiber, "wavelength", w)
            if fiber is None:
                # rollback
                for r_link, r_fiber, r_w in reservations:
                    #release_fiber(r_link, r_w, r_fiber, NetworkWavelengthsMap)
                    release_fiber(r_link, r_fiber, r_w, NetworkWavelengthsMap)
                    print("<li>fiber released (rollback)")
                return [(None, None, None, "path with wavelength continuity constraint (no conversion) - unavailable fiber capacity")]
            
            reservations.append((link_id, fiber, w))
            returnValue.append([link_id, fiber, w, "Pass"])
        #return link_id, fiber, w, "Pass"
        return returnValue
    
    elif criterion == "NumFibers":
        # Case 2: can use different wavelength per link
        print("<li>No Wavelength Continuity Constraint (wavelength conversions) for the current path")
        num_wavelengths = len(NetworkWavelengthsMap[0][0])
        #print("<li>number of wavelengths", num_wavelengths)
        for link_id in linkIDs:
            reserved = False
            #print("<li>current link", link_id)
            fiber, wavelength = find_any_free_wavelength(link_id, VLidTag, NetworkWavelengthsMap)
            print("<li>reserved fiber", fiber, "wavelength", wavelength)
            if (fiber is not None) and (wavelength is not None):
                reservations.append((link_id, fiber, wavelength))
                reserved = True
            if not reserved:
                # rollback
                for r_link, r_fiber, r_w in reservations:
                    #release_fiber(r_link, r_w, r_fiber, NetworkWavelengthsMap)
                    release_fiber(r_link, r_fiber, r_w, NetworkWavelengthsMap)
                    print("<li>fiber released (rollback)")
                return [(None, None, None, "path without wavelength continuity constraint (wavelength converters) - unavailable fiber capacity")]
            returnValue.append([link_id, fiber, wavelength, "Pass"])    
        return returnValue



def print_reservations(links, link_list):
    """Print the current reservations for debugging."""

    print("<p>Current Network Reservations Map")
    for i, link in enumerate(link_list):
        #print(f"<p>Link {link} (link {i}):")
        print(f"<p>Link {link} (link id:{i})</p>")
        print("<table>")
        for fiber_idx, fiber in enumerate(links[i]):
            print("<tr>")
            #slots_str = '</td><td>'.join([s if s != '' else '\u2205' for s in fiber])
            slots_str = '</td><td>'.join([s if s != '' else '&varnothing;' for s in fiber]) # &varnothing; is the empty set character 
            print(f"<td>Fiber {fiber_idx}</td><td>{slots_str}</td>")
            print("</tr>")
        #print()
        print("</table>")

def print_vl_reservation(routings, netmap, vl, vltag):
    """Print the reservations of a single path"""
    print("<li>VL to print its reservation",vl)
    reservation = []
    num_links = len(netmap)
    num_fibers = len(netmap[0])
    num_wavelengths = len(netmap[0][0])
    print("<li>lightpath physical links:")
    
    hops = routings[vl]
    for i in range(0, len(hops)-1, 2):
        print("[", hops[i][0], hops[i][1], "], ")

    print("<p>Virtual Link reservation:")
    for l in range(num_links):
        for f in range(num_fibers):
            for w in range(num_wavelengths):
                if netmap[l][f][w] == vltag:
                    reservation.append([l,f,w])
    print("<li>Reservation:",reservation)
    return reservation

#</24-9-2025>



def assignWavelengthChannelsConsideringLimits_FollowingWavelengthsAssignment(L, RoutingOfVirtualLinksOverWavelengths, NetworkWavelengthsMap, criterion, HasWavConv):

    #"WavConvEverywhere-BlockingDueToLimitedFibers"         --> "numFibers"
    #"NoWavConv-BlockingDueToWavelengthContinuity"          --> "FullWavContinuity"
    #"WavConvInSomeNodes-BlockingDueToWavelengthContinuity" --> "PartialWavContinuity"

    print("<li><em>Will assign wavelength channel according to the criterion:",criterion)

    newRoutings = {}
    routingResults = {}
    explanation = ""

    VLids = RoutingOfVirtualLinksOverWavelengths.keys()

    for vlid in VLids:
        Lightpath = RoutingOfVirtualLinksOverWavelengths.get(vlid)
        
        lightpathHops = reserveWavelengthForLightpath(L, vlid, Lightpath, NetworkWavelengthsMap, criterion, HasWavConv) #for a single lightpath
        
        PLiDs = []

        for lpHop in lightpathHops:
            link = lpHop[0]
            fiber = lpHop[1]
            wavelength = lpHop[2]
            explanation = lpHop[3]

            if link!=None and fiber!=None and wavelength!=None:
                src, dst = linkIDtoSrcDst(L, link)
                PLiDs.append((src, dst, fiber, wavelength))
            else:
                #PLid = (vlid[0], vlid[1], -1, -1)
                #break
                #28-9-2025
                #PLiDs.append((vlid[0], vlid[1], -1, -1))
                PLiDs.append((-1, -1, -1, -1))   # if any hop failed, the whole lightpath is considered failed, there is no physical link assigned to the virtual link
        
        addRoutingOfVirtualLinksOverPhysicalLinks(newRoutings,vlid,PLiDs)
        #newRoutings[vlid] = (src, dst, fiber, wavelength)
        routingResults[vlid] = explanation
        
            
    # success, reason, LindID, FiberID, WavelengthID = reserveWavelengthChannels(ShortestPath, VLidm, (PathWavConv == 1), NetworkWavelengthsMap, L) #for a single lightpath
        
    return newRoutings, routingResults

#end_of_def assignWavelengthChannelsConsideringLimits_FollowingWavelengthsAssignment()



#24-9-2025
# result = assignWavelengthChannelsConsideringLimits(NetworkWavelengthsMap) NOT USED
'''
def assignWavelengthChannelsConsideringLimits(NetworkWavelengthsMap, L, HasWavConv, ShortestPath, VLid):

    #24-9-2025
    #ShortestPath = [0,1,3,2]
    #ShortestPath = [2,1,0]

    PathWavConv = 1
    
    print("<table>")
    print("<tr>")
    print("<td>")
    print("shortest path",ShortestPath)
    pathlinks = path2links(ShortestPath)
    print("<p>path links",pathlinks)
    for lnk in pathlinks:
        srcNode = lnk[0]
        dstNode = lnk[1]
        lnknum = linknumber(L,srcNode,dstNode)
        PathWavConv *= HasWavConv[srcNode] * HasWavConv[dstNode]
        print(f"<p>link number: {lnknum:d} - link:",lnk)
        print(f"- src node:{srcNode:d} {'has' if HasWavConv[srcNode] else 'does not have':s} wavelength conversion ")
        print(f"- dst node:{dstNode:d} {'has' if HasWavConv[dstNode] else 'does not have':s} wavelength conversion.")
    
    if PathWavConv == 1:
        print(f"<p>All path nodes have wavelength conversion hardware - Wavelength continuity constraint will NOT be applied.")
        WavelengthContinuity = 0
    else:
        print(f"<p>At least one node of the path does not have wavelength conversion hardware - Wavelength continuity constraint will be applied.")
        WavelengthContinuity = 1
        
    
    success, reason, LindID, FiberID, WavelengthID = reserveWavelengthChannels(ShortestPath, VLidm, (PathWavConv == 1), NetworkWavelengthsMap, L) #for a single lightpath
    print("</td>")
    print("</tr>")
    print("<tr>")
    print("<td>")
    print_reservations(NetworkWavelengthsMap, L)
    print("</td>")
    print("</tr>")
    print("</table>")
    

    #>>> 25-9-2025


    # παλιά
    # maxWavelengthsPerFiber = 16 # max 16 wavelengths are multiplexed in each fiber
    # every 16 wavelengths a new fiber is assigned to the link

    #23-9-2025

    """αναθεση wavelength καναλιού σε κάθε link της διαδρομής

    εδω θα γινεται η αναθεση wavelength καναλιού σε κάθε link της διαδρομής
        συμφωνα με τους περιορισμους η μη
            περιορισμενος αριθμος fiber / απεριοριστος αριθμος
            wavelength continuity constraint (wavelength converters)
                χωρις converters / converters σε μερικους κομβους / converters παντου
    """
    

    """
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
    """
    return success, reason, LindID, FiberID, WavelengthID
#end_of_def assignWavelengthChannelsConsideringLimits()
'''



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


""" this does not produce a very good range
def generateTrafficRequestsVariableBalance(dbConnection, N, graphsPath, lenQs, X, xi, Queuelabel, queueID, distribution, Qpercent):

    ### generate and save lamda matrix traffic request values for the video queue

    requests=[] # the original requests
    #decoratedrequests=[] # the requests extended by an extra field about the priority class (0, 1, 2) 
                        # used for sorting by class ascending and then by traffic demand descending
    lamda=[]
    rqsts=[]
    Xvalue = X[xi]
    #orismos range random traffic requests
    #distributionMeanValueX = int(X[xi]/lenQs)
    #distributionMeanValueX = int(X[xi]*Qpercent)
    #traffic_demand_range_from = int(10 / lenQs)
    #traffic_demand_range_from = distributionMeanValueX-(distributionMeanValueX*Qpercent)
    #traffic_demand_range_from = 10*Qpercent #[(10*Q_HP_percent), (2*X*Q_HP_percent-(10*Q_HP_percent))]
    #traffic_demand_range_from = roundatdecimals(traffic_demand_range_from, 1)
    #traffic_demand_range_to = ((2 * distributionMeanValueX) - (int(10 / lenQs)))
    #traffic_demand_range_to = distributionMeanValueX+(distributionMeanValueX*Qpercent)
    #traffic_demand_range_to = 2*distributionMeanValueX-(10*Qpercent)
    #traffic_demand_range_to = (2*Xvalue*Qpercent-(10*Qpercent)) #[(10*Q_HP_percent), (2*X*Q_HP_percent-(10*Q_HP_percent))]
    #traffic_demand_range_to = roundatdecimals(traffic_demand_range_to, 1)

    distributionMeanValueX = int(X[xi]*Qpercent)
    XQueVal = Xvalue * Qpercent
    traffic_demand_range_from = roundatdecimals( (XQueVal / 2.0), 1)
    traffic_demand_range_to   = roundatdecimals( (2 * XQueVal - XQueVal / 2.0), 1)

    # save lamda to text file
    if (sys.argv[5]=="gensave"):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan='"+str(len(N))+"' style='background:orange;'>Generate and save lamda matrix traffic requests to the",sys.argv[6],"text file</th></tr>")
            print ("<tr><th colspan=",len(N),">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi],"for ",lenQs,"Queue." if lenQs==1 else "Queues.")
            
            if distribution=="Poisson":
                #Poisson distribution
                print ("<br><em style='font-size:0.8em'>The traffic demand between each node pair is random following a Poisson distribution around a mean traffic data amount,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gbps, ")
                print ("the actual demand between a node pair is generated by a random function distributed following the Poisson process within the range ")    
            elif distribution == "Uniform":
                #Uniform distribution
                print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a Uniform distribution within a certain range,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, ")
                print (f"the actual demand between a node pair is generated by a random function uniformly distributed within the range ")

            print (f"[{traffic_demand_range_from},{traffic_demand_range_to}] Gbps with mean value of the distribution X={distributionMeanValueX}.</em></th></tr>")
            
        #EOP

        komvoi = len(N)
        megethosdeigmatos = komvoi * komvoi - komvoi
        if distribution=="Poisson":
            #Poisson distribution
            deigma = generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos)
        elif distribution == "Uniform":
            #Uniform ditribution
            deigma = generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos) 
        stoixeioDeigmatos = 0

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graphDistribution(N, traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, deigma, distribution, graphsPath+pathseparatortoken()+f"TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png")
            print (f"<tr><th colspan='{str(len(N))}' style='background:orange;'>")
            print (f"<img src='{graphsPath+pathseparatortoken()}TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png' style='display: block; margin-left: auto; margin-right: auto; width: 30%;' ")
            print ("alt='Traffic requests sample data histogram'></th></tr>")
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
                    
                    rqsts = []
                    rqsts.append(float(deigma[stoixeioDeigmatos]))
                    stoixeioDeigmatos = stoixeioDeigmatos + 1

                    #if distribution=="Poisson":
                        #Poisson distribution
                        #rqsts=generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) #1 is the number of samples. If number greater than 1, it can be considered the grooming of Chatterjee et al.
                    #elif distribution == "Uniform":
                        #Uniform ditribution
                        #rqsts=generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) # X = [20, 40, 60, 80, 100, 120], one request
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(" m=",x,"n=",y)
                    #EOP

                    
                    for i in range(len(rqsts)):
                        requests.append([x, y, rqsts[i]])
                    
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
"""

def generateSplitTrafficRanges(Xval, Qpercent):
    if Xval < 20.0:
        base = 1.0
    else:
        base = 10.0
    distMeanX = int(Xval*Qpercent)
    range_from = roundatdecimals( (base*Qpercent), 1)
    range_to   = roundatdecimals( ((2*Xval-base)*Qpercent), 1)

    return distMeanX, range_from, range_to


def generateTrafficRequestsVariableBalance(dbConnection, N, graphsPath, lenQs, X, xi, Queuelabel, queueID, distribution, Qpercent):

    ### generate and save lamda matrix traffic request values for the video queue

    requests=[] # the original requests
    #decoratedrequests=[] # the requests extended by an extra field about the priority class (0, 1, 2) 
                        # used for sorting by class ascending and then by traffic demand descending
    lamda=[]
    rqsts=[]
    Xvalue = X[xi]

    distributionMeanValueX, traffic_demand_range_from, traffic_demand_range_to = generateSplitTrafficRanges(Xvalue, Qpercent)

    # save lamda to text file
    if (sys.argv[5]=="gensave"):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan='"+str(len(N))+"' style='background:orange;'>Generate and save lamda matrix traffic requests to the",sys.argv[6],"text file</th></tr>")
            print ("<tr><th colspan=",len(N),">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi],"for ",lenQs,"Queue." if lenQs==1 else "Queues.")
            
            if distribution=="Poisson":
                #Poisson distribution
                print ("<br><em style='font-size:0.8em'>The traffic demand between each node pair is random following a Poisson distribution around a mean traffic data amount,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gbps, ")
                print ("the actual demand between a node pair is generated by a random function distributed following the Poisson process within the range ")    
            elif distribution == "Uniform":
                #Uniform distribution
                print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a Uniform distribution within a certain range,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, ")
                print (f"the actual demand between a node pair is generated by a random function uniformly distributed within the range ")

            print (f"[{traffic_demand_range_from},{traffic_demand_range_to}] Gbps with mean value of the distribution X={distributionMeanValueX}.</em></th></tr>")
            
        #EOP

        komvoi = len(N)
        megethosdeigmatos = komvoi * komvoi - komvoi
        if distribution=="Poisson":
            #Poisson distribution
            deigma = generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos)
        elif distribution == "Uniform":
            #Uniform ditribution
            deigma = generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos) 
        stoixeioDeigmatos = 0

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graphDistribution(N, traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, deigma, distribution, graphsPath+pathseparatortoken()+f"TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png")
            print (f"<tr><th colspan='{str(len(N))}' style='background:orange;'>")
            print (f"<img src='{graphsPath+pathseparatortoken()}TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png' style='display: block; margin-left: auto; margin-right: auto; width: 30%;' ")
            print ("alt='Traffic requests sample data histogram'></th></tr>")
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
                    
                    rqsts = []
                    rqsts.append(float(deigma[stoixeioDeigmatos]))
                    stoixeioDeigmatos = stoixeioDeigmatos + 1

                    #if distribution=="Poisson":
                        #Poisson distribution
                        #rqsts=generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) #1 is the number of samples. If number greater than 1, it can be considered the grooming of Chatterjee et al.
                    #elif distribution == "Uniform":
                        #Uniform ditribution
                        #rqsts=generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) # X = [20, 40, 60, 80, 100, 120], one request
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(" m=",x,"n=",y)
                    #EOP

                    
                    for i in range(len(rqsts)):
                        requests.append([x, y, rqsts[i]])
                    
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
        
        demandsfilename = os.path.join(graphsPath, sys.argv[6])
        fout = open(demandsfilename,"a")
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




def generateTrafficRequests_0_2X(dbConnection, N, graphsPath, lenQs, X, xi, Queuelabel, queueID, distribution): #, startReqID):

    ### generate and save lamda matrix traffic request values for the video queue

    requests=[] # the original requests
    #decoratedrequests=[] # the requests extended by an extra field about the priority class (0, 1, 2) 
                        # used for sorting by class ascending and then by traffic demand descending
    lamda=[]
    rqsts=[]

    #orismos range random traffic requests
    distributionMeanValueX = int(X[xi] / lenQs) if lenQs>0 else int(X[xi]) # prevent division by zero
    traffic_demand_range_from = 0
    traffic_demand_range_to = 2*X[xi] #((2 * distributionMeanValueX) - (int(10 / lenQs)))
    
    # save lamda to text file
    if (sys.argv[5]=="gensave"):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan='"+str(len(N))+"' style='background:orange;'>Generate and save lamda matrix traffic requests to the",sys.argv[6],"text file</th></tr>")
            print ("<tr><th colspan=",len(N),">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi],"for ",lenQs,"Queue." if lenQs==1 else "Queues.")
            
            if distribution=="Poisson":
                #Poisson distribution
                print ("<br><em style='font-size:0.8em'>The traffic demand between each node pair is random following a Poisson distribution around a mean traffic data amount,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gbps, ")
                print ("the actual demand between a node pair is generated by a random function distributed following the Poisson process within the range ")    
            elif distribution == "Uniform":
                #Uniform distribution
                print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a Uniform distribution within a certain range,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, ")
                print (f"the actual demand between a node pair is generated by a random function uniformly distributed within the range ")

            print (f"[{traffic_demand_range_from},{traffic_demand_range_to}] Gbps with mean value of the distribution X={distributionMeanValueX}.</em></th></tr>")
            
        #EOP

        komvoi = len(N)
        megethosdeigmatos = komvoi * komvoi - komvoi
        if distribution=="Poisson":
            #Poisson distribution
            deigma = generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos)
        elif distribution == "Uniform":
            #Uniform ditribution
            deigma = generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos) 
        stoixeioDeigmatos = 0

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graphDistribution(N, traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, deigma, distribution, graphsPath+pathseparatortoken()+f"TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png")
            print (f"<tr><th colspan='{str(len(N))}' style='background:orange;'>")
            print (f"<img src='{graphsPath+pathseparatortoken()}TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png' style='display: block; margin-left: auto; margin-right: auto; width: 30%;' ")
            print ("alt='Traffic requests sample data histogram'></th></tr>")
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
                    
                    rqsts = []
                    rqsts.append(float(deigma[stoixeioDeigmatos]))
                    stoixeioDeigmatos = stoixeioDeigmatos + 1

                    #if distribution=="Poisson":
                        #Poisson distribution
                        #rqsts=generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) #1 is the number of samples. If number greater than 1, it can be considered the grooming of Chatterjee et al.
                    #elif distribution == "Uniform":
                        #Uniform ditribution
                        #rqsts=generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) # X = [20, 40, 60, 80, 100, 120], one request
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(" m=",x,"n=",y)
                    #EOP

                    
                    for i in range(len(rqsts)):
                        requests.append([x, y, rqsts[i]])
                    
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
        
        demandsfilename = os.path.join(graphsPath, sys.argv[6])
        fout = open(demandsfilename,"a")
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








def generateTrafficRequests(dbConnection, N, graphsPath, lenQs, X, xi, Queuelabel, queueID, distribution): #, startReqID):

    ### generate and save lamda matrix traffic request values for the video queue

    requests=[] # the original requests
    #decoratedrequests=[] # the requests extended by an extra field about the priority class (0, 1, 2) 
                        # used for sorting by class ascending and then by traffic demand descending
    lamda=[]
    rqsts=[]

    #orismos range random traffic requests
    distributionMeanValueX = int(X[xi] / lenQs) if lenQs>0 else int(X[xi]) # prevent division by zero
    traffic_demand_range_from = int(10 / lenQs) if lenQs>0 else 10 # prevent division by zero
    traffic_demand_range_to = ((2 * distributionMeanValueX) - (int(10 / lenQs))) if lenQs>0 else ((2 * distributionMeanValueX) - 10) # prevent division by zero
    
    #19-10-2025
    Xval = X[xi]
    distributionMeanValueX, traffic_demand_range_from, traffic_demand_range_to = generateSplitTrafficRanges(Xval, 1.0)

    # save lamda to text file
    if (sys.argv[5]=="gensave"):
        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<table class='table1c'>")
            print ("<tr><th colspan='"+str(len(N))+"' style='background:orange;'>Generate and save lamda matrix traffic requests to the",sys.argv[6],"text file</th></tr>")
            print ("<tr><th colspan=",len(N),">[lamda]: Traffic demand per node pair (requests) in Gbps","xi=",xi,", X[",xi,"]=",X[xi],"for ",lenQs,"Queue." if lenQs==1 else "Queues.")
            
            if distribution=="Poisson":
                #Poisson distribution
                print ("<br><em style='font-size:0.8em'>The traffic demand between each node pair is random following a Poisson distribution around a mean traffic data amount,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gbps, ")
                print ("the actual demand between a node pair is generated by a random function distributed following the Poisson process within the range ")    
            elif distribution == "Uniform":
                #Uniform distribution
                print ("<br><em style='font-size:0.6em'>The traffic demand between each node pair is random following a Uniform distribution within a certain range,")
                print (" which is centered at an identical average. That is, given an average demand intensity X &isin; {20,40, . . . ,120} Gb/s, ")
                print (f"the actual demand between a node pair is generated by a random function uniformly distributed within the range ")

            print (f"[{traffic_demand_range_from},{traffic_demand_range_to}] Gbps with mean value of the distribution X={distributionMeanValueX}.</em></th></tr>")
            
        #EOP

        komvoi = len(N)
        megethosdeigmatos = komvoi * komvoi - komvoi
        if distribution=="Poisson":
            #Poisson distribution
            deigma = generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos)
        elif distribution == "Uniform":
            #Uniform ditribution
            deigma = generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, megethosdeigmatos) 
        stoixeioDeigmatos = 0

        #SOP
        if (GlobalPrintOutEnabled==True) :
            graphDistribution(N, traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, deigma, distribution, graphsPath+pathseparatortoken()+f"TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png")
            print (f"<tr><th colspan='{str(len(N))}' style='background:orange;'>")
            print (f"<img src='{graphsPath+pathseparatortoken()}TR_sample_histogram_Q_{("HP" if queueID==0 else "LP"):s}.png' style='display: block; margin-left: auto; margin-right: auto; width: 30%;' ")
            print ("alt='Traffic requests sample data histogram'></th></tr>")
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
                    
                    rqsts = []
                    rqsts.append(float(deigma[stoixeioDeigmatos]))
                    stoixeioDeigmatos = stoixeioDeigmatos + 1

                    #if distribution=="Poisson":
                        #Poisson distribution
                        #rqsts=generateDistributedTrafficRequestValuesThatFollowThePoissonProcess(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) #1 is the number of samples. If number greater than 1, it can be considered the grooming of Chatterjee et al.
                    #elif distribution == "Uniform":
                        #Uniform ditribution
                        #rqsts=generateUniformlyDistributedTrafficRequestValues(traffic_demand_range_from, traffic_demand_range_to, distributionMeanValueX, 1) # X = [20, 40, 60, 80, 100, 120], one request
                    
                    #SOP
                    if (GlobalPrintOutEnabled==True) :
                        print(" m=",x,"n=",y)
                    #EOP

                    
                    for i in range(len(rqsts)):
                        requests.append([x, y, rqsts[i]])
                    
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

        demandsfilename = os.path.join(graphsPath, sys.argv[6])
        fout = open(demandsfilename,"a") # prefer to write lamda to the output text file since requests do not include the 0.0 capacity for nodes where i==Nj

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



#20-9-2025 keep only one file from the detailed report
def keep_and_rename_file(UUID, folder_path, keep_file):
    """
    Keeps only keep_file in folder_path, deletes all other contents,
    and renames keep_file to match the folder's name (keeping its extension).
    
    :param folder_path: Path to the folder
    :param keep_file: Name of the file to keep
    """
    folder_path = os.path.abspath(folder_path)
    
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist or is not a folder.")

    keep_file_path = os.path.join(folder_path, keep_file)
    if not os.path.isfile(keep_file_path):
        raise FileNotFoundError(f"File '{keep_file}' not found in '{folder_path}'.")

    # Delete all other files and folders
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.abspath(item_path) != os.path.abspath(keep_file_path):
            if os.path.isfile(item_path) or os.path.islink(item_path):
                try:
                    os.remove(item_path)
                    print(f"Deleted file '{item_path}'")
                except PermissionError:
                    print(f"File used by another process (permission error):'{item_path}'")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder '{item_path}'")

    # Rename the kept file to match the folder name
    folder_name = os.path.basename(folder_path)
    _, ext = os.path.splitext(keep_file)
    new_file_path = os.path.join(folder_path, UUID + "_" + folder_name + ext)

    # Only rename if the name is different
    if os.path.abspath(keep_file_path) != os.path.abspath(new_file_path):
        os.rename(keep_file_path, new_file_path)
        print(f"Renamed '{keep_file}' to '{folder_name + ext}'")
    else:
        print(f"File already has the correct name: '{folder_name + ext}'")


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


def pathseparatortoken():
    #select path separator based on the host OS
    pathseparator = ""
    if platform.system() == 'Windows':
        pathseparator = "\\"
    elif platform.system() == 'Linux':
        pathseparator = "/"
    else:
        pathseparator = "/"

    return pathseparator


def filexists(filename):
    import os

    return os.path.exists(filename)









def getRevisitsFromSQLite(sqliteConnection):
    #sql = f"SELECT quenum, num, src, dst, cap FROM TrafficRequests;"
    
    sql =   """SELECT distinct
                    quenum, num, src, dst, cap, type
            FROM 
                    TrafficRequests, RoutingTrafficRequestsOverVirtualTopology 
            WHERE 
                    type='Grm'
                    AND quenum = reqquenum 
                    AND num = reqnum
                    ORDER BY quenum, num;
            """
    
    cursor = sqliteConnection.execute(sql)
    
    dataset = cursor.fetchall() 
    print("<ul style='list-style-type: square'>")
    for row in dataset: 
        TRpath = ""
        
        quenum = row[0]
        reqnum = row[1]
        srcnum = row[2]
        dstnum = row[3]
        capact = row[4]
        print("<li>Traffic request</li>")
        print(f"<li>Traffic request: queue {quenum:d}, request {reqnum:d}, from source node {srcnum:d} to destination node {dstnum:d} demanding the transfer of capacity {capact:0.3f} Gbps.</li>")

        TRpath = getVirtualLinksOfTrafficRequest(sqliteConnection, quenum, reqnum, srcnum, dstnum)

        print(f"<li>Traffic request cascaded path(s) = {TRpath:s}</li>")

        TRpathStr = mergeStringListsInBrackets(TRpath)
        print(f"<li>Traffic request physical path {TRpathStr:s}</li>")
        TRpathList = string_to_int_list(TRpathStr)

        if has_revisits(TRpathList):
            print(f"<li><em>Revisits!</em> Nodes:",detect_node_revisits(TRpathList),"</li>")
        else:
            print("<li>NoR(evisits)")

    print("</ul>") 

    sqliteConnection.commit()
    
    #return len(dataset)

def getVirtualLinksOfTrafficRequest(sqliteConnection, quenum, reqnum, srcnum, dstnum):
    #revisits happen only for traffic grooming
    #sql = f"SELECT reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, routingStep, routStepVLseqnum, type FROM RoutingTrafficRequestsOverVirtualTopology WHERE type='Grm' AND reqquenum={quenum:d} AND reqnum = {reqnum:d} ORDER BY routStepVLseqnum ASC;"
    sql = f"SELECT reqquenum, reqnum, vlsrc, vldst, vlnum, utilcap, freecap, routingStep, routStepVLseqnum, type FROM RoutingTrafficRequestsOverVirtualTopology WHERE type='Grm' AND reqquenum={quenum:d} AND reqnum = {reqnum:d} ORDER BY type DESC, routStepVLseqnum ASC;"
    cursor = sqliteConnection.execute(sql)

    dataset = cursor.fetchall() 
    TRpath=""
    
    print("<ul style='list-style-type: disc'>")

    for row in dataset:         
        quenum = row[0]
        reqnum = row[1]
        vlsrc  = row[2]
        vldst  = row[3]
        vlnum  = row[4]
        utilcp = row[5]
        freecp = row[6]
        rtstep = row[7]
        rstseq = row[8]
        typeofVL = row[9]

        print(f"<li>Q {quenum:d}, request {reqnum:d}, src {srcnum:d} -> dst {dstnum:d}, ")
        print(f"VL ({vlsrc:d}, {vldst:d}, {vlnum:d}), typeofVL {typeofVL:s} utilcap {utilcp:0.3f}, freecap {freecp:0.3f}, rtStep (concurrent/sibling transmission) {rtstep:d}, ")
        print(f"cascaded VL sequence {rstseq:d}.</li>")
        
        if rstseq == 0:
            TRpath = getWavelengthsOFVirtualLinks(sqliteConnection, vlsrc, vldst, vlnum)
        elif rstseq > 0:
            TRpath += getWavelengthsOFVirtualLinks(sqliteConnection, vlsrc, vldst, vlnum)

        print(f"<li>path = {TRpath:s}</li>")

    print("</ul>")

    return TRpath


def getWavelengthsOFVirtualLinks(sqliteConnection, vlsrc, vldst, vlnum):
    sql = f"SELECT vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, type, NumberOfHops, ShortestpathAsInt, ShortestpathAsStr, PhysicalLinkDirection, PhysicalLinkCurrentSource, PhysicalLinkCurrentDestination, LatIP, LatTransp FROM RoutingVirtualLinksOverPhysicalTopology WHERE vlsrc={vlsrc:d} AND vldst={vldst:d} AND vlnum={vlnum:d};"
    cursor = sqliteConnection.execute(sql)

    dataset = cursor.fetchall() 
    TRpth = ""
    print("<ul style='list-style-type: circle'>")
    for row in dataset:         
        vlsrc                           = row[0]
        vldst                           = row[1]
        vlnum                           = row[2]
        plsrc                           = row[3]
        pldst                           = row[4]
        fiberid                         = row[5]
        waveid                          = row[6]
        typ                             = row[7]
        NumberOfHops                    = row[8]
        ShortestpathAsInt               = row[9]
        ShortestpathAsStr               = row[10]
        PhysicalLinkDirection           = row[11]
        PhysicalLinkCurrentSource       = row[12]
        PhysicalLinkCurrentDestination  = row[13]
        LatIP                           = row[14]
        LatTransp                       = row[15]

        TRpth = ShortestpathAsInt

        print(f"<li>VL ({vlsrc:d}, {vldst:d}, {vlnum:d}), type {typ:s}, currentPLsrc {PhysicalLinkCurrentSource:d}, currentPLdst {PhysicalLinkCurrentDestination:d}, fID {fiberid:d}, wID {waveid:d}, Shortest path {ShortestpathAsInt:s}.</li>")
    
    print("</ul>")

    return TRpth



def mergeStringListsInBrackets(s):
    """
    Merges a string of bracketed lists, removes adjacent duplicates at the borders,
    and returns a new list-like string.

    Example:
        "[5, 4][4, 3, 1][1, 2]" -> "[5, 4, 3, 1, 2]"
    """
    # Step 1: Extract all numbers using regex
    list_of_lists = re.findall(r'\[([^\[\]]+)\]', s)
    
    result = []
    for group in list_of_lists:
        numbers = [int(x.strip()) for x in group.split(',')]
        for n in numbers:
            if not result or result[-1] != n:
                result.append(n)

    # Step 2: Convert result list to string format
    return f"[{', '.join(map(str, result))}]"


def string_to_int_list(s):
    """
    Converts a string like "[1, 3, 5]" to a list of integers [1, 3, 5].

    Parameters:
        s (str): A string representing a list of integers.

    Returns:
        list of int: The parsed list of integers.
    """
    return [int(x.strip()) for x in s.strip("[]").split(",") if x.strip().isdigit()]


def detect_node_revisits(path):
    """
    Detects and reports node revisits in the given path.

    Parameters:
        path (list): A list of node identifiers (e.g., integers).
    
    Returns:
        list: A list of revisited nodes in order of reappearance.
    """
    seen = set()
    revisited = []

    for node in path:
        if node in seen:
            #print(f"Revisits detected: node {node}")
            revisited.append(node)
        else:
            seen.add(node)

    return revisited


def has_revisits(path):
    """
    Returns True if there are any revisited nodes in the path.

    Parameters:
        path (list of int): The sequence of node visits.

    Returns:
        bool: True if any node is revisited, False otherwise.
    """
    seen = set()
    for node in path:
        if node in seen:
            return True  # Revisit detected
        seen.add(node)
    return False  # No revisits



def VirtualPathLeadsToRevisitsOnPhysicalTopology(virtualpath, N, Nt, NmC):
    
    if not virtualpath:
        return False

    virtuallinks = path2links(virtualpath)
    
    #SOP
    if (GlobalPrintOutEnabled==True) :   
        print("<li><hr>")
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> N:",N)
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> Nt:",Nt)
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> NmC:",NmC)
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> virtual path:",virtualpath)
    #EOP

    subpaths = []

    for vlink in virtuallinks:
        #SOP
        if (GlobalPrintOutEnabled==True) :   
            print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> virtual link:",vlink)
            print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> from:",N[vlink[0]])
            print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> to:",N[vlink[1]])
        #EOP
        shortestsubpath = find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,N[vlink[0]],N[vlink[1]])
        #SOP
        if (GlobalPrintOutEnabled==True) :   
            print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> shortest physical path:",shortestsubpath)
        #EOP
        subpaths.append(shortestsubpath)

    # 1. Concatenate all sub-paths into one full path

    fullpath = subpaths[0][:]
    visitednodes = set(fullpath)
    revisitednodes = set()
        
    for subpath in subpaths[1:]:
        if not subpath:
            continue

        # Avoid duplicating the first node of current subpath if it's same as last of previous
        if fullpath[-1] == subpath[0]:
            nodes_to_add = subpath[1:]
        else:
            nodes_to_add = subpath

        for node in nodes_to_add:
            if node in visitednodes:
                revisitednodes.add(node)
            else:
                visitednodes.add(node)

        fullpath.extend(nodes_to_add)

    print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> full physical path:",fullpath)

    if revisitednodes:
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> Revisited nodes:", revisitednodes)
        HasRevisits = True
    else:
        print("<li>VirtualPathLeadsToRevisitsOnPhysicalTopology() >> No revisits found.")
        HasRevisits = False

    return HasRevisits



def resultsDBUpdateOfVLs_LPs(routingResult, dbConnection):   # results and db update for Virtual Links = Lightpaths

    passLPs = []
    blockedLPs = []

    for vlid in routingResult:
        if routingResult[vlid]=="Pass":
            passLPs.append(vlid)
        else:
            blockedLPs.append(vlid)

    #update RoutingTrafficRequestsOverVirtualTopology

    if len(passLPs)>0:
        sqlPass  = "UPDATE RoutingTrafficRequestsOverVirtualTopology "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (vlsrc, vldst, vlnum) IN ("
        for vlid in passLPs:
            sqlPass += f"({vlid[0]:d},{vlid[1]:d},{vlid[2]:d})," # (vlid[0],vlid[1],vlid[2]),
        sqlPass = sqlPass[:-1]+")"

        dbConnection.execute(sqlPass)
        dbConnection.commit()

    if len(blockedLPs)>0:
        sqlBlock  = "UPDATE RoutingTrafficRequestsOverVirtualTopology "
        sqlBlock += "SET result = 'Blocked' "
        sqlBlock += "WHERE (vlsrc, vldst, vlnum) IN ("
        for vlid in blockedLPs:
            sqlBlock += f"({vlid[0]:d},{vlid[1]:d},{vlid[2]:d})," # (vlid[0],vlid[1],vlid[2]),
        sqlBlock = sqlBlock[:-1]+")"

        dbConnection.execute(sqlBlock)
        dbConnection.commit()

    #update VirtualLinks

    if len(passLPs)>0:
        sqlPass  = "UPDATE VirtualLinks "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (src, dst, num) IN ("
        for vlid in passLPs:
            sqlPass += f"({vlid[0]:d},{vlid[1]:d},{vlid[2]:d})," # (vlid[0],vlid[1],vlid[2]),
        sqlPass = sqlPass[:-1]+")"

        dbConnection.execute(sqlPass)
        dbConnection.commit()

    if len(blockedLPs)>0:
        sqlBlock  = "UPDATE VirtualLinks "
        sqlBlock += "SET result = 'Blocked' "
        sqlBlock += "WHERE (src, dst, num) IN ("
        for vlid in blockedLPs:
            sqlBlock += f"({vlid[0]:d},{vlid[1]:d},{vlid[2]:d})," # (vlid[0],vlid[1],vlid[2]),
        sqlBlock = sqlBlock[:-1]+")"

        dbConnection.execute(sqlBlock)
        dbConnection.commit()

    return passLPs, blockedLPs



def resultsDBUpdateOfTRs(dbConnection):   # results and db update for Traffic Requests

    # prwta epilegw ta blocked TRs 
    sqlBlock = "select distinct reqquenum, reqnum from RoutingTrafficRequestsOverVirtualTopology where result='Blocked'"
    cursor = dbConnection.execute(sqlBlock)
    dataset = cursor.fetchall()
    blockedTRs = []
    for row in dataset:
        blockedTRs.append((row[0], row[1]))

    # meta epilegw ws pass TRs, osa den einai blocked 
    # giati an ta epilexw me kritirio tin timi 'Pass' tote to synoliko plithos bgainei megalytero apo to pragmatiko, dioti ena TR mpori na exei kai pass kai blocked routings logw twn traffic grooming
    sqlPass = """
                select distinct reqquenum, reqnum 
                from RoutingTrafficRequestsOverVirtualTopology 
                where (reqquenum, reqnum) not in 
                    (select distinct reqquenum, reqnum 
                     from RoutingTrafficRequestsOverVirtualTopology 
                     where result='Blocked')
              """
    cursor = dbConnection.execute(sqlPass)
    dataset = cursor.fetchall()
    passTRs = []
    for row in dataset:
        passTRs.append((row[0], row[1]))

    
    #update TrafficRequests
    if len(passTRs)>0:
        sqlPass  = "UPDATE TrafficRequests "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (quenum, num) IN ("
        for trq in passTRs:
            sqlPass += f"({trq[0]:d},{trq[1]:d})," # (trq[0],trq[1]),
        sqlPass = sqlPass[:-1]+")"

        dbConnection.execute(sqlPass)
        dbConnection.commit()

    if len(blockedTRs)>0:
        sqlBlock  = "UPDATE TrafficRequests "
        sqlBlock += "SET result = 'Blocked' "
        sqlBlock += "WHERE (quenum, num) IN ("
        for trq in blockedTRs:
            sqlBlock += f"({trq[0]:d},{trq[1]:d})," # (trq[0],trq[1]),
        sqlBlock = sqlBlock[:-1]+")"

        dbConnection.execute(sqlBlock)
        dbConnection.commit()

    return passTRs, blockedTRs



def updateDB_RoutingVirtualLinksOverPhysicalTopology_forHeaviestHottestAndComparison(newRoutings, routingResults, dbConnection):

    newRoutings = normalize_dict(newRoutings)

    countPass = 0
    countBlocked = 0

    arrayOfWavelengthAssignments = []
    for key in newRoutings:
        numberofphysicallinks = len(newRoutings[key])

        for i in range(numberofphysicallinks):
            arrayOfWavelengthAssignments.append( (key[0], key[1], key[2], newRoutings[key][i][0], newRoutings[key][i][1], newRoutings[key][i][2], newRoutings[key][i][3], routingResults[key]) )
            # (vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result)

    #print("<li>updateDB_RoutingVirtualLinksOverPhysicalTopology() >> array:",array)

    # SQL clause 3: insert routings and results as a new table to the database
    # boithitikos pinakas gia apothikeusi twn routings kai twn apotelesmatwn tous

    if len(arrayOfWavelengthAssignments) > 0:
        sqlCreateTable = """CREATE TABLE IF NOT EXISTS RoutingVirtualLinksOverPhysicalTopologyWavelengthAssignmentsAfterLimitsResults 
                            (
                                vlsrc integer NOT NULL,
                                vldst integer NOT NULL,
                                vlnum integer NOT NULL,
                                plsrc integer NOT NULL,
                                pldst integer NOT NULL,
                                fiberid integer NOT NULL,
                                waveid integer NOT NULL,
                                result text NOT NULL,
                                PRIMARY KEY (vlsrc, vldst,vlnum, plsrc, pldst, fiberid, waveid),
                                FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num),
                                FOREIGN key (plsrc, pldst) REFERENCES PhysicalLinks (src, dst)
                            );
                            """
        
        #there is no physical link related in case of a blocked lightpath
        #therefore, the foreign key constraint for the PhysicalLinks is removed
        '''
            FOREIGN key (plsrc, pldst) REFERENCES PhysicalLinks (src, dst)
        );
        ''' 

        dbConnection.execute(sqlCreateTable)
        dbConnection.commit()

        for wa in arrayOfWavelengthAssignments:
            #get virtual link information from DB
            vlsrcWA = wa[0]
            vldstWA = wa[1]
            vlnumWA = wa[2]
            sqlVLs = f"select * from VirtualLinks where src={vlsrcWA:d} and dst={vldstWA:d} and num={vlnumWA:d}"
            cursorVLs = dbConnection.execute(sqlVLs)
            datasetVLs = cursorVLs.fetchall()

            #get physical link information from DB
            plsrcWA = wa[0]
            pldstWA = wa[1]
            sqlPLs = f"select * from PhysicalLinks where src={plsrcWA:d} and dst={pldstWA:d}"
            cursorPLs = dbConnection.execute(sqlPLs)
            datasetPLs = cursorPLs.fetchall()
            if len(datasetPLs)==0:
                plsrcWA = wa[1] # swap physical link source and destination since they are bidirectional
                pldstWA = wa[0]
                sqlPLs = f"select * from PhysicalLinks where src={plsrcWA:d} and dst={pldstWA:d}"
                cursorPLs = dbConnection.execute(sqlPLs)
                datasetPLs = cursorPLs.fetchall()

            if len(datasetVLs)==1 and len(datasetPLs)>=1:
                #insert wavelength assignment into DB
                vlsrc   = wa[0]
                vldst   = wa[1] 
                vlnum   = wa[2]
                plsrc   = wa[3]
                pldst   = wa[4]
                fiberid = wa[5]
                waveid  = wa[6]
                result  = wa[7]
                if (vlsrc==vlsrcWA) and (vldst==vldstWA) and (vlnum==vlnumWA) and (plsrc==plsrcWA) and (pldst==pldstWA):
                    sqlPut  = "INSERT INTO RoutingVirtualLinksOverPhysicalTopologyWavelengthAssignmentsAfterLimitsResults "
                    sqlPut += "(vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result) "
                    sqlPut += f"VALUES ({vlsrc:d},{vldst:d},{vlnum:d},{plsrc:d},{pldst:d},{fiberid:d},{waveid:d},'{result:s}');"
                    dbConnection.execute(sqlPut)
                    dbConnection.commit()
        
        #update RoutingVirtualLinksOverPhysicalTopology
        sqlPass  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (vlsrc, vldst, vlnum) IN ("

        sqlBlocked  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlBlocked += "SET result = 'Blocked' "
        sqlBlocked += "WHERE (vlsrc, vldst, vlnum) IN ("

        for row in arrayOfWavelengthAssignments:        
            if row[7] == "Pass":
                sqlPass += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countPass += 1
            else:
                sqlBlocked += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countBlocked += 1
        
        sqlPass = sqlPass[:-1]+")"
        sqlBlocked = sqlBlocked[:-1]+")"

        if countPass > 0:
            dbConnection.execute(sqlPass)
            dbConnection.commit()

        if countBlocked > 0:
            dbConnection.execute(sqlBlocked)
            dbConnection.commit()




def updateDB_RoutingVirtualLinksOverPhysicalTopology(newRoutings, routingResults, dbConnection):

    newRoutings = normalize_dict(newRoutings)

    countPass = 0
    countBlocked = 0

    array = []
    for key in newRoutings:
        numberofphysicallinks = len(newRoutings[key])

        for i in range(numberofphysicallinks):
            array.append( (key[0], key[1], key[2], newRoutings[key][i][0], newRoutings[key][i][1], newRoutings[key][i][2], newRoutings[key][i][3], routingResults[key]) )
            # (vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result)

    #print("<li>updateDB_RoutingVirtualLinksOverPhysicalTopology() >> array:",array)

    # SQL clause 3: insert routings and results as a new table to the database
    # boithitikos pinakas gia apothikeusi twn routings kai twn apotelesmatwn tous

    if len(array) > 0:
        sql4 = """
                CREATE TABLE IF NOT EXISTS RoutingVirtualLinksOverPhysicalTopologyWithLimitResults (
                    vlsrc integer NOT NULL,
                    vldst integer NOT NULL,
                    vlnum integer NOT NULL,
                    plsrc integer NOT NULL,
                    pldst integer NOT NULL,
                    fiberid integer NOT NULL,
                    waveid integer NOT NULL,
                    result text NOT NULL,
                    PRIMARY KEY (vlsrc, vldst,vlnum, plsrc, pldst, fiberid, waveid),
                    FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num));
                """
        
        #there is no physical link related in case of a blocked lightpath
        #therefore, the foreign key constraint for the PhysicalLinks is removed
        '''
            FOREIGN key (plsrc, pldst) REFERENCES PhysicalLinks (src, dst)
        );
        ''' 

        dbConnection.execute(sql4)
        dbConnection.commit()

        sql5 = "INSERT INTO RoutingVirtualLinksOverPhysicalTopologyWithLimitResults (vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result) VALUES (?,?,?,?,?,?,?,?);"
        dbConnection.executemany(sql5, array)
        dbConnection.commit()

        
        #update RoutingVirtualLinksOverPhysicalTopology
        sqlPass  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (vlsrc, vldst, vlnum) IN ("

        sqlBlock  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlBlock += "SET result = 'Blocked' "
        sqlBlock += "WHERE (vlsrc, vldst, vlnum) IN ("

        for row in array:        
            if row[7] == "Pass":
                sqlPass += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countPass += 1
            else:
                sqlBlock += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countBlocked += 1
        
        sqlPass = sqlPass[:-1]+")"
        sqlBlock = sqlBlock[:-1]+")"

        if countPass > 0:
            dbConnection.execute(sqlPass)
            dbConnection.commit()

        if countBlocked > 0:
            dbConnection.execute(sqlBlock)
            dbConnection.commit()




def updateDB_RoutingVirtualLinksOverPhysicalTopology_Copy(newRoutings, routingResults, dbConnection):

    countPass = 0
    countBlocked = 0

    array = []
    for key in newRoutings:
        numberofphysicallinks = len(newRoutings[key][0])

        for i in range(numberofphysicallinks):
            array.append( (key[0], key[1], key[2], newRoutings[key][0][i][0], newRoutings[key][0][i][1], newRoutings[key][0][i][2], newRoutings[key][0][i][3], routingResults[key]) )
            # (vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result)

    #print("<li>updateDB_RoutingVirtualLinksOverPhysicalTopology() >> array:",array)

    # SQL clause 3: insert routings and results as a new table to the database
    # boithitikos pinakas gia apothikeusi twn routings kai twn apotelesmatwn tous

    if len(array) > 0:
        sql4 = """
                CREATE TABLE IF NOT EXISTS RoutingVirtualLinksOverPhysicalTopologyWithLimitResults (
                    vlsrc integer NOT NULL,
                    vldst integer NOT NULL,
                    vlnum integer NOT NULL,
                    plsrc integer NOT NULL,
                    pldst integer NOT NULL,
                    fiberid integer NOT NULL,
                    waveid integer NOT NULL,
                    result text NOT NULL,
                    PRIMARY KEY (vlsrc, vldst,vlnum, plsrc, pldst, fiberid, waveid),
                    FOREIGN key (vlsrc, vldst, vlnum) REFERENCES VirtualLinks (src, dst, num));
                """
        
        #there is no physical link related in case of a blocked lightpath
        #therefore, the foreign key constraint for the PhysicalLinks is removed
        '''
            FOREIGN key (plsrc, pldst) REFERENCES PhysicalLinks (src, dst)
        );
        ''' 

        dbConnection.execute(sql4)
        dbConnection.commit()

        sql5 = "INSERT INTO RoutingVirtualLinksOverPhysicalTopologyWithLimitResults (vlsrc, vldst, vlnum, plsrc, pldst, fiberid, waveid, result) VALUES (?,?,?,?,?,?,?,?);"
        dbConnection.executemany(sql5, array)
        dbConnection.commit()

        
        #update RoutingVirtualLinksOverPhysicalTopology
        sqlPass  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlPass += "SET result = 'Pass' "
        sqlPass += "WHERE (vlsrc, vldst, vlnum) IN ("

        sqlBlock  = "UPDATE RoutingVirtualLinksOverPhysicalTopology "
        sqlBlock += "SET result = 'Blocked' "
        sqlBlock += "WHERE (vlsrc, vldst, vlnum) IN ("

        for row in array:        
            if row[7] == "Pass":
                sqlPass += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countPass += 1
            else:
                sqlBlock += f"({row[0]:d},{row[1]:d},{row[2]:d})," # (vlsrc, vldst, vlnum),
                countBlocked += 1
        
        sqlPass = sqlPass[:-1]+")"
        sqlBlock = sqlBlock[:-1]+")"

        if countPass > 0:
            dbConnection.execute(sqlPass)
            dbConnection.commit()

        if countBlocked > 0:
            dbConnection.execute(sqlBlock)
            dbConnection.commit()


def removeDB_BlockedVirtualLinksOverPhysicalTopology(newRoutings, routingResults, dbConnection):
    
    sqlBlock = "DELETE from RoutingVirtualLinksOverPhysicalTopology Where result = 'Blocked'"

    dbConnection.execute(sqlBlock)
    dbConnection.commit()


def calculateWmnFromSQLite(dbConnection,L):

    sql= """
            select count(waveid)
            from RoutingVirtualLinksOverPhysicalTopology
            group by plsrc, pldst
         """
    cursor = dbConnection.execute(sql)
    dataset = cursor.fetchall()


def calculatePhysicalLinkStatisticsAndPowerParameters(N, L, S, Wmn, CUmn, Lmn, fmn, Em, El, Amn, LatRouterPort, LatTransponder, LatEDFA, LatFiberKilometer, dbConnection):
    # used for power calculation

    #SOP
    if (GlobalPrintOutEnabled==True) :   
        print ("<table class='data'>")
        print ("<tr><th colspan=9>Statistics about Physical Links before applying limitations</th></tr>")
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
        CU = roundatdecimals(CUmn.get(key),3)                                                                        # CU : capacity utilised
        CR = wl * maxGbpsPerWavelength                                                                               # CR : capacity required
        CF = roundatdecimals((CR - CU), 3)                                                                           # CF : capacity free
        wU = roundatdecimals((CU / CR * 100.0), 1) if CR>0 else 0                                                    # wU : wavelength utilisation percentage # prevent division by zero
        fU = roundatdecimals((CU / (fibers * maxFiberCapacity) * 100.0), 1) if (fibers * maxFiberCapacity)>0 else 0  # fU : fiber link utilisation percentage # prevent division by zero

        wUtotal += wU
        fUtotal += fU

        updateTotals(fmn, key, fibers)
        distance = Lmn.get(key)

        #SOP
        if (GlobalPrintOutEnabled==True) :    
            print("<tr><td>",N[L[key][0]]+"-"+N[L[key][1]],"</td><td>",wl,"</td><td>",fibers,"</td><td>",distance,"</td><td>",CU,"</td><td>",CF,"</td><td>",CR,"</td><td>",wU,"</td><td>",fU,"</td></tr>")
        #EOP

    wUaverage = wUtotal / len(keys) if len(keys)>0 else 0.0 # prevent division by zero
    fUaverage = fUtotal / len(keys) if len(keys)>0 else 0.0 # prevent division by zero

    wUaverage = roundatdecimals(wUaverage,1)
    fUaverage = roundatdecimals(fUaverage,1)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("</table>")
    #EOP

    ##########used for power calculation
    ##########key = linknumber(L, sp[0],sp[1])
    ##########numOfEDFAs = int ( ( dist[key] / distEDFA - 1.0 ) + 2.0 )

    for physicallink in L:
        key = linknumber(L,physicallink[0],physicallink[1])
        LmnValue = Lmn.get(key)
        value = numpy.ceil(LmnValue / S - 1.0) + 2 if S>0 else 0  # prevent division by zero
        accumulatePowerParameters(Amn, key, value)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        printAmn(Amn, N, L)
    #EOP

    return wUaverage, fUaverage



def getWmnFromDB(Wmn, L, dbConnection):

    Wmn = {}

    sql = "SELECT plsrc, pldst, count(waveid) FROM RoutingVirtualLinksOverPhysicalTopology GROUP BY plsrc, pldst;"
    cursor = dbConnection.execute(sql)
    dataset = cursor.fetchall()
    for row in dataset:
        key = linknumber(L, row[0], row[1])
        Wmn[key] = roundatdecimals(float(row[2]),0)   # number of wavelengths on physical link (m,n)
    
    return Wmn




def getCUmnFromDB(CUmn, L, dbConnection):

    CUmn = {}

    sql = "SELECT plsrc, pldst, sum(routeTReqOverVTutilCap) FROM route_traffic_requests_over_virtual_and_physical_topology GROUP BY plsrc, pldst;"
    cursor = dbConnection.execute(sql)
    dataset = cursor.fetchall()
    for row in dataset:
        key = linknumber(L, row[0], row[1])
        CUmn[key] = roundatdecimals(row[2],3)   # number of wavelengths on physical link (m,n)
    
    return CUmn


def getSigmaCijFromDB(SigmaCij, N, dbConnection):

    SigmaCij = {}

    sql = "SELECT vlsrc, count(vlnum) FROM routingTrafficRequestsOverVirtualTopology where type = 'New' and result<>'Blocked' GROUP BY vlsrc;"
    cursor = dbConnection.execute(sql)
    dataset = cursor.fetchall()
    for row in dataset:
        srcnode = row[0]
        SigmaCij[srcnode] = roundatdecimals(row[1],3)   # number of wavelengths on physical link (m,n)
    
    return SigmaCij



def evaluatePowerConsumptionUsingLeeRheeFormula(GvirtualLinkTotals, RoutingOfVirtualLinksOverWavelengths, G, N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B):

    # Evaluate Power (start) >>>

    ValueOfPower = 0.0

    gamma = 1.0 # EPI = 100%
    # Elinecardmax = 
    d = Lmn # distances
    p_max = maxFiberCapacity # max capacity of a fiber in Gbps

    EnergyIP = 0.0

    LPids = list(GvirtualLinkTotals.keys())
    #LPids.sort()
    for lpid in LPids:
        lp = GvirtualLinkTotals.get(lpid) 
        p_lp = lp[0] #traffic load of lightpath (virtual link) in Gbps
        Elinecardmax = p_lp * 10.0 # Watts

        EnergyIP += (1 - gamma) * Elinecardmax + (p_lp / p_max) * gamma * Elinecardmax
    
    EnergyWDMcoefficient = 0.0

    utilisedLinks={}   # {(m,n):True, ...}
    LPids = list(GvirtualLinkTotals.keys())   # {(2, 3, 0): [(2, 1, 4, 0), (1, 3, 3, 3)],...}
    
    for lpid in LPids:
        src=lpid[0]
        dst=lpid[1]
        Lnum = linknumber(L, lpid[0], lpid[1])
        if Lnum!=None:
            for wavelengthAssignment in RoutingOfVirtualLinksOverWavelengths.get(lpid, []):
                plsrc = wavelengthAssignment[0]
                pldst = wavelengthAssignment[1]
                linkKey = (plsrc, pldst)
                if linkKey not in utilisedLinks:
                    utilisedLinks[linkKey] = True

    for linkKey in utilisedLinks:
        Lnum = linknumber(L, linkKey[0], linkKey[1])
        if Lnum!=None:
            d_l = d[Lnum]
            EnergyWDMcoefficient += numpy.ceil( d_l / B ) + 1
        
    EnergyWDM = Ee * EnergyWDMcoefficient
    
    EnergyIP = roundatdecimals(EnergyIP/1000.0,3)
    EnergyWDM = roundatdecimals(EnergyWDM/1000.0,3)
    
    Energy = EnergyIP + EnergyWDM
    Energy = roundatdecimals(Energy, 3)    

    return EnergyIP, EnergyWDM, Energy





def evaluatePowerConsumption(N, L, SigmaCij, Wmn, CUmn, Lmn, fmn, Em, El, Amn, Di, Er, Et, Ee, B):

    # Evaluate Power (start) >>>

    ValueOfPower = 0.0

    #SOP
    if (GlobalPrintOutEnabled==True) :
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
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[k],"</td><td>",Er, "* (",valDi,"+",valSigmaCij,") =",ValueOfPower,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
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
        ValueOfPower = Et * (valWmn if valWmn is not None else 0.0)
        PowerTransponders += ValueOfPower

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>",Et, "*",valWmn,"=",ValueOfPower,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
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
        if (GlobalPrintOutEnabled==True) :
            print("<tr><td>",N[L[i][0]],"-",N[L[i][1]],"</td><td>",Ee, "*",valAmn,"*",valfmn,"=",ValueOfPower,"</td></tr>")
        #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print("<tr><th colspan=2>Total:",PowerEDFAs,"Watts</th></tr>")
        print("</table>")
    #EOP

    PowerTotal = PowerIP + PowerTransponders + PowerEDFAs
    PowerTotal = roundatdecimals(PowerTotal/1000.0,3)

    PowerIP = roundatdecimals(PowerIP/1000.0,3)
    PowerTransponders = roundatdecimals(PowerTransponders/1000.0,3)
    PowerEDFAs = roundatdecimals(PowerEDFAs/1000.0,3)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='tablePow'>")
        print ("<tr><th>Evaluation of total energy consumption in the network</th></tr>")
        print ("<tr><td>",mathPowerFormula(),"</td></tr>")
        print ("<tr><th>Total power consumption",PowerTotal,"kWatts</th></tr>")
        print ("</table>")
    #EOP

    # >>> Evaluate Power (end)

    return PowerIP, PowerTransponders, PowerEDFAs, PowerTotal






def convertVTtoOldFormatForRoutingOverPhysicalTopology(VirtualLinkTotals, N):
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
    if (GlobalPrintOutEnabled==True) :
        print ("<table class='table1c'>")
        print ("<tr><th colspan=5>The virtual topology for routing over physical topology</th></tr>")
        print ("<tr><th>source&rarr;destination </th><th>source (s)</th><th>destination (d)</th><th>number (n)</th><th>capacity</th>")
    #EOP

    VTfinal = newVTFinal

    for link in VTfinal:
        capacities = VTfinal.get(link)
        lines = len(capacities)

        #SOP
        if (GlobalPrintOutEnabled==True) :
            print ("<tr><td rowspan=",lines,">",N[link[0]],"&rarr;",N[link[1]],"</td>")
            print ("<td rowspan=",lines,">",link[0],"</td>")
            print ("<td rowspan=",lines,">",link[1],"</td>")
            print ("<td rowspan=",lines,">",link[2],"</td>")
        #EOP

        for c in capacities:
            VirtualLinks.append([N[link[0]], N[link[1]], link[2], c])

            #SOP
            if (GlobalPrintOutEnabled==True) :
                print ("<td>",c,"</td>")
                print("</tr>")
            #EOP

    #SOP
    if (GlobalPrintOutEnabled==True) :
        print ("</table>")
    #EOP

    VT = VirtualLinks
    return VT, VTfinal



def calculateSomePowerParametersForNodesAndLinks(VT, N, Cij, SigmaCij):
    # used for power calculation
    #Cij: calculated as the number of virtual links (lightpaths) between a node pair (i,j) 
    for vl in VT:
        t=(nodenumber(N,vl[0]),nodenumber(N,vl[1]))
        accumulatePowerParameters(Cij, t, 1)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        printCij(Cij, N)
    #EOP

    #SigmaCij: calculated as the number of virtual links (lightpaths) that originate from a node i
    for k in Cij:    
        val = Cij.get(k)
        accumulatePowerParameters(SigmaCij, k[0], val)

    #SOP
    if (GlobalPrintOutEnabled==True) :
        printSigmaCij(SigmaCij, N)
    #EOP

    return Cij, SigmaCij



def normalize_dict(data: dict) -> dict:
    """
    Normalize dictionary values so each key maps to a flat list of tuples.
    
    Input can be either:
        {(a, b, c): [[(i, j, k, l), (w, x, y, z)]], ...}
    or
        {(a, b, c): [(i, j, k, l), (w, x, y, z)], ...}
        
    Returns:
        {(a, b, c): [(i, j, k, l), (w, x, y, z)], ...}
    """
    normalized = {}
    for key, value in data.items():
        if len(value) > 0 and isinstance(value[0], list):
            # case 1: value is wrapped in an extra list
            # flatten it
            flat_list = []
            for sublist in value:
                flat_list.extend(sublist)
            normalized[key] = flat_list
        else:
            # case 2: already a flat list
            normalized[key] = value
    return normalized





def shortestHopDistance_notUsed(Nmc, src, dst):
    # use Dijkstra's algorithm to find the shortest path
    import heapq

    queue = [(0, src)]  # (cost, node)
    visited = set()
    min_cost = {src: 0}

    while queue:
        cost, node = heapq.heappop(queue)

        if node in visited:
            continue
        visited.add(node)

        if node == dst:
            return cost

        for neighbor in Nmc.get(node, {}):
            if neighbor in visited:
                continue
            new_cost = cost + Nmc[node][neighbor]
            if new_cost < min_cost.get(neighbor, float('inf')):
                min_cost[neighbor] = new_cost
                heapq.heappush(queue, (new_cost, neighbor))

    return float('inf')  # return infinity if there is no path



def sortTrafficRequestsByHottestAndComparison(TReqs, N, Nt, NmC):
            
    # calculate shortest hop distance for each request
    hopdist = {}
    for TR in TReqs:
        src = TR[0]
        dst = TR[1]
        src_str = N[TR[0]]
        dst_str = N[TR[1]]
        ShortestPath = find_shortest_path_using_Dijkstra_and_transition_costs(N,Nt,NmC,src_str,dst_str)
        hopdist.update({(src,dst):ShortestPath})
        #print("<li>request/flow",TR,"shortest path",ShortestPath)

    # calculate the ratio of traffic demand / shortest hop distance for each request
    ratio = {}
    for TR in TReqs:
        src = TR[0]
        dst = TR[1]
        cap = TR[2]
        shortestHopDistance = len(hopdist.get((src,dst)))-1
        if shortestHopDistance > 0:
            r = cap / shortestHopDistance if shortestHopDistance>0 else 0.0 # prevent division by zero
        else:
            r = float('inf') # if shd is 0 then the source is the destination, so I put infinty to make sure it will be the first request to be served
        r = roundatdecimals(r,3)
        ratio.update({(src,dst,cap):r})
        #print("<li>req",TR,"ratio",r)

    # sort requests based on the ratio in descending order
    TReqs.sort(key=lambda x: ratio.get((x[0],x[1],x[2])), reverse=True)
    print("<li>TReqs sorted by hottest and comparison")
    for TR in TReqs:
        print("<li>request/flow",TR,"ratio",ratio.get((TR[0],TR[1],TR[2])))
    return TReqs



def AverageLatencyOfTrafficRequests(dbConnection):
    sql = "select avg(TrafficRequestLatency) from LatencyOfTrafficRequest"
    cursor = dbConnection.execute(sql)
    dataset = cursor.fetchall()
    avgLatency = 0.0
    for row in dataset:
        avgLatency = roundatdecimals(row[0],3)
    return str(avgLatency)


#12-10-2025
def blockTrafficAccordingToHardLatencyCap(dbConnection, RoutingOfVirtualLinksOverWavelengths, Q_HP_latency_cap, Q_LP_latency_cap):
    
    print("<li><em>Will calculate blocking according to the hard latency limit cap criterion")
    
    #calculateLatencyPerTrafficRequestTempDatabase(dbConnection)   #not needed
    #calculateLatencyPerTrafficRequestTempDatabase_according_to_the_old_latency_formula(dbConnection)   #not needed
    
    countBlockedVL_Q_HP = 0
    countBlockedVL_Q_LP = 0
    newRoutingOfVirtualLinksOverWavelengths = {}
    blockedDueToHardLatencyCap = {}

    rkeys = RoutingOfVirtualLinksOverWavelengths.keys()
    for VL in RoutingOfVirtualLinksOverWavelengths:

        src = VL[0]
        dst = VL[1]
        num = VL[2]

        value = RoutingOfVirtualLinksOverWavelengths[(src, dst, num)]

        sql = f"""
                select TReqQueNum, sum(2*routeVLoverPT_LatIP+routeVLoverPT_LatTransp+PLlatEDFA+PLlatFibLen)
                from route_traffic_requests_over_virtual_and_physical_topology
                where vlsrc = '{src:d}' 
                and   vldst = '{dst:d}'
                and   vlnum = '{num:d}'
                group by vlsrc, vldst, vlnum;
              """

        cursor = dbConnection.execute(sql)
        dbConnection.commit()
    
        dataset = cursor.fetchall() 
        for row in dataset: 
            que = row[0]
            lat = float(row[1])

            if ((que=="0") and (lat > Q_HP_latency_cap)) or ((que=="1") and (lat > Q_LP_latency_cap)):
                blockedDueToHardLatencyCap[(src, dst, num)] = "BlockedHardLatCap"
                countBlockedVL_Q_HP += 1 if que == "0" else 0
                countBlockedVL_Q_LP += 1 if que == "1" else 0
            else:
                blockedDueToHardLatencyCap[(src, dst, num)] = "PassHardLatCap"
                newRoutingOfVirtualLinksOverWavelengths[(src, dst, num)] = value

    return newRoutingOfVirtualLinksOverWavelengths, blockedDueToHardLatencyCap, countBlockedVL_Q_HP, countBlockedVL_Q_LP



def getListOfLatenciesForAllTrafficRequestsNEWformula(dbConnection):
    # sql_by_quenum_reqnum = "Select * from LatencyOfTrafficRequest order by TReqQueNum ASC, TReqQueNum ASC;"
    
    sql = "Select TrafficRequestLatency from LatencyOfTrafficRequest order by TrafficRequestLatency ASC;"

    cursor = dbConnection.execute(sql)
    dbConnection.commit()
    dataset = cursor.fetchall() 
    strOutput = "["
    for row in dataset:
        value = roundatdecimals(float(row[0]),3)
        strOutput += str(value)+","
    strOutput += "]"

    return strOutput



def getListOfLatenciesForAllTrafficRequestsOLDformula(dbConnection):
    # sql_by_quenum_reqnum = "Select * from LatencyOfTrafficRequest order by TReqQueNum ASC, TReqQueNum ASC;"
    
    sql = "Select TotalLatency from LatencyPerTrafficRequestAccordingToTheOldFormula order by TotalLatency ASC;"

    cursor = dbConnection.execute(sql)
    dbConnection.commit()
    dataset = cursor.fetchall() 
    strOutput = "["
    for row in dataset:
        value = roundatdecimals(float(row[0]),3)
        strOutput += str(value)+","
    strOutput += "]"

    return strOutput


