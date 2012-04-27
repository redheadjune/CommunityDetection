
import CommunityDetection as CD
import networkx as nx

def all_detection_methods(graph, param=None):
    """ Takes a graph and returns all results
    """
    found = {}
    
    # Find the modularity communities
    mod_part = CD.modularity_run(graph)
    found['Modularity Communities'] = CD.part_to_sets(mod_part)
    print "Finished Modularity"
    
    # Find the linearity communities
    dendo = CD.create_dendogram_linear(graph, param[0], param[1], param[2])
    lin_part = CD.partition_at_level(dendo, len(dendo) - 1)
    lin_sets = CD.part_to_sets(lin_part)
    lin_sets = [set(c) for c in lin_sets]
    found['Linearity Communities'] = CD.linear_expand(graph,
                                          lin_sets,
                                          param[0],
                                          param[1],
                                          param[2])
    print "Finished Linearity"
    
    # Find the communities in parallel
    if graph.number_of_nodes() < 200:
        seeds = CD.core_seeds(graph, 0.55, param[3])
    else:
        seeds = CD.distant_seeds(graph, min_size=param[3])
        
    all_info = CD.expand_all(graph, seeds)
    communities = all_info[0]
    found['Parallel Communities'] = [c.nodes.keys() for c in communities]
    print "Finished Parallel"
    
    return found