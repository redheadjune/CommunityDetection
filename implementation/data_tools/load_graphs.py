# -*- coding: utf-8 -*-

from constants import *

import CommunityDetection as CD
import datetime
import networkx as nx
import pickle
import random

def dolphins():
    """ Loads the dolphin social graph
    """
    try:
        gml_graph = nx.read_gml(DATA_PATH_1 + DOLPHINS)
    except:
        gml_graph = nx.read_gml(DATA_PATH_2 + DOLPHINS)
        
    dgraph = nx.Graph()
    dgraph.add_nodes_from(gml_graph.nodes(), size=1.)
    edges = gml_graph.edges()
    edges = [(u, v, {'weight': 1.}) for (u,v) in edges]
    dgraph.add_edges_from(edges)
    return dgraph


def wiki_voting():
    """ Loads the wiki voting network
    Returns
    -------
    wgraph : a networkx graph, with users as nodes and edges as similarity
    e_outcome : a dictionary keys on election number and valued at whether or
                not the election was successful
    user_voting_record : a dictionary keyed on users and valued on a dictionary
                         of the election they voted in to how they voted
    
    Method:
    let each user have a vector representing how they voted, consisting of
    -1, 0, 1
    the edge weight is the jaccard measure, the dotproduct of the voting vetors
    divided by the number of election one or the other of the users voted in
    """
    wgraph = nx.Graph()
    
    try:
        wfile = open(DATA_PATH_1 + WIKI_VOTING, 'rb')
    except:
        wfile = open(DATA_PATH_2 + WIKI_VOTING, 'rb')   
        
    e_outcome = {}
    user_voting_record = {}
    user_nomination = {}
    e_name = 0
    
    def add_user_vote(user, vote):
        if user == -1:
            return
        
        # adds the vote to the user record
        if user not in user_voting_record:
            user_voting_record[user] = {}
            
        user_voting_record[user][e_name] = vote 
        
    for line in wfile:
        if line[0] != '#':
            line = line[:-1]
            if line[0] == 'E':
                e_name += 1
                (e, out) = line.split('\t')
                e_outcome[e_name] = int(out)
            elif line[0] == 'U':
                (u, user) = line.split('\t')
                user = int(user)
                if user not in user_nomination:
                    user_nomination[user] = []
                user_nomination[user].append(e_name)
            elif line[0] == 'N':
                (n, user) = line.split('\t')
                add_user_vote(int(user), 1)
            elif line[0] == 'V':
                (v, vote, user, time) = line.split('\t')
                add_user_vote(int(user), int(vote))
                
    wfile.close()
                
    # now to add the edges in, not it is a symmetric graph, so consider only n>m
    wgraph.add_nodes_from(user_voting_record.keys(), size=1.)
    # adding edges
    count = 0
    edges = []
    for n in wgraph.nodes():
        for m in wgraph.nodes():
            if m > n:
                count += 1
                if count % 1000000 == 0:
                    print "through ", str(count)[:-6], "edges of 19 million"
                score = jaccard(n, m, user_voting_record)
                if score > .05:
                    edges.append((n, m, {'weight':score}))
                    
    wgraph.add_edges_from(edges)
                    
    pf = open('05_graph_outcome_votes.pkl', 'wb')
    pickle.dump(["wiki_graph with .05 threshold on edges, the election" +
                 "outcomes and the user voting record, user nomiation, "+
                 "generated with wiki_voting()", wgraph, e_outcome,
                 user_voting_record, user_nomination], pf)
    pf.close()
    return wgraph, e_outcome, user_voting_record, user_nomination
    
    
def jaccard(n, m, record):
    """ Computes the dot product of n and m similarities divided by the number
    of records either has participated in
    """
    votes = 0
    one_votes = set(record[n].keys()).union(set(record[m].keys()))
    both_vote = set(record[n].keys()).intersection(set(record[m].keys()))
    for e in both_vote:
        if e in record[n] and e in record[m]:
            votes += record[n][e] * record[m][e]            
        
    return votes / float(len(one_votes))


