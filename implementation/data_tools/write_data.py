# -*- coding: utf-8 -*-


def write_edges(graph, path, prefix):
    """ Write a networkx graph to a file.
    Does it simply without carrying over edge weights or node sizes
    """
    
    output = open(path, 'wb')
    output.write(prefix)
    
    for (n, m) in graph.edges():
        output.write(str(n)+'\t'+str(m)+'\n')
        
    output.close()
    
    
def write_graph(graph, path, prefix):
    """ Stores the entire graph structure in a pickle file.
    """
    pf = open(path, 'wb')
    
    pickle.dump((prefix, graph), pf)
    
    pf.close()
    
    
def write_detailed(graph, path, prefix):
    """Write a detailed account
    """
    output = open(path, 'wb')
    
    output.write(prefix)
    
    output.write("# Node properties formatted as 'node\tproperties\n' ")
    for n in graph.nodes():
        output.write(str(n) + '\t' + graph.node[n] + '\n')
        
    output.write("# Edge properties formatted as 'node\tnode\tproperties\n'")
    for n,m in graph.edges():
        output.write(str(n) + '\t' + str(m) + '\t' + graph[n][m] + '\n')
        
    output.close()