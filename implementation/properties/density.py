# -*- coding: utf-8 -*-

""" This module is for getting the density of subgraphs.
"""

def get_internal_density(graph, subset=None):
    """Returns the internal density of the subset within the graph
    
    Parameters
    ----------
    graph : presumes an unweighted, single node node, graph
    subset : a set of nodes
    """
    if subset:
        graph = graph.subgraph(subset)
        
    s = graph.number_of_nodes()
        
    return 2 * graph.number_of_edges() / float(s * (s - 1))
    
    
def get_external_density(graph, subset):
    """Returns the external density of the subset within the graph
    
    JTODO : needs a rewrite to be much faster
    
    Parameters
    ----------
    graph : a networkx weighted graph, keyed on 'weight'
    subset : a set of nodes
    """
    if set(graph.nodes()) == set(subset):
        return 0.
    
    s = 0
    extedges = 0
    for n in subset:
        s += graph.nodes[n]['size']
        for m in graph.neighbors(n):
            if m not in subset:
                extedges += graph[n][m]['weight']
                
    gs = 0
    for n in graph.nodes():
        gs += graph.nodes[n]['size']
                
    return extedges / float( s * (gs - s) )