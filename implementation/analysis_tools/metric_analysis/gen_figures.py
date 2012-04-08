# -*- coding: utf-8 -*-

import CommunityDetection as CD
import matplotlib.pyplot as plt
import networkx as nx

import matplotlib.patches as patch

"""
This is for generating figures for the paper
"""

def gen_4_plots_sets(metric):
    """ Plots out how modularity performs in the (I, E, S) space
    """
    graphs = [CD.karate_club_graph(),
              CD.football_graph(),
              CD.coauthor_relativity(),
              CD.coauthor_astro()]
    names = ["Zachary's Karate Club",
             'College Football League',
             'Relativity Co-author Network',
             'Astrophysics Co-author Network'] 
    parameters = [[1., 1., 1./float(graphs[0].number_of_edges())],
                  [1., 1., 1./float(graphs[0].number_of_edges())],
                  [1., 1., 1./float(graphs[0].number_of_edges())],
                  [1., 1., 1./float(graphs[0].number_of_edges())]]
    for i in range(4):
        if metric == "modularity":
            dendo = CD.generate_dendogram(graphs[i])
        elif metric == "linearity":
            dendo = CD.create_dendogram(graphs[i],
                                        parameters[i][0],
                                        parameters[i][1],
                                        parameters[i][2])
        
        d_sets = CD.dendo_to_hierarchy(dendo)
        (I, E, S) = CD.path_I_E_S(graphs[i], d_sets)
        gen_path_set(I, E, S, names[i], ylim=[0, .5])
        print "Finished with ", names[i]


def gen_4_plots_single(metric):
    """ Generates the 4 plots of the paper according to the metric
    Parameters
    ----------
    metric : name of the metric to use
    """
    graphs = [CD.karate_club_graph(),
              CD.football_graph(),
              CD.coauthor_relativity(),
              CD.coauthor_astro()]
    seeds = [[32, 34],
             [1, 36],
             [773, 4164],
             [3, 289]]
    names = ["Zachary's Karate Club",
             'College Football League',
             'Relativity Co-author Network',
             'Astrophysics Co-author Network']  
    ylim = [[0, .4],
            [0, .1],
            [0, .02],
            [0, .01]]
    k = [7/34., 7/115., 7/270., 7/1550.]
    arrow_width = [0.01, 0.0025, 0.0007, 0.0005]
    #n_ls = [40, 160, 320, 640] # use for external
    #n_ls = [40, 40, 30, 30] # use for volume
    n_ls = [20, 20, 20, 20] # use for conductance
    for i in range(4):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        if metric == "volume":
            CD.draw_ls("volume", n_ls[i], 7, graphs[i].number_of_nodes(), ylim[i][1])
            gen_path_single(graphs[i],
                            seeds[i],
                            names[i],
                            ax,
                            CD.m_volume,
                            CD.compare_maximize,
                            ylim=ylim[i],
                            width = arrow_width[i])
        elif metric == "internal":
            CD.draw_ls("internal", n_ls[i], -1, -1, 1)            
            gen_path_single(graphs[i],
                            seeds[i],
                            names[i],
                            ax,
                            CD.m_prev_internal,
                            CD.compare_minimize,
                            ylim=ylim[i],
                            width = arrow_width[i])   
        elif metric == "cee":
            CD.draw_ls("cut ratio", n_ls[i], -1, -1, 1)
            gen_path_single(graphs[i],
                            seeds[i],
                            names[i],
                            ax,
                            CD.m_cut_ratio,
                            CD.compare_minimize,
                            ylim=ylim[i],
                            width = arrow_width[i])
        elif metric == "conductance":
            CD.draw_ls("conductance", n_ls[i], 7, graphs[i].number_of_nodes(), 1)
            gen_path_single(graphs[i],
                            seeds[i],
                            names[i],
                            ax,
                            CD.m_conductance,
                            CD.compare_minimize,
                            ylim=ylim[i],
                            width = arrow_width[i])
    

