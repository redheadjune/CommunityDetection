# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable

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
    graph : a networkx graph
    ext_n : the dictionary of information about external nodes
    int_n : the dictionary of information about internal nodes
    bounds : the limits of the e and p values
    desired : what we wish would have been recovered
    
    Method
    ------
    """
    
    def get_values(source, keys, order):
        return [[source[n][key] for n in order] for key in keys]
    
    fig = plt.figure(figsize=(5.5, 5.5))
    
    ax = fig.add_subplot(111)
    
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
    p1, = ax.plot(int_nodes_p, int_nodes_e, 'r.')
    p2, = ax.plot(ext_nodes_p, ext_nodes_e, 'k.')
    p3, = ax.plot(have_nodes_p, have_nodes_e, 'm.')
    p4, = ax.plot(want_nodes_p, want_nodes_e, 'g.')
    
    ax.legend([p1, p2, p3, p4],
               ["$C_s - C$", "$V - C$", "$C_s \cap C$", "$C - C_s$"])
    
    # format
    ax.set_xlim(0, 1)
    ax.set_title(title)
    ax.set_xlabel("percentage of edges included in C, for each node,"+ \
                  " $\\frac{|E(n, C_s)|}{degree(n)}$")
    ax.set_ylabel("number of edges included in C, for each node, $|E(n, C_s)|$")

    plt.show()
    
    # include bounds
    ycap = ax.get_ylim()
    ax.plot([bounds['min_p'], bounds['min_p']], ycap, '--', color='purple', alpha=.8, linewidth=3)
    ax.plot(ax.get_xlim(), [bounds['min_e'], bounds['min_e']], '--', color='purple', alpha=.8, linewidth=3)
    if bounds['slope'] + bounds['offset'] > ycap[1]:
        xpoints = [0, (ycap[1] - bounds['offset'])/float(bounds['slope'])]
        ypoints = [bounds['offset'], ycap[1]]
    else:
        xpoints = [0, 1]
        ypoints = [bounds['offset'], bounds['slope'] + bounds['offset']]
        
    ax.plot(xpoints, ypoints, '--', color='purple', alpha=.8, linewidth=3)
    
    divider = make_axes_locatable(ax)
    
    axCMDe = divider.new_horizontal("20%", pad=0.6, sharey=ax)
    axCMDe.tick_params(labelleft="off")
    fig.add_axes(axCMDe)
    
    axCMDp = divider.new_vertical("20%", pad=0.6, sharex=ax)
    axCMDp.tick_params(labelbottom="off")
    fig.add_axes(axCMDp)
    
    #axCMDe = divider.append_axes("right", 1.2, pad=0.6, sharex=ax)
    
    # make some labels invisible
    #plt.setp(axCMDp.get_xticklabels(), # + axCMDe.get_yticklabels(),
    #         visible=False)    
    
    # include cumulative distributions
    
    e_values = int_nodes_e
    e_values.extend(ext_nodes_e)
    e_values.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    
    x = range(max(max(int_nodes_e), max(ext_nodes_e)))
    y = [sum([n<=xx for n in e_values])/float(len(e_values)) for xx in x]

    x.reverse()
    y.reverse()
    axCMDe.plot(y, x)
    axCMDe.set_xticks([0, 1])
    #axCMDe.set_xtick_labels(['0', '1'])
    
    p_values = int_nodes_p
    p_values.extend(ext_nodes_p)
    p_values.extend([0. for i in range(len(w_nodes) - len(want_nodes))])
    
    x = range(1001)
    x = [xx/1000. for xx in x]
    y = [sum([n<xx for n in p_values])/float(len(p_values)) for xx in x]
    
    axCMDp.plot(x, y)
    axCMDp.set_title("Cumulative Distribution for nodes by %.")
    axCMDp.set_yticks([0, 1])
    """
    for t1 in axCMDp.get_xticklabels():
        t1.set_visible(False)
    """    
    plt.draw()
    plt.show()
    
    
