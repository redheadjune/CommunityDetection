# -*- coding: utf-8 -*-

from constants import *

import CommunityDetection as CD
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
        
    Communities
    -----------
    Communities correspond to football leagues, which are cliques.  The
structure has a dense set of 'noise' of inter-league teams.
    """
    return load_graph(FOOTBALL, format_1)
    
    
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
        
    Communities
    ----------
    Up to interpretation here what the communities are.  While there is a well
known break of the group - that doesn't correspond with our necessary notion of
communities.  Any method should either return sub-communities or the entire
thing.
    """
    return load_graph(KARATE, format_1)
    
    
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
    pgraph = load_graph(PHYSICS_CITATIONS, format_1)
    CD.clean_fragments(pgraph, 15)
    return pgraph
    
    
def coauthor_astro():
    """ Creates Clean graph of astrophysics ArchiveX collaborations.
    
    This is the hardest clean - well connected.
    
    Cleaned to produce a graph with 15507 nodes and 193396 edges.
    During the cleaning process removed 3268 nodes with average degree 1.43.
    """
    agraph = load_graph(ASTRO_COAUTHOR, format_2)
    CD.clean_fragments(agraph, 20)
    CD.clean_coauthor_network(agraph, 3)
    prefix = gen_prefix("Astrophysics", 15507, 193396)
    CD.write_edges(agraph,
                   DATA_PATH_2+"CollaborationNetworks/cleaned-astro.txt",
                   prefix)
    return agraph
    
    
def coauthor_cond():
    """ Creates Clean graph of condensed matter ArchiveX collaborations
    
    Cleaned to produce a graph with 16966 nodes and 84747 edges.
    During the cleaning process removed 3528 nodes with average degree 1.41.
    """
    cgraph = load_graph(COND_COAUTHOR, format_2)
    CD.clean_fragments(cgraph, 30)
    CD.clean_coauthor_network(cgraph, 3)
    prefix = gen_prefix("Condensed Matter", 16966, 84747)
    CD.write_edges(cgraph,
                   DATA_PATH_2+"CollaborationNetworks/cleaned-cond.txt",
                   prefix)
    return cgraph
    
    
def coauthor_energy():
    """ Creates clean graph of high energy physics collaborations in ArchiveX
    
    Cleaned to produce a graph with 8480 nodes and 113600 edges.
    During the cleaning process removed 3528 nodes with average degree 1.38.
    """
    egraph = load_graph(ENERGY_COAUTHOR, format_2)
    CD.clean_fragments(egraph, 20)
    CD.clean_coauthor_network(egraph, 3) # keep nodes of degree 3 or higher
    prefix = gen_prefix("High Energy Physics", 8480, 113600)
    CD.write_edges(egraph,
                   DATA_PATH_2+"CollaborationNetworks/cleaned-energy.txt",
                   prefix)
    return egraph

    
def coauthor_energy_theory():
    """ Creates clean graph pf high energy theory physics collaborations in
    ArchiveX.

    Note
    ----
    There is a discrepancy in the number of edges that actually exist and the
    number claimed on the SNAP website.  There are multiple copies and self
    loops in the graph.  We clean those out to get 25998 edges.
    
    With additional cleaning we take the graph from 9877 nodes to 5446 nodes
    and 20337 edges.  So the average degree of the nodes removed is 1.35
    """
    egraph = load_graph(ENERGY_THEORY_COAUTHOR, format_2)
    CD.clean_fragments(egraph, 30)
    CD.clean_coauthor_network(egraph, 3) # keep nodes of degree 3 or higher
    prefix = gen_prefix("High Energy Theory Physics", 5446, 20337)
    CD.write_edges(egraph,
                   DATA_PATH_2+"CollaborationNetworks/cleaned-energy-theory.txt",
                   prefix)
    return egraph

    
def coauthor_relativity():
    """ General Relativity coauthor graph.
    
    Note
    ----
    Same discrepancy from self-loops and duplicate edges.
    
    The graph begins with 5242 nodes and 14484 edges.
    The graph returns is cleaned of 2548 nodes (nodes that are disconnected
    from the main component, or not that well connected to the big component)
    
    The resultant graph has 2694 nodes and 11400 edges.  The average degree of
    nodes removed is ~1.21
    """
    rgraph = load_graph(RELATIVITY_COAUTHOR, format_2)
    CD.clean_fragments(rgraph, 20)
    CD.clean_coauthor_network(rgraph, 3) # keep nodes of degree 3 or higher
    prefix = gen_prefix("General Relativity", 2694, 11400)
    CD.write_edges(rgraph,
                   DATA_PATH_2+"CollaborationNetworks/cleaned-relativity.txt",
                   prefix)
    return rgraph


def amazon():
    """ Amazon co-purchasing graph
    
    Note
    ----
    The Amazon purchasing network is an enormous network with 410236 nodes and
    2439437 edges.  It is a single connected component.  The graph needs no
    cleaning.
    """
    agraph = load_graph(AMAZON, format_2)
    return agraph


def load_graph(path, form):
    """Given the standard fileCreates a networkx graph for a given data set
    Parameters
    ----------
    """
    try:
        gfile = open(DATA_PATH_1 + path, 'rb')
    except:
        gfile = open(DATA_PATH_2 + path, 'rb')
    
    nodes = set()
    edges = []
    
    for line in gfile:
        if line != '\\n' and line[0] != '#':
            n, m = form(line)
            nodes.update([n, m])
            edges.append((n, m, {'weight': 1.}))

    gfile.close()
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes, size=1.)
    graph.add_edges_from(edges)
    
    # remove self edges
    for n in graph.nodes():
        if graph.has_edge(n, n):
            graph.remove_edge(n, n)
            
    return graph
    
    
def format_1(line):
    """ For reading in edges in the form of "n m\n"
    """
    (n, end) = line.split(' ')
    m = end[:-1]
    
    return int(n), int(m)
    
    
def format_2(line):
    """ For reading in edges in the form "n\tm\t\n"
    """
    (n, end) = line.split('\t')
    m = end[:-2]
    
    return int(n), int(m)
    
    
def gen_prefix(name, nodes, edges):
    prefix = """# This is the cleaned %(name)s Collaboration Network
# It has had fragments (small disconnected subgraphs) removed             
# All nodes of degree 1 and 2 have been removed. Where
# necessary they have been replaced with a bridge between
# higher degree nodes.
#
# %(nodes)s nodes and %(edges)s edges
# nodes are authors and edges represent a collaboration.
#
# format is:
# "node\\tnode\\n"
""" % locals()

    return prefix