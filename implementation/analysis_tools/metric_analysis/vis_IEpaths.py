# -*- coding: utf-8 -*-

from math import pi
import numpy as np

                                    
def plot_path(I_path, E_path, ax, color, name, arrow_width):
    """In ax plots with arrows and dots the path of IE
    Parameters
    ----------
    I_path : a list of internal density values
    E_path : a list of external density values
    ax : the subplot to map the values onto
    color : the color of the arrows
    name : the name of the metric that produced the IE path
    arrow_width : the width of the arrow heads
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
                
        length = max(0., length - arrow_width**.5 / 3.)
            
        dx = length * np.cos(theta)
        dy = length * np.sin(theta)
            
        ax.arrow(I_path[i],
                 E_path[i], 
                 dx,
                 dy,
                 width=arrow_width/10.,
                 color=color,
                 head_width=arrow_width)
                   
    for i in range(len(I_path)): # plot point
        ax.plot(I_path, E_path, color+'o', linewidth=4,)
    ax.plot(I_path[0], E_path[0], color+'o', linewidth=4,label=name)
       
    