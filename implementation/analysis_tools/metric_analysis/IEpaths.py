# -*- coding: utf-8 -*-

import CommunityDetection as CD

def path_I_E_S(graph, sets):
    """ Given a graph and a set of communities, finds the series of (I, E, S)
    values.
    
    Parameters
    ----------
    graph : a networkx graph
    sets : a list of lists, where each internal list is a set of communities
    """
    I_path = []
    E_path = []
    S_path = []
    for c_set in sets:
        (I, E, S) = CD.I_E_S(graph, c_set)
        I_path.append(I)
        E_path.append(E)
        S_path.append(S)
        
    return I_path, E_path, S_path
    

def path_I_E(graph, seed, f, compare, param=None, stop=100):
    """Traces the path of the best f metric community through the IE plane
    Parameters
    ----------
    graph - a networkx graph
    seed - a set of nodes to start from
    f - a metric to optimize
    compare - the function that determines if the metric is being improved
    param - a box to hand in any parameters f depends on, such as in linearity
    
    Returns
    -------
    I_values - a list of the subsequent I values
    E_values - a list of the subsequent E values
    order - the order in which nodes are added
    
    Method
    ------
    At each stage, finds a node that if added to the set decreases conductance
    """
    all_nodes = set(graph.nodes())
    
    I_values = []
    E_values = []
    order = seed[:]
    
    addition = True
    
    while addition != None and len(order) < stop:
        (next_I, next_E) = CD.I_E(graph, order)
        I_values.append(next_I)
        E_values.append(next_E)
        
        addition = greedy_selection(graph, order, f, compare, param)
        if type(addition) == int:
            order.append(addition)
        elif addition != None:
            addition = None
        
    return I_values, E_values, order
   

def greedy_selection(graph, seed, f, compare, param):
    """A slow method to find the next best node to add to the seed
    """
    seed = seed[:]
    if param == None:
        m = f(graph, seed)
    else:
        m = f(graph, seed, param)
    
    possible_n = CD.get_ball(graph, seed, 1) - set(seed)

    inc_m = 0.
    best = None
    
    for n in possible_n:
        seed.append(n)
        if param == None:
            new_m = f(graph, seed)
        else:
            new_m = f(graph, seed, param)    
        
        seed = seed[:-1]        
        if compare(m, new_m) >= inc_m:
            inc_m = compare(m, new_m)
            best = n
            
            
    if best == None: # then need to check if entire graph may improve
        if param == None:
            new_m = f(graph, graph.nodes())
        else:
            new_m = f(graph, graph.nodes(), param) 
        
        if compare(m, new_m) > 0.:
            best = set(graph.nodes())
        
    return best