def gen_path_set(I_path, E_path, S_path, name, ylim=[0, 1],
                 legend=False, width=0.01):
    """ Given an I E S path plots
    Parameters
    ----------
    I_path : a list of I(S) values
    E_path : a list of E(S) values
    S_path : a list of |S| values
    name : the title and saving file name
    ylim : the maximum value of E(S)
    legend : whether or not to show legend (not likely)
    width : the width of the arrow head
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    CD.plot_path(I_path[:], E_path[:], ax, 'r', name, width)    
    
    ax.set_title(name, fontsize=24)    
    plt.xticks([0, .3, .7, 1], ['0', '0.3', '0.7', '1'])
    plt.yticks(ylim, [str(y) for y in ylim])
    ax.set_xlim(-.01, 1.01)
    ax.set_ylim(ylim[0] - width/2., ylim[1] + width/2.)
    ax.set_xlabel(r'$I(S)$', fontsize=24)
    ax.set_ylabel(r'$E(S)$', fontsize=24)
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc=2)
    
    plt.show() 
    
    # save the figure
    plt.savefig(name + ".eps")
    plt.savefig(name + ".pdf")  
    
    
def gen_path_single(graph, seed, name, ax, metric, comp, ylim=[0, .3],
                    legend=False, width=0.01): 
    """ Generates and plots the I E path and manages the space
    Parameters
    ----------
    graph : a networkx graph
    seed : a list of nodes to start from
    name : the title of the graph
    ax : the subplot to put everything
    metric : the single community metric to optimize
    comp : the comparison function either CD.compare_min or max
    legend : whether or not to show the legend
    width : the width of the arrow head
    """
    # plot metric optimized path
    (I_path, E_path, order) = CD.path_I_E(graph, seed[:], metric, comp)
    CD.plot_path(I_path[:], E_path[:], ax, 'r', name, width)
    
    # plot corner cases
    ax.plot(1, 0, 'kD', label='Ideal', markersize=10)
    (graph_I, graph_E) = CD.I_E(graph, graph.nodes())
    ax.plot(graph_I, 0, 'mD', label='Entire Graph', markersize=10)   
    
    # set labels etc
    ax.set_title(name, fontsize=24)    
    plt.xticks([0, .3, .7, 1], ['0', '0.3', '0.7', '1'])
    plt.yticks(ylim, [str(y) for y in ylim])
    ax.set_xlim(-.01, 1.01)
    ax.set_ylim(ylim[0] - width/2., ylim[1] + width/2.)
    ax.set_xlabel(r'$I(C)$', fontsize=24)
    ax.set_ylabel(r'$E(C)$', fontsize=24)
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc=2)
    
    plt.show() 
    
    # save the figure
    plt.savefig(name + ".eps")
    plt.savefig(name + ".pdf")
    
def sets_corner_cases():
    """ Plots the three corner cases of optimizing 2 but not 3 parameters of
    I, E, and |S|
    """
    
    graph = nx.Graph()
    graph.add_nodes_from(range(4))
    graph.add_edges_from([(0, 1), (1, 2), (2, 3)])
    
    fig = plt.figure(figsize=(10, 3))
    pos = {0:(0, 0), 1:(1, 0), 2:(2, 0), 3:(3, 0)}
    
    # optimizes I and E, but not |S|, each edge is a community
    ax = fig.add_subplot(131)    
    nx.draw(graph,
            pos,
            node_color='r',
            node_size=30,
            with_labels=False)
    for i in range(3):
        community = patch.Circle((.5 + i, 0), .7, facecolor='b', alpha=0.3)
        ax.add_artist(community)   
        
    ax.set_xlim(-1, 4)
    ax.set_ylim(-5, 5)    
    
    # optimizes E and |S|, but not I, the entire graph is a community
    ax = fig.add_subplot(132)    
    nx.draw(graph,
            pos,
            node_color='r',
            node_size=30,
            with_labels=False)
    community = patch.Circle((1.5, 0), 1.7, facecolor='b', alpha=0.3)
    ax.add_artist(community)   
    ax.set_xlim(-1, 4)
    ax.set_ylim(-5, 5)
    
    # optimizes I and |S|, but not E, each clique is a community.
    ax = fig.add_subplot(133)    
    nx.draw(graph,
            pos,
            node_color='r',
            node_size=30,
            with_labels=False)
    for i in range(2):
        community = patch.Circle((.5 + 2*i, 0), .7, facecolor='b', alpha=0.3)
        ax.add_artist(community)   
        
    ax.set_xlim(-1, 4)
    ax.set_ylim(-5, 5) 
    
    
    
    
    