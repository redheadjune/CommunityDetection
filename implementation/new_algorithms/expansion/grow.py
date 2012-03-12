# -*- coding: utf-8 -*-

import candidates
import community
import copy
import math
import matplotlib.pyplot as plt
import numpy as np

def expand(graph, subset, maxit):
    """This is just a rough sketch.
    Parameters
    ----------
    graph : the networkx graph
    subset : the subset to be expanded
    maxit : the maximum number of iterations or nodes to expand by
    
    Method
    ------
    See paper, expands by best candidate
    
    Returns
    -------
    order : the order in which the nodes were engulfed
    """
    # set up cumulative data structures
    cs = community.Community()
    external_nodes = cs.init(graph, subset)
    cand = candidates.Candidates(graph, external_nodes, cs)
    
    # set up accounting data structures for experimentation
    order = list(subset)
    failed = []    
    closure_history = [closure(cs, cand)] 
    slope_history = []
    e_p_history = [(cs.bounds['min_e'], cs.bounds['min_p'])]
    count = 0
    
    while good_history(closure_history, e_p_history) and count < maxit:
        if count % 1 == 0:
            print "Stepped ", count, "times." +\
                  "Closure of: ", str(closure(cs, cand))+ \
                  cs.to_string()
            
        m = cand.get_best()
        if cs.is_candidate(cand.close[m]):
            order.append(m)
            changed = cs.add_node(graph, m, cand.fringe)
            cand.add_connectivity(changed)
            cand.remove_node(m)
        else:
            print "Partitioning of Fringe and Close grew old."
            failed.append(m)
            cand.remove_node(m)
            
        closure_history.append(closure(cs, cand))
        slope_history.append((cs.bounds['slope'], cs.bounds['offset']))
        e_p_history.append((cs.bounds['min_e'], cs.bounds['min_p']))
        count += 1
        
    """ Old cutting code
    min_c = min(closure_history)
    cut_off = filter(lambda i: closure_history[i] == min_c,
                     range(len(closure_history)))
    
    order = order[:cut_off[-1]+1]
    closure_history = closure_history[:cut_off[-1]+1] 
    """  
            
    print "Finished in ", count, " steps.  With Closure: ", closure(cs, cand)
        
    return cs, cand, order, failed, closure_history, slope_history


def is_community(bounds, closure_history):
    """ Tests whether or not we have a community
    """
    return min(closure_history) < 0.1


def good_history(closure_history, e_p_history):
    """ checks if it is worth continuing.
    """
    if closure_history[-1] == 0:
        # we've finished
        return False    
    
    closure_slope = get_slope(np.array(range(min(len(closure_history), 30))),
                              np.array(closure_history[-30:]))
    p_slope = get_slope(np.array(range(min(len(e_p_history), 30))),
                        np.array([p for e,p in e_p_history[-30:]]))
    e_slope = get_slope(np.array(range(min(len(e_p_history), 30))),
                        np.array([e for e,p in e_p_history[-30:]]))
    if len(closure_history) < 10 \
       or closure_slope < 0.01 \
       or p_slope > 0. \
       or e_slope > 0.:
        # either haven't seen enough or am doing well
        return True
    else:
        # doing worse
        return False
    
    
def get_slope(x, y):
    """Finds the best fit slope through x and y
    
    Parameters
    ----------
    x : a numpy array
    y : a numpy array
    """
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, y)[0]
    return m

    
def closure(cs, cand):
    """ Finds the closure of the community.
    Parameters
    ----------
    cand - a Candidate class
    cs - the Community class
    
    Returns
    -------
    the % of elligable nodes outside of the community, relative to its size.
    """
    return len(cand.close) / float(len(cs.nodes))    
    
    
