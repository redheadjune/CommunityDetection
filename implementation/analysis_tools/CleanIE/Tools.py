# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

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
        
    
    return hierarchy
    

def part_to_sets(partition):
    """Turns the partition dictionary into a list of lists
    """
    sets = {}
    
    for n in partition:
        if type(partition[n]) == list:
            for c in partition[n]:
                so_far = sets.get(c, [])
                so_far.append(n)
                sets[c] = so_far
        else:
            c = partition[n]
            so_far = sets.get(c, [])
            so_far.append(n)
            sets[c] = so_far
        
    return sets.values()
    
    
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
    
def c_density(sub_graphs):
    densities = []
    for g in sub_graphs:
        if g.number_of_nodes() > 1:
            densities.append(2 * g.number_of_edges()/
                             float(g.number_of_nodes() *
                                   (g.number_of_nodes() - 1)))
        else:
            densities.append(1)
    return densities
    
    
def vis_local_com(communities, n, graph, sub_graph):
    """Visualize the local community structure.
    
    Parameters
    ----------
    communities : a list of lists, where internal lists are the communities
    n : the central node around which the communities are centered
    graph : the local subgraph around n to plot
    
    """
    if type(communities) == list:
        communities = sets_to_part(communities)
        
    community_names = []
    for m in graph:
        community_names.extend(communities[m])
        
    # let's see how popular these communities are.
    pop_com_names = [(c, community_names.count(c))
                        for c in set(community_names)]
                        
    community_names = filter(lambda p: p[1] > 1, pop_com_names)
    community_names = sorted(community_names, key=lambda p: p[1], reverse=True)
    community_names = [c for c,p in community_names]
        
    c_colors = {}
    i = 0.
    for c in community_names:
        c_colors[c] = i
        i += 1.
        
    node_colors = []
    for m in graph:
        if len(communities[m]) > 1: # find the most popular
            found = False
            for c in community_names:
                if c in communities[m]:
                    node_colors.append(c_colors[c])
                    found = True
                    break
            if not found:
                node_colors.append(-2)
        elif communities[m][0] not in community_names:
            node_colors.append(-2)
        else:
            node_colors.append(c_colors[communities[m][0]])
    
    pos = nx.spring_layout(graph, pos={n:np.array([0., 0.])})
    
    fig = plt.figure()
    ax = fig.add_subplot(121)
    nx.draw(graph, pos, node_color=node_colors, alpha=0.4)
    ax = fig.add_subplot(122)
    nx.draw(sub_graph, alpha=0.4)
    
    plt.show()
    
    return node_colors