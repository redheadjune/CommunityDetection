

import CommunityDetection as CD
import networkx as nx

def create_heirarchical_community_graph(graph, communities, overlap=.7):
    """ Creates the graph
    """
    print "Starting with ", len(communities), " Communities."
    communities = clean_of_duplicate_c(communities)
    print "Cleaned to ", len(communities), " Communities."
    
    heir_graph = nx.Graph()
    heir_graph.add_nodes_from(range(len(communities)))
    
    for i in range(len(communities)):
        # find the other communities that ci is heavily related to
        ci = communities[i]
        connections = filter(lambda j:len(ci.intersection(communities[j]))
                                      > .5 * len(ci),
                             range(len(communities)))
        heir_graph.add_edges_from([(i, j) for j in connections])
        
    for i in heir_graph.nodes():
        heir_graph.remove_edge(i, i)
    
    return heir_graph 


def clean_of_duplicate_c(communities, overlap=0.9):
    """ If a community overlaps with another community by 75% with similar size,
    removes that c
    
    Parameters
    ----------
    communities : a list of sets
    overlap : the overlap required for two communities to be the same
    
    Returns
    -------
    unique : a list of communities that are either contained in a super community
    or completely unique
    """
    if type(communities[0]) != set:
        communities = [set(c) for c in communities]
    
    def check_against(to_check, to_store):
        for c in to_check:
            seen = max([len(cs.intersection(c)) / float(len(c))
                        for cs in to_store])
            if seen < overlap:
                to_store.append(c)
                
                
    communities.sort(key=lambda n: len(n), reverse=True)
    unique_forward = [communities[0]]
    check_against(communities, unique_forward)
    unique_forward.reverse()
    unique_backward = [unique_forward[0]]
    check_against(unique_forward, unique_backward)
    return unique_backward