

import CommunityDetection as CD
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pickle

def gen_overlap_fig(communities, xticks, yticks, labels, name, colors):
    """ Generates a histogram to represent the number of communities each node
    belongs to.
    Parameters
    ----------
    xticks : the xticks to use
    yticks:
    labels : a list of labels
    name : the name to store everything under
    colors : list of colors to use
    """
    belongs = []
    for c_set in communities:
        overlap = {}
        for c in c_set:
            for n in c:
                overlap[n] = overlap.get(n, 0) + 1
                
        belongs.append(overlap.values())
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    bins = ax.hist(belongs,
                   40,
                   color=colors,
                   label=labels)
    ax.legend()
    ax.set_title('Communities a Node belongs to.', fontsize=24)
    ax.set_ylabel('Number of Nodes', fontsize=24)
    ax.set_xlabel('Number of Communities', fontsize=24)
    ax.set_xlim([0, max([max(b) for b in belongs])])
    ax.set_ylim([0, max(yticks)])
    plt.xticks(xticks, xticks)
    plt.yticks(yticks, yticks)
    plt.show()
    plt.savefig(name + '_n_communities.eps')
    plt.savefig(name + '_n_communities.pdf')    


def gen_csize_fig(xticks, yticks, data, labels, name, colors):
    """ Generates the histograms for the size of communities
    Parameters
    ----------
    xticks : the xticks to use
    yticks:
    data : an array of arrays
    labels : a list of labels
    name : the name to store everything under
    colors : list of colors to use
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    bins = ax.hist(data,
                   30,
                   color=colors,
                   label=labels,
                   normed=True)
    ax.legend()
    ax.set_title('Community Sizes', fontsize=24)
    ax.set_ylabel('Number of Communities', fontsize=24)
    ax.set_xlabel('Community Size', fontsize=24)
    ax.set_xlim(0, max(xticks))
    ax.set_ylim(0, max(yticks))
    plt.xticks(xticks, xticks)
    plt.yticks([], [])
    plt.show()
    plt.savefig(name + '_csize.eps')
    plt.savefig(name + '_csize.pdf')
    
    
def gen_paper_fig_ch5():
    """ Generates the
    """
    find_karate_communities()
    find_football_communities()
    r_communities = gen_relativity_analysis()
    
    
def gen_relativity_analysis():
    """ Generates all figures in ch5 for the relativity coauthor network
    To get subcommunities, uncomment code in vis_coauthoer_communities
    """
    rgraph = CD.coauthor_relativity()
    rparam = [1., 5., 5./2694., 3, 10, .8, 200]
    rpath = "CommunityDetection/implementation/data/CollaborationNetworks/" +\
             "metis/relativity_metis"
    roptions = CD.all_detection_methods(rgraph,
                                        param=rparam,
                                        path=rpath)  
    
    keys = ['Modularity Communities', 'Linearity Communities',
            'Parallel Communities', 'Modularity Communities',
            'Modularity Communities']
    c_id = [24, 108, 319, 10, 3]
    
    for i in []: #range(len(c_id)):
        vis_coauthor_communities(rgraph,
                                  keys[i],
                                  c_id[i],
                                  'relativity_' + str(c_id[i]) + '_',
                                  roptions,
                                  0,
                                  .75)
                              
    gen_csize_fig([0, 100, 200],
                  [0, .05, .1],
                  [[len(c) for c in roptions[key]]
                   for key in ['Linearity Communities',
                               'Parallel Communities',
                               'Metis Communities',
                               'Modularity Communities']],
                   ['Linearity', 'Parallel', 'Metis', 'Modularity'],
                   'relativity_',
                   ['r', 'k', 'b', 'g'])
    
    gen_overlap_fig([roptions['Linearity Communities'],
                     roptions['Parallel Communities']],
                    [0, 15],
                    [0, 200],
                    ['Linear', 'Parallel'],
                    'relativity_linear_parallel',
                    ['r', 'k'])
    return roptions


def gen_cond_analysis():
    """ Generates all figures for the condensed matter network
    """
    cgraph = CD.coauthor_cond()
    cparam = [1., 1., 5./16966., 4, 10, .8, 300]
    cpath = "CommunityDetection/implementation/data/CollaborationNetworks/" +\
             "metis/condensed_metis"
    coptions = CD.all_detection_methods(cgraph, param=cparam, path=cpath)

    gen_csize_fig([0, 40, 80],
                  [0, .03],
                  [[len(c) for c in coptions[key]]
                   for key in ['Linearity Communities',
                               'Parallel Communities',
                               'Modularity Communities',
                               'Metis Communities']],
                   ['Linearity', 'Parallel', 'Modularity', 'Metis'],
                   'cond_',
                   ['r', 'k', 'b', 'g'])
    
    gen_overlap_fig([coptions['Linearity Communities'],
                     coptions['Parallel Communities']],
                    [0, 15, 20],
                    [0, 250, 500],
                    ['Linear', 'Parallel'],
                    'cond_linear_parallel',
                    ['r', 'k'])    
    return coptions


def gen_archivex():
    """ Generates the plots corresponding to the physics archivx
    """
    pgraph = CD.physics_citations()
    pparam_big = [0., 0., 1/30000., 5, 200, .8, 900]
    ppath = "CommunityDetection/implementation/data/" +\
             "PhysicsArchive/archivx_metis"
    poptions_big = CD.all_detection_methods(pgraph, pparam_big, ppath)
    
    pf = open('big_c_physics_2', 'wb')
    pickle.dump(poptions_big, pf)
    pf.close()
    """
    pparam_small = [0., 0., 1/30000., 3, 20, .8, 100] 
    poptions_small = CD.all_detection_methods(pgraph, pparam_small, ppath)
    
    pf = open('small_c_physics', 'wb')
    pickle.dump(poptions_small, pf)
    pf.close()    
    
    gen_csize_fig([0, 40, 80],
                  [0, .03],
                  [[len(c) for c in poptions[key]]
                   for key in ['Linearity Communities',
                               'Parallel Communities',
                               'Modularity Communities',
                               'Metis Communities']],
                   ['Linearity', 'Parallel', 'Modularity', 'Metis'],
                   'archivx_',
                   ['r', 'k', 'b', 'g'])
    gen_overlap_fig([poptions['Linearity Communities'],
                     poptions['Parallel Communities']],
                    [0, 15, 20],
                    [0, 250, 500],
                    ['Linear', 'Parallel'],
                    'archivex_linear_parallel',
                    ['r', 'k'])    
    """
    
    return poptions_big #, poptions_small
    

def vis_coauthor_communities(graph, source, i, prefix, options, radius, overlap):
    """ Finds the communities produced by different methods for the astro
    citation network
    """    
    interest = CD.get_ball(graph, options[source][i], radius)
    print "Displaying and computing for a subset of ", len(interest), " nodes."
    sgraph = nx.subgraph(graph, interest)
    
    cleaned = {}
    for key in options.keys():
        """ for generating sub community structure
        """
        if key == source:
            # split the overarching with the substructure
            cleaned[source] = [options[source][i]]
            options['Parallel Subcommunities'] = options[source][:i]
            options['Parallel Subcommunities'].extend(options[source][i+1:])
            key = 'Parallel Subcommunities'
        
        filtered = [filter(lambda n: n in interest, c) for c in options[key]]
        filtered = filter(lambda c: len(c) > 0, filtered)
        cleaned[key] = filtered
        cleaned[key] = CD.clean_of_duplicate_c(cleaned[key], overlap=overlap)

    compare_methods(sgraph, prefix, options=cleaned)
    
    
def find_dolphin_communities():
    """ Finds the communities produced by different methods for dolphins
    """
    dgraph = CD.dolphins()
    compare_methods(dgraph,
                    'dolphins_',
                    param=[1., 5., 3.5/62., 3, 0, .55, 62],
                    data_path="Dolphins/dolphins")
    

def find_karate_communities():
    """ Finds the communities produced by different methods
    Uses compare to plot.
    """
    kgraph = CD.karate_club_graph()
    known = CD.karate_known_c()
    compare_methods(kgraph,
                    'karate_',
                    param=[1., 5., 3.5/34., 3, 0, .55, 34],
                    known=known, 
                    color_map={27:0, 1:2, 17:3, 25:4},
                    data_path="KarateClub/karate_metis")
    
    
def why_parallel_karate():
    """ A plot to explain why the parallel method does not work well on small
    graphs
    
    Could use with some mods
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
    """ Finds the communities produced for the football network, uses compare
    methods to graph
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
    
    compare_methods(fgraph,
                    'football_',
                    param=[1., 1., 5./115., 4, 0, .7, 20],
                    known=known,
                    pos=pos,
                    color_map={76:1, 11:2, 7:3, 102:4, 104:5, 47:6, 98:7,
                               96:8, 23:9, 94:10, 27:0},
                    data_path="FootballGames/football_metis")
    
    
def compare_methods(graph, prefix, param=None, known=None, pos=None,
                    color_map={}, options=None, data_path=None):
    """ Given the graph compares all detection methods
    Parameter
    ---------
    graph : a networkx graph
    param : the parameters of [a, b, c, min_seed_size]
    prefix : the filename to save variations with
    known : a list of communities if known
    pos : a dictionary of node positions for graphing
    color_map : a dictionary of node colors
    options : if the communities have already been computed input here
    data_path : the path within the data folder to store metis output
    
    Notes
    -----
    Presumes this code is run from the parent directory of CommunityDetection
    """
    if options == None:
        path = "CommunityDetection/implementation/data/" + data_path
        options = CD.all_detection_methods(graph, param=param, path=path)
        
    if known != None:
        options['Known Communities'] = known
    
    color = ['#00FF00', '#00FFFF', '#FF1493', '#FFFF00', '#8A2BE2', '#FF7F50',
             '#FF00FF', '#F08080', '#BA55D3', '#00FA9A', '#A0522D',
             '#D2B48C', '#8B0000', 'b']

    def get_color(store, communities, overlap=[]):
        offset = 1
        for c in communities:
            c_name = None
            for n in c:
                if n in color_map:
                    c_name = color_map[n]
                    
            if c_name == None:
                c_name = (len(color_map) + offset) % len(color)
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
        
        
    # mark nodes not in communities
    for n in graph.nodes():
        for key in options:
            if n not in options[key]:
                options[key][n] = 'k'
        
    if pos == None:
        pos = nx.spring_layout(graph)
        
    nodes = graph.nodes()   
    key_label = {'Known Communities':'known',
                 'Modularity Communities':'module',
                 'Linearity Communities':'linear',
                 'Parallel Communities':'parallel',
                 'Metis Communities':'metis',
                 'Parallel Subcommunities':'subparallel'}
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
        plt.savefig(prefix + key_label[key] + '.eps')
        plt.savefig(prefix + key_label[key] + '.pdf')
        