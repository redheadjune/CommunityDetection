# -*- coding: utf-8 -*-

import networkx as nx

def find_sub_cliques(graph):
    """ Finds all the cliques within the graph.
    Parameters
    ---------
    graph : a networkx graph
    
    Returns
    -------
    cliques : a list of all possible maximal cliques
    
    Recommendations
    --------------
    Do not call this on large graphs over 100 nodes!!!
    """
    gencliques = nx.find_cliques(graph)
    
    allcliques = []
    
    while True:
        try:
            allcliques.append(gencliques.next())
        except:
            return allcliques