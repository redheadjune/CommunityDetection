# -*- coding: utf-8 -*-


def distribution(part, subset):
    """Given a known partition, finds the distribution of where subset falls
    Parameters
    ---------
    part : a dictionary representing a partition
    subset : a subset of nodes
    
    Returns:
    -------
    dist : a dictionary racking up where subset nodes fall in the partition
    """
    dist = {}
    
    for n in subset:
        dist[part[n]] = dist.get(part[n], 0) + 1
        
    return dist