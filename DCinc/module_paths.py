from DCinc.class_dijkstra import Dijkstra
from DCinc.module_utilspathslinks import nodenumber
import heapq
import copy

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



#16-7-2026 Add Yen's algorithm to find not only the shortest path but the K-shortest paths

#sources: https://people.csail.mit.edu/minilek/yen_kth_shortest.pdf
#         https://dev.to/whoakarsh/finding-the-k-shortest-paths-using-yens-algorithm-in-python-1gka
#         https://www.neo4j.com/docs/graph-data-science/current/algorithms/yens/

'''
def dijkstra_for_yen(adj_matrix, start_node, end_node):
    """
    A standalone Dijkstra algorithm designed to work with Yen's algorithm.
    Takes an adjacency matrix (cost matrix) and returns a path as a list of node indices.
    """
    num_nodes = len(adj_matrix)
    distances = {node: float('inf') for node in range(num_nodes)}
    distances[start_node] = 0
    previous_nodes = {node: None for node in range(num_nodes)}
    pq = [(0, start_node)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Stop early if we reached the destination
        if current_node == end_node:
            break
            
        if current_distance > distances[current_node]:
            continue
            
        for neighbor in range(num_nodes):
            weight = adj_matrix[current_node][neighbor]
            # Assuming weight > 0 is a valid link, and 'inf' or 0 means no link
            if weight != float('inf') and weight > 0: 
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
                    
    # Reconstruct the path
    path, current_node = [], end_node
    if previous_nodes[current_node] is None and current_node != start_node:
        return [] # No path found
        
    while current_node is not None:
        path.insert(0, current_node)
        current_node = previous_nodes[current_node]
        
    return path



def find_k_shortest_paths(N, NmC, start_idx, end_idx, K=3):
    """
    Yen's algorithm to find the top K shortest paths.
    :param N: List of nodes (for reference)
    :param NmC: 2D array representing the cost/transition matrix
    :param start_idx: Integer index of the source node
    :param end_idx: Integer index of the destination node
    :param K: Number of alternative paths to find
    :return: List of paths (each path is a list of node indices)
    """
    # Helper to calculate total cost of a path
    def get_path_cost(path, matrix):
        cost = 0
        for i in range(len(path) - 1):
            cost += matrix[path[i]][path[i+1]]
        return cost

    # A stores the final K shortest paths
    A = []
    # B stores potential candidate paths (cost, path)
    B = []

    # 1. Find the 1st absolute shortest path
    #first_path = dijkstra_for_yen(Nt, start_idx, end_idx)
    first_path = dijkstra_for_yen(NmC, start_idx, end_idx)
    if not first_path:
        return A
        
    A.append(first_path)

    # 2. Iterate to find the K-1 alternative paths
    for k in range(1, K):
        for i in range(len(A[k-1]) - 1):
            spur_node = A[k-1][i]
            root_path = A[k-1][:i+1]
            
            # Create a temporary copy of the cost matrix to modify
            temp_NmC = copy.deepcopy(NmC)
            
            # Remove links used by previous shortest paths that share the same root
            for p in A:
                if len(p) > i and root_path == p[:i+1]:
                    u = p[i]
                    v = p[i+1]
                    temp_NmC[u][v] = float('inf') 
                    
            # Remove nodes in the root path from the graph to prevent looping back
            for root_path_node in root_path[:-1]:
                for neighbor in range(len(temp_NmC)):
                    temp_NmC[root_path_node][neighbor] = float('inf')
                    temp_NmC[neighbor][root_path_node] = float('inf')
            
            # Find the spur path from the spur node to the destination
            #spur_path = dijkstra_for_yen(temp_Nt, spur_node, end_idx)
            spur_path = Dijkstra.dijkstra_for_yen(temp_NmC, spur_node, end_idx)
            
            if spur_path:
                # Combine root path and spur path (spur_node is duplicated, so slice it out)
                total_path = root_path[:-1] + spur_path
                total_cost = get_path_cost(total_path, NmC)
                
                # Add to candidates B if it's uniquely new
                if total_path not in [b_path for _, b_path in B]:
                    B.append((total_cost, total_path))
        
        if not B:
            break
            
        # Sort candidates by cost and select the best one
        B.sort(key=lambda x: x[0])
        A.append(B.pop(0)[1])
        
    return A
'''


