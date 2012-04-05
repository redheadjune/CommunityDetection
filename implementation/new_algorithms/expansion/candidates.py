import CommunityDetection as CD
import numpy as np

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
        self.stats = {'total_e':0., 'total_e_sq':0.,
                      'total_p':0., 'total_p_sq':0.,
                      'all_e':[], 'all_p':[],
                      'dirty':True}
        
        for n, spec in candidates.iteritems():
            self.update_stats(spec)
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
                    
                    
    def update_stats(self, spec, add=True):
        """Updates the stats to reflect adding/removing a node
        """
        self.stats['dirty'] = True
        multi = 1.
        if not add:
            multi = -1.
        """
        n = max(float(len(self.fringe) + len(self.close)), 1.0)            
        if multi > 0:
            self.stats['all_e'].append(spec['e'])
            self.stats['all_p'].append(spec['p'])
        else:
            self.stats['all_e'].remove(spec['e'])
            self.stats['all_p'].remove(spec['p'])
        """
        self.stats['total_e'] += multi * spec['e']
        self.stats['total_p'] += multi * spec['p']
        self.stats['total_e_sq'] += multi * spec['e']**2
        self.stats['total_p_sq'] += multi * spec['p']**2  
        

    def stat_import(self, spec):
        """ Finds by how much variance the spec can be important
        """
        if self.stats['dirty']:
            n = max(float(len(self.fringe) + len(self.close)), 1.0)              
            self.stats['avg_e'] = self.stats['total_e'] / n
            self.stats['avg_p'] = self.stats['total_p'] / n
            self.stats['var_e'] = self.stats['total_e_sq'] / n \
                - self.stats['avg_e']**2
            self.stats['var_p'] = self.stats['total_p_sq'] / n \
                - self.stats['avg_p']**2  
            self.stats['dirty'] = False

        if self.stats['var_e'] > 0:
            e_import = (spec['e'] - self.stats['avg_e']) / self.stats['var_e']**.5
        else:
            e_import = 0.
        
        if self.stats['var_p'] > 0.:
            p_import = (spec['p'] - self.stats['avg_p']) / self.stats['var_p']**.5
        else:
            p_import = 0.
            
        return {'e':e_import, 'p':p_import}
        """
        # for using the power law interpretation
        if self.stats['dirty']:
            if len(self.stats['all_e']) == 0:
                print "WOOOOW"
            power_e = CD.plfit.plfit(np.array(self.stats['all_e']))
            power_p = CD.plfit.plfit(np.array(self.stats['all_p']))
            (e_min, e_alpha) = power_e.plfit(silent=True, quiet=True, discrete=True, xmin=2.9)
            (p_min, p_alpha) = power_p.plfit(silent=True, quiet=True, discrete=False, xmin=0.05)
            self.stats['e_min'] = e_min
            self.stats['e_alpha'] = e_alpha
            self.stats['p_min'] = p_min
            self.stats['p_alpha'] = p_alpha
            self.stats['dirty'] = False
        
        return {'e':(spec['e']/self.stats['e_min'])**(1 - self.stats['e_alpha']),
                'p':(spec['p']/self.stats['p_min'])**(1 - self.stats['p_alpha'])}
        """

    
    
    def stats_string(self):
        """Forms a string for easy printing
        """
        if self.stats['var_e'] >=0 and self.stats['var_p'] >= 0:
            return "avg e: " + str(self.stats['avg_e']) + \
                   " standard deviance e: " + str(self.stats['var_e']**.5) + \
                   " avg p: " + str(self.stats['avg_p']) + \
                   " standard deviance p: " + str(self.stats['var_p']**.5)
        else:
            return "Hope that was the end, because deviance is tapped " + \
                   str(self.stats['var_p']) + " " + str(self.stats['var_e'])
        """
        return "Power law of (e_min, e_alpha)" + str((self.stats['e_min'], self.stats['e_alpha'])) + \
               " (p_min, p_alpha) " + str((self.stats['p_min'], self.stats['p_alpha']))
        """
                                                     
    
                    
    def rework_fringe(self):
        """If the bounds have changed in a non-connective way, then need to
        check the fringe and reclassify the ones that are now eligable
        """
        change = {}
        for n, spec in self.fringe.iteritems():
            if self.c.is_candidate(spec):
                change[n] = spec.copy()
                
        self.reclassify(change)
                
                
    def get_best(self):
        """Returns the best 
        """
        best, reclassify = self.get_outlier(self.close)
        self.reclassify(reclassify)
        if best in reclassify:
            best, reclassify = self.get_outlier(self.close)
            
        return best
    
    
    def get_forced(self):
        """presumes that close is empty and we want to force picking from fringe
        """
        best, reclassify = self.get_outlier(self.fringe)
        return best
    
    
    def get_outlier(self, data):
        """Finds the furtherest outlier in the data by the standard deviation
        Parameter
        ---------
        data : a dictionary of spec's, presumably close or fringe
        
        Returns
        -------
        best : the key of the furtherest outlier
        reclassify : the set of nodes that were not candidates
        """
        best = None
        prob = 1.
        reclassify = {}
        for n, spec in data.iteritems():
            if not self.c.is_candidate(spec):
                # then need to update where this node is
                reclassify[n] = spec
                
            n_stat = self.stat_import(spec)
            n_prob = max(n_stat['e'], n_stat['p'])
            if n_prob >= prob:
                best = n
                prob = n_prob
                    
        return best, reclassify    
        
        
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
        self.update_stats(spec)
        
        
    def remove_node(self, n):
        """Removes a node, presumably in close
        """
        if n in self.close:
            spec = self.close.pop(n)
        if n in self.fringe:
            spec = self.fringe.pop(n)
            
        self.update_stats(spec, add=False)
            
        
    def update_node(self, n, spec, inc):
        """Updates the node n's connectivity to the community by inc.
        """
        if spec != {'e':0., 'p':0.}:
            self.update_stats(spec, add=False)

        spec['e'] += inc
        spec['p'] = spec['e'] / float(self.graph.degree(n))
        self.update_stats(spec)
        
        
    def get_all_nodes(self):
        """Returns a dict of all info for easier processing elsewhere
        """
        all_nodes = {}
        for n, spec in self.close.iteritems():
            all_nodes[n] = spec
            
        for n, spec in self.fringe.iteritems():
            all_nodes[n] = spec
            
        return all_nodes
        