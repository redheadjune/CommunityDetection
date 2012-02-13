# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx

def clean_fragments(graph, threshold):

    components = nx.connected_components(graph)
    
    to_remove = []
    
    for c in components:
        if len(c) < threshold:
            to_remove.extend(c)
            
    graph.remove_nodes_from(to_remove)


def clean_coauthor_network(graph, threshold):
    """ Given a collaboration network, removes low degree nodes. And adds the
    bridges those low degree nodes created between higher degree nodes.

    Method
    ------
    Uses the bridges
    """
    
    toremove = filter(lambda n: graph.degree(n) < threshold, graph.nodes_iter())
    
    bridges = CD.find_bridges(graph, threshold)
    
    print "Cleaned graph by removing ", len(toremove), " nodes."
    print "Cleaned graph by adding ", len(bridges), " bridges."
    
    graph.remove_nodes_from(toremove)
    graph.add_edges_from(bridges)