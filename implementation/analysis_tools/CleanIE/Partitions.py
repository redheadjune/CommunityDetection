# -*- coding: utf-8 -*-

"""
 This module controls partition methods.
 
 In particular for modularity and linearity.
 
 Much of the code is modified from:
  #    Copyright (C) 2009 by
  #    Thomas Aynaud <thomas.aynaud@lip6.fr>
  #    All rights reserved.
  #    BSD license.
 
"""
__PASS_MAX = -1
__MIN = 0.00000001


import networkx as nx
import sys
import types
import array
from Status import Status
   

def partition(G, metric_type, part=None, param=None) :
    """Give the metric, computes the maximal partitioning of G.
    The algorithm's structure uses the Louvain heuristices.

    Parameters
    ----------
    G : networkx.Graph the networkx G which is decomposed
    metric : a string of 'modularity' or 'linearity' 
    param : (a, b, c) if using linearity

    Returns
    -------
    partition : a dictionary, keyed on nodes and valued at their community id

    See Also
    --------
    generate_dendogram to obtain all the decompositions levels

    References
    ----------
    .. 1. Blondel, V.D. et al. Fast unfolding of communities in large networks.
J. Stat. Mech 10008, 1-12(2008).

    Examples
    --------
    >>>  #Basic usage
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> part = best_partition(G)
    
    >>> #other example to display a graph with its community :
    >>> #better with karate_graph() as defined in networkx examples
    >>> #erdos renyi don't have true community structure
    >>> G = nx.erdos_renyi_graph(30, 0.05)
    >>> #first compute the best partition
    >>> partition = community.best_partition(G)
    >>>  #drawing
    >>> size = float(len(set(partition.values())))
    >>> pos = nx.spring_layout(G)
    >>> count = 0.
    >>> for com in set(partition.values()) :
    >>>     count = count + 1.
    >>>     list_nodes = [nodes for nodes in partition.keys()
    >>>                                 if partition[nodes] == com]
    >>>     nx.draw_networkx_nodes(G, pos, list_nodes, node_size = 20,
                                    node_color = str(count / size))
    >>> nx.draw_networkx_edges(G,pos, alpha=0.5)
    >>> plt.show()
    """
    dendo = generate_dendogram(G, metric_type, part=part, param=param)
    
    partition = dendo[0].copy()
    for index in range(1, len(dendo)) :
        for node, community in partition.iteritems() :
            partition[node] = dendo[index][community]
            
    return dendo, partition


def generate_dendogram(G, metric_type, part=None, param=None) :
    """Find the dendogram associated with heirarchically unioning communities.

    A dendogram is a tree and each level is a partition of the graph's nodes. 
Level 0 is the first partition, which contains the smallest communities, and the
best is len(dendogram) - 1. The higher the level is, the bigger are the
communities

    Parameters
    ----------
    G : networkx.Graph to be decomposed
    metric_type : the metric used to determine the quality of a partition
    param : (a, b, c) if using linearity

    Returns
    -------
    dendogram : a list of partitions, where each partition is a dictionary.
Values of the ith dictionary are the keys of the i+1st dictionary.  The first
dictionary's keys are the nodes of the graph.
    
    Raises
    ------
    TypeError If G is not a networkx.Graph

    Notes
    -----
    Only called by partition

    Examples
    --------
    >>> G=nx.erdos_renyi_graph(100, 0.01)
    >>> dendo = generate_dendogram(G)
    >>> for level in range(len(dendo) - 1) :
    >>>     print "partition at level", level, "is", partition_at_level(dendo,
level)
    """    
    if type(G) != nx.Graph :
        raise TypeError("Bad graph type, use only non directed graph")
    current_G = G.copy()
    status = Status()
    status.init(current_G, {}, part=part)
    
    status_list = []
    partition = __renumber(status.node2com)
    status_list.append(partition)
    current_G = induced_graph(partition, current_G)
    status.init(current_G, node_weights(status.com_sizes, partition))
    
    m = __metric(status, metric_type, param)
    new_m = m
    
    while True :
        # print "Doing one level of dendogram", current_G.number_of_nodes()
        __one_level(current_G, status, metric_type, param)
        partition = __renumber(status.node2com)
        status_list.append(partition)
        
        new_m = __metric(status, metric_type, param)
        # print "*** metrics ", status, new_m, m
        if new_m - m < __MIN:
            # print 'Breaking out, of here, hit min improvement'
            # print 'Here were the comparisons, ', m, ' ', new_m
            break
                        
        m = new_m
        current_G = induced_graph(partition, current_G)
        status.init(current_G, node_weights(status.com_sizes, partition))
        
    return status_list[:]
    

