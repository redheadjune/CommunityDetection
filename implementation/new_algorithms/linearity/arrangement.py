# -*- coding: utf-8 -*-

import copy


class Bar :
    """ At each level there will be many bottles, this is how to control them.
    
    Parameters
    ---------
    graph       : a networkx weighted graph
    n           : a node of the graph
    b1          : a bottle that n is currently in
    b2          : a bottle that n will be put in
    
    Fields
    ------
    bottles     : a dictionary of bottles indexed by their names
    ntob        : a dictionary mapping nodes to bottles
    intedges    : the number of internal edges across the bar
    idealint    : the number int edges should all bottles be cliques
    extedges    : the number of external edges across the bar
    s           : the number of non-empty bottles
    
    Methods
    -------
    test_swap   : returns the deltaI, deltaE, deltaS of swapping a node
    swap        : actually swaps a node between bottles
    bottle_neighbors : creates the list of bottles a node is connected to
    lin_metris  : computes the metric value of the current configuration
    
    """
    
    def __init__(self, graph):
        """ Creates a set of bottles that each contain 1 node
        """
        self.bottles = {}
        self.ntob = {}
        self.intedges = 0.
        self.idealint = 0.
        self.extedges = 0.
        for n in graph:
            self.bottles[n] = Bottle(n, graph, [n])
            self.intedges += self.bottles[n].intedges
            self.extedges += self.bottles[n].extedges
            self.idealint += self.bottles[n].idealint
            self.ntob[n] = n
            
        self.s = len(self.bottles)
        
    def __str__(self):
        return "Bar with internal edges: "+ str(self.intedges) + "\n" + \
               "         external edges: "+ str(self.extedges) + "\n" + \
               "         ideal edges: "+ str(self.idealint) + "\n" + \
               "         non-empty bottles: "+ str(self.s) + "\n"
        
    def test_swap(self, graph, n, b1, b2):
        """Tests the changes that would occur moving n from b1 to b2
        
        Returns
        -------
        deltaint : the change in the number of internal edges
        deltaext : the change in the number external edges
        deltas   : the change in the number of non-empty bottles
        """
        if n not in b1.contains:
            raise Exception("tried to test an invalid move of node from bottle")
        
        aint = self.intedges
        aideal = self.idealint
        aext = self.extedges
        a_s = self.s
        
        swap(graph, n, b1, b2)
        
        bint = self.intedges
        bideal = self.idealint
        bext = self.extedges
        b_s = self.s
        
        swap(graph, n, b2, b1)
        
        return (aint/aideal - bint/bideal), (aext - bext), (a_s - b_s)
        
    def swap(self, graph, n, b1, b2):
        """ Swaps the node n from bottle b1 to b2
        """
        self.intedges -= (b1.intedges + b2.intedges)
        self.extedges -= (b1.extedges + b2.extedges)
        self.idealint -= (b1.idealint + b2.idealint)
        
        b1.remove_member(graph, b)
        if b1.size == 0:
            self.size -= 1
            
        if b2.size == 0:
            self.size += 1
        b2.add_member(graph, b)
        
        self.ntob[n] = b2.name
        
        self.intedges += (b1.intedges + b2.intedges)
        self.extedges += (b1.extedges + b2.extedges)
        self.idealint += (b1.idealint + b2.idealint)
        
        
    def bottle_containing(self, n):
        """ Returns the Bottle containing n
        """
        return self.ntob[n]
        
        
    def bottle_neighbors(self, graph, n):
        """ Returns all Bottles, n, is connected to.
        """
        return list(set([self.ntob[m] for m in graph.neighbor_iter(n)]))
        
        
    def lin_metric(self, a, b, c):
        """Returns the current metric evaluation of Bar
        """
        return a * self.intedges / self.idealint \
               - b * self.extedges \
               - c * self.s

class Bottle :
    """ Bottle is a group of nodes tenatively put together.
    
    Fields
    ------
    name : name of the bottle
    contains : a list of the members of nodes in the bottle
    size : number of members
    intedges : number of internal edges, should the bottle be a community
    extedges : number of external edges, should the bottle be a community
    
    Parameters
    ----------
    name : anything
    #graph : a networkx graph with edge attribute 'weight' for all edges
    members : a list of node names
    member : a single node name
    
    Maintains
    ---------
    invariably maintains intedges, extedges, size
    
    Raises
    ------
    Raises add/remove errors if try to add/remove nodes that the Bottle does
    not have control over.
    """
        
    def __init__(self, name, graph, members):
        
        self.name = name
        self.contains = list(copy.copy(members))
        self.size = len(self.contains)
        self.intedges = 0.
        self.extedges = 0.
        
        for n in self.contains:
            for m in graph.neighbors_iter(n):
                if m == n:
                    self.intedges += 2 * graph[n][m]['weight']
                elif m in self.contains:
                    self.intedges += graph[n][m]['weight']
                else:
                    self.extedges += graph[n][m]['weight']
                    
        self.update_ideal()
                    
                    
    def __str__(self):
        return "Bottle: " + str(self.name) + "\n" + \
               "      internal edges:" + str(self.intedges) + "\n" +\
               "      external edges:" + str(self.extedges) + "\n" +\
               "      contains:" + str(self.contains) + "\n" +\
               "      size: " + str(self.size)
               
           
    def update_ideal(self):
        """ Updates the number of ideal nodes
        """
        self.idealint = float(self.size * (self.size - 1))
              
    def remove_member(self, graph, member):
        """ Removes a member from the bottle and updates the fields.
        """
        if member not in self.contains:
            raise Exception("Tried to remove a non-member," + str(member) + \
                            " from Bottle: " + str(self.name))
        
        self.size -= 1.
        
        for m in graph.neighbors_iter(member):
            if m in self.contains:
                self.intedges -= 2 * graph[member][m]['weight']
                if m != member:
                    self.extedges += graph[member][m]['weight']
            else:
                self.extedges -= graph[member][m]['weight']
                
        self.contains.remove(member)
        self.update_ideal()
        
        
    def add_member(self, graph, member):
        """ Adds a member to the bottle and updates the fields.
        """
        if member in self.contains or member not in graph:
            raise Exception("Tried to add an invalid node," + str(member) + \
                            " to Bottle: " + str(self.name))
        self.size += 1
        self.contains.append(member)
        self.update_ideal()
        
        for m in graph.neighbors_iter(member):
            if m in self.contains:
                self.intedges += 2 * graph[member][m]['weight']
                if m != member:
                    self.extedges -= graph[member][m]['weight']
            else:
                self.extedges += graph[member][m]['weight']
                
                