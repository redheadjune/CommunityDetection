# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from pylab import text

import matplotlib.pyplot as plt


def PlotModularityConstant(I, E, mag_V, L, plt):
    
    for i in range(len(I)):
        count = 5000.0
        max_c = 0
        while I[i]/2.0*max_c**2 + E[i]*max_c*(mag_V - max_c) < L and \
               max_c < mag_V:
            max_c += 10
        da = max_c/float(mag_V)/count
        a = [k*da for k in range(int(count)+1)]
        
        p = [(ai*mag_V)**2/2.0/L for ai in a]
        q = [ai*(1-ai)*mag_V**2/2.0/L for ai in a]
        
        MC = [p[j]*I[i] - (p[j]*I[i]/2.0 + q[j]*E[i])**2 
              for j in range(int(count) + 1)]
        
        if I[i] == .002:
            offset = .4
        else:
            offset = .025
        text( a[-1] - offset, MC[-1]-.025,
              r'$(I,E)=('+str(I[i])+','+str(E[i])+')$',
                fontsize=20, bbox=dict(alpha=1, facecolor='white'))
        cutoff = len(filter(lambda x: x>0, MC))
        plt.plot(a[:cutoff], MC[:cutoff], 'g-')
        plt.plot(a[cutoff:], MC[cutoff:], 'r-')
    plt.xlim([0, 1])
    plt.ylim([-.2, .8])
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1.0])
    plt.yticks([-0.15, 0, .3, .7], [-.15, 0, 0.3, .7])
    plt.xlabel(r'$a$', fontsize=24)
    plt.ylabel(r'Modularity', fontsize=24)
    plt.title(r"$a$'s Influence on Modularity", fontsize=24)
    
    
# plot the modularity level sets
def PlotModularity(limits, plt, ax, n_LS, mag_C, mag_V, L):
    
    [b0, b1, a0, a1] = limits
    
    p = mag_C*(mag_C-1)/2.0/L
    q = mag_C*(mag_V - mag_C)/2.0/L
    corners = [ p*b0 - (p/2.0*b0 + q*a1)**2, 
                p*b1 - (p/2.0*b1 + q*a1)**2, 
                p*b0 - (p/2.0*b0 + q*a0)**2,
                p*b1 - (p/2.0*b1 + q*a0)**2 ]
    
    L_min = min(corners)
    L_max = max(corners)
    
    print 'min level set, ', L_min, 'max level set for modularity, ', L_max
    
    def f(x, Ls, mag_C, mag_V):
        return (np.sqrt(p*x - Ls) - p/2*x)/q
        
    plot_ls([b0, b1, a0, a1], 
            get_modularity_corners(L),
            n_LS,
            mag_C,
            mag_V,
            f,
            lambda x: x < 0,
            "A Module's Level Sets")
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0.0, .002], [0, 0.002])
    plt.xlabel(r'$I(C)$', fontsize=24)
    plt.ylabel(r'$E(C)$', fontsize=24)
    plt.ylim([a0, a1])
    plt.xlim([b0, b1])
    plt.title(r'Level Sets of Modularity', fontsize=24)



def plot_linear_ls(plt, n_LS, p):
    """ Plots the level sets associated with a linear metric
    """
    corners = [0, p, p - (1 - p) * 0.002, -(1 - p) * .002]
    
    def f(x, Ls):
        return (p * x - Ls) / float(1 - p)
        
    plot_ls([0.0, 1.0, 0.0, 0.002, min(corners), max(corners)], 
                 plt, n_LS, f, lambda y: y<0)
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0.0, 0.002], [0, 0.002])
    plt.xlabel(r'$I(C)$', fontsize=24)
    plt.ylabel(r'$E(C)$', fontsize=24)
    plt.title(r'Level Sets of $M_L$',
                fontsize=24)


