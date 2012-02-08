# -*- coding: utf-8 -*-


import CommunityDetection as CD

def test_bottle():
    """ Tests the data structure Bucket
    """
    
    print "Testing the Bottle Structure."
        
    print "Testing initialization:"
    kgraph = CD.karate_club_graph()
    b = CD.Bottle('sally', kgraph, [1, 2, 3, 4])
    check_bottle(b, 'sally', 12, 29, 4, 12)
        
    print "Testing add node:"
    b.add_member(kgraph, 31)
    check_bottle(b, 'sally',14, 31, 5, 20)
    
    print "Testing remove node:"
    b.remove_member(kgraph, 31)
    check_bottle(b, 'sally', 12, 29, 4, 12)
        
        
def check_bottle(b, name, intedges, extedges, size, idealint):
    """ Checks that the bottle b, has correct values
    """
    if b.size != size or \
       b.name != name or \
       b.intedges != intedges or \
       b.extedges != extedges or \
       b.idealint != idealint:
        print "    ***Failed.***"
        print b
    else:
        print "    pass."
    
    
def test_bar():
    """Tests the data structure Bar
    """
    
    print "Testing the Bar Structure"
    
    print "Testing initialization"
    fgraph = CD.football_graph()
    b = CD.Bar(fgraph, 1226, 1., 1., 1.)
    check_bar(b, 0, 1226, 115, 0)
    
    print "Testing possible swap"
    
    
    print "JTODO: Testing"
    
    
def check_bar(b, intedges, extedges, s, idealint):
    if b.intedges != intedges or \
       b.extedges != extedges or \
       b.s != s or \
       b.idealint != idealint:
        print "    ***Failed.***" 
        print b
    else:
        print "    pass."
        
    
if __name__ == '__main__':
    test_bottle()
    test_bar()