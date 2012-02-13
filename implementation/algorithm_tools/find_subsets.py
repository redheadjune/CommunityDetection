# -*- coding: utf-8 -*-


"""This is by far an incomplete module
"""

def get_ball(graph, core, radius):
    """ Returns the ball centered around the core of radius radius.
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

