# -*- coding: utf-8 -*-


def find_bridges(graph, threshold):
    """ Finds the bridges in the graph.
    A bridge is, given a threshold, any node with degree less than the
    threshold connected to two nodes with degree >= the threshold that would
    not otherwise be connected.

    Parameters
    ----------
    graph : a networkx graph
    threshold :
    
    Returns
    -------
    bridges : a set of tuple pairs, where each pair should be bridged
    """
    
    bridges = set()
    
    lowdegree = filter(lambda n: graph.degree(n)<threshold, graph.nodes_iter())
    
    for n in lowdegree:
        neighbors = graph.neighbors(n)
        links = []
        for m in neighbors: # potential linkage
            if graph.degree(m) >= threshold:
                links.append(m)
                
        links.sort()        # check if they should in fact be bridged
        for i in range(len(links)):
            for m in links[i+1:]:
                if not graph.has_edge(links[i], m):
                    bridges.update( [ (links[i], m) ] )
                        
    return bridges
    
    
    
    