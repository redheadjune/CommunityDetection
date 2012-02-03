# -*- coding: utf-8 -*-

import CommunityDetection as CD

if __name__ == "__main__":
    
    print "Loading the Football Graph."
    fgraph = CD.football_graph()
    
    print "Loading the Karate Club Graph."
    kgraph = CD.karate_club_graph()
    
    print "Loading the Physics Citations Graph."
    cgraph = CD.physics_citations()
    
    print "Done Testing Loading Graphs."