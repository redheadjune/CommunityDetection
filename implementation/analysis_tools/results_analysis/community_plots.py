

import CommunityDetection as CD
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def find_karate_communities():
    """ Finds the communities produced by different methods
    """
    kgraph = CD.karate_club_graph()
    known = CD.karate_known_c()
    compare_methods(kgraph, param=[1., 5., 3.5/34., 3], known=known)
    
    
def why_parallel_karate():
    """ A plot to explain why the parallel method does not work well on small
    graphs
    """
    graph = CD.karate_club_graph()
    known = CD.karate_known_c()  
  
    communities = []
    candidates = []
  
    for c in known:
        comm = CD.Community()
        ext_nodes = comm.init(graph, c)
        cand = CD.Candidates(graph, ext_nodes, comm)
        comm.init_bounds(cand)
        cand.rework_fringe()
        communities.append(comm)
        candidates.append(cand)
        
    for c, cand in zip(communities, candidates):
        CD.vis_e_p(graph, c, cand)    
    
    
def find_football_communities():
    """ Finds the communities produced for the football network
    """
    fgraph = CD.football_graph()
    known = CD.football_known_c()
    temp7 = known[7]
    temp8 = known[8]
    temp9 = known[9]
    known[7] = temp8
    known[8] = temp9
    known[9] = temp7

    center_g = nx.Graph()
    center_g.add_nodes_from(range(12))
    centers = nx.circular_layout(center_g, scale = 10)
            
    pos = {}
    subgraphs = [nx.subgraph(fgraph, c) for c in known]
    count = -1
    for g in subgraphs:
        count += 1
        (off_x, off_y) = centers[count]
        pos_local = nx.circular_layout(g, scale=2.)
        for n, place in pos_local.iteritems():
            pos[n] = place + np.array([off_x, off_y])
    
    compare_methods(fgraph, param=[1., 1., 5./115., 4], known=known, pos=pos)
    
    
def compare_methods(graph, param, known=None, pos=None):
    """ Given the graph compares all detection methods
    Parameter
    ---------
    graph : a networkx graph
    param : the parameters of [a, b, c, min_seed_size]
    known : a list of communities if known
    
    BUGS
    ----
    solve overlapping
    """
    
    options = CD.all_detection_methods(graph, param=param)
    
    print "Found a bunch of communities: "
    print [(k, len(options[k])) for k in options]
    
    # manipulations to options for the figures
    # add in known
    if known != None:
        options['Known Communities'] = known
      
    # switch order linear communities to correspond to other colors for karate
    #options['Linearity Communities'] = [options['Linearity Communities'][1],
    #                                    options['Linearity Communities'][0]]
    #order_lin = [1, 0] # for karate
    color_map = {76:1, 11:2, 7:3, 102:4, 104:5, 47:6, 98:7, 96:8,23:9,
                 94:10, 27:0}
    
    color = ['#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#008B8B', '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#A0522D',
             '#D2B48C', '#8B0000',
             'b',
             '#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#008B8B', '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#DA70D6',
             '#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#008B8B', '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#DA70D6',
             '#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#008B8B', '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#DA70D6',]

    def get_color(store, communities, overlap=[]):
        offset = 0
        for c in communities:
            c_name = None
            for n in c:
                if n in color_map:
                    c_name = color_map[n]
                    
            if c_name == None:
                c_name = len(color_map) + offset
                offset += 1
            
            for n in c:
                if n in overlap:
                    store[n] = '#5F9EA0'
                else:
                    store[n] = color[c_name]
        return store
    
    # map the nodes to their community color
    for key in options.keys():
        overlap = []
        if key == 'Linearity Communities' or key == 'Parallel Communities':
            counts = {}
            for c in options[key]:
                for n in c:
                    counts[n] = counts.get(n, 0) + 1
                    
            overlap = filter(lambda n: counts[n] > 1, counts.keys())
            
        options[key] = get_color({}, options[key], overlap=overlap)
        
        
    # mark nodes not in communities for Parallel Communities 
    for n in graph.nodes():
        if n not in options['Parallel Communities']:
            options['Parallel Communities'][n] = 'k'        
        
    if pos == None:
        pos = nx.spring_layout(graph)
        
    nodes = graph.nodes()        
    for key, colors in options.iteritems():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        nx.draw(graph,
                pos=pos,
                node_color=[colors[n] for n in nodes],
                node_size=200,
                alpha=1.,
                with_labels=False,
                width=.5,
                edge_color='#5F9EA0')
        ax.set_title(key, fontsize=28)
        plt.show()
        plt.savefig(key + '.eps')
        plt.savefig(key + '.pdf')
        