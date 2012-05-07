
import CommunityDetection as CD
import networkx as nx
import os

def all_detection_methods(graph, param=None, path=None):
    """ Takes a graph and returns all results
    
    Parameters
    ----------
    param : an array of [a, b, c, min_degree, force_steps, ithresh, max_it]
          : (a,b,c) are the parameters for linearity
          : core_size, is the minimum clique to begin with
          : force_steps, is how many steps to force in grow
          : ithresh is the internal threshold for a seed
          : max_it is the maximum number of iterations for parallel
    """
    found = {}
    
    # Find the modularity communities
    mod_part = CD.modularity_run(graph)
    found['Modularity Communities'] = CD.part_to_sets(mod_part)
    print "Finished Modularity"
    
    # Find the linearity communities
    if param[0] == 0:
        found['Linearity Communities'] = [graph.nodes()]
    else:
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
    if graph.number_of_nodes() < 3000:
        seeds = CD.core_seeds(graph, param[5], param[3])
    else:
        seeds = CD.distant_seeds(graph, min_size=param[3])
        
    all_info = CD.expand_all(graph, seeds, param[4], param[6])
    communities = all_info[0]
    found['Parallel Communities'] = [c.nodes.keys() for c in communities]
    print "Finished Parallel"
    
    # Find the communities from Metris
    if path:
        k = str(max(len(found["Linearity Communities"])/2,
                    len(found["Parallel Communities"])/2))
        mapping = CD.write_metis_format(graph, path)
        # execute metis
        os.system("./CommunityDetection/implementation/known_algorithms/" +
                  "metis-5.0.2/bin/gpmetis " + path + " " + k)
        r_mapping = {}
        for n, n_id in mapping.iteritems():
            r_mapping[n_id] = n
        part = CD.load_metis_partition(path + ".part." + k, r_mapping)
        found["Metis Communities"] = part.values()
        
    print "Finished Metris"
    
    return found