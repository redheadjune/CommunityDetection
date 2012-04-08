# -*- coding: utf-8 -*-

import networkx as nx

def part_to_subgraphs(graph, partition):
    """ Transforms a partition of the graph into a set of subgraphs, each
        corresponding to a partition.
    """
    return sets_to_subgraphs(graph, part_to_sets(partition))


def part_to_sets(partition):
    """ Transforms a partition into a list of communities, each community is a
        list
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
    
    

def dendo_to_hierarchy(dendo):
    """Takes a dendogram and returns what the communities are at each level
    """
    prev = {}
    for i in dendo[0]:
        c = prev.get(dendo[0][i], set())
        c.update([i])
        prev[dendo[0][i]] = c
        
    next = {}
    hierarchy = [prev.copy()]
    
    for layer in dendo[1:]:
        for i in layer:
            c = next.get(layer[i], set())
            c.update(prev[i])
            next[layer[i]] = c
                        
        hierarchy.append(next.copy())
        prev = next
        next = {}
        
    return [[list(c) for c in sets.values()] for sets in hierarchy]


def sets_to_part(sets):
    """Turns the list of lists into a dictionary
    """
    part = {}
    c_name = 0
    for c in sets:
        for n in c:
            belongs = part.get(n, [])
            belongs.append(c_name)
            part[n] = belongs
        c_name += 1
        
    return part
    