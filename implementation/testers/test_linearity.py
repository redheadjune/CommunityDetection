# -*- coding: utf-8 -*-

import CommunityDetection as CD


def test_linearity():
    
    print "Testing linearity on Karate for Cliques: "
    
    kgraph = CD.karate_club_graph()    
    part = CD.linearity_run(kgraph, 1., 0., .00000001)
    check_partition(part, 1)
    
    print "Testing linearity on football for Complete Cover: "
    
    fgraph = CD.football_graph()
    partition = CD.linearity_run(fgraph, 0., 1., 0.)
    check_partition(partition, 1)
    
    
    print "Testing linearity on physics archive for Complete Cover: "
    
    pgraph = CD.physics_citations()  
    print "    Loaded Graph"  
    partition = CD.linearity_run(pgraph, 1., 0., 0.00000000001)
    check_partition(partition, 1)
    
        
        
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