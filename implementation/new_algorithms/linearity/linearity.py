# -*- coding: utf-8 -*-


def linearity(graph, a, b, c):
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
    dendo = create_dendogram(graph.copy(), __A, __B, __C)
    
    # traces the final community by marching through the dendo's heirarchy
    partition = dendo[0].copy()
    for level in range(1, len(dendo)) :
        for n in partition:
            partition[n] = dendo[level][partition[n]]
            
    return partition
    
    
def create_dendogram(graph, __A, __B, __C):
    """ Creates the dendogram according to the paper
    """
    nedges = graph.number_of_edges()
    
    bar = Bar(graph, nedges, __A, __B, __C)
    
    dendo = [bar.nodes_to_bottles()]
    print 'Did dendo:', dendo
    
    changed = True
    lin = bar.lin_metric()
    
    while changed:
        changed = False
        
        __shell_game(graph, bar)
        
        newlin = bar.lin_metric()
        
        if newlin > lin:
            changed = True
            lin = newlin
            
            dendo.append(bar.nodes_to_bottles())
            newgraph = compress_graph(graph, bar)
            del(bar) # may have to provide a deconstructor
            del(graph)
            graph = newgraph
            bar = Bar(graph, nedges, __A, __B, __C)
            
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
    newgraph.add_nodes_from(set(compression.values()))
    
    for n in graph:
        for m in graph.neighbors(n):
            if n >= m:
                newn = compression[n]
                newm = compression[m]
                weight = graph[n][m]['weight'] \
                         + newgraph[newn].get(newm, {'weight':0.})['weight']
                newgraph.add_edge(newn, newm, {'weight': weight})

    return newgraph
    
   
def __shell_game(graph, bar):
    """ Moves all the nodes of graph around until no improvements can be made
    """
    changed = True
    lin = bar.lin_metric()
    
    while changed:
        changed = False
        
        for n in graph.nodes():
            bhome = bar.bottle_containing(n)
            bneighbors = bar.bottle_neighbors(n)
            
            bestneighbor = bhome
            bestimprovement = 0.
            
            for b in bneighbors:
                improvement = bar.test_swap(graph, n, bhome, b)
                
                if improvement > bestimprovement:
                    bestneighbor = b
                    bestimprovement = improvement
                    
            bar.swap(graph, n, bhome, bestneighbor)
                
        newlin = bar.lin_metric()
        if newlin > lin:
            changed = True
            lin = newlin

