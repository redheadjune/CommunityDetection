# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx
import matplotlib.pyplot as plt


def vis_ball(graph, core, radius):
    """ Plots the subgraph corresponding to the ball around core of the given
        radius.
        
    Parameters
    ----------
    graph : a networkx graph
    core : a subset of nodes from graph
    radius : how far out to consider from core
    """
    
    ball = CD.get_ball(graph, core, radius)
    
    subgraph = graph.subgraph(ball)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    pos = nx.spring_layout(subgraph)
    nx.draw(subgraph, pos)
        
        
def vis_e_p(graph,
            ext_n,
            int_n,
            bounds={},
            desired=[],
            title="Community under E and P."):
    """ Plots the layout of the nodes in terms of E(n, Cs) and P(n, Cs)
    
    Parameters
    ---------
    
    Method
    ------
    """
    
    def get_values(source, keys, order):
        return [[source[n][key] for n in order] for key in keys]
    
    fig = plt.figure()
    ax = fig.add_subplot(222)
    
    int_nodes = int_n.keys()
    (int_nodes_e, int_nodes_p) = get_values(int_n, ['e', 'p'], int_nodes)
    
    ext_nodes = ext_n.keys()
    (ext_nodes_e, ext_nodes_p) = get_values(ext_n, ['e', 'p'], ext_nodes)
    
    have_nodes = list(set(desired).intersection(int_nodes))
    (have_nodes_e, have_nodes_p) = get_values(int_n, ['e', 'p'], have_nodes)
    
    w_nodes = list(set(desired) - set(have_nodes))
    want_nodes = filter(lambda n: n in ext_n, w_nodes)
    (want_nodes_e, want_nodes_p) = get_values(ext_n, ['e', 'p'], want_nodes)
    want_nodes_e.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    want_nodes_p.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    
    # plot actual points
    p1, = plt.plot(int_nodes_p, int_nodes_e, 'r.')
    p2, = plt.plot(ext_nodes_p, ext_nodes_e, 'b.')
    p3, = plt.plot(have_nodes_p, have_nodes_e, 'g.')
    p4, = plt.plot(want_nodes_p, want_nodes_e, '.', color='purple')
    
    plt.legend([p1, p2, p3, p4],
               ["$C_s - C$", "$V - C$", "$C_s \cap C$", "$C - C_s$"])
    
    # format
    ax.set_xlim(0, 1)
    ax.set_title(title)
    ax.set_xlabel("percentage of edges included in C, for each node,"+ \
                  " $\\frac{|E(n, C_s)|}{degree(n)}$")
    ax.set_ylabel("number of edges included in C, for each node, $|E(n, C_s)|$")
    
    # include bounds
    
    # include cumulative distributions
    ax = fig.add_subplot(221)
    
    e_values = int_nodes_e
    e_values.extend(ext_nodes_e)
    e_values.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    
    x = range(max(max(int_nodes_e), max(ext_nodes_e)))
    y = [sum([n<=xx for n in e_values])/float(len(e_values)) for xx in x]
    plt.plot(x, y)
    
    ax = fig.add_subplot(224)
    
    p_values = int_nodes_p
    p_values.extend(ext_nodes_p)
    p_values.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    
    x = range(1001)
    x = [xx/1000. for xx in x]
    y = [sum([n<xx for n in p_values])/float(len(p_values)) for xx in x]
    plt.plot(x, y)
    
    plt.show()
    
    
