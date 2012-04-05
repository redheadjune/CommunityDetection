# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
from math import pi
import matplotlib.pyplot as plt
import IEPaths as IEP

def paper_karate(graph, seed):
    """Plots the progression of metrics in the IE plane
    Parameters
    ----------
    graph : a networkx graph, try graphs from scripts and Load_Data
    seed : a set, and subset of nodes of graph
    
    Produces
    --------
    a graph of the greedy algorithmic progression of cut_ratio, volume,
    and conductance as metrics through the IE space
    
    Note
    ----
    currently optimized for the karate club with seed [34, 32]
    """
    colors = ['b', 'g', 'r']
    measures = [cut_ratio, volume, conductance]
    compare = [cut_ratio_compare, volume_compare, conductance_compare]
    names = ['Cut Ratio', 'Volume', 'Conductance']
    
    fig = plt.figure(); ax = fig.add_subplot(111)
    
    for i in range(3):
        (I_path, E_path, sets_c) = IEP.path_I_E(graph,
                                                seed.copy(),
                                                measures[i],
                                                compare[i],
                                                [1., 2.])
        plot_path(I_path, E_path, ax, colors[i], names[i])
        
    ax.plot(1, 0, 'kD', label='Ideal', markersize=10)
    ax.plot(0.14, 0, 'mD', label='Entire Graph', markersize=10)
        
    ax.set_xticks([0, .3, .7, 1], ['0', '0.3', '0.7', '1'])
    ax.set_yticks([0, .3], ['0', '0.3'])
    
    ax.set_xlabel(r'$I(C)$', fontsize=24)
    ax.set_ylabel(r'$E(C)$', fontsize=24)
    ax.set_title(r'Course of Metric Improvements', fontsize=24)
    
    ax.set_xlim(-.0, 1.05)
    ax.set_ylim(-.05, .55)
    
    handles, labels = ax.get_legend_handles_labels()
    
    m_handles = [handles[2], handles[0], handles[1]]
    m_labels = [labels[2], labels[0], labels[1]]
    
    f_handles = [handles[4], handles[3]]
    f_labels = [labels[4], labels[3]]
   
    ax.legend(f_handles, f_labels, loc=1)
    plt.show()
    ax.legend(m_handles, m_labels, loc=2)
    plt.show()
                                 
                                 
                                    
def plot_path(I_path, E_path, ax, color, name):
    """In ax plots with arrows and dots the path of IE
    """
    eps = 0.01
    
    for i in range(len(I_path) - 1): # plot arrow
        dx = (I_path[i+1] - I_path[i])
        dy = (E_path[i+1] - E_path[i])
        length = float( ( dx**2 + dy**2 )**.5 )
        theta = np.arcsin(np.abs(dy) / length)
        if dx > 0:
            if dy < 0:
                theta = 2 * pi - theta
        else:
            if dy > 0:
                theta = pi - theta
            else:
                theta = pi + theta
                
        length = max(0., length - 0.032)
            
        dx = length * np.cos(theta)
        dy = length * np.sin(theta)
            
        ax.arrow( I_path[i],
                   E_path[i], 
                   dx,
                   dy,
                   width=0.001,
                   color=color,
                   head_width=0.01)
                   
    for i in range(len(I_path)): # plot point
        ax.plot(I_path, E_path, color+'o', linewidth=4,)
    ax.plot(I_path[0], E_path[0], color+'o', linewidth=4,label=name)
       
    