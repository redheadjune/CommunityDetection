# -*- coding: utf-8 -*-

import CommunityDetection as CD
import matplotlib.pyplot as plt


def plot_dendo(dendo, graph):
    
    colors = ['r', 'g', 'b', 'k', 'c', 'm']
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    groups = CD.dendo_to_hierarchy(dendo)
    
    for i in range(len(groups)-1):
        plot_set(ax, graph, groups[i].values(), colors[i])
        
    plt.show()


def plot_set(ax, graph, group, color):
    
    # find the I,E values of all the members of the group
    
    I_values = []
    E_values = []
    for c in group:
        I, E, rubish = CD.measure_community(c,
                                           graph, 
                                           'linearity',
                                           param=(1., 1.))
        E_values.append(E)
        I_values.append(I)
        
    ax.plot(I_values, E_values, color+'o')