def plot_mod_ratio_ls(limits, plt, p, n_LS):
    """ Plots the level sets for modularity ratio
    """
    [i0, i1, e0, e1] = limits
    L_min = p-1
    L_max = p
    
    def f(x, Ls):
        #return p*np.sqrt(x) - Ls
        return (p*x - Ls)/float(1-p)
        
    plot_ls([i0, i1, e0, e1, L_min, L_max], plt, n_LS, f, lambda x: x < 0)    
    plt.xticks([0.0, .3, .7, 1], [0, 0.3, 0.7, 1.0])
    plt.yticks([0.0, .3, .7, 1], [0, 0.3, 0.7, 1.0])
    plt.xlabel(r'$I(C)$', fontsize=24)
    plt.ylabel(r'$E(C)$', fontsize=24)
    plt.ylim([e0, e1])
    plt.xlim([i0, i1])
    plt.title(r'Level Sets of $G_L$',
                fontsize=24)
                
    
def PlotModularityRatio(limits, plt, n_LS, mag_C, mag_V, L):
    """ Plots the level sets for modularity?
    """
    [i0, i1, e0, e1] = limits
    
    corners = []
    
    L_min = mag_C**2 * L**2 /float(mag_C**2 + 2*mag_C*(mag_V - mag_C))**2
    L_max = 100*L**2/float(mag_C**2)
    # this is just an arbitrary number, since it really is \infty
    
    print 'min level set, ', L_min, 'max level set for modularity ratio, ', \
           L_max
    
    def f(x, Ls):
        return (L*np.sqrt(mag_C*(mag_C -1)*x/Ls) -
                mag_C*(mag_C -1)*x)/float(2*mag_C*(mag_V-mag_C))
        #return (np.sqrt(mag_C*(mag_C-1)*x/float(2*Ls)) - p/2.0*x)/q
        
    plot_ls([i0, i1, e0, e1, L_min, L_max], plt, n_LS, f, lambda x: x < 1)
    
    plt.xticks([0.0, .3, .7, 1], [0, 0.3, 0.7, 1.0])
    plt.yticks([e0, e1], [e0, e1])
    plt.xlabel(r'$I(C)$', fontsize=24)
    plt.ylabel(r'$E(C)$', fontsize=24)
    plt.ylim([e0, e1])
    plt.xlim([i0, i1])
    plt.title(r'Level Sets of Modularity Ratio',
                fontsize=24)
    
    
def draw_ls(metric, n_ls, mag_C, mag_V, ylim, new_fig=False, L=0):
    """ Given a metric, draws the level sets
    Parameters
    ----------
    metric : a string name of the metric
    n_ls : number of level sets to draw
    mag_C : number of nodes in the community
    mag_V : number of nodes in the graph
    ylim : the maximum y value
    """
    if new_fig:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlim(-0.01, 1.01)
        ax.set_ylim(-0.01, ylim + 0.01)
        plt.show()
    
    if metric == "volume":
        plot_ls([0, 1, 0, ylim],
                volume_corners,
                n_ls,
                mag_C,
                mag_V,
                volume_y,
                lambda y: y<0,
                "Volume Level Sets")
    elif metric in ["cut ratio", "edges cut", "expansion", "external density"]:
        plot_ls([0, 1, 0, ylim],
                external_density_corners,
                n_ls,
                mag_C,
                mag_V,
                external_density_y,
                lambda y: y<0,
                "Cut Ratio, Edges Cut, & Expansion Level Sets")
    elif metric == "internal":
        delta = 1.0 / float(n_ls + 1)
        for i in range(n_ls + 1):
            x = [i * delta, i * delta]
            plt.plot(x, [0, ylim], 'g-')
    elif metric == "conductance":
        plot_ls([0, 1, 0, ylim],
                conductance_corners,
                n_ls,
                mag_C,
                mag_V,
                conductance_y,
                lambda y: y > 0.5,
                "Conductance Level Sets")
    elif metric == "modularity":
        plot_ls([0, 1, 0, ylim],
                get_modularity_corners(L),
                n_ls,
                mag_C,
                mag_V,
                get_modularity_y(L),
                lambda y: y < 0,
                "A Single Module's Level Sets")
    elif metric == "linearity":
        plot_ls([0, 1, 0, ylim],
                get_linearity_corners(L),
                n_ls,
                mag_C,
                mag_V,
                get_linearity_single_y(L),
                lambda y: y < 0,
                "Linearity for Single Communities: Level Sets")
    
