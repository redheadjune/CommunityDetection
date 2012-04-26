
import CommunityDetection as CD

def all_detection_methods(graph, param=None):
    """ Takes a graph and returns all results
    """
    found = {}
    
    # Find the modularity communities
    mod_part = CD.modularity_run(graph)
    found['modularity'] = CD.part_to_sets(mod_part)
    
    # Find the linearity communities
    dendo = CD.create_dendogram_linear(graph, param[0], param[1], param[2])
    lin_part = CD.partition_at_level(dendo, len(dendo) - 1)
    lin_sets = CD.part_to_sets(lin_part)
    found['linearity'] = CD.linear_expand(graph,
                                          lin_sets,
                                          param[0],
                                          param[1],
                                          param[2])
    
    # Find the communities in parallel
    
      
    
    return found