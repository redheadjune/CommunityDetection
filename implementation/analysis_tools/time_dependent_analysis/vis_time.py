
import CommunityDetection as CD
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pickle
import random

def hack_to_load():
    """ A hack to reload the communities after a crash
    """
    pf = open('big_c_physics_2', 'rb')
    big_c = pickle.load(pf)
    pf.close()
    pf = open('small_c_physics', 'rb')
    small_c = pickle.load(pf)
    pf.close()
    
    p_com = big_c['Parallel Communities']
    p_com.extend(small_c['Parallel Communities'])
    
    p_com = CD.clean_of_duplicate_c(p_com, .25)
    
    return p_com, small_c['Modularity Communities'], small_c['Metis Communities']

def calc_cite_correlation(graph, communities, dates):
    """ Calculates the number of communities a paper cites from and is cited by
    """
    outgoing = {}
    incoming = {}
    for n in graph.nodes():
        outgoing[n] = filter(lambda m: dates[m] < dates[n], graph.neighbors(n))
        incoming[n] = filter(lambda m: dates[m] > dates[n], graph.neighbors(n))
        
    n_to_c = {}
    for n in graph.nodes():
        n_to_c[n] = []
        
    c_name = 0
    for c in communities:
        c_name += 1
        for n in c:
            n_to_c[n].append(c_name)
            
    outgoing_to_c = {}
    incoming_from_c = {}
    for n in graph.nodes():
        c_cited = []
        for m in outgoing[n]:
            c_cited.extend(n_to_c[m])
        outgoing_to_c[n] = set(c_cited)
        c_cited = []
        for m in incoming[n]:
            c_cited.extend(n_to_c[m])
        incoming_from_c[n] = set(c_cited)
        
    nodes = graph.nodes()
    return ([len(outgoing_to_c[n]) for n in nodes],
            [len(incoming_from_c[n]) for n in nodes],
            [len(incoming[n]) for n in nodes])
        


def plot_community_connectivity_impact(graph, par_com, mod_com, dates, sample):
    """Plots the correlation between number of communities a paper is cited by
    and the number of citations a paper receives
    """
    p_correlation = []
    m_correlation = []
    for n in sample:
        citations = len(filter(lambda m: dates[m]>dates[n], graph.neighbors(n)))
        par_cited_by = get_c_n_connects_to(graph,
                                           n,
                                           par_com,
                                           dates,
                                           cites=False)
        mod_cited_by = get_c_n_connects_to(graph,
                                           n,
                                           mod_com,
                                           dates,
                                           cites=False)
        p_correlation.append((len(par_cited_by), citations))
        m_correlation.append((len(mod_cited_by), citations))
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot([x for (x,y) in p_correlation],
             [y for (x,y) in p_correlation],
             'r*',
             label='Parallel')
    plt.plot([x for (x,y) in m_correlation],
             [y for (x,y) in m_correlation],
             'b*',
             label='Modularity')
    plt.legend()
    ax.set_ylabel('Number of Papers a Node is Cited By.', fontsize=18)
    ax.set_xlabel('Number of Communities a Node is Cited By.', fontsize=18)
    ax.set_title('Communities and Citations Correlation', fontsize=24)
    plt.xticks([0, 150, 300], [0, 150, 300])
    plt.yticks([0, 1500, 2500], [0, 1500, 2500])
    plt.show()
    
    plt.savefig('correlation_c_cites_citations.eps')
    plt.savefig('correlation_c_cites_citations.pdf')
    
        
def draw_time_communities(graph,
                          dates,
                          communities,
                          color_map={},
                          prefix="rubish",
                          limit_nodes=[]):
    """ Draws the communities in a time dependent manner
    Parameters
    ----------
    graph : a networkx graph
    dates : a dictionary of dates
    communities : a list of communities
    """
    color = ['#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#A0522D',
             '#D2B48C', '#8B0000', 'b']

    def get_color(store, communities, overlap=[]):
        offset = 1
        for c in communities:
            c_name = None
            for n in c:
                if n in color_map:
                    c_name = color_map[n]
                    
            if c_name == None:
                index = len(color_map) + offset
                if index >= len(color):
                    c_name = -1
                else:
                    c_name = (len(color_map) + offset) % len(color)

                offset += 1
            
            for n in c:
                if n in overlap:
                    store[n] = '#5F9EA0'
                else:
                    store[n] = color[c_name]
                    
        return store
    
    
    
    # map the nodes to their community color
    overlap = []
    counts = {}
    if limit_nodes:
        communities = [filter(lambda n: n in limit_nodes, c)
                       for c in communities]
    
    for c in communities:
        for n in c:
            counts[n] = counts.get(n, 0) + 1
                
        overlap = filter(lambda n: counts[n] > 1, counts.keys())
        
    colored_nodes = get_color({}, communities, overlap)
    sgraph = nx.subgraph(graph, colored_nodes.keys())
    
    to_remove = filter(lambda n: sgraph.degree()[n]>40, sgraph.nodes())
    sgraph.remove_nodes_from(to_remove)
    
    communities.sort(key=lambda c:len(c), reverse=True)
    order = order_communities_y(graph, communities)
    communities = [communities[i] for i in order]
    count = 0
    y_pos = {}
    for c in communities:
        for n in c:
            y_pos[n] = count + random.randint(-3, 3)
            
        count += 10
        
    nodes = sgraph.nodes()
    pos = {}
    for n in nodes:
        pos[n] = (dates[n], y_pos[n])
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    nx.draw(sgraph,
            pos=pos,
            node_color=[colored_nodes[n] for n in nodes],
            node_size=100,
            alpha=1.,
            with_labels=False,
            width=.5,
            edge_color='#5F9EA0')
    #ax.set_title("Parallel Communities in a Time Setting", fontsize=28)
    plt.show()
    plt.savefig(prefix + '.eps')
    plt.savefig(prefix + '.pdf')  
  
  