def linearity_k():
    """ Charts how linearity responds to community size
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot([0, 1], [1, 1], 'r-')
    ax.set_ylim(0, 2)
    ax.set_xlim(0, 1)
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0, 1, 2], [0, 1, 2])
    plt.xlabel(r'$k$', fontsize=24)
    plt.ylabel(r'Metric$(k)$', fontsize=24)
    plt.title(r"$k$'s Influence on Linearity", fontsize=20) 
    plt.show()
    
    
def get_linearity_single_y(param):
    """ Provides a wrapped function with access to param = (a, b)
    """
    def linearity_single_corners(x, ls, mag_C, mag_V):
        """ Returns the linearity values at each of the corners
        """
        return (param[0] * x - ls) / float(param[1])
    
    return linearity_single_corners
            
    
def get_linearity_corners(param):
    """ Provides a wrapped function with access to param = (a, b)
    """
    def linearity_corners(mag_C, mag_V, ylim):
        """ Returns the linearity values at each of the corners
        """
        return [0, param[0], -param[1] * ylim, param[0] - param[1] * ylim]
    
    return linearity_corners
        
        
def get_modularity_corners(L):
    """ Provides a wrapped function with access to L
    """
    def modularity_corners(mag_C, mag_V, ylim):
        """ Returns the modularity metric values at each of the corners
        """
        p = mag_C * (mag_C - 1) / L
        q = mag_V * (mag_V - mag_C)/ L
        return [0,
                p - p**2,
                - q**2 * ylim **2,
                p - (p + q * ylim)**2]
    return modularity_corners


def get_modularity_y(L):
    """ Provides a wrapped function that has access to L
    Allows all other previously written functions to remain the same
    """
    def modularity_y(x, ls, mag_C, mag_V):
        """ Finds the y intersept for internal density x and level set ls
        """
        p = mag_C * (mag_C - 1) / L
        q = mag_V * (mag_V - mag_C)/ L
        inside = max(p*x - ls, 0.)
        return (np.sqrt(inside) - p/2*x)/q
    
    return modularity_y
        
    
def volume_corners(mag_C, mag_V, ylim):
    """ Returns the voume metric values at each of the corners
    """
    return [0,
            mag_C * (mag_C - 1),
            mag_C * (mag_C - 1) + mag_C * (mag_V - mag_C) * ylim,
            mag_C * (mag_V - mag_C) * ylim]

def volume_y(x, ls, mag_C, mag_V):
    """ Given x and the LS value, finds the corresponding y value
    """
    return (ls - mag_C * (mag_C - 1) * x) / float(mag_C * (mag_V - mag_C))


def volume_k(I, E, mag_V):
    """ plots the affect k has on volume
    Parameters
    ----------
    I : 
    E : 
    mag_V : 
    
    Notes
    -----
    To reproduce the figure in the paper, use (I, E, mag_V) = (.5, .2, 34)
    """    
    count = 5000.0
    dk = 1.0/count
    k = [i*dk for i in range(int(count)+1)]
    vol = [ki * mag_V * (ki * mag_V - 1) * I + ki * (1 - ki) * mag_V**2 * E
           for ki in k]
    plt.plot(k, vol, 'g:')
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0, 300, 600], [0, 300, 600])
    plt.xlabel(r'$k$', fontsize=24)
    plt.ylabel(r'Volume', fontsize=24)
    plt.title(r"$k$'s Influence on Volume", fontsize=24)
  
  
def external_density_corners(mag_C, mag_V, ylim):
    """ provides the corners of level set values for cut ratio
    """
    return [0, 1, 0, ylim]


def external_density_y(x, ls, mag_C, mag_V):
    """ Given x and ls, returns the only possible y value
    """
    return ls


def external_k(E, mag_V):
    """ Plots the affect a community's size, parameterized by k has on external
    density based metrics
    
    Parameters
    ----------
    E - external density value
    mag_V - the number of nodes in the network
    
    Notes
    -----
    To reproduce the figure in the paper use E = 0.06 and mag_v = 34
    """
    count = 5000.0
    dk = 1.0/count
    k = [i*dk for i in range(int(count)+1)]
    
    functions  = [lambda k: E, 
                  lambda k: k * (1 - k) * mag_V**2 * E,
                  lambda k: (1 - k) * mag_V * E]
    
    labels = ['Cut Ratio', 'Edges Cut', 'Expansion']
    color = ['b--', 'g:', 'r-']
    
    for i in range(3):
        CC = [functions[i](ki) for ki in k]
        plt.plot(k, CC, color[i])
        
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0, 1, 2, 10], [0, 1, 2, 10])
    plt.xlabel(r'$k$', fontsize=24)
    plt.ylabel(r'Metric$(k)$', fontsize=24)
    plt.title(r"$k$'s Influence on Cut Ratio, Edge Cuts, & Expansion",
                fontsize=20)
    
    plt.legend(labels[:3])
    
    
def conductance_corners(mag_C, mag_V, ylim):
    """ Returns the level set values at the corners
    """
    delta = 0.002
    return [delta, 1 - delta, delta, 1 - delta]


def conductance_y(x, ls, mag_C, mag_V):
    """ Given an x and ls value finds what y must be
    """
    k = mag_C / float(mag_V)
    return ls * k * x / float((1 - ls) * (1 - k))
    
    
def conductance_k(I, E):
    """ Plots the affect k has on conductance for a fixed I and E
    
    Notes
    -----
    to reproduce the figure in the paper, use I = [1., 1., 10.] and
    E = [10., 1., 1.]
    """
    count = 5000.0
    da = 1.0/count
    a = [i*da for i in range(int(count)+1)]
    
    for i in range(len(I)):
        CC = [(1-ai)*E[i]/(ai*I[i] + (1-ai)*E[i]) for ai in a]
        text( .325, CC[1900]-.1, r'$\frac{I}{E} = ' + \
                                 str(I[i] / float(E[i])) + '$',
                fontsize=20, bbox=dict(alpha=1, facecolor='white'))
        cutoff = len(filter(lambda x: x>.5, CC))
        plt.plot(a[:cutoff], CC[:cutoff], 'r-')
        plt.plot(a[cutoff:], CC[cutoff:], 'g-')
        
    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.xlabel(r'$k$', fontsize=24)
    plt.ylabel(r'Conductance', fontsize=24)
    plt.title(r"$k$'s Influence on Conductance ", fontsize=24)
    
    
def plot_ls(limits, f_corners, n_ls, mag_C, mag_V, f_metric, thresh, name, width=0.3):
    """ Plots the prescribed level sets.
    Parameters
    ----------
    limits : a list of bounds and level set min max values
    f_corners : a function that returns the value at the corners
    n_LS : the number of level sets to plot
    f_metric : a function, that given a level set and an x(internal density) value,
        returns the y value(external density)
    thresh : a function on the level set value, indicating if the level set is
             desired
    name : the title of the plot
    width : the width of the arrows
    """
    count = 5000.0
    [x0, x1, y0, y1] = limits
    corners = f_corners(mag_C, mag_V, limits[3])
    ls_min = min(corners)
    #ls_max = max(corners)
    ls_max = 1
    dls = (ls_max - ls_min)/float(n_ls - 1)
    dx = (x1 - x0)/count
    x = [x0 + i*dx for i in range(int(count)+1)]
    for i in range(n_ls):
        ls = ls_min + i*dls
        y = [f_metric(xt, ls, mag_C, mag_V) for xt in x]
        
        color = 'g-'
        if thresh(ls):
            color = 'r-'
            
        # now to find how much to trim
        done_left = False; done_right = False;
        trim_left = -1;    trim_right = 0
        for i in range(len(y)):
            yl = y[i]; yr = y[-i-1]
            if not done_left and not(yl>=y0 and yl<=y1):
                trim_left += 1
            else:
                done_left = True
                
            if not done_right and not(yr>=y0 and yr<=y1):
                trim_right += 1
            else:
                done_right = True
                
        if trim_left + trim_right < len(y):  
            if trim_right > 0:
                plt.plot(x[trim_left+1:-trim_right],
                         y[trim_left+1:-trim_right], color, linewidth=width)
            else:
                plt.plot(x[trim_left+1:], y[trim_left+1:], color, linewidth=width)
                

    plt.xticks([0.0, .3, .7, 1.0], [0, 0.3, 0.7, 1])
    plt.yticks([0.0, limits[3]], [0, limits[3]])
    plt.xlabel(r'$I(C)$', fontsize=24)
    plt.ylabel(r'$E(C)$', fontsize=24)
    plt.title(name, fontsize=24)                