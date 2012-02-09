# -*- coding: utf-8 -*-

import CommunityDetection as CD
import networkx as nx
import pickle


def mod_cliques(graph):
    """Given a graph, find the modularity partitions.  Then return the cliques
       within each partition.
       
    Returns
    ------
    saves the work in a pickle file in the format of (graph, partition,
    cliques), where cliques is a tuple of (nodes considered, [all maximal
    cliques among the nodes])
    """
    pf = open('cliques_within_mod_communities.pkl', 'wb')
    part = CD.modularity_run(graph)    
    c = CD.part_to_subgraphs(graph, part)
    cliques = []
    for subgraph in c:
        cliques.append( (subgraph.nodes(), CD.find_sub_cliques(subgraph)) )
        
    pickle.dump((graph, part, cliques), pf)
    pf.close()
    
    return cliques
    
    
def lin_cliques(graph):
    """Given a graph, finds the linearity partitions.  Then returns the cliques
       within each partition.
    """
    pf = open('cliques_within_lin_communities.pkl', 'wb')
    part = CD.linearity_run(graph, .5, .5, .001)
    c = CD.part_to_subgraphs(graph, part)
    cliques = []
    for subgraph in c:
        cliques.append( (subgraph.nodes(), CD.find_sub_cliques(subgraph)) )
        
    pickle.dump( (graph, part, cliques), pf )
    pf.close()
        
    return cliques
    
    
def all_cliques(graph, count):
    """ Now, given a large graph, sample the cliques and test for homogeneity
    Parameters
    ----------
    graph : a networkx graph
    
    Method
    ------
    * creates a mapping from nodes to communities
    * uses networkx to generate several cliques and maps the clique members to
      communities, if the clique has at least 4 members
    """
    pf = open('cliques_within_the_graph.pkl', 'wb')
    
    part = CD.modularity_run(graph)
    cgen = nx.find_cliques(graph)
    found = []
    
    for i in xrange(count):
        try:
            clump = cgen.next()
            if len(clump) > 2:
                found.append( ([part[n] for n in clump], clump) )
        except:
            pickle.dump( (graph, part, found) , pf)
            pf.close()
            return found
            
    pickle.dump( (graph, part, found) , pf)
    pf.close()
    return found