def induced_graph(partition, G) :
    """Produce the graph where nodes are the communities.  The weight of edges
between the nodes represents the sum of edges between their respective nodes.

    Parameters
    ----------
    partition : a dictionary keyed on nodes and valued on a node's community
    
    G : the initial graph

    Returns
    -------
    G : networkx.Graph
       a networkx G where nodes are the parts

    Examples
    --------
    >>> n = 5
    >>> G = nx.complete_graph(2*n)
    >>> part = dict([])
    >>> for node in G.nodes() :
    >>>     part[node] = node % 2
    >>> ind = induced_graph(part, g)
    >>> goal = nx.Graph()
    >>> goal.add_weighted_edges_from([(0,1,n*n),(0,0,n*(n-1)/2), (1, 1,
n*(n-1)/2)])
    >>> nx.is_isomorphic(int, goal)
    True
    """
    ret = nx.Graph()
    ret.add_nodes_from(partition.values())
    
    for node1, node2, datas in G.edges_iter(data = True) :
        weight = datas.get("weight", 1)
        com1 = partition[node1]
        com2 = partition[node2]
        w_prec = ret.get_edge_data(com1, com2, {"weight":0}).get("weight", 1)
        ret.add_edge(com1, com2, weight = w_prec + weight)
        
    return ret
    

def node_weights(prev_weights, partition):
    """ Helper function to keep track of how many nodes each com holds
    """
    weights = {}
    for node,com in partition.iteritems():
        if com not in weights:
            weights[com] = 0
        weights[com] += prev_weights.get(node, 1)
    
    return weights


def __renumber(dictionary) :
    """Renumber the values of the dictionary from 0 to n
    """
    count = 0
    ret = dictionary.copy()
    new_values = dict([])
    
    for key in dictionary.keys() :
        value = dictionary[key]
        new_value = new_values.get(value, -1)
        if new_value == -1 :
            new_values[value] = count
            new_value = count
            count = count + 1
        ret[key] = new_value
        
    return ret


def __one_level(G, status, metric_type, param):
    """ This is the switch to control which metric is used to maximize the
partition.

    Parameters
    ----------
    G : a networkx graph
    status : a Status class instance that contains all info about the partition
    metric_type : 'linearity' or 'modularity' to indicate which metric to use
    param : (a, b, c) if using linearity
    
    Returns
    -------
    nothing : updates Status to represent node merges in place
    """
    if metric_type == 'linearity':
        return __one_level_linearity(G, status, param)
    if metric_type == 'modularity':
        return __one_level_modularity(G, status)
        
    raise Exception("Unknown Metric, not linearity or modularity")


def __one_level_modularity(G, status) :
    """Compute one level of communities
    """
    modif = True
    nb_pass_done = 0
    cur_mod = __modularity(status)
    new_mod = cur_mod
    
    while modif  and nb_pass_done != __PASS_MAX :
        cur_mod = new_mod
        modif = False
        nb_pass_done += 1
        
        for node in G.nodes() :
            com_node = status.node2com[node]
            degc_totw = status.gdegrees.get(node, 0.) / (status.total_weight*2.)
            neigh_communities = __neighcom(node, G, status)
            __remove(node, com_node,
                     neigh_communities.get(com_node, 0.), status)
            best_com = com_node
            best_increase = 0
            for com, dnc in neigh_communities.iteritems() :
                incr =  dnc  - status.degrees.get(com, 0.) * degc_totw
                if incr > best_increase :
                    best_increase = incr
                    best_com = com                    
            __insert(node, best_com,
                     neigh_communities.get(best_com, 0.), status)
            if best_com != com_node :
                modif = True                
        new_mod = __modularity(status)
        if new_mod - cur_mod < __MIN :
            break
            

def __one_level_linearity(G, status, (__A, __B, __C)) :
    """Compute one level of communities
    """
    modif = True
    
    c_sizes = [status.com_sizes[c] + sum(status.com_size_changes[c]) \
                for c in status.com_sizes]
    int_ideal = float( sum( [s * (s - 1) for s in c_sizes] ) )
    int_exists = 2 * sum(status.internals.values())
    
    I = (int_ideal == 0 and 1.) or int_exists / int_ideal
    
    orig_c = status.node2com.copy()
    
    count = 0
    while modif:
        modif = False  
                                       
        for node in G.nodes():
            c1 = status.node2com[node]
            node_size = status.com_sizes[orig_c[node]] # ??? bug if changes communities
            c1_old_size = status.com_sizes[c1] + sum(status.com_size_changes[c1])
            c1_new_size = c1_old_size - node_size
            c1_old_ideal = c1_old_size * (c1_old_size - 1)
            c1_new_ideal = c1_new_size * (c1_new_size - 1)
            
            if c1_new_size == 0:
                inc_S = 1
            else:
                inc_S = 0
            
            neighbor_c = __neighcom(node, G, status)
        
            # print "    Removing ", node, " from  ", c1
        
            __remove(node, c1, neighbor_c.get(c1, 0.) - status.loops.get(orig_c[node], 0), status)            
            best_c = c1
            best_inc = 0
            
            for c2, cc_weight in neighbor_c.iteritems():
                c2_old_size = status.com_sizes[c2] + sum(status.com_size_changes[c2])
                c2_old_ideal = c2_old_size * (c2_old_size - 1)
                
                if c1 == c2 or c2_old_size < 1:
                    inc = 0
                    # print 'Taking auto 0'
                else:
                    s = node_size + c2_old_size
                    new_int_exists = int_exists + 2 * cc_weight - 2 * neighbor_c.get(c1, 0) + 2 * status.loops.get(orig_c[node], 0)
                    new_int_ideal = float( int_ideal + 
                                           s * (s - 1) +
                                           c1_new_ideal -
                                           c1_old_ideal -
                                           c2_old_ideal )
                                        
                    inc_I = new_int_exists / new_int_ideal - I 
                    inc_E = (cc_weight - neighbor_c.get(c1, 0) + status.loops.get(orig_c[node], 0)) / \
                             float(status.total_weight)
                
                    inc = __A * inc_I + __B * inc_E + __C * inc_S 
                    """
                    print '**** inc is: ', inc, 'From I, E, S: ', \
                          inc_I, inc_E, inc_S, 'from: ', \
                          c1, c2, __A, __B, __C
                    """
                          
                if inc > best_inc:
                    best_inc = inc
                    best_c = c2
                    best_int_ideal = new_int_ideal
                    best_int_exists = new_int_exists
                    
            if best_c != c1: # need to update the ideal int edges
                int_ideal = best_int_ideal
                int_exists = best_int_exists
                I = (int_ideal == 0 and 1.) or int_exists / int_ideal
                    
                __insert(node, best_c, neighbor_c.get(best_c, 0.), status)
            else:
                __insert(node,
                         best_c,
                         neighbor_c.get(best_c, 0.) - status.loops.get(orig_c[node], 0),
                         status)
                    
            # print "    Adding ", node, " to ", best_c
            # print 'After node: ', node, 'status: ', status
            
            if best_c != c1:
                modif = True
                

