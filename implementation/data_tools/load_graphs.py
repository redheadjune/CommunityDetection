# -*- coding: utf-8 -*-

from constants import *

import networkx as nx
    
def football_graph():
    """Creates the graph for which college football teams played each other in a
            set year.

    Requires
    --------
    SNAP formulated data file: www-personal.umich.edu/~mejn/netdata/football.zip

    Returns
    -------
    G : a NetworkX graph, where each node is a team and edges indicate games
        played
    """
    return load_graph(FOOTBALL)
    
    
def karate_club_graph():
    """Creates the graph for which members of a karate club had lunch together.

    Requires
    --------
    Formulated data file: www-personal.umich.edu/~mejn/netdata/karate.zip
    Data acquired by W. W. Zachary, An information flow model for conflict and
    fission in small groups, Joirnal of Anthropological REsearch 33, 452-473
    (1977)

    Returns
    -------
    G : a NetworkX graph, where each node is a club member and edges indicates
        a social interaction, primarily lunch
    """
    return load_graph(KARATE)
    
    
def physics_citations():
    """Creates the graph papers citing other papers.

    Requires
    --------
    SNAP formulated data file: www.snap.stanford.edu/data/index.html

    Returns
    -------
    G : a NetworkX graph, where each node is a paper and edges indicate
        a citation within the paper to another paper
    """
    return load_graph(PHYSICS_CITATIONS)


def load_graph(path):
    """Given the standard fileCreates a networkx graph for a given data set
    Parameters
    ----------
    """
    gfile = open(path, 'rb')
    
    nodes = set()
    edges = []
    
    for line in gfile:
        if line != '\\n' and line[0] != '#':
            (n, end) = line.split(' ')
            m = end[:-1]
            n = int(n)
            m = int(m)
            nodes.update([n, m])
            edges.append((n, m, {'weight': 1.}))

    gfile.close()
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph