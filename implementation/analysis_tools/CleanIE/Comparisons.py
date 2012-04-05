# -*- coding: utf-8 -*-

import numpy as np

def compare_partitions(part_1, part_2):
    """Given two lists of sets, computes the similarity matrix
    """
    part_1 = filter(lambda s: len(s)>5, part_1)
    part_2 = filter(lambda s: len(s)>5, part_2)
    similarity = np.zeros( (len(part_1), len(part_2)) )
    for i in range(len(part_1)):
        for j in range(len(part_2)):
            similarity[i][j] = overlap(part_1[i], part_2[j])
            
    max_part_1 = np.zeros(len(part_1))
    for i in range(len(part_1)):
        max_part_1[i] = max(similarity[i][:])
        
    max_part_2 = np.zeros(len(part_2))
    for j in range(len(part_2)):
        max_part_2[j] = max([v[j] for v in similarity])
        
    return similarity, max_part_1, part_1, max_part_2, part_2
            
            
def overlap(set_1, set_2):
    set_1 = set(set_1)
    set_2 = set(set_2)
    
    return 2*len(set_1.intersection(set_2))/float(len(set_1) + len(set_2))