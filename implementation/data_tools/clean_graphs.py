# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx

def clean_fragments(graph, threshold):
    """Removes any disconnected sections of the graph of size smaller than
    threshold.
    
    Parameters
    ----------
    graph : a networkx graph
    threshold : the size at which a disconnected subgraph is kept
    
    Method
    ------
    Uses the networkx function for finding the connected components
    
    Returns
    -------
    Nothing, does in place pruning of graph
    """

    components = nx.connected_components(graph)
    
    to_remove = []
    
    for c in components:
        if len(c) < threshold:
            to_remove.extend(c)
            
    graph.remove_nodes_from(to_remove)


def clean_coauthor_network(graph, threshold):
    """ Given a collaboration network, removes low degree nodes. And adds the
    bridges those low degree nodes created between higher degree nodes.
    
    Parameters
    ----------
    graph : a networkx graph
    threshold : any node of degree less than threshold will be removed

    Method
    ------
    Uses the bridges.  A node is a bridge if it connects two node of degree
    threshold or higher that are not otherwise connected.  Removes the node and
    adds an edge between the higher degree nodes to maintain the graph
    structure.
    """
    
    toremove = filter(lambda n: graph.degree(n) < threshold, graph.nodes_iter())
    
    bridges = CD.find_bridges(graph, threshold)
    
    print "Cleaned graph by removing ", len(toremove), " nodes."
    print "Cleaned graph by adding ", len(bridges), " bridges."
    
    graph.remove_nodes_from(toremove)
    graph.add_edges_from(bridges)