
import networkx as nx
"""Metrics
"""

def m_internal_density(graph, c):
    """ Returns the internal density of c, as described in the paper
    """
    subgraph = graph.subgraph(c)
    possible = 0.5 * subgraph.number_of_nodes() * (subgraph.number_of_nodes() - 1)
    return subgraph.number_of_edges() / possible
    
    
def m_external_density(graph, c):
    """ Returns the external density of c, as described in the paper
    """
    exists = 0.0
    for n in c:
        for m in graph.neighbors(n):
            if m not in c:
                exists += 1.0
    
    possible = float(len(c) * graph.number_of_nodes())
    return exists / possible


def m_conductance(graph, c):
    """ Returns the conductance of c
    """
    ic = m_internal_density(graph, c)
    ec = m_external_density(graph, c)
    k = len(c) / float(graph.number_of_nodes())
    return (1 - k) * ec / float(k * ic + (1 - k) * ec)


def m_cut_ratio(graph, c):
    """ Computes the cut ratio
    """
    ic = m_internal_density(graph, c)
    ec = m_external_density(graph, c)
    k = len(c) / float(graph.number_of_nodes())
    return k * (1 - k) * graph.number_of_nodes()**2 * ec


def m_edge_cuts(graph, c):
    """
    """
    return m_external_density(graph, c)


def m_expansion(graph, c):
    """
    """
    ic = m_internal_density(graph, c)
    ec = m_external_density(graph, c)
    k = len(c) / float(graph.number_of_nodes())    
    return (1 - k) * graph.number_of_nodes() * ec


def m_previous_internal_density(graph, c):
    """ Returns the internal density metric in use before the paper
    """
    return 1 - m_internal_density(graph, c)


def m_volume(graph, c):
    """ Returns the volume of c
    """
    ic = m_internal_density(graph, c)
    ec = m_external_density(graph, c)
    k = len(c) / float(graph.number_of_nodes())
    return len(c)**2 * ic + (1 - k) * len(c) * graph.number_of_nodes() * ec

    
    