def __neighcom(node, G, status) :
    """
    Compute the communities in the neighborood of node in the graph given
        with the decomposition node2com
                if neighbor != node :
    """
    weights = {}
    for neighbor, datas in G[node].iteritems() :
        weight = datas.get("weight", 1)
        neighborcom = status.node2com[neighbor]
        weights[neighborcom] = weights.get(neighborcom, 0) + weight
            
    return weights


def __remove(node, com, weight, status) :
    """ Remove node from community com and modify status"""
    status.degrees[com] = ( status.degrees.get(com, 0.)
                                    - status.gdegrees.get(node, 0.) )
    status.internals[com] = float( status.internals.get(com, 0.) - weight - status.loops.get(node, 0.))
    status.com_size_changes[com].append( -1 * status.com_sizes.get(node, 1) )
    status.node2com[node] = -1
    

def __insert(node, com, weight, status) :
    """ Insert node into community and modify status"""
    status.node2com[node] = com
    status.degrees[com] = ( status.degrees.get(com, 0.) +
                                status.gdegrees.get(node, 0.) )
    status.internals[com] = float( status.internals.get(com, 0.) +
                                  weight + status.loops.get(node, 0.) )
    status.com_size_changes[com].append(status.com_sizes.get(node, 1))
    
    
def __update_sizes(status):
    
    for com in status.com_sizes:
        status.com_sizes[com] += sum(status.com_size_changes[com])
        status.com_size_changes[com] = []

def __metric(status, metric_type, param):
    """ This is the switch to control which metric is used to maximize the
partition.

    Parameters
    ----------
    status : a Status class instance that contains all info about the partition
    metric_type : 'linearity' or 'modularity' to indicate which metric to use
    
    Returns
    -------
    m : the value of the partition under the given metric_type
    
    """
    if metric_type == 'linearity':
        return __linearity(status, param)
    if metric_type == 'modularity':
        return __modularity(status)
        
    raise Exception("Unknown Metric, not linearity or modularity")


def __linearity(status, (__A, __B, __C)):
    """
    Computes the linear metric of a partition of a graph, given status
    
    Notes
    -----
    Called by __metric only
    """
    ext_edges = float(status.total_weight)
    
    int_edges = 0.
    int_ideal = 0.    
    for community, size in status.com_sizes.iteritems():
        size += sum(status.com_size_changes[community])
        if size > 1:
            int_edges += 2 * status.internals.get(community, 0.)
            int_ideal += size * (size - 1)
        
    if int_ideal == 0:
        I = 1.
    else:
        I = int_edges / int_ideal
        
    S = len(filter(lambda c: status.com_sizes[c] + \
                             sum(status.com_size_changes[c]) > 0,
                   status.com_sizes.keys()))
    return __A * I - \
           __B * (ext_edges - int_edges / 2.0) / ext_edges - \
           __C * S
           
           
def visualize_subgraph(com, G):
    
    nodes = [n for n in com]

    for j in range(min(20, len(nodes))):
        n = nodes[j]
        edges = G.edges(n)
        print [((n,m) in edges and 1) or 0 for m in nodes[:j]]

    
def __modularity(status) :
    """
    Compute the modularity of the partition of the graph fastly using status.
    
    Notes
    -----
    Called by __metric only
    """
    links = float(status.total_weight)
    result = 0.
    for community in set(status.node2com.values()) :
        in_degree = status.internals.get(community, 0.)
        degree = status.degrees.get(community, 0.)
        if links > 0 :
            result = result + in_degree / links - ((degree / (2.*links))**2)
    return result

    
