# -*- coding: utf-8 -*-

import CommunityDetection as CD

def test_cliques():
    
    kgraph = CD.karate_club_graph()
    
    modcliques = CD.mod_cliques(kgraph)
    
    lincliques = CD.lin_cliques(kgraph)
    
    
    
    
    
if __name__ == "__main__":
    test_cliques()