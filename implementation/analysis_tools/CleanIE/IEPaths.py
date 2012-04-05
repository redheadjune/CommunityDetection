# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np            
    

def path_I_E(graph, seed, f, compare, param):
    """Traces the path of the best conductance community through the IE plane
    Parameters
    ----------
    graph - a networkx graph
    seed - a set of nodes to start from
    
    Returns
    -------
    I_values - a list of the subsequent I values
    E_values - a list of the subsequent E values
    set_of_C - a list of the increasing sets
    
    Method
    ------
    At each stage, finds a node that if added to the set decreases conductance
    """
    all_nodes = set(graph.nodes())
    
    I_values = []
    E_values = []
    set_of_C = []
    (I, E, m) = f(graph, seed, param)
    
    addition = True
    
    while addition:
        (next_I, next_E, next_m) = f(graph, seed, param)
        I_values.append(next_I)
        E_values.append(next_E)
        set_of_C.append(seed.copy())
        
        addition = expand(graph, seed, f, compare, param)
        if type(addition) == int:
            seed.update([addition])
        else:
            seed = addition
        
    return I_values, E_values, set_of_C
   

def expand(graph, seed, f, compare, param):
    """A slow method to find the next best node to add to the seed
    """
    (I, E, m) = f(graph, seed, param)
    possible_n = set(graph.nodes()) - seed

    inc_m = 0.
    best = None
    
    for n in possible_n:
        (I, E, new_m) = f(graph, seed.union([n]), param)
        if compare(m, new_m) >= inc_m:
            inc_m = compare(m, new_m)
            best = n
            
    if not best: # then need to check if entire graph may improve
        (I, E, new_m) = f(graph, graph.nodes(), param)
        if compare(m, new_m) > 0.:
            return set( graph.nodes() )
        
    return best
        
         
         
def conductance(graph, seed, param):
    """Calculates the conductance of seed within graph
    """    
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
                
    return I, E, out_degree / float(in_degree + out_degree)
    
def conductance_compare(m, new_m):
    return m - new_m
    
    
    
def linearity(graph, seed, param):
    """Conducts the linear metric of the seed within the graph
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, param[0] * I - param[1] * E
    
def linearity_compare(m, new_m):
    return new_m - m
    
    
    
def expansion(graph, seed, param):
    """finds the expansion of the seed
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, out_degree / float(len(seed))

def expansion_compare(m, new_m):
    return m - new_m
    
   
    
def cut_ratio(graph, seed, param):
    """finds the cut ratio
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, E
    
def cut_ratio_compare(m, new_m):
    return m - new_m
    
    
    
def edge_cuts(graph, seed, param):
    """finds the edge cuts
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, out_degree
    
def edge_cuts_compare(m, new_m):
    return m - new_m
    
    
    
def internal(graph, seed, param):
    """finds the internal density metric
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, 1 - I
    
def internal_compare(m, new_m):
    return m - new_m
    
    
def volume(graph, seed, param):
    """finds the internal density metric
    """
    in_degree, out_degree = in_and_out(graph, seed)
    I, E = I_and_E(in_degree, out_degree, graph, seed)
        
    return I, E, in_degree + out_degree
    
def volume_compare(m, new_m):
    return new_m - m
    
        
        
def I_and_E(in_degree, out_degree, graph, seed):
    """Returns the internal and external density of one
    community in the graph.
    """
    if len(seed) == 1:
        I = 1.
    else:
        I = in_degree / float(len(seed) * (len(seed) - 1))
    
    if len(graph) == len(seed):
        E = 0.
    else:
        E = out_degree / float(len(seed) * (len(graph) - len(seed)))
    
    return I, E
    
        
def in_and_out(graph, seed):
    """Finds the number of internal and external edges of seed within graph.
    
    """
    out_degree = 0.
    in_degree = 0.
    for n in seed:
        edges = graph.edges(n)
        for (u,v) in edges:
            if v not in seed:
                out_degree += 1.
            else:
                in_degree += 1.
                
    return in_degree, out_degree