def order_communities_y(graph, communities):
    """ Orders the communities with the y direction
    presumes the first community is the largest
    """
    ordering = [0]
    on_c = 0
    
    # attach the next best
    while len(ordering) < len(communities):
        i = ordering[-1]
        connection_strength = []
        possible = filter(lambda k: k not in ordering, range(len(communities)))
        for j in possible:
            connection_strength.append((j, strength_c_connection(graph,
                                                                 communities[i],
                                                                 communities[j])))
        connection_strength.sort(key=lambda s: s[1], reverse=True)
        ordering.append(connection_strength[0][0])
        
    return ordering
    

def classify_nodes(graph, communities, escape_thresh=20):
    """ Classifies the nodes into types
    Parameters
    ----------
    
    Returns
    -------
    stable : a node that only cites from a few community
    rockstar : a node that cites from many communities
    creators : nodes that create a community
    interpretors : nodes that make a community popular
    spanners : nodes that cite many communities
    reviewers : nodes that unify a community
    escapers : nodes that have a broad impact
    dark : nodes that do not belong to a community
    """
    seen = set()
    for c in communities:
        seen.update(c)

    stable = []
    rockstar = []
    creators = []
    interpretors = []
    spanners = []
    reviewers = []
    escapers = []        
    dark = set(graph.nodes()) - seen
    
    count = 0
    for n in seen:
        count += 1
        if count % 100 == 0:
            print "cleared node ", count
         
        before = get_c_n_connects_to(graph, n, communities, dates, cites=True)
        after = get_c_n_connects_to(graph, n, communities, dates, cites=False)
        cites = sum([s for (c,s) in before])
        citations = sum([s for (c, s) in after])
        if is_stable(before, after):
            stable.append(n)
            
        if is_rockstar(before, after):
            rockstar.append(n)
            
        if is_creator(before, after):
            creator.append(n)
            
        if is_interpretor(before, after):
            interpretors.append(n)
            
        if is_spanner(before, after):
            spanners.append(n)
            
        if is_reviewer(before, after):
            reviewers.append(n)
            
        if is_escaper(before, after):
            escapers.append(n)
            
    return creator, interpretors, spanners, reviewers, escapers, dark

def is_stable(before, after):
    """ Returns True/False on whether or not
    """
    if len(before) < 3:
        return True
    
    return False

def is_rockstar(before, after):
    """ Returns True/False on whether or not
    """
    if len(before) > 20:
        return True
    
    return False

def is_creator(before, after):
    """ Returns True/False on whether or not
    JTODO
    """
    if True:
        return True
    
    return False

def is_interpretor(before, after):
    """ Returns True/False on whether or not
    JTODO
    """
    if True:
        return True
    
    return False

def is_spanner(before, after):
    """ Returns True/False on whether or not
    """
    if len(before) > 10:
        return True
    
    return False

def is_reviewer(before, after):
    """ Returns True/False on whether or not
    """
    if sum([s for (c, s) in before]) > 50:
        return True
    
    return False

def is_escaper(before, after):
    """ Returns True/False on whether or not
    """
    if len(after) > 20:
        return True
    
    return False


def information_rate(graph, communities, ages):
    """ Finds the time it takes a citation to occur for internal and external
    edges
    """
    k = 1000
    ext_edges, int_edges = edge_classification(graph, communities)
    int_time = [np.abs(ages[m] - ages[n]) for (m, n) in int_edges]
    ext_time = [np.abs(ages[m] - ages[n]) for (m, n) in ext_edges]
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    bins = ax.hist([int_time, ext_time], k)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ((int_counts, ext_counts), bins, patches) = ax.hist([int_edges, ext_edges],
                                                        k)
    
    norm_factor = [max(float(int_counts[i] + ext_counts[i]), 1.)
                   for i in range(k)]
    int_contribution = [int_counts[i]/norm_factor[i] for i in range(k)]
    ext_contribution = [ext_counts[i]/norm_factor[i] for i in range(k)]
    """
    plt.bar(bins, int_contribution, .01, color='r')
    plt.bar(bins, ext_contribution, .01, color='b', bottom=int_contribution)
    plt.show()
    """
    return int_counts, ext_counts, int_contribution, ext_contribution, bins
        

