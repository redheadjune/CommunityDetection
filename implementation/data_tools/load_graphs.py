# -*- coding: utf-8 -*-


    
def football_graph():
    """loads networkx graph of which college football teams played
    """
    return load_graph(FOOTBALL)
    
    
def karate_club_graph():
    """loads networkx graph of which Karate Club members lunched
    """
    return load_graph(KARATE)
    
    
def physics_citations():
    """loads networkx graph of which papers cited which papers
    """
    return load_graph(PHYSICS_CITATIONS)


def load_graph(path):
    """creates a networkx graph for a given data set
    Parameters
    ----------
    """
    gfile = open(path, 'rb')
    
    nodes = set()
    edges = []
    
    for line in gfile:
        if line != '\\n' and line[0] != '#':
            (n, end) = line.split(' ')
            m = end[:-1]
            n = int(n)
            m = int(m)
            nodes.update([n, m])
            edges.append((n, m))

    g_file.close()
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    return graph