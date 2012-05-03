# -*- coding: utf-8 -*-

import networkx as nx

"""
This module can determine the metric value of communities and
sets of communities.

It is meant to be used to test the merits of different methods
of finding communities.
"""

def m_precision(graph, communities):
    """ Given a graph and communities compute the precision
    """
    pass



def m_avg_diameter(graph, communities):
    """ Finds the average diameter of the communities
    """
    diameters = []
    for c in communities:
        sgraph = nx.subgraph(graph, c)
        try:
            diameters.append(nx.diameter(sgraph))
        except:
            pass

    print "Max diameter: ", max(diameters), "Min Diameter: ", min(diameters)
    return sum(diameters) / float(len(diameters))

def m_ncp(graph, communities):
    """ Finds the network community profile - the conductance of every community
    and then maxed per size.
    """
    ncp_values = []
    for c in communities:
        ncp_values.append( (len(c), m_conductance(graph, c)) )
    
    best_k = {}
    for i in range(max([len(c) for c in communities])):
        possible = filter(lambda (k, n): k == i, ncp_values)
        if possible != []:
            best_k[i] = min([n for (k, n) in possible])
            
    return best_k
    

def m_linearity_single(graph, seed, param):
    """ Computes the linearity of the seed. Presumes that
    """
    I, E = I_E(graph, seed)
    (a, b) = param
    return a * I - b * E

def m_modularity_module(graph, seed):
    """ Computes the contribution of the single module to modularity
    """
    int_edges, ext_edges = in_and_out(graph, seed)
    L = float(graph.number_of_edges())
    return int_edges / L - (2 * int_edges + ext_edges)**2 / 4. / L**2


def m_normalized_cut(graph, seed):
    """ Computes the normalized cut value of the seed
    """
    int_edges, ext_edges = in_and_out(graph, seed)
    left = 1.0 / float(2* int_edges + ext_edges)
    right = 1.0 / float(2 * (graph.number_of_edges() - int_edges) + ext_edges)
    return ext_edges * (left + right)


def m_conductance(graph, seed):
    """Calculates the conductance of seed within graph, couple with minimize
    """  
    internal_edges, external_edges = in_and_out(graph, seed)
    return external_edges / float(external_edges + 2 * internal_edges)


def m_expansion(graph, seed):
    """finds the expansion of the seed, couple with minimize
    """
    internal_edges, external_edges = in_and_out(graph, seed)
    return external_edges / float(len(seed))


def m_cut_ratio(graph, seed):
    """finds the cut ratio, couple with minimize
    """
    I, E = I_E(graph, seed)
    return E


def m_edges_cut(graph, seed):
    """finds the edge cuts, couple with  minimize
    """
    internal_edges, external_edges = in_and_out(graph, seed)
    return external_edges

def m_prev_internal(graph, seed):
    """finds the internal density metric, couple with minimize
    """
    I, E = I_E(graph, seed)
    return 1 - I


def m_volume(graph, seed):
    """finds the internal density metric, couple with maximize
    """
    internal_edges, external_edges = in_and_out(graph, seed)
    return 2 * internal_edges + external_edges


def compare_maximize(m, new_m):
    """ Gives a comparison function for maximization
    """
    return new_m - m


def compare_minimize(m, new_m):
    """ Gives a comparison function for minimization
    """
    return m - new_m


def I_E(graph, seed):
    """ compute in the internal and external density of community c
    """
    in_degree, out_degree = in_and_out(graph, seed)
    return map_degree(in_degree, out_degree, graph, seed) 


def I_E_S(graph, communities):
    """ computes the internal, external density, and number of communities
    according the the definition for a set of communities
    """
    external_edges = set(graph.edges())
    found_internal = 0.
    for c in communities:
        internal_edges = get_internal_edges(graph, c)
        found_internal += len(internal_edges)
        external_edges = external_edges - set(internal_edges)
            
    ideal_int_edges = float(sum([len(c) * (len(c) - 1) for c in communities]))
    I = 1.
    if ideal_int_edges > 0:
        I = found_internal / ideal_int_edges
        
    E = len(external_edges) / float(graph.number_of_edges())
    S = float(len(communities))
    
    return I, E, S


def map_degree(in_degree, out_degree, graph, seed):
    """Returns the internal and external density of one
    community in the graph, based on the in and out degree.
    """
    I = 1.
    if len(seed) > 1:
        I = 2 * in_degree / float(len(seed) * (len(seed) - 1))
    
    E = 0.
    if len(graph) != len(seed):
        E = out_degree / float(len(seed) * (len(graph) - len(seed)))
    
    return I, E
    
        
def in_and_out(graph, seed):
    """Finds the number of internal and external edges of seed within graph.
    
    """
    out_degree = 0.
    in_degree = 0.
    for n in seed:
        for m in graph.neighbors(n):
            if m not in seed:
                out_degree += 1.
            else:
                in_degree += 0.5
                
    return in_degree, out_degree


def get_internal_edges(graph, c):
    """ Finds the edges within c, according the graph
    """
    internal_edges = []
    for n in c:
        for m in graph.neighbors(n):
            if m in c:
                internal_edges.append((n,m))
                
    return internal_edges