def edge_classification(graph, communities):
    """ Classifies the edge as info inside a community or between communities
    Parameters
    ----------
    graph : a networkx graph
    communities : a list of communities
    
    Returns
    -------
    ext_edges : 
    """
    ext_graph = nx.subgraph(graph, graph.nodes())
    int_graph = nx.Graph()
    int_graph.add_nodes_from(graph.nodes())
    for c in communities:
        sgraph = nx.subgraph(graph, c)
        ext_graph.remove_edges_from(sgraph.edges())
        int_graph.add_edges_from(sgraph.edges())

    return ext_graph.edges(), int_graph.edges()
    
    
def get_c_n_connects_to(graph, n, communities, dates=[], cites=True):
    """ Returns all the communities in which n cites papers and orders them by
    number of citations
    Parameters
    ----------
    graph : a networkx graph
    n : the node in consideration
    communities : a list of communities
    dates : dates of nodes
    cites : True - only consider papers a node cites,
            False - only consider papers that cite it
    
    Returns
    -------
    communities n connects to, if dates is non-empty,
    limits to communities n cites
    """
    found = []
    for j in range(len(communities)):
        if dates != []:
            if cites:
                found.append((j, strength_c_connection(graph,
                                                       [n],
                                                       communities[j],
                                                       lambda n, m: 
                                                       dates[m]<dates[n])))
            else:
                found.append((j, strength_c_connection(graph,
                                                       [n],
                                                       communities[j],
                                                       lambda n, m: 
                                                       dates[m]>dates[n])))
        else:
            found.append((j, strength_c_connection(graph,
                                                   [n],
                                                   communities[j])))
                          
    if len(found) > len(communities):
        print "buggy ", len(found), n, len(communities), found[:5]
    found = filter(lambda (j, s): s>0, found)
    found.sort(key=lambda (j, s): s, reverse=True)
    return found

    
def strength_c_connection(graph, com_a, com_b, criteria=None):
    """
    returns the number edges between com_a and com_b
    """
    s = 0
    for n in com_a:
        for m in graph.neighbors(n):
            if m in com_b:
                if criteria == None or criteria(n,m):
                    s += 1
                
                
    return s

def find_interpretors(graph, communities, dates):
    """ Find interpretors
    
    Returns
    -------
    interps : a list of nodes, that are not the creators of a topic, ie 1 year
    after the start of the community, but cause many internal citations
    have few forward cites within the community and have many later cites
    """
    ages = [min([dates[n] for n in c]) for c in communities]
    interps = []
    for i in range(len(communities)):
        later_part = filter(lambda n: dates[n] - ages[i] > 365., communities[i])
        starters = set(communities[i]) - set(later_part)
        starter_power = strength_c_connection(graph,
                                              starters,
                                              communities[i])
        if starter_power < 10:
            for n in later_part:
                cites_before = strength_c_connection(graph,
                                                     [n],
                                                     communities[i],
                                                     lambda n,m:
                                                     dates[m]<dates[n])
                cites_after = strength_c_connection(graph,
                                                    [n],
                                                    communities[i],
                                                    lambda n,m:
                                                    dates[m]>dates[n])
                if 1 < cites_before < 5 and cites_after > 10:
                    interps.append((n, i))
        
    return interps


def find_spanners(graph, to_check, communities, dates):
    """ Finds the papers that span communities
    Parameters
    ----------
    graph : networkx graph
    to_check : nodes to consider
    communities : a list of communities
    dates : dates of publication
    
    Returns
    -------
    spanners : a list of nodes that are widely cited by multiple communities
    """
    spanners = []
    ndegree = graph.degree()
    for n in to_check:
        if ndegree[n] > 20:
            followers = get_c_n_connects_to(graph,
                                            n,
                                            communities,
                                            dates,
                                            cites=False)
            if len(followers) > 20:
                spanners.append(n)
            
    return spanners


def find_review_papers(graph, dates):
    """ Finds the review papers
    Parameters
    ----------
    graph : networkx graph
    dates : a dictionary of dates
    
    Return
    ------
    reviews : a list of papers with more than 50 papers they cite
    """
    reviews = []
    for n in graph.nodes():
        n_cites = filter(lambda m: dates[m] < dates[n], graph.neighbors(n))
        if len(n_cites) >= 50:
            reviews.append(n)
            
    return reviews


def find_creators(graph, to_check, communities, dates):
    """ Finds the creators of communities
    Parameters
    ----------
    graph : networkx graph
    communities : a list of communities
    
    Returns
    -------
    creators : a list of nodes that do not relate heavily to previous communities
    """
    creators = []
    for n in to_check:
        came_from = get_c_n_connects_to(graph, n, communities, dates)
        if came_from == [] or came_from[0][1] < 2:
            creators.append(n)
            
    return creators