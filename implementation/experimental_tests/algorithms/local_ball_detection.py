# -*- coding: utf-8 -*-

import CommunityDetection as CD

def test_ball(subgraph, core, realcom):
    """Given a subgraph, a core, and the real communities.  Find what running
community detection on the ball of radius 1 returns.
    """
    subgraph.remove_nodes_from(core)
    
    part = CD.modularity_run(subgraph)
    
    sets = CD.part_to_sets(part)
    
    realistically = []
    for s in sets:
        realistically.append([realcom[n] for n in s])
        
        
    return realistically