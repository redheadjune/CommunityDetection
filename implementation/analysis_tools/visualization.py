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
        
    
    
    
