# -*- coding: utf-8 -*-


import networkx as nx

from arrangement import Bar

def linearity_run(graph, __A, __B, __C):
    """Computes the best linearity based metric for partitioning the graph.
    Parameters
    ---------
    graph : a networkx graph
    a : the constant weighting of I(C)
    b : the constant weighting of E(C)
    c : the constant weighting of |S|
    
    Returns
    -------
    parition : a dictionary of which nodes belong to which community
    
    Method
    ------
    Adapts the Louvain algorithm to create a partition.
    
    It is recommended to run this with the expansion
    """
    
    # create the dendogram
    dendo = create_dendogram_linear(graph.copy(), __A, __B, __C)
    
    # traces the final community by marching through the dendo's heirarchy
    partition = dendo[0].copy()
    for level in range(1, len(dendo)) :
        for n in partition:
            partition[n] = dendo[level][partition[n]]
            
    return partition
    
    
def create_dendogram_linear(graph, __A, __B, __C):
    """ Creates the dendogram according to the paper
    """
    delta = __B / 100.
    temp_b = delta
    nedges = 2. * graph.number_of_edges()
    
    bar = Bar(graph, nedges, __A, __B, __C)
    
    dendo = [bar.nodes_to_bottles()]
    
    lin = bar.lin_metric()
    
    # This if for starting from maximal cliques
    clique_game(graph, bar)
    dendo.append(bar.nodes_to_bottles())
    new_graph = compress_graph(graph, bar)
    del(bar)
    del(graph)
    graph = new_graph
    bar = Bar(graph, nedges, __A, temp_b, __C)
    
    changed = True    
    while changed and temp_b <= __B:
        changed = False
        
        shell_game(graph, bar)
        newlin = bar.lin_metric()
        
        if newlin > lin:
            changed = True
            lin = newlin
            
            dendo.append(bar.nodes_to_bottles())
            new_graph = compress_graph(graph, bar)
            del(bar)
            del(graph)
            graph = new_graph
            bar = Bar(graph, nedges, __A, temp_b, __C)
        else:
            temp_b += delta
            changed = True
            
    return dendo
    
    
def compress_graph(graph, bar):
    """Using the bar as a set of buckets compresses the graph.
    Parameters
    ----------
    graph : a networkx graph
    bar : a Bar object
    
    Returns
    -------
    newgraph : a networkx graph, where the graph has been correspondingly
               compressed.  Ie, if nodes 1, 2, 3, are in bottle 1, then the new
               graph has a node of (1, 2, 3) and the compressed edges, with
               possible self-loops, the weight of the edges is how many edges
               the new edge represents.
    """
    compression = bar.nodes_to_bottles()
    newgraph = nx.Graph()
    newgraph.add_nodes_from(set(compression.values()), size=0.)
    
    for n in graph:
        newn = compression[n]
        newgraph.node[newn]['size'] += graph.node[n]['size']
        for m in graph.neighbors(n):
            if n >= m:
                newm = compression[m]
                weight = graph[n][m]['weight'] \
                         + newgraph[newn].get(newm, {'weight':0.})['weight']
                newgraph.add_edge(newn, newm, {'weight': weight})

    return newgraph
    
   
def shell_game(graph, bar):
    """ Moves all the nodes of graph around until no improvements can be made
    """
    changed = True
    lin = bar.lin_metric()
    
    while changed:
        changed = False
        
        for n in graph.nodes():
            bhome = bar.bottle_containing(n)
            
            bestneighbor = bar.shift(graph, n)
            if bhome != bestneighbor:
                bar.swap(graph, n, bhome, bestneighbor)
                
        newlin = bar.lin_metric()
        if newlin > lin:
            changed = True
            lin = newlin
            
            
def clique_game(graph, bar):
    """ Moves the nodes of the graph into maximal cliques
    """
    gen_cliques = nx.find_cliques(graph)
    cliques = [c for c in gen_cliques]
    cliques.sort(key=lambda c: len(c), reverse=True)
    compressed = set()
    
    for c in cliques:
        if len(c) > 2 and len(set(c).intersection(compressed)) == 0:
            compressed.update(c)
            for n in c[1:]:
                bhome = bar.bottle_containing(n)
                bestneighbor = bar.bottle_containing(c[0])
                bar.swap(graph, n, bhome, bestneighbor)