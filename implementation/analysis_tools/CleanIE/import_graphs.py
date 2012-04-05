# -*- coding: utf-8 -*-


import networkx as nx


def createGraph(g_file):
    
    dict_graph = loadGraph(g_file)
    
    nx_graph = nx.Graph()
    
    nx_graph.add_nodes_from(dict_graph.keys())
    
    for n1 in dict_graph.keys():
        nx_graph.add_edges_from([(n1, n2) for n2 in dict_graph[n1]])
        
    return nx_graph
    
    
# structure graphs as a dictionary of sets
def loadGraph(data_file):

    graph = {}

    pf = open(data_file)
    
    for line in pf:
        if line[0] != '#':
            [n1, n2] = line[:-1].split('\t')
            addEdge(int(n1), int(n2), graph)
    return graph
    
    
            
def addEdge(n1, n2, graph):

    addNode(n1, graph)
    addNode(n2, graph)
    
    graph[n1].update([n2])
    graph[n2].update([n1])

            
def addNode(n, graph):
    if n not in graph:
        graph[n] = set()
      