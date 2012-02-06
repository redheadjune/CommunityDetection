# -*- coding: utf-8 -*-


def find_clique4(graph, n, size):
    """ Finds a clique in the graph of the given size containing n
    """
    
    cand1 = set(graph.neigbors(n))
    for m in graph.neighbors_iter(n):
        if n != m:
            
    
    
    
    
    
class find_clique3 :
    """ Is an iterator object for finding triangles involving a particular node
    
    Marches through to find the path n, m, p, where n is set
    """
    
    def __init__(self, graph, n):
        self.n = n
        self.m = graph.neighbors(n)
        self.mpos = 0
        self.p = graph.neigbors(m)
        else.ppos = 0
        
        
    def next(self, graph):
        
        if mpos >= len(m):
            raise StopIteration()
        
        if ppos >= len(p):
            mpos += 1
            ppos = 0
            p = graph.neighbors(m[mpos])
            return self.next(graph)
            
        if triangle:
            return (n, m[mpos], p[pos])
            
        else:
            ppos += 1
            return self.next(graph)