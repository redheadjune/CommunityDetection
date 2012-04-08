import CommunityDetection as CD
import networkx as nx
import matplotlib.pyplot as plt
import random

"""This module is to analyze previous metrics
"""

def draw_metric_change_vectors(metric, degree, fig=None, c=None):
    """ Draws the vector of possible changes in the metric by adding nodes
    
    """
    
    # create a subset of the football graph to work with
    graph = CD.football_graph()
    nodes = graph.nodes()
    if c == None:
        c = [nodes[random.randint(0, len(nodes) - 1)] for i in range(20)]
    else:
        c = c[:]
        
    ext_nodes = list(set(nodes) - set(c))
    
    if fig == None:
        fig = plt.figure(); ax = fig.add_subplot(111);
        
    change_graph = nx.DiGraph()
    change_graph.add_node("center")
    pos = {"center":(CD.m_internal_density(graph, c), CD.m_external_density(graph, c))}
    value = {"center":metric(graph, c)}
    
    for i in range(degree+1):
        n = ext_nodes[i]
        c.append(n)
        pos[n] = (CD.m_internal_density(graph, c), CD.m_external_density(graph, c))
        value[n] = metric(graph, c)
        change_graph.add_edge("center", n)
        c = c[:-1]
        
    inc = [20 + 15*i for i in range(degree+2)]
    rank = [(n, value[n]) for n in value.keys()]
    rank.sort(key=lambda v1: v1[1])
    order = {}
    for i in range(len(rank)):
        order[rank[i][0]] = i
    
    sizes = [inc[order[n]] for n in change_graph]
    nx.draw(change_graph,
            pos,
            node_color='b',
            node_size=sizes,
            with_labels=False)
        