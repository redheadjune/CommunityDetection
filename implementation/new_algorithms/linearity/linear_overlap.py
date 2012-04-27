
import CommunityDetection as CD

def linear_expand(graph, sets, __A, __B, __C):
    """ Given the sets, expands the sets to include nodes as long as inc metric
    """
    __B = __B / float(graph.number_of_edges())
    # initialize counts for the set of communities
    (n_int_edges, base_int_edges, ext_edges) = get_int_counts(graph, sets)
    for c in sets:
        # initialize counts for the single community
        connected = get_connected_counts(graph, c)   
        inc = 1.
        while inc > 0:
            # find and test the best node, v
            v = get_best_connected(connected)
            if v == None:
                break
            
            new_int_den = (n_int_edges + len(connected[v])) \
                           / float(base_int_edges + 2 * len(c))
            old_int_den = n_int_edges / float(base_int_edges)
            delta_i = new_int_den - old_int_den
            delta_e = len(ext_edges.intersection(set(connected[v])))
            inc = __A * delta_i + __B * delta_e
            if inc > 0:
                n_int_edges += len(connected[v])
                base_int_edges += 2 * len(c)
                ext_edges -= set(connected[v])
                c.update([v])
                connected.pop(v)
    
    return sets


def get_int_counts(graph, sets):
    """ Finds the initial values of the internal and external densities
    """
    n_int_edges = 0
    base_int_edges = 0
    ext_edges = set(graph.edges())
    for c in sets:
        c_int_edges = CD.get_internal_edges(graph, c)
        ext_edges -= set(c_int_edges)
        n_int_edges += len(c_int_edges)
        base_int_edges += len(c) * (len(c) - 1)
    
    return n_int_edges, base_int_edges, ext_edges
 
 
def get_connected_counts(graph, c):
    """ Creates a dictionary keyed on nodes connected to c valued on {E(n, c)}
    Note: each edge is added twice to the connected
    """
    connected = {}
    for n in c:
        for m in graph.neighbors(n):
            if m not in c:
                if m not in connected:
                    connected[m] = []
                connected[m].extend([(n, m), (m, n)])
                
    return connected


def get_best_connected(connected):
    """ Finds the best node to add in connected
    """
    n = None
    connectivity = -1
    for (m, conn) in connected.iteritems():
        if len(conn) > connectivity:
            n = m
            connectivity = len(conn)
            
    return n