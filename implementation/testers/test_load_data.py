# -*- coding: utf-8 -*-

import CommunityDetection as CD

def check_graph(graphfun, nodes, edges, name):
    """Checks the number of nodes and edges are correct
    """
    print "Loading the %(name)s" %locals()
    
    graph = graphfun()
    
    gnodes = graph.number_of_nodes()
    gedges = graph.number_of_edges()
    
    if gnodes == nodes and gedges == edges:
        print "    Loaded the %(name)s well." % locals()
        
    else:
        print "    *** Mistake in loading the %(name)s," % locals() +\
              " nodes: %(gnodes)s, edges: %(gedges)s ***" % locals()
              
              
if __name__ == "__main__":
    
    ###Football Graph###
    check_graph(CD.football_graph, 115, 613, 'College Football')   
    
    ###Karate Club###
    check_graph(CD.karate_club_graph, 34, 78, 'Karate Club')
    
    ###Physics Citations###
    check_graph(CD.physics_citations, 27770, 352324, 'Physics Citation')
    
    print "Done Testing Loading Graphs."
    
    