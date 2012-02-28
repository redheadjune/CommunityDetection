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
    
    extn, intn, buckets = init_trackers(graph, subset)
    
    print "Finished the setup. "
   
    count = 0
    while check_closure(extn, intn) > .1 and count < maxit:
        count += 1
        if count % 100 == 0:
            print "Progressed in ", count, "steps, to: "
            print "             closure of:", check_closure(extn, intn)
            print "             limits of: ", intn['min_p'], intn['min_e']
            
        m = pull_best(buckets)
        if add(extn, intn, m):
            order.append(m)
            update_trackers(graph, extn, intn, buckets, m)
        
    return order, order, {}
        
        
        
def init_trackers(graph, subset):
    """Initializes the trackers of node status needed to expand.
    Parameters
    ----------
    
    Returns
    -------
    extn - a dictionary of nodes external to the subset, with their info
    intn - a dict of nodes internal to the subset, with their info
    buckets - a list of lists, where the further along in the top list the more
likely to be in C, each sublist is a bucket of nodes with that approximate value

    Notes
    -----
    In these data structures 'e' refers to $E(n, C_s)$, the connectivity of n
    into the subset, and 'p' refers to $\frac{E(n, C_s)}{degree(n)}$, the
    percentage of edges of each node going into the subset.
    """
    extn = {}
    intn = {}
    buckets = [ [] ]
    
    for n in subset:
        for m in graph.neighbors(n):
            if m not in subset:
                extn[m] = extn.get(m, 0) + 1
            else:
                intn[m] = intn.get(m, 0) + 1
    
    # set up the details of the external, but connected nodes
    exttemp = {}
    exttemp['all'] = []
    exttemp['overhead'] = 3
    exttemp['void'] = ['all', 'overhead', 'void']
    for m, dm in extn.iteritems():
        exttemp[m] = {'e':dm, 'p':dm/float(graph.degree(m)), 'b_id':0}
        exttemp['all'].append((exttemp[m]['p'], exttemp[m]['e']))
        buckets[0].append(m)
        
    extn = exttemp
        
    # set up the details of the internal nodes
    inttemp = {}
    inttemp['all_e'] = []
    inttemp['all_p'] = []
    inttemp['void'] = ['all_e', 'all_p', 'void', 'overhead', 'min_e', 'min_p',
                       'slope']
    inttemp['overhead'] = 4
    for n, dn in intn.iteritems():
        inttemp[n] = {'e':dn,
                      'p':dn/float(graph.degree(n)),
                      'slope':float(graph.degree(n))}
        inttemp['all_e'].append(inttemp[n]['e'])
        inttemp['all_p'].append(inttemp[n]['p'])
        
    intn = inttemp
    update_bounds(intn)
    intn['overhead'] += 3
    
    update_buckets(extn, intn, buckets, copy.copy(buckets[0]))
 
    return extn, intn, buckets
    
    
def update_bounds(intn):
    """ Finds the bounds of what 'e' or 'p' have to be at least to be in C
    
    Method
    ------
    Presumes that all data in intn is meant to stay, uses a line between the
    origin and the (average p, average e), classifies points as above or below
    the line.  If above, the points contribute to what the minimum e must be,
    and if below, points must contribute to what the minimum p must be.
    """
    
    slope = sum(intn['all_e']) / float(sum(intn['all_p']))
    
    mine = len(intn['all_e'])
    minp = 1.
    valid_e = []
    valid_p = []
    
    for n, infon in intn.iteritems():
        if n not in intn['void']:
            if infon['e'] / infon['p'] > slope:
                valid_e.append(infon['e'])
                mine = min(mine, infon['e'])
            else:
                valid_p.append(infon['p'])
                minp = min(minp, infon['p'])
                
    valid_e.sort()
    valid_p.sort()       
            
    intn['min_e'] = max(intn.get('min_e', 0.), valid_e[len(valid_e)/50])
    intn['min_p'] = max(intn.get('min_p', 0.), valid_p[len(valid_p)/50])
    intn['slope'] = slope


def update_trackers(graph, extn, intn, buckets, n):
    """ Adds n into the community and updates all the data structures in place
    Parameters
    ----------
    
    Returns
    -------
    nothing : but changes extn, intn, and buckets to reflect n now in C
    """
    intn[n] = extn.pop(n)
    intn[n]['r'] = []
    intn['all_e'].append(intn[n]['e'])
    intn['all_p'].append(intn[n]['p'])
    changed = []
    
    for m in graph.neighbors(n):
        if m in intn:
            intn['all_e'].remove(intn[m]['e'])
            intn['all_p'].remove(intn[m]['p'])
            intn[m]['e'] += 1
            intn[m]['p'] = intn[m]['e'] / float(graph.degree(m))
            intn['all_e'].append(intn[m]['e'])
            intn['all_p'].append(intn[m]['p'])
            
        else:
            if m in extn:
                extn['all'].remove( (extn[m]['p'], extn[m]['e']) )
            else:
                extn[m] = {'e':0, 'b_id':0}
                buckets[0].append(m)
            
            extn[m]['e'] += 1
            extn[m]['p'] = extn[m]['e'] / float(graph.degree(m))
            extn['all'].append( (extn[m]['p'], extn[m]['e']) )
            changed.append(m)
            
    update_bounds(intn)
    update_buckets(extn, intn, buckets, changed)
    
    
def update_buckets(extn, intn, buckets, changed):
    """ Given that the status of nodes in changed is updated, shuffles the
    buckets.  All operations are done in place.

    Parameters
    ---------
    
    Method
    ------
    Uses the function bucket_id to find the new place for nodes
    """
    
    for n in changed:
        buckets[extn[n]['b_id']].remove(n)
        newb = bucket_id(extn[n], extn, intn)
        extn[n]['b_id'] = newb
        if newb > len(buckets):
            buckets.extend([[] for i in range(len(buckets), newb + 2)])
        buckets[newb].append(n)
            

def bucket_id(spec, extn, intn):
    """ Is an ordered function that finds which bucket spec is in.
    """
        
    return int (spec['e']/intn['min_e'] + 100 * spec['p']/intn['min_p'])
    
    
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
    
    
def check_closure(extn, intn):
    """ Returns the fraction of nodes not already in C that meet the
requirements
    
    Returns
    -------
    The fraction of nodes, qualified but not included.  Is 0 if the community
is closed.
    """
    
    outside = filter(lambda (a,b): a>intn['min_p'] or b>intn['min_e'],
                     extn['all'])
                     
    return len(outside) / float(len(intn) - intn['overhead'])
    
    
def add(extn, intn, m):
    """ Checks whether or not should really add m
    """
    if extn[m]['e'] < 6 and extn[m]['e'] < .2:
        print "reallllly, ", m, extn[m]
    if extn[m]['e'] > intn['min_e'] or extn[m]['e'] > intn['min_p']:
        return True
        
    return False
            
    
    
    
    