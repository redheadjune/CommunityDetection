# -*- coding: utf-8 -*-



def linearity(graph, a, b, c):
    """Computes the best linearity based metric for partitioning the graph.
    Parameters
    ---------
    graph : a networkx graph
    a : the constant weighting of I(C)
    b : the constant weighting of E(C)
    c : the constant weighting of |S|
    
    Returns
    -------
    parition : a dictionary of which nodes belong to which community
    
    Method
    ------
    Adapts the Louvain algorithm to create a partition.
    
    It is recommended to run this with the expansion
    """
    
    # create the dendogram
    dendo = create_dendogram(graph.copy(), a, b, c)
    
    # traces the final community by marching through the dendo's heirarchy
    partition = dendo[0].copy()
    for level in range(1, len(dendo)) :
        for n in partition:
            partition[n] = dendo[level][partition[n]]
            
    return partition
    
    
def create_dendogram(graph, a, b, c):
    """ Creates the dendogram according to the paper
    """
    
    
    
    
    status = Status()
    status.init(current_graph, part_init)
    mod = __modularity(status)
    status_list = list()
    __one_level(current_graph, status)
    new_mod = __modularity(status)
    partition = __renumber(status.node2com)
    status_list.append(partition)
    mod = new_mod
    current_graph = induced_graph(partition, current_graph)
    status.init(current_graph)
    
    while True :
        __one_level(current_graph, status)
        new_mod = __modularity(status)
        if new_mod - mod < __MIN :
            break
        partition = __renumber(status.node2com)
        status_list.append(partition)
        mod = new_mod
        current_graph = induced_graph(partition, current_graph)
        status.init(current_graph)
    return status_list[:]
    
    
    
def __one_level(graph, bar):
    """
    """
    
    
    
