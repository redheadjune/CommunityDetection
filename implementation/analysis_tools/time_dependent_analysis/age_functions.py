

def get_age_stats(graph, dates, communities):
    """ For each community returns the 10%, 50%, and 90% date
    Parameters
    ----------
    graph : networkx graph
    dates : a dictionary of dates in ordinal form
    communities : a list of communities
    
    Returns
    -------
    a list of tulpes (10%, 50%, 90%) ages of nodes in the community
    """
    c_ages = []
    for c in communities:
        ages = [dates[n] for n in c]
        ages.sort()
        c_ages.append((ages[len(ages)/10],
                       ages[len(ages)/2],
                       ages[len(ages)*9/10]))
        
    return c_ages