def load_archivex_dates():
    """ Loads the Dates of the archivex papers
    Returns
    ------
    dates : a dictionary keyed on paper and valued at the ordinal date published
    """
    try:
        dfile = open(DATA_PATH_1 + PHYSICS_PAPER_DATES, 'rb')
    except:
        dfile = open(DATA_PATH_2 + PHYSICS_PAPER_DATES, 'rb')
        
    dates = {}
    for line in dfile:
        line = line[:-1]
        (n, d) = line.split(' ')
        n = int(n)
        (y, m, d) = d.split('-')
        y = int(y)
        m = int(m)
        d = int(d)
        dates[n] = datetime.date(y, m, d)
        dates[n] = dates[n].toordinal()
        
    return dates    


def load_metis_partition(f_name, mapping=None):
    """ Loads the partition created by metis
    Parameters
    ----------
    f_name : the partition file created by metis
    mapping : a mapping of order of node id to real node id
    
    Returns
    -------
    partitions : a dictionary of {community name : members}
    
    Note
    ----
    the members may have to mapped back, because metis does not maintain node id
    """
    p_file = open(f_name, 'rb')
    
    partition = {}
    n_id = 1
    for line in p_file:
        c_id = int(line)
        part = partition.get(c_id, [])
        part.append(n_id)
        partition[c_id] = part
        n_id += 1
        
    if mapping:
        for c_id, members in partition.iteritems():
            partition[c_id] = [mapping[n_id] for n_id in members]

    return partition  
    

def merge_graph(graphs, p):
    """Given a set of graphs, merges them, with the underlying connectivity p
    Parameters
    ----------
    graph : a list of networkx graphs
    p : the probability with which 2 nodes from different graphs are connected
    """
    big_graph = nx.Graph()
    for g in graphs:
        big_graph.add_nodes_from(g.nodes())
        
    for g in graphs:
        big_graph.add_edges_from(g.edges())
        
    for g in graphs:
        for n in g.nodes():
            for m in big_graph.nodes():
                multi = g.degree(n) / 15.
                if m not in g.nodes() and random.random() < p / 2. * multi:
                    big_graph.add_edge(n, m)
                    
    return big_graph


def random_tier_graph(offset=0):
    """Create a set of 3 nested graphs, where the inner core is most dense
    Parameters
    ----------
    offset : the base node name
    
    Returns
    -------
    graph : a networkx graph with nodes named offset to offset + 150
    """
    rings = [set(range(offset, offset + 20)),
             set(range(offset + 20, offset + 60)),
             set(range(offset + 60, offset + 150))]
    p = [0.8, 0.2, 0.05]
    
    graph = nx.Graph()
    graph.add_nodes_from(range(offset, offset + 150))
    
    def get_d(n):
        for i in range(len(rings)):
            if n in rings[i]:
                return i
    
    for n in range(offset, offset + 150):
        n_d = get_d(n)
        for m in range(n+1, offset + 150):
            m_d = get_d(m)
            if random.random() < .15*p[n_d] + .85*p[m_d]:
                graph.add_edge(n, m, {'weight': 1.})
    
    return graph


def random_dual_core_graph(offset=0, r_rings=False):
    """Creates a random graph with 2 cores and of size 400 and 3 tiers
    """
    row_size = 20
    def get_rectangle(corner, height, width):
        core = set()
        for i in range(height):
            core.update(range(corner + row_size * i,
                              corner + row_size * i + width))
            
        return core    
    
    cores = [get_rectangle(offset + row_size * 7 + 7, 5, 2),
             get_rectangle(offset + row_size * 7 + 10, 5, 2)]
    rings = [set(cores[0]).union(set(cores[1]))]
    rings.append(get_rectangle(offset + row_size * 4 + 4, 10, 10) - rings[0])
    rings.append(get_rectangle(offset, 20, 20) - rings[0] - rings[1])
    
    p = [0.8, 0.05, 0.005]
    
    graph = nx.Graph()
    graph.add_nodes_from(range(offset, offset + 400))
    
    def get_d(n):
        for i in range(len(rings)):
            if n in rings[i]:
                return i
            
    def populate_ring(nodes):
        for n in nodes:
            n_d = get_d(n)
            for m in nodes:
                if m > n:
                    m_d = get_d(m)
                    if random.random() < .15*max(p[n_d], p[m_d]) + .85*min(p[n_d], p[m_d]):
                        graph.add_edge(n, m, {'weight': 1.})
                        
    for i in range(len(cores)):
        populate_ring(cores[i])
        for j in range(1, len(rings)):
            populate_ring(cores[i].union(rings[j]))
            
    if r_rings:
        return graph, cores, rings
            
    return graph

    
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