#17-7-2026

def dijkstra_for_yen(adj_matrix, start_node, end_node):
    """
    A standalone Dijkstra algorithm designed to work with Yen's algorithm.
    Takes a nested dictionary (cost matrix) and returns a path as a list of node names.
    """
    # Initialize distances and previous_nodes using dictionary keys
    distances = {node: float('inf') for node in adj_matrix}
    distances[start_node] = 0
    previous_nodes = {node: None for node in adj_matrix}
    pq = [(0, start_node)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Stop early if we reached the destination
        if current_node == end_node:
            break
            
        if current_distance > distances[current_node]:
            continue
            
        # Iterate only through actual neighbors in the dictionary
        for neighbor, weight in adj_matrix.get(current_node, {}).items():
            # Assuming weight > 0 is a valid link, and 'inf' or 0 means no link
            if weight != float('inf') and weight > 0: 
                distance = current_distance + weight
                
                # Safety catch in case a destination node has no outbound links
                # and wasn't explicitly added to the base dictionary keys
                if neighbor not in distances:
                    distances[neighbor] = float('inf')
                    previous_nodes[neighbor] = None

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
                    
    # Reconstruct the path
    path, current_node = [], end_node
    
    # Use .get() to avoid KeyError if the end_node was never reached
    if previous_nodes.get(current_node) is None and current_node != start_node:
        return [] # No path found
        
    while current_node is not None:
        path.insert(0, current_node)
        current_node = previous_nodes.get(current_node)
        
    return path


'''
def find_k_shortest_paths(N, NmC, start_idx, end_idx, K=3):
    """
    Yen's algorithm to find the top K shortest paths.
    """
    # ---------------------------------------------------------
    # NEW FIX: Map integer indices to dictionary string keys
    # If the simulation passes an integer, translate it using N
    # ---------------------------------------------------------
    start_node = N[start_idx] if isinstance(start_idx, int) else start_idx
    end_node = N[end_idx] if isinstance(end_idx, int) else end_idx

    # Helper to calculate total cost of a path
    def get_path_cost(path, matrix):
        cost = 0
        for i in range(len(path) - 1):
            # Use .get to safely calculate cost with string keys
            cost += matrix[path[i]].get(path[i+1], float('inf'))
        return cost

    # A stores the final K shortest paths
    A = []
    # B stores potential candidate paths (cost, path)
    B = []

    # 1. Find the 1st absolute shortest path (using the translated string keys)
    first_path = Dijkstra.dijkstra_for_yen(NmC, start_node, end_node) 
    if not first_path:
        return A
        
    A.append(first_path)

    # 2. Iterate to find the K-1 alternative paths
    for k in range(1, K):
        for i in range(len(A[k-1]) - 1):
            spur_node = A[k-1][i]
            root_path = A[k-1][:i+1]
            
            # Create a temporary copy of the cost dict to modify
            temp_NmC = copy.deepcopy(NmC)
            
            # Remove links used by previous shortest paths that share the same root
            for p in A:
                if len(p) > i and root_path == p[:i+1]:
                    u = p[i]
                    v = p[i+1]
                    # Check if the connection exists before modifying
                    if v in temp_NmC.get(u, {}):
                        temp_NmC[u][v] = float('inf') 
                        
            # Remove nodes in the root path from the graph to prevent looping back
            for root_path_node in root_path[:-1]:
                # Remove all outbound links from the root path node
                if root_path_node in temp_NmC:
                    temp_NmC[root_path_node] = {} 
                    
                # Remove all inbound links to the root path node
                for n in temp_NmC:
                    if root_path_node in temp_NmC[n]:
                        temp_NmC[n][root_path_node] = float('inf')
            
            # Find the spur path from the spur node to the destination
            spur_path = dijkstra_for_yen(temp_NmC, spur_node, end_node)
            
            if spur_path:
                # Combine root path and spur path (spur_node is duplicated, so slice it out)
                total_path = root_path[:-1] + spur_path
                total_cost = get_path_cost(total_path, NmC)
                
                # Add to candidates B if it's uniquely new
                if total_path not in [b_path for _, b_path in B]:
                    B.append((total_cost, total_path))
        
        if not B:
            break
            
        # Sort candidates by cost and select the best one
        B.sort(key=lambda x: x[0])
        A.append(B.pop(0)[1])
        
    return A
'''

def find_k_shortest_paths(N, NmC, start_idx, end_idx, K=3):
    """
    Yen's algorithm to find the top K shortest paths.
    Takes either integer indices or string node names.
    """
    # ---------------------------------------------------------
    # Map integer indices to dictionary string keys
    # ---------------------------------------------------------
    start_node = N[start_idx] if isinstance(start_idx, int) else start_idx
    end_node = N[end_idx] if isinstance(end_idx, int) else end_idx

    # Helper to calculate total cost of a path safely
    def get_path_cost(path, matrix):
        cost = 0
        for i in range(len(path) - 1):
            # Chain .get() to entirely prevent KeyErrors
            cost += matrix.get(path[i], {}).get(path[i+1], float('inf'))
        return cost

    # A stores the final K shortest paths
    A = []
    # B stores potential candidate paths (cost, path)
    B = []

    # 1. Find the 1st absolute shortest path
    # (Removed the 'Dijkstra.' prefix)
    first_path = dijkstra_for_yen(NmC, start_node, end_node) 
    if not first_path:
        return A
        
    A.append(first_path)

    # 2. Iterate to find the K-1 alternative paths
    for k in range(1, K):
        for i in range(len(A[k-1]) - 1):
            spur_node = A[k-1][i]
            root_path = A[k-1][:i+1]
            
            # Create a temporary copy of the cost dict to modify
            temp_NmC = copy.deepcopy(NmC)
            
            # Remove links used by previous shortest paths that share the same root
            for p in A:
                if len(p) > i and root_path == p[:i+1]:
                    u = p[i]
                    v = p[i+1]
                    # Check if the connection exists before modifying
                    if v in temp_NmC.get(u, {}):
                        temp_NmC[u][v] = float('inf') 
                        
            # Remove nodes in the root path from the graph to prevent looping back
            for root_path_node in root_path[:-1]:
                # Remove all outbound links from the root path node
                if root_path_node in temp_NmC:
                    temp_NmC[root_path_node] = {} 
                    
                # Remove all inbound links to the root path node
                for n in temp_NmC:
                    if root_path_node in temp_NmC[n]:
                        temp_NmC[n][root_path_node] = float('inf')
            
            # Find the spur path from the spur node to the destination
            # (Removed the 'Dijkstra.' prefix here as well)
            spur_path = dijkstra_for_yen(temp_NmC, spur_node, end_node)
            
            if spur_path:
                # Combine root path and spur path (spur_node is duplicated, so slice it out)
                total_path = root_path[:-1] + spur_path
                total_cost = get_path_cost(total_path, NmC)
                
                # Add to candidates B if it's uniquely new
                if total_path not in [b_path for _, b_path in B]:
                    B.append((total_cost, total_path))

        if not B:
            break
            
        # Sort candidates by cost and select the best one
        B.sort(key=lambda x: x[0])
        A.append(B.pop(0)[1])
        
    # ---------------------------------------------------------
    # NEW FIX: Translate the string paths back into integer paths
    # before returning, so the main simulator doesn't crash!
    # ---------------------------------------------------------
    integer_paths = []
    for path in A:
        int_path = []
        for node in path:
            # Map the string name (e.g., 'Node0') back to its index (e.g., 0)
            if isinstance(node, str) and node in N:
                int_path.append(N.index(node))
            else:
                int_path.append(node) # Fallback if it's already an integer
        integer_paths.append(int_path)
        
    return integer_paths