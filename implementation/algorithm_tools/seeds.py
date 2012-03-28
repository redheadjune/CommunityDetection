# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx

""" This module is for providing different ways of getting seed communities.
"""

def distant_seeds(graph, method='mod'):
    """Finds seeds that are far apart in the graph
    Parameters
    ----------
    graph : a networkx graph
    method : optional input for which local community method to find
    
    Method
    ------
    For a decreasing min clique size, finds a clique of that size, finds the
    best seed involving that clique, appends it, and removes the ball of radius 1
    from the graph.  Then repeats until there are no more cliques of that size
    and terminates when the graph is empty.
    """

    graph = graph.copy()
    seeds = []
    clique_size = 20
    
    while graph.number_of_nodes() > 0 and clique_size > 10:
        more = True
        gen_cliques = nx.find_cliques(graph)
        clique = gen_cliques.next()
        while more:
            if len(clique)>= clique_size:
                print "     found seed", len(seeds), graph.number_of_nodes()
                more = False
                possibleseeds = local_seed_communities(graph,
                                                       clique,
                                                       1,
                                                       0.5 * len(clique),
                                                       method)
                possibleseeds.sort(reverse=True)
                seeds.append(possibleseeds[0])
                graph.remove_nodes_from(CD.get_ball(graph, possibleseeds[0], 1))
            
            try:
                clique = gen_cliques.next()
            except:
                break
            
        if more:
            print "ran through that size of clique ", clique_size
            clique_size -= 1
    
    return seeds

def ind_seeds(graph, ithresh, dthresh, method='mod'):
    """ Finds all seed communities within the graph, starting from an
    individual node,
    
    Parameters
    ----------
    graph : a networkx graph, weighted with node sizes
    ithresh : the internal density threshold of what is a seed
    dthresh : the threshold on the degree of which nodes to consider
    method : a string of 'mod' or 'lin' corresponding to using modularity or
            linearity for the local detection parth
    
    Method
    ------
    Finds the Ball of radius 1 around every individual node, removes that node,
    runs modularity/linearity on the remaining subgraph.  For every community
    community detection returns adds in the original centered node and tests if
    the internal density of the community meets the required threshold to be
    a seed community.
    
    Notes
    -----
    I do not consider this to be a very good method.  The issue is that 1 node
    by itself does not provide interesting information in the graph - not even
    by including all of its neighbors.  Most seeds produced by this method are
    small or not dense.
    
    Returns
    -------
    A list of sets that are seed communities under this method.
    """
    seeds = []
    
    for n in graph.nodes():
        if graph.degree(n) >= dthresh:
            possibleseeds = local_communities(graph, [n], 1, 1, method)
            for s in possibleseeds:
                idensity = CD.get_internal_density(graph, s)
                if idensity >= ithresh:
                    seeds.append(s)
                
    return seeds
        
        
def core_seeds(graph, ithresh, csize, method='mod'):
    """ Finds all seed communities within the graph.
    
    Parameters
    ----------
    graph : a networkx graph, weighted with node sizes
    ithresh : the internal density threshold of what is a seed
    csize : minimum clique size to try as a core
    method : 'mod'/'lin' to indicate use of modularity or linearity in the
            local detection
    
    Method
    ------
    Finds all cliques in the graph (uses the networkx function, which is
    relatively quick).  For each clique, finds the Ball of radius 1 around every
    clique, removes that clique, runs modularity/linearity on the remaining
    subgraph. For every community local community deteciton returns adds in the
    original clique core and tests if the internal density of the subset
    meets the required threshold to be a seed community.
    
    Returns
    -------
    A list of sets that are seed communities under this method.
    
    Judgement Calls
    ---------------
    only consider a ball of radius 1 around clique
    only consider nodes attached to at least half of the core
    only consider cores that have at least 95% new nodes to consider
    
    with these judgements, almost all cores are big in range 10-60 nodes!
    """
    
    seeds = []
    
    # find and set up cores
    coresiter = nx.find_cliques(graph)
    cores = [c for c in coresiter]
    cores = filter(lambda c: len(c) >= csize, cores)
    cores.sort(key=lambda c: len(c), reverse=True)
    print "Finished getting all Cliques for Cores"
    
    accounted = set()
    count = 0
    used = 0
    for core in cores:
        count += 1
        if count%1000 == 0:
            print count, " out of ", len(cores), " cores considered," + \
                  "and covered", len(accounted), " nodes.  Used "+\
                  str(used), " cores down to a size of ", len(core)
        if len(accounted.intersection(set(core))) < .05 * len(core):
            #accounted.update(core)
            used += 1
            
            possibleseeds = local_seed_communities(graph,
                                                   core,
                                                   1,
                                                   0.5 * len(core),
                                                   method)
            
            for seed in possibleseeds:
                subgraph = graph.subgraph(seed)
                idensity = CD.get_internal_density(subgraph)
                if idensity >= ithresh:
                    accounted.update(seed)
                    seeds.append(list(seed))
        
    return seeds
    
    
    
def local_seed_communities(graph, core, r, d, method):
    """A helper function that does the heart of pulling out local communities.
    
    Parameters
    ---------
    graph : the overall graph
    core : a really dense subset of nodes to work from
    r : the radius out to consider
    d : the minimum degree connectivity to the core for a node to be considered
    method : 
    
    Returns
    -------
    possibleseeds : a list of lists, where each list is the core unioned with
    the communities found in the fractured ball of radius r around the core -
    all with using the modularity maximization method.
    
    Judgements
    ----------
    All judgement calls are passed in through r and d
    Additional judgement made for running linearity on abc parameters
    """
    
    possibleseeds = []
    
    ball = CD.get_ball(graph, core, r)
    subgraph = graph.subgraph(ball)
    
    # now need to filter out nodes that are not well enough connected to thecore
    degree = {}
    for n in core:
        for m in subgraph.neighbors(n):
            degree[m] = degree.get(m, 0) + 1
    for m in degree:
        if degree[m] < d:
            subgraph.remove_node(m)
    
    subgraph.remove_nodes_from(core)
    
    if subgraph.number_of_edges() != 0:
        if method == 'mod':
            split = CD.modularity_run(subgraph)
        else:
            split = CD.linearity_run(subgraph, 1., .01, .01)
            
        possibleseeds = CD.part_to_sets(split)
        for c in possibleseeds:
            c.extend(core)
            
    possibleseeds.append(core)
            
    return possibleseeds
                
                