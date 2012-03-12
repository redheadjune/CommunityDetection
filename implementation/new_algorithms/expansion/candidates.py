

class Candidates:
    """Keeps track of the candidates for adding to a community.
    
    There are two types of nodes to keep track of, both of which are connected
    to the community, but only one set of which is elligable to be added.
    
    fringe : a dictionary of inelligable nodes with their connectivity
    close : a dictionary of elligable nodes with their connectivity
    
    Both have the format:
    in particular {n:{'e':0, 'p':0.}}
    """
    
    def __init__(self, graph, candidates, c):
        """Divides and stores the candidates into fringe and close based on c.
        
        Parameters
        ----------
        graph : a networkx graph
        candidates : a dictionary with the nodes attached to but not in c and info
        c : a Community
        """
        self.graph = graph
        self.c = c
        self.fringe = {}
        self.close = {}
        
        for n, spec in candidates.iteritems():
            if self.c.is_candidate(spec):
                self.close[n] = spec
            else:
                self.fringe[n] = spec
                
                
    def reclassify(self, changed):
        """Reclassify the changed nodes, presumes their new datum is handed in.
        """
        for n, spec in changed.iteritems():
            if self.c.is_candidate(spec):
                self.close[n] = spec
                if n in self.fringe:
                    self.fringe.pop(n)
            elif spec['e'] == 0:
                self.remove_node(n)
            else:
                self.fringe[n] = spec
                if n in self.close:
                    self.close.pop(n)
                
                
    def get_best(self):
        """Returns the best 
        """
        closest = None
        d = 0
        reclassify = {}
        for n, spec in self.close.iteritems():
            if not self.c.is_candidate(spec):
                # then need to update where this node is
                reclassify[n] = spec
                
            n_dist = self.c.distance(spec)
            if n_dist >= d:
                closest = n
                d = n_dist
                
        self.reclassify(reclassify)
        return closest
        
        
    def drop_connectivity(self, to_drop):
        """Drops the connectivity of nodes in to_drop by 1 and reclassifies them
        """
        self.change_connectivity(to_drop, -1)
        
        
    def add_connectivity(self, to_inc):
        """Increases the connectivity of nodes in to_inc by 1 and reclassifies.
        """
        self.change_connectivity(to_inc, 1)
        
        
    def change_connectivity(self, to_change, inc):
        """Changes the connectivity of to_change nodes by inc.
        Then updates close/fringe.
        
        Parameters
        ----------
        to_change : a list of nodes to change their 'e' values by
        inc : an int of how much to change 'e' by
        """
        changed = {}
        for n in to_change:
            spec = self.get_spec(n)
            self.update_node(n, spec, inc)
            changed[n] = spec
            
        self.reclassify(changed)
        
        
    def get_spec(self, n):
        """Finds the spec of n, whether it is in close or fringe
        """
        if n in self.close:
            return self.close[n]
        
        if n in self.fringe:
            return self.fringe[n]
        
        return {'e':0, 'p':0.0}
        

    def add_node(self, n, spec):
        """Adds a node
        """
        self.reclassify({n:spec})
        
        
    def remove_node(self, n):
        """Removes a node, presumably in close
        """
        if n in self.close:
            self.close.pop(n)
        if n in self.fringe:
            self.fringe.pop(n)
            
        
    def update_node(self, n, spec, inc):
        """Updates the node n's connectivity to the community by inc.
        """
        spec['e'] += inc
        spec['p'] = spec['e'] / float(self.graph.degree(n))
        
        
    def get_all_nodes(self):
        """Returns a dict of all info for easier processing elsewhere
        """
        all_nodes = {}
        for n, spec in self.close.iteritems():
            all_nodes[n] = spec
            
        for n, spec in self.fringe.iteritems():
            all_nodes[n] = spec
            
        return all_nodes
        