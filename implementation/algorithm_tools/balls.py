# -*- coding: utf-8 -*-


"""This is by far an incomplete module
"""

def get_ball(graph, core, radius):
    """ Returns the ball centered around the core of radius radius.
    Parameters
    ----------
    graph : a networkx graph
    core : a set of nodes
    radius : the radius to march out from the core from
    """
    
    prevlayer = core
    curlayer = []
    
    for i in range(radius):
        for n in prevlayer:
            curlayer.extend(graph.neighbors(n))
            
        curlayer.extend(prevlayer)
        prevlayer = set(curlayer)
        curlayer = []
        
    return prevlayer
