
from constants import *

import networkx as nx

def football_known_c():
    """ Returns the set of known football communities
    """
    try:
        known_fgraph = nx.read_gml(DATA_PATH_1 + "FootballGames/football.gml")
    except:
        known_fgraph = nx.read_gml(DATA_PATH_2 + "FootballGames/football.gml") 
    
    sets = {}
    conferences = nx.get_node_attributes(known_fgraph, 'value')    
    for n in known_fgraph.nodes():
        if conferences[n] not in sets:
            sets[conferences[n]] = set()
            
        sets[conferences[n]].update([n+1])
    
    return sets.values()

def karate_known_c():
    """ Returns the two known sets of 
    """
    sets = [set([27,16, 30, 21, 19, 24, 26, 28, 25, 32, 29, 33, 34, 15, 23, 10, 31, 9])]
    sets.append(set([3, 14, 20, 4, 2, 1, 8, 22, 18, 12,13, 5, 6, 7, 11, 17]))
    return sets

"""
# if it was recorded nicely
known_kgraph = nx.read_gml('../data/KarateClub/karate.gml')
sets = {}
for n in known_kgraph.nodes():
    split = nx.get_node_attributes(known_kgraph, 'value')
    if split not in sets:
        sets[split] = set()
        
    sets[split].update([n])

return sets.values()
"""