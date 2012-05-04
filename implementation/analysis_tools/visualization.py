# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable

def vis_g_np_graph(graph, show_nodes, fig=None, color=None):
    """ Presumes the setup of 4 subgraphs, joined with 
    """
    row_size = 20
    
    def get_pos(n):
        offset = (n / row_size**2) * row_size**2
        n = n - offset
        y = n / row_size
        x = n - row_size * y
        return (x, y, offset / row_size**2)
    
    def get_color(d):
        if d > 50:
            return 'g'
        if d > 9:
            return 'y'
        return 'r'
    
    pos = {}
    for n in graph:
        (x, y, offset) = get_pos(n)
        if offset in [2, 3]:
            y += 20
        
        if offset in [1, 3]:
            x += 20
            
        pos[n] = (x, y)
        
    if color == None:
        color = [get_color(graph.degree(n)) for n in graph.nodes()]
        
    if fig == None:
        fig = plt.figure(); ax = fig.add_subplot(111);
        
    nx.draw(graph,
            pos,
            node_color=color,
            node_size=20,
            with_labels=False,
            edgelist=[],
            nodelist=show_nodes)
        

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
            cs,
            cand,
            desired=[],
            title="Community under Properties $\chi_p$ and $\chi_e$."):
    """ Plots the layout of the nodes in terms of E(n, Cs) and P(n, Cs)
    
    Parameters
    ---------
    graph : a networkx graph
    cs : a community object
    cand : a candidate object
    bounds : the limits of the e and p values
    desired : what we wish would have been recovered
    
    Method
    ------
    """
    
    def get_values(source, keys, order):
        return [[source[n][key] for n in order] for key in keys]
    
    fig = plt.figure(figsize=(5.5, 5.5))
    
    ax = fig.add_subplot(111)
    
    ext_n = cand.get_all_nodes()
    int_n = cs.nodes
    bounds = cs.bounds
    
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
    p1, = ax.plot(int_nodes_p, int_nodes_e, 'r.', markersize=10)
    p2, = ax.plot(ext_nodes_p, ext_nodes_e, 'k.', markersize=10)
    if desired != []:
        p3, = ax.plot(have_nodes_p, have_nodes_e, 'm.', markersize=10)
        p4, = ax.plot(want_nodes_p, want_nodes_e, 'g.', markersize=10)
        
        ax.legend([p1, p2, p3, p4],
                  ["$C_s - C$", "$V - C$", "$C_s \cap C$", "$C - C_s$"],
                  loc=9)
    else:
        ax.legend([p1, p2], ["$C$", "$V - C$"], loc=1)
    
    # format
    ax.set_xlim(0, 1.01)
    ax.set_title(title, fontsize=24)
    ax.set_xlabel("$\chi_p(n, C)$  percentage of edges in C", fontsize=20)
    ax.set_ylabel("$\chi_e(n, C)$  number of edges in C", fontsize=20)

    plt.show()
    
    # include bounds
    ycap = ax.get_ylim()
    ax.plot([bounds['min_p'], bounds['min_p']], ycap, '--', color='purple', alpha=.8, linewidth=3)
    ax.plot(ax.get_xlim(), [bounds['min_e'], bounds['min_e']], '--', color='purple', alpha=.8, linewidth=3)
    
    if desired != []:    
        divider = make_axes_locatable(ax)
        
        axCMDe = divider.new_horizontal("20%", pad=0.6, sharey=ax)
        axCMDe.tick_params(labelleft="off")
        fig.add_axes(axCMDe)
        
        axCMDp = divider.new_vertical("20%", pad=0.6, sharex=ax)
        axCMDp.tick_params(labelbottom="off")
        fig.add_axes(axCMDp)
        
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
        axCMDp.set_title("$X_p(n, C) \leq p$.", size='large')
        axCMDp.set_yticks([0, 1])
    """
    for t1 in axCMDp.get_xticklabels():
        t1.set_visible(False)
    """    
    plt.draw()
    plt.show()
    
    
def vis_local_com(communities, n, graph, sub_graph):
    """Visualize the local community structure.
    
    Parameters
    ----------
    communities : a list of lists, where internal lists are the communities
    n : the central node around which the communities are centered
    graph : the local subgraph around n to plot
    
    """
    if type(communities) == list:
        communities = CD.sets_to_part(communities)
        
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


def vis_distribution(graph, c):
    """ Visualizes the distributions of connectivity
    Parameters
    ----------
    graph : the networkx graph
    c : the set of nodes within the community
    
    Returns
    -------
    creates and stores a plot of the connectivity into the community
    """
    in_node_degree = {}
    out_node_degree = {}
    
    for n in c:
        in_node_degree[n] = 0
        for m in graph.neighbors(n):
            if m in c:
                in_node_degree[n] += 1
            else:
                out_node_degree[m] = out_node_degree.get(m, 0) + 1
                
    for char in ['E', 'P']:
        if char == 'P':
            for n in in_node_degree:
                in_node_degree[n] = in_node_degree[n] / float(graph.degree()[n])
            for m in out_node_degree:
                out_node_degree[m] = out_node_degree[m] / \
                    float(graph.degree()[m])
                
            bins = range(51)
            bins = [b / 50. for b in bins]
            
        else:
            max_degree = max(max(in_node_degree.values()),
                             max(out_node_degree.values()))
            bins = range(max_degree+1)
            bins = [b + 0.5 for b in bins]
            
        fig = plt.figure()
        ax = fig.add_subplot(111)        
        bins_in = ax.hist([in_node_degree.values(), out_node_degree.values()],
                          bins=bins,
                          color=['r', 'k'],
                          label=['Internal nodes', 'External nodes'])
        ax.legend()
        ax.set_ylabel("Number of Nodes", fontsize=24)
        ax.set_xlabel(char + "edges into $C$", fontsize=24)
        ax.set_title("Distribution of edges into $C$.", fontsize=24)
        plt.show()
        plt.savefig(char + 'distribution.eps')
        plt.savefig(char + 'distribution.pdf')