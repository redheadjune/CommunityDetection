
import CommunityDetection as CD
"""This module for the analysis of coverage and overlap
"""


def analyze_coverage(graph, communities):
    """Finds the percentage of nodes that are covered by the communities.
    
    Parameters
    ----------
    graph : a networkx graph
    communities : a bunch of community objects
    
    Returns
    -------
    p : the percentage of the graph covered by the communities
    """
    
    covered = set()
    for c in communities:
        covered.update(c.nodes.keys())
        
    return len(covered) / float(graph.number_of_nodes())


def analyze_overlap(graph, communities):
    """Finds how many communities each node belongs to as well as the overlap
    between communities
    
    Parameters
    ----------
    graph : a networkx graph
    communities : a bunch of community objects
    
    Returns
    -------
    avg_n_overlap : the average number of communities each node belongs to
    dist_n_overlap : an array of the number of communities each node belongs to
    avg_c_overlap : the average % each community overlaps with its closest c
    dist_c_overlap : an array of the % max overlap of c with its closest neighbor
    """
    
    node_overlaps = {}
    home_communities = {}
    for n in graph.nodes():
        node_overlaps[n] = []
        home_communities[n] = []
        
    c_name = -1
    for c in communities:
        set_c = set(c.nodes.keys())
        c_name += 1
        for n in c.nodes.keys():
            #if not majorly seen before
            if home_communities[n] == [] or \
               max([len(set_c.intersection(c1))/float(len(set_c)) for c1 in home_communities[n]]) <= .3:
                home_communities[n].append(set_c)
                node_overlaps[n].append(c_name)
            
    dist_n_overlap = [len(v) for v in node_overlaps.values()]
    dist_n_overlap = filter(lambda x: x>0, dist_n_overlap)
    avg_n_overlap = sum(dist_n_overlap) / float(len(dist_n_overlap))
    
    set_c = [set(c.nodes.keys()) for c in communities]
    
    c_overlaps = [[len(s1.intersection(s2)) for s2 in set_c] for s1 in set_c]
    
    c_overlaps[0] = max(c_overlaps[0][1:]) / float(len(set_c[0]))
    c_overlaps[-1] = max(c_overlaps[-1][:-1]) / float(len(set_c[-1]))
    for i in range(1, c_name):
        c_overlaps[i] = max(max(c_overlaps[i][:i]), max(c_overlaps[i][i+1:])) /\
                        float(len(set_c[i]))

    avg_c_overlap = sum(c_overlaps)/float(len(c_overlaps))
    
    return avg_n_overlap, dist_n_overlap, avg_c_overlap, c_overlaps


def partition_compare(part_c, expand_c):
    """Finds the % that communities are parts and % parts are communities
    
    Parameters
    ----------
    part_c : a list of a lists of communities from the partition
    expand_c : a list of community objects
    
    Returns
    -------
    c_to_part : for each community the largest % contained within a part
    part_to_c : for each part the largest % covered by a community
    """
    expand_c = [set(c.nodes.keys()) for c in expand_c]
    part_c = [set(c.nodes.keys()) for c in part_c]
    c_to_part = [max([len(c.intersection(p)) for p in part_c]) / float(len(c)) for c in expand_c]
    part_to_c = [max([len(c.intersection(p)) for c in expand_c]) / float(len(p)) for p in part_c]
    
    return c_to_part, part_to_c