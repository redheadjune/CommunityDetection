# -*- coding: utf-8 -*-

import candidates
import community
import copy
import math
import matplotlib.pyplot as plt
import numpy as np

def expand_all(graph, seeds, forced=0, maxit=-1):
    """Expands all seeds within the graph
    """
    found_c = []
    found_cand = []
    found_closure = []
    found_stat = []
    found_sd = []
    found_order = []
    
    for s in seeds:
        if maxit < 0:
            maxit = min(150, graph.number_of_nodes()/30.)
            maxit = max(50, maxit)
            
        c, cand, order, stat_hist, sd_hist, closure_hist = expand(graph,
                                                                  s,
                                                                  maxit,
                                                                  forced=forced)
        found_c.append(c)
        found_cand.append(cand)
        found_order.append(order)
        found_stat.append(stat_hist)
        found_sd.append(sd_hist)
        found_closure.append(closure_hist)
            
        if len(found_c) % 100 == 0:
            print "completed ", len(found_c), " expansions out of ", len(seeds)
        
    return found_c, found_cand, found_order, found_stat, found_sd, found_closure
        

def expand(graph, subset, maxit, forced=0):
    """Expands the given subset with the more likely determined by 
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
    # set up community and candidate data structures
    cs = community.Community()
    external_nodes = cs.init(graph, subset)
    cand = candidates.Candidates(graph, external_nodes, cs)
    cs.init_bounds(cand)
    cand.rework_fringe()
    
    # set up accounting data structures for experimentation
    order = list(subset)    
    m = order[-1]
    stat_hist = [(copy.copy(cs.nodes[m]),
                          cand.stat_import(cs.nodes[m]),
                          cand.stats_string())]
    sd_hist = [cand.stat_import(cs.nodes[m])[cs.nodes[m]['reason']]]
    closure_hist = [closure(cs, cand)]
    
    count = 0
    while (forced or closure(cs, cand) > 0) and count < maxit:
        if closure(cs, cand) == 0:
            forced -= 1
        
        m = cand.get_best()
        if m == None:
            if not forced:
                break
            else:
                m = cand.get_forced()
                if m == None:
                    #print "Ran out of nodes."
                    break
           
        if forced or cs.is_candidate(cand.close[m]):
            order.append(m)
            changed = cs.add_node(graph, m, cand.fringe)
            cand.add_connectivity(changed)
            cand.remove_node(m)
        else:
            print "BUG (?) in EXPAND"
            
        stat_hist.append((copy.copy(cs.nodes[m]),
                          cand.stat_import(cs.nodes[m]),
                          cand.stats_string()))
        sd_hist.append(cand.stat_import(cs.nodes[m])[cs.nodes[m]['reason']])
        closure_hist.append(closure(cs, cand))
            
        count += 1
                   
    cs, cand = cut_last_closure(graph, order, cs, cand, closure_hist)
    imp = cand.stat_import({'e':cs.bounds['min_e'], 'p':cs.bounds['min_p']})
    """
    print "Finished in ", count, " steps."
    print "         With Closure: ", closure(cs, cand), " With ", len(cs.nodes), " nodes."
    print "         The standard deviation away for e is: ", imp['e'], " and p: ", imp['p']
    """
    return cs, cand, order, stat_hist, sd_hist, closure_hist


def cut_last_closure(graph, order, cs, cand, closure_history):
    """collapses community down to the last time it was closed
    """
    if closure_history[-1] != min(closure_history):
        closure_history.reverse()
        cut = closure_history.index(min(closure_history))
        closure_history.reverse()
        cs = community.Community()
        external_nodes = cs.init(graph, order[:-cut])
        cand = candidates.Candidates(graph, external_nodes, cs)
        cs.init_bounds(cand)
        cand.rework_fringe()
        return cs, cand
    else:
        return cs, cand

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
    
    
