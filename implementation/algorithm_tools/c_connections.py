
"""This module is for the comparison of communities
"""

def closest_community(graph, c1, set_of_c2):
    """Finds the community most strongly connected to c
    
    Parameters
    ----------
    graph : a networkx graph containing all communities
    c1 : a community object
    set_of_c2 : a array of community objects
    
    Returns
    -------
    closest : a community object in set_of_c with the highest number of
    connections to c
    """
    best = -1
    closest_c = None
    set_a = set(c1.nodes.keys())
    for c2 in set_of_c2:
        count = edges_between(graph, set_a, set(c2.nodes.keys()))
        if count > best:
            best = count
            closest_c = c2
            
    return closest_c
            
    
def edges_between(graph, set_a, set_b):
    """Finds the number of edges between set_a and set_b, includes edges in the
    overlap
    """
    count = 0
    disjoint = set_b - set_a
    overlap = set_b.intersection(set_a)
    for n in set_a:
        set_neighbors = set(graph.neighbors(n))
        count += len(set_neighbors.intersection(disjoint))
        count += 0.5 * len(set_neighbors.intersection(overlap))
        
    return count
            