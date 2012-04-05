# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import networkx as nx
import Partitions as P
import Tools as T
import Expand as E

def local_com(n, graph, param, radius):
    """Find the communities a node belongs to.
    
    Parameters
    ----------
    n : a node in the graph
    graph : a networkx undirected graph
    param : (a, b, c) that govern finding the local communities
    radius : prefereably only 1 or 2 and determines the radius to seek out
    
    Notes
    -----
    The method is to pull out the local Ball of radius 2 around the node n, and
then find the communities in the ball.  Given these seed communities, we use
expansion to find the more complete communities.
    """
    sub_graph = find_ball_graph(n, radius, graph)
            
    if radius == 1: # can remove the central node
        sub_graph.remove_node(n)    
    
    partition = P.partitions(sub_graph, 'linearity', param=param)
    # partition = E.expand_partition(partition, graph, param)
    
    sets = T.part_to_sets(partition)
    
    if radius == 1: # put the central node back in
        sub_graph.add_node(n)
        for m in graph.neighbors(n):
            graph.add_edge(n, m)
        for s in sets:
            s.append(n)
    else: # remove communities not including n
        to_remove = []
        for s in sets:
            if n not in s:
                to_remove.append(s)
                
        for bad in to_remove:
            sets.remove(bad)
            
    T.vis_local_com(sets, n, sub_graph)
    
    return sets, sub_graph
            
            
def find_ball_graph(nodes, radius, graph):
    """ Pull out the ball of radius around n in the graph.
    """
    sub_graph = nx.Graph()
    nodes = [n for n in nodes]
    for i in range(radius):
        to_append = []
        for m in nodes:
            to_append.extend(graph.neighbors(m))
        nodes.extend(to_append)
                    
    nodes = set(nodes)
    
    for m in nodes:
        neighbors = graph.neighbors(m)
        for p in neighbors:
            if p in nodes:
                sub_graph.add_edge(m,p)
            
    return sub_graph
    
    