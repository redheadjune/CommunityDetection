# -*- coding: utf-8 -*-

import networkx as nx

def karate_club():
    interactions_file = open('Data/karate_club_edges.txt', 'rb')
    
    return load_graph(interactions_file)
    
def football():
    games = open('Data/football_games.txt', 'rb')
    
    return load_graph(games)

    
def load_graph(interactions_file):
    nodes = set()
    edges = []
    for line in interactions_file:
        if line != '\\n' and line[0] != '#':
            (n, end) = line.split(' ')
            m = end[:-1]
            n = int(n)
            m = int(m)
            nodes.update([n, m])
            edges.append((n, m))

    interactions_file.close()
    
    k_graph = nx.Graph()
    k_graph.add_nodes_from(nodes)
    k_graph.add_edges_from(edges)
    
    return k_graph