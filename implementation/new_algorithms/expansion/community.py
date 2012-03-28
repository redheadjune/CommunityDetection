
import numpy as np

class Community:
    """controls the set of nodes we are expanding to become a community.
    
    Data Structures
    ---------------
    nodes : a dictionary of each and its information in regard to the community
    in particular { n:{'e':0, 'p':0., 'reason':'e' or 'p'} }
    
    bounds: a dictionary of summary information
    in particular {'min_e':0, 'min_p':0.,
                   'stats':{'avg_e':0., 'sd_e':0., 'avg_p':0., 'sd_p':0.}}
    """
    
    def init(self, graph, nodes):
        """ Creates a community.
        Parameters
        ----------
        graph : a networkx graph
        nodes : the nodes to include in the community
        
        Returns
        -------
        candidates : a dict of nodes connected to C and their #edges into C
        """
        
        self.nodes = {}
        for n in nodes:
            self.nodes[n] = {'e':0}
            
        external_nodes = {}
        
        for n in nodes:
            for m in graph.neighbors(n):
                if m in nodes:
                    self.nodes[m]['e'] += 1
                else:
                    if m not in external_nodes:
                        external_nodes[m] = {'e':0}
                        
                    external_nodes[m]['e'] += 1

        for n, spec in self.nodes.iteritems():
            spec['p'] = spec['e'] / float(graph.degree(n))    

        for n, spec in external_nodes.iteritems():
            spec['p'] = spec['e'] / float(graph.degree(n))
            
        return external_nodes
    
    
    def init_bounds(self, cand):
        """Initializes the bounds
        """
        self.bounds = {}
        self.cand = cand
        self.update_bounds()
    
    
    def update_bounds(self):
        """Updates the bounds to find the new min_e and min_p. Updates the
        reason of why each node is in the community as well.
        """
        self.bounds['min_e'] = len(self.nodes)
        self.bounds['min_p'] = 1.0
        for n, spec in self.nodes.iteritems():
            spec['reason'] = self.classification(spec)
            if spec['reason'] == 'e':
                self.bounds['min_e'] = min(self.bounds['min_e'], int(spec['e']))
            else:
                self.bounds['min_p'] = min(self.bounds['min_p'], spec['p'])
                    
            
    def classification(self, spec):
        """ Returns why a spec is significant.
        Parameters
        ----------
        spec : A dictionary with 'e' and 'p'.
        
        Returns
        -------
        'e' or 'p' depending on which is more statistically significant
        """
        stats = self.cand.stat_import(spec)
        if stats['e'] > stats['p']:
            return 'e'
        
        return 'p'
    
    
    def is_candidate(self, spec):
        """Checks whether or not the spec is within the bounds.
        """
        return spec['e'] >= self.bounds['min_e'] or \
               spec['p'] >= self.bounds['min_p']
    
    
    def add_node(self, graph, n, external_nodes):
        """Adds the node n to the community and returns which nodes in
        candidates need updated.
        
        Parameters
        ----------
        graph : a networkx graph
        n : a node
        
        Returns
        -------
        changed : a list of nodes not in the community that need updated
        """
        self.nodes[n] = {'e':0}
        changed = []
        for m in graph.neighbors(n):
            if m in self.nodes:
                self.update_node(graph, m, 1)
                self.nodes[n]['e'] += 1
            else:
                changed.append(m)
                
        self.update_node(graph, n, 0)
        self.update_bounds()
        return changed
                
                
    def remove_node(self, graph, n, external_nodes):
        """Removes n from the community and returns which nodes to be updated.
        
        Parameters
        ----------
        graph : a networkx graph
        n : the node to be removed
        
        Returns
        -------
        changed : a list of nodes not in the community that need updated
        """
        self.nodes.pop(n)
        changed = [n]
        for m in graph.neighbors(n):
            if m in self.nodes:
                self.update_node(graph, m, -1)
            else:
                changed.append(m)
                
        self.update_bounds()
        return changed
                
                
    def update_node(self, graph, n, inc):
        """Updates the node n's connectivity to the community by inc.
        """
        self.nodes[n]['e'] += inc
        self.nodes[n]['p'] = self.nodes[n]['e'] / float(graph.degree(n))
        self.nodes[n]['reason'] = self.classification(self.nodes[n])
        
        
    def to_string(self):
        """Provides a string representing the Community
        """
        return "\nCommunity of: " + str(len(self.nodes)) + " nodes.\n" + \
               "              " + str(self.bounds['min_p']) + " minimum %.\n" + \
               "              " + str(self.bounds['min_e']) + " minimum E.\n" + \
               "              " + \
               str(self.cand.stat_import({'e':self.bounds['min_e'],
                                          'p':self.bounds['min_p']}))