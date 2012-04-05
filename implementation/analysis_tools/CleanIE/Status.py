# -*- coding: utf-8 -*-
class Status :
    """
    To handle several data in one struct.

    Could be replaced by named tuple, but don't want to depend on python 2.6
    """
    node2com = {}
    total_weight = 0
    internals = {}
    degrees = {}
    gdegrees = {}
    
    def __init__(self) :
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.loops = dict([])
        self.com_sizes = dict([])
        self.com_size_changes = dict([])
        
    def __str__(self) :
        return ("node2com : " + str(self.node2com) + " degrees : "
            + str(self.degrees) + " internals : " + str(self.internals)
            + " total_weight : " + str(self.total_weight)+ " Community Sizes:"
            + str(self.com_sizes) )

    def copy(self) :
        """Perform a deep copy of status"""
        new_status = Status()
        new_status.node2com = self.node2com.copy()
        new_status.internals = self.internals.copy()
        new_status.com_sizes = self.com_sizes.copy()
        new_status.com_size_changes = self.com_size_changes.copy()
        new_status.degrees = self.degrees.copy()
        new_status.gdegrees = self.gdegrees.copy()
        new_status.total_weight = self.total_weight

    def init(self, G, node_weights, part = None) :
        """Initialize the status of a G with every node in one community"""
        count = 0
        self.node2com = dict([])
        self.total_weight = 0
        self.degrees = dict([])
        self.gdegrees = dict([])
        self.internals = dict([])
        self.total_weight = G.size(weighted = True)
        self.com_sizes = dict([])
        
        if part == None :
            for node in G.nodes() :
                self.node2com[node] = count
                deg = float(G.degree(node, weighted = True))
                self.degrees[count] = deg
                self.gdegrees[node] = deg
                self.loops[node] = float(G.get_edge_data(node, node,
                                                 {"weight":0}).get("weight", 1))
                self.internals[count] = self.loops[node]
                self.com_sizes[count] = node_weights.get(node, 1)
                # the problem is node, is no longer node in node_weights
                self.com_size_changes[count] = []
                count = count + 1
        else :
            for node in G.nodes() :
                com = part[node]
                self.node2com[node] = com
                deg = float(G.degree(node, weighted = True))
                self.degrees[com] = self.degrees.get(com, 0) + deg
                self.gdegrees[node] = deg
                inc = 0.
                for neighbor, datas in G[node].iteritems() :
                    weight = datas.get("weight", 1)
                    if part[neighbor] == com :
                        if neighbor == node :
                            inc += float(weight)
                        else :
                            inc += float(weight) / 2.
                self.internals[com] = self.internals.get(com, 0) + inc
                self.com_sizes[com] = node_weights.get(node, 1)
                self.com_size_changes[com] = []
                
                
                
