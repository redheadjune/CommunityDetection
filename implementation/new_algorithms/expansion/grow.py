# -*- coding: utf-8 -*-

import copy
import math
import matplotlib.pyplot as plt

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
    order = list(subset)
    
    ext_n, int_n, bounds, buckets = init_trackers(graph, subset)
    
    print "Finished the setup. "
   
    count = 0
    while check_closure(ext_n, int_n, bounds) > .1 and count < maxit:
        count += 1
        if count % 10 == 0:
            print "Progressed in ", count, "steps.  Closure of:" + \
                  str(check_closure(ext_n, int_n, bounds))+ " limits of: " + \
                  str(bounds['min_p']) + "% and ", bounds['min_e'], "E"
            
        m = pull_best(buckets)
        if add(bounds, ext_n[m]):
            order.append(m)
            update_trackers(graph, ext_n, int_n, bounds, buckets, m)
        else:
            # don't consider this node again until something has changed.
            ext_n[m]['b_id'] = 0
            buckets[0].append(m)
        
    return order, ext_n, int_n, bounds
        
        
def init_trackers(graph, subset):
    """Initializes the trackers of node status needed to expand.
    Parameters
    ----------
    
    Returns
    -------
    ext_n - a dictionary of nodes external to the subset, with their info
    int_n - a dict of nodes internal to the subset, with their info
    bounds - a dict of the info of the community bounds in variables e and p
    buckets - a list of lists, where the further along in the top list the more
likely to be in C, each sublist is a bucket of nodes with that approximate value

    Notes
    -----
    In these data structures 'e' refers to $E(n, C_s)$, the connectivity of n
    into the subset, and 'p' refers to $\frac{E(n, C_s)}{degree(n)}$, the
    percentage of edges of each node going into the subset.
    """
    ext_n = {}
    int_n = {}
    buckets = [ [] ]
    
    for n in subset:
        for m in graph.neighbors(n):
            if m not in subset:
                ext_n[m] = ext_n.get(m, 0) + 1
            else:
                int_n[m] = int_n.get(m, 0) + 1
    
    # set up the details of the external, but connected nodes
    for m, dm in ext_n.iteritems():
        ext_n[m] = {'e':dm, 'p':dm/float(graph.degree(m)), 'b_id':0}
        buckets[0].append(m)
    
    # set up the details of the internal nodes
    for n, dn in int_n.iteritems():
        int_n[n] = {'e':dn,
                    'p':dn/float(graph.degree(n)),
                    'slope':float(graph.degree(n))}
    
    bounds = {'total_ext_degree' : 0.0 }
    update_bounds(graph, int_n, ext_n, bounds, ext_n.keys(), [])
    
    update_buckets(ext_n, bounds, buckets, copy.copy(buckets[0]))
 
    return ext_n, int_n, bounds, buckets
    
    
def update_bounds(graph, int_n, ext_n, bounds, newly_attached, newly_removed):
    """ Finds the bounds of what 'e' or 'p' have to be at least to be in C
    
    Parameters
    ----------
    int_n : dictionary of internal nodes
    bounds : bounds dictionary with all info
    newly_attached : nodes that have now joined the fray
    newly_removed : nodes that have been included into the community
    
    Method
    ------
    Presumes that all data in int_n is meant to stay, uses a line between the
    origin and the (average p, average e), classifies points as above or below
    the line.  If above, the points contribute to what the minimum e must be,
    and if below, points must contribute to what the minimum p must be.
    """

    bounds['total_ext_degree'] -= sum([graph.degree(n) for n in newly_removed])
    bounds['total_ext_degree'] += sum([graph.degree(n) for n in newly_attached])
    
    bounds['ext_slope'] = bounds['total_ext_degree'] / float(len(ext_n))
    

    bounds['min_p'] = 1.
    bounds['min_e'] = float(len(int_n))
    for n, dn in int_n.iteritems():
        if dn['slope'] > bounds['ext_slope']:
            bounds['min_e'] = min(bounds['min_e'], dn['e'])
        else:
            bounds['min_p'] = min(bounds['min_p'], dn['p'])    


def update_trackers(graph, ext_n, int_n, bounds, buckets, n):
    """ Adds n into the community and updates all the data structures in place
    Parameters
    ----------
    
    Returns
    -------
    nothing : but changes ext_n, int_n, and buckets to reflect n now in C
    """
    int_n[n] = ext_n.pop(n)
    int_n[n]['slope'] = graph.degree(n)
    
    changed = []
    newly_attached = []
    for m in graph.neighbors(n):
        if m in int_n:
            int_n[m]['e'] += 1
            int_n[m]['p'] = int_n[m]['e'] / float(graph.degree(m))
            
        else:
            if m not in ext_n:
                ext_n[m] = {'e':0, 'b_id':0}
                buckets[0].append(m)
                newly_attached.append(m)
            
            ext_n[m]['e'] += 1
            ext_n[m]['p'] = ext_n[m]['e'] / float(graph.degree(m))
            changed.append(m)
            
    update_bounds(graph, int_n, ext_n, bounds, newly_attached, [n])
    update_buckets(ext_n, bounds, buckets, changed)
    
    
def update_buckets(ext_n, bounds, buckets, changed):
    """ Given that the status of nodes in changed is updated, shuffles the
    buckets.  All operations are done in place.

    Parameters
    ---------
    
    Method
    ------
    Uses the function bucket_id to find the new place for nodes
    """
    
    for n in changed:
        buckets[ext_n[n]['b_id']].remove(n)
        newb = bucket_id(ext_n[n], bounds)
        ext_n[n]['b_id'] = newb
        if newb >= len(buckets):
            buckets.extend([[] for i in range(len(buckets), newb + 2)])
        buckets[newb].append(n)
            

def bucket_id(spec, bounds):
    """ Is an ordered function that finds which bucket spec is in.
    """
        
    return int ( spec['e']/bounds['min_e'] + \
                 bounds['ext_slope'] * spec['p']/bounds['min_p'] )
    
    
def pull_best(buckets):
    """ Finds the node most likely to be in the community.      
    """
    buckets.reverse()
    for b in buckets:
        if b != []:
            pull = b[0]
            b.remove(pull)
            buckets.reverse()
            return pull
            
    buckets.reverse()
    return False
    
    
def check_closure(ext_n, int_n, bounds):
    """ Returns the fraction of nodes not already in C that meet the
requirements
    
    Returns
    -------
    The fraction of nodes, qualified but not included.  Is 0 if the community
is closed.
    """
    
    outside = filter(lambda (n, info_n): info_n['e'] > bounds['min_e'] or \
                                         info_n['p'] > bounds['min_p'],
                     ext_n.iteritems())
                     
    return len(outside) / float( len(int_n) )
    
    
def add(bounds, spec):
    """ Checks whether or not should really add m
    """
    if spec['e'] < 6 and spec['p'] < .2:
        print "reallllly, ", spec
    if spec['e'] > bounds['min_e'] or spec['p'] > bounds['min_p']:
        return True
        
    return False
            
    
    
    
    
