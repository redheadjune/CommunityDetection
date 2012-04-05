# -*- coding: utf-8 -*-

import networkx as nx
import Partitions as P
import Metrics as M
import Expand as E
import Tools as T
import Local_Communities as LC

# This is for scripts necessary to test the modules.

def debug_toy_graph_1():
    """ Small Diamond graph with two fingers.  Checks all methods
    
    Parameters
    ----------
    
    Returns
    -------
    
    
    """
    
    toy_graph = nx.Graph()
    toy_graph.add_nodes_from(range(9))
    toy_graph.add_edges_from([(0, 1), (1, 2), (2, 3), (2, 4), (2, 5), (3, 4),
                              (3, 6), (4, 5), (4, 6), (5, 6), (5, 7), (7, 8)])
    param = (0.2, 0.15, 1/180.)
    
    return run_on_toy(toy_graph, param)
            
    
def debug_toy_graph_2():
    """ Small nearly two clique graph.  Checks all methods
    
    Parameters
    ----------
    
    Returns
    -------
    
    
    """
    
    toy_graph = nx.Graph()
    toy_graph.add_nodes_from(range(9))
    toy_graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4), (2, 4), (3, 1),
                              (5, 6), (5, 7), (6, 7), (1, 6), (0, 2), (0, 3),
                              (4, 8), (4, 1)])
    param = (0.2, 0.15, 1/180.)
    
    return run_on_toy(toy_graph, param)
    
def debug_toy_graph_3():
    """ parallel cliques.  Checks all methods
    
    Parameters
    ----------
    
    Returns
    -------
    
    
    """
    
    toy_graph = nx.Graph()
    toy_graph.add_nodes_from(range(6))
    toy_graph.add_edges_from([(0, 1), (1, 2), (2, 0), (0, 3), (1, 4), (2, 5),
                              (3, 5), (3, 4), (4, 5), (0, 5), (2, 3)])
    param = (0.1, 1/9., 1/180.)
    
    return run_on_toy(toy_graph, param)
   
    
def debug_delta_C():
    """ Feeds a partition to see how the algorithms expand C.  Checks all
methods
    """
    
    toy_graph = nx.Graph()
    toy_graph.add_nodes_from(range(13))
    toy_graph.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3),
                              (5, 4), (4, 6), (4, 7), (4, 8), (5, 6), (5, 7),
                              (5, 8), (6, 7), (6, 8), (7, 8),
                              (11, 12),
                              (8, 11), (1, 5),
                              (10, 4), (10, 5), (10, 6), (10, 7), (10, 8),
                              (9, 5), (9, 6), (9, 7), (9, 8), (3, 9), (9, 11)])
    param = (0.1, 1/9., 1/180.)
    part = {0:0, 1:1, 2:2, 3:3, 4:4, 5:4, 6:4, 7:4, 8:4, 9:5, 10:6, 11:7, 12:8}
    
    return run_on_toy(toy_graph, param, part=part), toy_graph
    
def delta_test():
    
    toy_graph = nx.Graph()
    toy_graph.add_nodes_from(range(10))
    toy_graph.add_edges_from([(0, 1), (0, 2),(1, 2),
                              (3, 4), (3, 5), (3, 6), (3, 7), (4, 5), (4, 6),
                              (4, 7), (5, 6), (5, 7),
                              (8, 5), (8, 6), (8, 7),
                              (9, 5),
                              (0, 3)])
    param = (0.1, 1/9., 1/180.)
    part = {0:0, 1:1, 2:2, 3:3, 4:4, 5:4, 6:4, 7:4, 8:4, 9:5}
    
    return run_on_toy(toy_graph, param, part=part), toy_graph
    
    
def run_on_toy(toy_graph, param, part=None):
    
    mod_part = P.partition(toy_graph, 'modularity', part=part)
    measure(mod_part, toy_graph, param, 'Modularity')
    
    lin_part = P.partition(toy_graph, 'linearity', param=param, part=part)   
    measure(lin_part, toy_graph, param, 'Linearity')
         
    elin_part = E.expand_linearity(lin_part.copy(),
                                   toy_graph,
                                   param=param)
    measure(elin_part, toy_graph, param, 'Expanded Linearity')
    
    emod_part = E.expand_linearity(mod_part.copy(),
                                   toy_graph, 
                                   param=param)
    measure(elin_part, toy_graph, param, 'Expanded Linearity')  
    
    #communities, sub_graph = LC.local_com(6, toy_graph, param, 1)
    #LC.vis_local_com(communities, 6, toy_graph)
    
    return T.part_to_sets(mod_part), \
           T.part_to_sets(emod_part), \
           T.part_to_sets(lin_part), \
           T.part_to_sets(elin_part)
   
    
    
    
def debug_astro(astro_graph=None,
                lin_part=None,
                mod_part=False,
                elin_part=False,
                param=None):
    """Uses the astrophysics citation graph and compares partition methods.
    
    Parameters
    ----------
    astro_graph : the networkx undirected graph of the network
    lin_part : an already computed partition for linearity
    mod_part : Boolean for whether or not to compute modularity
    elin_part : Boolean for whether or not to expand the lin_part
    param : preset (a, b, c) weightings of I, E, |S|
    
    Returns
    -------
    astro_graph : the networkx undirected graph of the network
    lin_part : the partition created by linearity
    mod_part : the partition create by modularity
    elin_part : the overlapping communities created by expanding lin_part 
    
    Notes
    -----
    For the astro graph, computes the three kinds of partitions and checks how
    they compare across the modularity and linearity metrics.
    
    """
    
    if astro_graph == None:
        astro_graph = load_graph('CA-AstroPh.txt')
            
    if param == None:
        param = (0.2, 0.15, 1/float(astro_graph.number_of_edges() - 100))
        
    if lin_part == None:        
        lin_part = P.partition(astro_graph, 'linearity', param=param) 
        lin_part = lin_part 
        
    measure(lin_part, astro_graph, param, 'Linearity')
    
    if mod_part:
        mod_part = P.partition(astro_graph, 'modularity')
        measure(mod_part, astro_graph, param, 'Modularity')
    
    if elin_part:
        elin_part = E.expand_linearity(lin_part, astro_graph, param)
        measure(elin_part, astro_graph, param, 'Expanded Linearity')
    
    return astro_graph, lin_part, mod_part, elin_part, param
         
    
def measure(part, graph, param, algorithm):
    sets = T.part_to_sets(part)
    print "Testing ", algorithm, " Algorithm: "
    (I, E, mag_S, lin) = M.measure_communities(sets,
                                               graph,
                                               'linearity',
                                               param=param)
    print "    performance under Linearity Metric: "
    print "        I: ", I
    print "        E: ", E
    print "       |S|: ", mag_S
    print "        TT: ", lin
    
    mod = M.measure_communities(sets, graph, 'modularity')
    print "    performance under Modularity Metric: ", mod
    
    print "     Sets: "
    #for s in sets:
    #    print "          ", s
           
    
    
def load_graph(file_name):
    graph = nx.Graph()
    f = open(file_name, 'rb')
    for line in f:
        if line[0] != '#' and line != '\\n':
            [n, m] = line[:-2].split('\t')
            n = int(n)
            m = int(m)
            graph.add_edge(n,m)
            
    f.close()
    # remove duplicates
    for n in graph.nodes():
        try:
            graph.remove_edge(n, n)
        except:
            True
    print "Loaded Graph"
    
    return graph
   