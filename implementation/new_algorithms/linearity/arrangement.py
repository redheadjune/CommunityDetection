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
    
    def __init__(self, graph, numedges, __A, __B, __C):
        """ Creates a set of bottles that each contain 1 node
        """
        self.bottles = {}
        self.ntob = {}
        self.intedges = 0.
        self.idealint = 0.
        self.extedges = 0.
        self.idealext = float(numedges)
        self.__A = __A
        self.__B = __B
        self.__C = __C
        for n in graph:
            self.bottles[n] = Bottle(n, graph, [n])
            self.intedges += self.bottles[n].intedges
            self.extedges += self.bottles[n].extedges
            self.idealint += self.bottles[n].idealint
            self.ntob[n] = n
            
        self.s = len(self.bottles)
        
    def __str__(self):
        barstr =  "Bar with internal edges: "+ str(self.intedges) + "\n" + \
                  "         external edges: "+ str(self.extedges) + "\n" + \
                  "         ideal int edges: "+ str(self.idealint) + "\n" + \
                  "         ideal ext edges: "+ str(self.idealext) + "\n" + \
                  "         non-empty bottles: "+ str(self.s) + "\n" + \
                  "         a: " + str(self.__A) + "\n" + \
                  "         b: " + str(self.__B) + "\n" + \
                  "         c: " + str(self.__C) + "\n"
        
        """         
        for b in self.bottles.values():
            barstr += "   " + str(b)
        """
         
        return barstr
        
        
    def shift(self, graph, n):
        """Finds the best spot to put n.
        This is the heart of the matter.
        
        Given that we want to consider moving n, finds the best bottle to put n
        in.
        Parameters
        ---------
        graph : a networkx graph
        n : the node we want to consider moving
        
        Returns
        -------
        bestbname : the name of the best bottle to put n in
        """
        bestimprovement = 0.
        bestbname = self.bottle_containing(n)
        bhome = self.bottles[bestbname]
        bhomename = bestbname
        
        # find the change in number of communities
        cmod = 0
        if graph.node[n]['size'] == bhome.size:
            cmod = -1 * self.__C
            
        # makes finding the change in external density easier
        en = {bestbname:0}
        for m in graph.neighbors(n):
            if m != n:
                b = self.bottle_containing(m)
                en[b] = en.get(b, 0.) + graph[n][m]['weight']
                
        bmod = 2 * self.__B / self.idealext
                
        # makes finding the change in internal density easier
        ibefore = self.__A
        if self.idealint > 0:
            ibefore = self.__A * self.intedges / self.idealint
            
        deltasize = graph.node[n]['size']
        itop = self.intedges - 2 * en[bestbname]
        ibottom = self.idealint + self.change_ideal(bhome.size, -deltasize)
        
        for bneighbor in en.keys():
            if bneighbor != bhomename:
                currentsize = self.bottles[bneighbor].size
                newitop = itop + 2 * en[bneighbor]
                newibottom = ibottom + self.change_ideal(currentsize, deltasize)
                
                improvement = self.__A * newitop / newibottom - ibefore\
                              - bmod * (en[bhomename] - en[bneighbor])\
                              - cmod
                       
                if improvement > bestimprovement:
                    bestbname = bneighbor
                    bestimprovement = improvement
        
        return bestbname
        
        
    def test_swap(self, graph, n, b1, b2):
        """Tests the changes that would occur moving n from b1 to b2
        
        Returns
        -------
        deltaint : the change in the number of internal edges
        deltaext : the change in the number external edges
        deltas   : the change in the number of non-empty bottles
        """
        if n not in self.bottles[b1].contains:
            raise Exception("tried to test an invalid move of node from bottle")
        
        stay = self.lin_metric()
        self.swap(graph, n, b1, b2)
        
        go = self.lin_metric()
        self.swap(graph, n, b2, b1)
        
        return go - stay
        
        
    def swap(self, graph, n, b1, b2):
        """ Swaps the node n from bottle b1 to b2
        """
        b1 = self.bottles[b1]
        b2 = self.bottles[b2]
        self.intedges -= (b1.intedges + b2.intedges)
        self.extedges -= (b1.extedges + b2.extedges)
        self.idealint -= (b1.idealint + b2.idealint)
        
        b1.remove_member(graph, n)
        if b1.size == 0:
            self.s -= 1
            
        if b2.size == 0:
            self.s += 1
        b2.add_member(graph, n)
        
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
        return list(set([self.ntob[m] for m in graph.neighbors_iter(n)]))
        
    
    def nodes_to_bottles(self):
        """Creates the mapping of nodes of the graph to their storage bottles.
        """
        mapping = {}
        for b in self.bottles.values():
            for n in b.contains:
                mapping[n] = b.name
                
        return mapping
        
        
    def lin_metric(self):
        """Returns the current metric evaluation of Bar
        """
        if self.idealint == 0.:
            first = 1.
        else:
            first = self.intedges / self.idealint
        
        return self.__A * first \
               - self.__B * self.extedges / self.idealext \
               - self.__C * self.s
               
               
    def change_ideal(self, size, delta):
        """ let size1 be the original size and size 2 be the new size of
community
        """
        return -size * (size - 1) + (size + delta) * (size + delta - 1)
        

class Bottle :
    """ Bottle is a group of nodes tenatively put together.
    
    Fields
    ------
    name : name of the bottle
    contains : a list of the members of nodes in the bottle
    size : number of members (including previously compressed in nodes)
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
        self.size = sum([graph.node[n]['size'] for n in self.contains])
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
               "      ideal internal:" + str(self.idealint) + "\n" +\
               "      external edges:" + str(self.extedges) + "\n" +\
               "      contains:" + str(self.contains) + "\n" +\
               "      size: " + str(self.size) + "\n"
               
           
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
        
        self.size -= graph.node[member]['size']
        
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
        self.size += graph.node[member]['size']
        self.contains.append(member)
        self.update_ideal()
        
        for m in graph.neighbors_iter(member):
            if m in self.contains:
                self.intedges += 2 * graph[member][m]['weight']
                if m != member:
                    self.extedges -= graph[member][m]['weight']
            else:
                self.extedges += graph[member][m]['weight']
                
                