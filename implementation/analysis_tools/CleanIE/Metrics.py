# -*- coding: utf-8 -*-
"""
This module can determine the metric value of communities and
sets of communities.

It is meant to be used to test the merits of different methods
of finding communities.
"""


def measure_community(C, G, metric, param=None):
    
    if metric == 'linearity':
        return linear_single(C, G, param)
        
    elif metric == 'conductance':
        return conductance(C, G)
        
    else:
        Exception("We have not implemented " +
                  metric + " for single communities")


def measure_communities(S, G, metric, param=None):
    
    if metric == 'linearity':
        return linear_set(S, G, param)
        
    elif metric == 'modularity': # have to create the partition
        partition = {}
        name = 0
        for C in S:
            for n in C:
                partition[n] = name
            name += 1
            
        for n in G.nodes():
            if n not in partition:
                partition[n] = name
                name += 1
                
        return modularity(partition, G)
        
    else:
        Exception("We have not implemented " +
                  metric + " for sets of communities")


def linear_single(C, G, param):
    """Compute the linear metric value of community C, a subset of graph G.
        
        Parameters
        ----------
        C: a subset of nodes of G
        G: a networkx undirected, unweighted graph, with no self-loops
        param = (a, b): the relative weighting of I and E
        
        Returns
        -------
        I: the internal density of C
        E: the external density of C
        M: the measure of C, given param

        Raises
        ------
        IOException: if any inputs are incorrectly formed
    """
    
    int_edge_count = 0
    ext_edge_count = 0
    
    for n in C:
        for (u,v) in G.edges(n):
            if u in C and v in C:
                int_edge_count += 1
            else:
                ext_edge_count += 1
                
    if len(C) < 2:
        I = 1.
    else:
        I = int_edge_count / float(len(C) * (len(C) - 1))
        
    if len(C) == 0 or len(C) == len(G):
        E = 0.
    else:
        E = ext_edge_count / float(len(C) * (len(G) - len(C)))
    
    (a, b) = param
    
    return I, E, (a * I - b * E)
    
    
def conductance(C, G):
    """Compute the conductance metric value of community C, a subset of graph G.
        
        Parameters
        ----------
        C: a subset of nodes of G
        G: a networkx undirected, unweighted graph, with no self-loops
        
        Returns
        -------
        conductance: the ratio of internal and all edges

        Raises
        ------
        IOException: if any inputs are incorrectly formed
    """
    
    int_edge_count = 0
    ext_edge_count = 0
    
    for n in C:
        for (u,v) in G.edges(n):
            if u in C and v in C:
                int_edge_count += 1
            else:
                ext_edge_count += 1
                
    return int_edge_count / float(int_edge_count + 2 * ext_edge_count)
            
            
def linear_set(S, G, param):
    """Compute the linear metric value of a set of communities.
        
        Parameters
        ----------
        S: a list of subsets of nodes
        G: a networkx undirected, unweighted graph, with no self-loops
        param = (a, b, c): the relative weighting of I, E, and |S|
        
        Returns
        -------
        I: the internal density of C
        E: the external density of C
        mag_S: the number of communities
        M: the measure of C, given param

        Raises
        ------
        IOException: if any inputs are incorrectly formed
    """
    int_edge_count = 0
    ext_edge_count = 0
    
    edges = {}
    for n in G.nodes():
        edges[n] = G.neighbors(n)
        
    for C in S:
        for n in C:
            for m in G.neighbors(n):
                if m in C:
                    int_edge_count += 1
                    
                    if m in edges[n]:
                        edges[n].remove(m)
                        edges[m].remove(n)
                    
    # now edges contains only edges external to every community
    ext_edge_count = sum([len(neighbors) for neighbors in edges.values()]) / 2
    
    E = ext_edge_count / float(G.number_of_edges())
    
    ideal_I = sum([len(C) * (len(C) - 1) for C in S])
    
    if ideal_I == 0:
        I = 1.
    else:
        I = int_edge_count / float(ideal_I)
        
    (a, b, c) = param
    return I, E, len(S), (a * I - b * E - c * len(S))
    

def modularity(partition, graph) :
    """Compute the modularity of a partition of a graph
    This code is taken from
        #    Copyright (C) 2009 by
        #    Thomas Aynaud <thomas.aynaud@lip6.fr>
        #    All rights reserved.
        #    BSD license.
        
    Parameters
    ----------
    partition : dict
       the partition of the nodes, i.e a dictionary where keys are their nodes
and values the communities
    graph : networkx.Graph
       the networkx graph which is decomposed

    Returns
    -------
    modularity : float
       The modularity

    Raises
    ------
    KeyError
       If the partition is not a partition of all graph nodes
    ValueError
        If the graph has no link
    TypeError
        If graph is not a networkx.Graph

    References
    ----------
    .. 1. Newman, M.E.J. & Girvan, M. Finding and evaluating community structure
in networks. Physical Review E 69, 26113(2004).

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)
    >>> modularity(part, G)
    """

    inc = dict([])
    deg = dict([])
    links = graph.size(weighted = True)
    if links == 0 :
        raise ValueError("A graph without link has an undefined modularity")
    
    for node in graph :
        com = partition[node]
        deg[com] = deg.get(com, 0.) + graph.degree(node, weighted = True)
        for neighbor, datas in graph[node].iteritems() :
            weight = datas.get("weight", 1)
            if partition[neighbor] == com :
                if neighbor == node :
                    inc[com] = inc.get(com, 0.) + float(weight)
                else :
                    inc[com] = inc.get(com, 0.) + float(weight) / 2.

    res = 0.
    for com in set(partition.values()) :
        res += (inc.get(com, 0.) / links) - (deg.get(com, 0.) / (2.*links))**2
    return res