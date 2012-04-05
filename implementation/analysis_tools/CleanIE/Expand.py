# -*- coding: utf-8 -*-

import networkx as nx
import Metrics as M


def expand_linearity(partition, G, param):
    """ Expands all communities in the partition to find the best overlapping set of communities

    Parameters
    ---------
    parition : a dictionary for which community each node belongs to
    G : a networkx graph with nodes, edges
    a : a float indicating the weight of I, internal density
    b : a float indicating the weight of E, external density
    c : a float indicating the weight of |S|

    Returns
    -------
    set_c : a dictionary for which communities each node belongs to

    Notes
    ----
    Uses the partition as a basis and expands communities of the basis
    to generate overlapping communities.  Expands these communities
    until a I - b E - c |S| can no longer be increased.

    """
    (a, b, c) = param
    
    c_sizes = {}
    for c in partition.values():
        c_sizes[c] = c_sizes.get(c, 0) + 1

    int_exists = 0. # number of internal edges
    ext_exists = {} # dictionary of external edges
    for n in G.nodes():
        ext_exists[n] = []
        for m in G.neighbors(n):
            if partition[n] == partition[m]: # internal edge
                int_exists += 1.
            else: # external edge
                ext_exists[n].append(m)

    int_ideal = float(sum([ce * (ce - 1) for ce in c_sizes.values()]))
    if int_ideal > 0:
        I = int_exists / int_ideal
    else:
        I = 0.

    for n in partition: # turn partition values into lists to handle more values
        partition[n] = [partition[n]]

    for c in c_sizes: # expand each community, c
        heap = build_heap(c, partition, G)
        mod = True
        if c%10 == 11:
            print "  C: ", c, " of size ", c_sizes[c], " connected to " + \
                    str(len(heap) - 1), " with best of " + \
                    str( heap[min(len(heap)-1, 1)][1] )
        while mod and len(heap) > 1:
            mod = False
            (n, number_e) = heap[1]
            new_int_ideal = int_ideal + 2 * c_sizes[c]
            new_int_exists = int_exists + 2 * number_e

            new_covered = filter(lambda m: c in partition[m], ext_exists[n])
            
            inc_M = a * (new_int_exists / new_int_ideal - I) + \
                    b * len(new_covered) / float(G.number_of_edges())

            if inc_M > 0: # add n into c and update all variables
                #print "Great expanded! ", c, n
                partition[n].append(c)
                int_ideal = new_int_ideal
                int_exists = new_int_exists
                I = int_exists / int_ideal

                for m in new_covered:
                    ext_exists[n].remove(m)
                    ext_exists[m].remove(n)

                c_sizes[c] += 1
                mod = True
            heap = pop(heap)

    return partition


def pop(heap):
    """ Pops the max off the heap and restores the heap
    """

    swap(heap, 1, len(heap) - 1)
    heap = heap[:-1]
    bubble(heap, 1)

    return heap


def build_heap(c, partition, G):
    """Bulids a max heap of nodes connected to the partition s.

    Parameters
    ---------
    c : an int indicating which partition to center on
    parition : a dictionary for which community each node belongs to
    G : the networkx graph representing everything

    Returns
    -------
    heap : a list of tuples in a max heap, where the tuple (m, |e|)
           is a tuple of node m and the number of edges e from m into s

    """

    connected = {}
    
    for n in partition:
        if c in partition[n]:
            for m in G.neighbors(n):
                if c not in partition[m]:
                    connected[m] = connected.get(m, 0) + 1

    heap = [[-1, -1]]
    heap.extend([(m, w) for m, w in connected.iteritems()])
    heapify(heap, 1, len(heap)/2 + 1)

    return heap


def heapify(heap, start, stop):
    """Converts a list of (key, value) pairs into a heap.

    Parameters
    ---------
    heap : a list of tuples, where the tuples are (key, value)
    start : the index to start
    stop : the index to stop

    Returns
    -------
    in place organizes heap into a max heap on values

    """
    for i in range(stop, start-1, -1):
        bubble(heap, i)


def bubble(heap, i):
    """If in the subheap anchored at i the only element that could
    be out of place is i, bubble properly bubbles the ith element
    down until the subheap at i is a max heap.
    """
    p_v = get_value(heap, i)
    ch1_v = get_value(heap, 2 * i)
    ch2_v = get_value(heap, 2 * i + 1)

    if p_v < ch1_v or p_v < ch2_v:
        if ch1_v > ch2_v:
            swap(heap, 2 * i, i)
            bubble(heap, 2 * i)
        else:
            swap(heap, 2 * i + 1, i)
            bubble(heap, 2 * i + 1)

def swap(heap, top, bottom):
    """Swap, switches the elements at top and bottom
    """
    temp = heap[bottom]
    heap[bottom] = heap[top]
    heap[top] = temp


def get_value(heap, i):
    """Returns the value of the (key, value) pair in the heap at i.
    Returns None, if i is not in the heap
    """

    v = None
    if i < len(heap):
        v = heap[i][1]

    return v
