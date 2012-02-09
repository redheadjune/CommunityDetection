# -*- coding: utf-8 -*-

import networkx as nx

def part_to_subgraphs(graph, partition):
    """ Transforms a partition of the graph into a set of subgraphs, each
        corresponding to a partition.
    """
    return sets_to_subgraphs(graph, part_to_sets(partition))


def part_to_sets(partition):
    """ Transforms a partition into a list of communities
    """
    communities = {}
    
    for n in partition:
        cname = partition[n]
        toadd = communities.get(cname, [])
        toadd.append(n)
        communities[cname] = toadd
        
    return communities.values()
    
    
def sets_to_subgraphs(graph, sets):
    """ Creates a subgraph disconnected from graph for each set
    """
    return [graph.subgraph(s) for s in sets]
    
    