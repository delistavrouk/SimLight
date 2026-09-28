
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
        