# -*- coding: utf-8 -*-

import CommunityDetection as CD


def test_linearity():
    
    print "Testing linearity on Karate for Cliques: "
    
    kgraph = CD.karate_club_graph()    
    part = CD.linearity_run(kgraph, 0.75, 1., .01)
    check_partition(part, 19)
    
    print "Testing linearity on football for Complete Cover: "
    
    fgraph = CD.football_graph()
    part = CD.linearity_run(fgraph, 0., 1., 0.)
    check_partition(part, 1)
    print "    Now for real analysis"
    part = CD.linearity_run(fgraph, 1., 1., .01)
    check_partition(part, 13)
    
    
    print "Testing linearity on physics archive for Connected Components: "
    pgraph = CD.physics_citations()  
    print "    Loaded Graph"  
    part = CD.linearity_run(pgraph, 0., 0., 0.0001)
    check_partition(part, 143)
    print "Testing linearity on physics archive for Cliques: "
    part = CD.linearity_run(pgraph, 1., 0., 0.0000001)
    check_partition(part, 13112)
        
        
def check_partition(part, size):
    if len(set(part.values())) != size:
        print "       ***Failed***:"
        if len(set(part.values())) < 50:
            print set(part.values())
        else:
            print "       ", len(set(part.values()))
    else:
        print "        pass."
        
        
def check_bar(bar, s, base, lin):
    
    if not base or bar.s != s or bar.lin_metric() != lin:
        print "        *** Failed***:"
        print "        " + str(bar)
        
    else:
        print "        pass."
        
        
if __name__ == "__main__":
    
    test_linearity()