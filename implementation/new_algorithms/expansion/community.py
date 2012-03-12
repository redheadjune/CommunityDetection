
import numpy as np

class Community:
    """controls the set of nodes we are expanding to become a community.
    
    Data Structures
    ---------------
    nodes : a dictionary of each and its information in regard to the community
    in particular { n:{'e':0, 'p':0., 'slope':0., 'reason':'e' or 'p'} }
    
    bounds: a dictionary of summary information
    in particular {'min_e':0, 'min_p':0., 'slope':0.}
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
            self.nodes[n] = {'e':0, 'slope':float(graph.degree(n))}
            
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

        self.bounds = {}
        self.update_bounds(external_nodes)
            
        return external_nodes
    
    
    def update_bounds(self, external_nodes):
        """Updates the bounds to find the new min_e and min_p. Updates the
        reason of why each node is in the community as well.
        """
        self.bounds['min_e'] = len(self.nodes)
        self.bounds['min_p'] = 1.0
        (self.bounds['slope'], self.bounds['offset']) = self.find_slope(external_nodes)
        for n, spec in self.nodes.iteritems():
            spec['reason'] = self.classification(spec)
            if spec['reason'] == 'e':
                self.bounds['min_e'] = min(self.bounds['min_e'], int(spec['e']))
            else:
                self.bounds['min_p'] = min(self.bounds['min_p'], spec['p'])
                    
                     
    def find_slope(self, points):
        """Finds the slope of the best fit line through the points
        Parameters
        ----------
        points : a dictionary of at least {'e':0, 'p':0.}
        
        Returns
        -------
        m : the slope of the best fit line
        """
        points = filter(lambda pt: pt['e']>2 or pt['p']>.05, points.values())
        """ uses a fitted line, but just doesn't seem to work
        x = []
        y = []
        for spec in points:
            x.append(spec['p'])
            y.append(spec['e'])
            
        x = np.array(x)
        y = np.array(y)
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y)[0]
        
        return 2*m, c
        """
        # uses the average rotation
        thetas = [np.arctan(pt['e'] / pt['p']) for pt in points]
        return np.tan(sum(thetas) / len(thetas)), 0.
        
        
            
    def classification(self, spec):
        """ Returns why a spec is significant.
        Parameters
        ----------
        spec : A dictionary with 'slope'.
        
        Returns
        -------
        'e' or 'p' depending on whether or not the 'slope' is larger or smaller
        than the slope indicated by bounds.
        """
        if spec['e'] >= self.bounds['slope']*spec['p'] + self.bounds['offset']:
            return 'e'
        
        return 'p'
    
    
    def is_candidate(self, spec):
        """Checks whether or not the spec is within the bounds.
        """
        return spec['e'] >= self.bounds['min_e'] or \
               spec['p'] >= self.bounds['min_p']
    
    
    def distance(self, spec):
        """Computes the distance a spec is from the bounds of the community.
        The higher the number the better.
        
        Parameters
        ----------
        spec : a dictionary of 'e' and 'p' values
        
        Returns
        -------
        d : a float heuristic distance from the bounds of the community
        """
        d = 0.
        if spec['e'] > self.bounds['min_e']:
            d += (spec['e'] - self.bounds['min_e'])
            
        if spec['p'] > self.bounds['min_p']:
            d += (spec['p'] - self.bounds['min_p']) * self.bounds['slope']
        
        return d
    
    
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
        self.nodes[n] = {'e':0, 'slope':graph.degree(n)}
        changed = []
        for m in graph.neighbors(n):
            if m in self.nodes:
                self.update_node(graph, m, 1)
                self.nodes[n]['e'] += 1
            else:
                changed.append(m)
                
        self.update_node(graph, n, 0)
        self.update_bounds(external_nodes)
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
                
        self.update_bounds(external_nodes)
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
               "              " + str(self.bounds['slope']) + " slope of classifier.\n" + \
               "              " + str(self.bounds['offset']) + " intercept."