# -*- coding: latin-1 -*-
# 
# intended to implement a power-law fitting routine as specified in.....
# http://www.santafe.edu/~aaronc/powerlaws/
#
# The MLE for the power-law alpha is very easy to derive given knowledge
# of the lowest value at which a power law holds, but that point is 
# difficult to derive and must be acquired iteratively.

"""
plfit.py - a python power-law fitter based on code by Aaron Clauset
http://www.santafe.edu/~aaronc/powerlaws/
http://arxiv.org/abs/0706.1062 "Power-law distributions in empirical data" 
Requires pylab (matplotlib), which requires numpy

example use:
from plfit import plfit

MyPL = plfit(mydata)
MyPL.plotpdf(log=True)


"""

import numpy 
import time
import pylab
try:
    import fplfit
    fortranOK = True
except:
    fortranOK = False
try:
    import cplfit
    cyOK = True
except:
    cyOK = False

import numpy.random as npr
from numpy import log,log10,sum,argmin,argmax,exp,min,max
try:
    import scipy.stats
    scipyOK = True
except ImportError:
    scipyOK = False
    print "scipy didn't import.  Can't compute certain basic statistics."

class plfit:
    """
    A Python implementation of the Matlab code http://www.santafe.edu/~aaronc/powerlaws/plfit.m
    from http://www.santafe.edu/~aaronc/powerlaws/

    See A. Clauset, C.R. Shalizi, and M.E.J. Newman, "Power-law distributions
    in empirical data" SIAM Review, 51, 661-703 (2009). (arXiv:0706.1062)
    http://arxiv.org/abs/0706.1062

    The output "alpha" is defined such that p(x) ~ (x/xmin)^-alpha
    """

    def __init__(self,x,**kwargs):
        """
        Initializes and fits the power law.  Can pass "quiet" to turn off 
        output (except for warnings; "silent" turns off warnings)
        """
        if (x<0).sum() > 0:
            print "Removed %i negative points" % ((x<0).sum())
            x = x[x>0]
        self.data = x
        self.plfit(**kwargs)


    def alpha_(self,x):
        def alpha(xmin,x=x):
            """
            given a sorted data set and a minimum, returns power law MLE fit
            data is passed as a keyword parameter so that it can be vectorized

            if there is only one element, return alpha=0
            """
            gexmin = x>=xmin
            n = gexmin.sum()
            if n < 2:
                return 0
            x = x[gexmin]
            a = float(n) / sum(log(x/xmin))
            return a
        return alpha

    def kstest_(self,x):
        def kstest(xmin,x=x):
            """
            given a sorted data set and a minimum, returns power law MLE ks-test w/data
            data is passed as a keyword parameter so that it can be vectorized

            The returned value is the "D" parameter in the ks test...
            """
            x = x[x>=xmin]
            n = float(len(x))
            if n == 0: return numpy.inf
            a = float(n) / sum(log(x/xmin))
            cx = numpy.arange(n,dtype='float')/float(n)
            cf = 1-(xmin/x)**a
            ks = max(abs(cf-cx))
            return ks
        return kstest
    

    def plfit(self, nosmall=True, finite=False, quiet=False, silent=False,
            usefortran=False, usecy=False, xmin=None, verbose=False, 
            discrete=None, discrete_approx=True, discrete_n_alpha=1000):
        """
        A Python implementation of the Matlab code http://www.santafe.edu/~aaronc/powerlaws/plfit.m
        from http://www.santafe.edu/~aaronc/powerlaws/

        See A. Clauset, C.R. Shalizi, and M.E.J. Newman, "Power-law distributions
        in empirical data" SIAM Review, 51, 661-703 (2009). (arXiv:0706.1062)
        http://arxiv.org/abs/0706.1062

        There are 3 implementations of xmin estimation.  The fortran version is fastest, the C (cython)
        version is ~10% slower, and the python version is ~3x slower than the fortran version.
        Also, the cython code suffers ~2% numerical error relative to the fortran and python for unknown
        reasons.

        There is also a discrete version implemented in python - it is different from the continous version!
        *discrete* [ bool | None ]
            If *discrete* is None, the code will try to determine whether the
            data set is discrete or continous based on the uniqueness of the
            data.  If *discrete* is True or False, the distcrete or continuous
            fitter will be used, respectively.

        *xmin* [ float / int ]
            If you specify xmin, the fitter will only determine alpha assuming
            the given xmin; the rest of the code (and most of the complexity)
            is determining an estimate for xmin and alpha.

        *nosmall* [ bool (True) ]
            When on, the code rejects low s/n points

        *finite* [ bool (False) ]
            There is a 'finite-size bias' to the estimator.  The "alpha" the code measures
            is "alpha-hat" s.t.

        *quiet* [ bool (False) ]
            If False, delivers messages about what fitter is used and the fit results

        *verbose* [ bool (False) ] 
            Deliver descriptive messages about the fit parameters (only if *quiet*==False)

        *silent* [ bool (False) ] 
            If True, will print NO messages
        """
        x = self.data
        z = numpy.sort(x)
        t = time.time()
        xmins,argxmins = numpy.unique(z,return_index=True)#[:-1]
        self._nunique = len(xmins)
        
        if self._nunique == len(x) and discrete is None:
            if verbose: print "Using CONTINUOUS fitter"
            discrete = False
        elif self._nunique < len(x) and discrete is None:
            if verbose: print "Using DISCRETE fitter"
            discrete = True

        t = time.time()
        if xmin is None:
            if discrete:
                self.discrete_best_alpha( approximate=discrete_approx,
                        n_alpha=discrete_n_alpha, verbose=verbose, finite=finite)
                return self._xmin,self._alpha
            elif usefortran and fortranOK:
                dat,av = fplfit.plfit(z,int(nosmall))
                goodvals=dat>0
                sigma = ((av-1)/numpy.sqrt(len(z)-numpy.arange(len(z))))[argxmins]
                dat = dat[goodvals]
                av = av[goodvals]
                if nosmall:
                    # data, av a;ready treated for this.  sigma, xmins not
                    nmax = argmin(sigma<0.1)
                    xmins = xmins[:nmax]
                    sigma = sigma[:nmax]
                if not quiet: print "FORTRAN plfit executed in %f seconds" % (time.time()-t)
            elif usecy and cyOK:
                dat,av = cplfit.plfit_loop(z,nosmall=nosmall,zunique=xmins,argunique=argxmins)
                goodvals=dat>0
                sigma = (av-1)/numpy.sqrt(len(z)-argxmins)
                dat = dat[goodvals]
                av = av[goodvals]
                if not quiet: print "CYTHON plfit executed in %f seconds" % (time.time()-t)
            else:
                av  = numpy.asarray( map(self.alpha_(z),xmins) ,dtype='float')
                dat = numpy.asarray( map(self.kstest_(z),xmins),dtype='float')
                sigma = (av-1)/numpy.sqrt(len(z)-argxmins+1)
                if nosmall:
                    # test to make sure the number of data points is high enough
                    # to provide a reasonable s/n on the computed alpha
                    goodvals = sigma<0.1
                    nmax = argmin(goodvals)
                    if nmax > 0:
                        dat = dat[:nmax]
                        xmins = xmins[:nmax]
                        av = av[:nmax]
                        sigma = sigma[:nmax]
                    else:
                        if not silent: 
                            print "Not enough data left after flagging - using all positive data."
            if not quiet: 
                print "PYTHON plfit executed in %f seconds" % (time.time()-t)
                if usefortran: print "fortran fplfit did not load"
                if usecy: print "cython cplfit did not load"
            self._av = av
            self._xmin_kstest = dat
            self._sigma = sigma
            xmin  = xmins[argmin(dat)] 
        z     = z[z>=xmin]
        n     = len(z)
        alpha = 1 + n / sum( log(z/xmin) )
        if finite:
            alpha = alpha*(n-1.)/n+1./n
        if n < 50 and not finite and not silent:
            print '(PLFIT) Warning: finite-size bias may be present. n=%i' % n
        ks = max(abs( numpy.arange(n)/float(n) - (1-(xmin/z)**(alpha-1)) ))
        # Parallels Eqn 3.5 in Clauset et al 2009, but zeta(alpha, xmin) = (alpha-1)/xmin.  Really is Eqn B3 in paper.
        L = n*log((alpha-1)/xmin) - alpha*sum(log(z/xmin))
        #requires another map... Larr = arange(len(unique(x))) * log((av-1)/unique(x)) - av*sum
        self._likelihood = L
        self._xmin = xmin
        self._xmins = xmins
        self._alpha= alpha
        self._alphaerr = (alpha-1)/numpy.sqrt(n)
        self._ks = ks  # this ks statistic may not have the same value as min(dat) because of unique()
        if scipyOK: self._ks_prob = scipy.stats.kstwobign.sf(ks*numpy.sqrt(n))
        self._ngtx = n
        if n == 1:
            if not silent:
                print "Failure: only 1 point kept.  Probably not a power-law distribution."
            self._alpha = alpha = 0
            self._alphaerr = 0
            self._likelihood = L = 0
            self._ks = 0
            self._ks_prob = 0
            self._xmin = xmin
            return xmin,0
        if numpy.isnan(L) or numpy.isnan(xmin) or numpy.isnan(alpha):
            raise ValueError("plfit failed; returned a nan")

        if not quiet:
            if verbose: print "The lowest value included in the power-law fit, ",
            print "xmin: %g" % xmin,
            if verbose: print "\nThe number of values above xmin, ",
            print "n(>xmin): %i" % n,
            if verbose: print "\nThe derived power-law alpha (p(x)~x^-alpha) with MLE-derived error, ",
            print "alpha: %g +/- %g  " % (alpha,self._alphaerr), 
            if verbose: print "\nThe log of the Likelihood (the maximized parameter; you minimized the negative log likelihood), ",
            print "Log-Likelihood: %g  " % L,
            if verbose: print "\nThe KS-test statistic between the best-fit power-law and the data, ",
            print "ks: %g" % (ks),
            if scipyOK:
                if verbose: print " occurs with probability  ",
                print "p(ks): %g" % (self._ks_prob)
            else:
                print

        return xmin,alpha


    def discrete_best_alpha(self, alpharangemults=(0.9,1.1), n_alpha=201, approximate=True, verbose=True, finite=True):
        """
        Use the maximum L to determine the most likely value of alpha

        *alpharangemults* [ 2-tuple ]
            Pair of values indicating multiplicative factors above and below the
            approximate alpha from the MLE alpha to use when determining the
            "exact" alpha (by directly maximizing the likelihood function)
        """

        data = self.data
        self._xmins = xmins = numpy.unique(data)
        if approximate:
            alpha_of_xmin = [ discrete_alpha_mle(data,xmin) for xmin in xmins ]
        else:
            alpha_approx = [ discrete_alpha_mle(data,xmin) for xmin in xmins ]
            alpharanges = [(0.9*a,1.1*a) for a in alpha_approx]
            alpha_of_xmin = [ most_likely_alpha(data,xmin,alpharange=ar,n_alpha=n_alpha) for xmin,ar in zip(xmins,alpharanges) ]
        ksvalues = numpy.array([ discrete_ksD(data, xmin, alpha) for xmin,alpha in zip(xmins,alpha_of_xmin) ])
        self._av = numpy.array(alpha_of_xmin)
        self._xmin_kstest = ksvalues
        
        ksvalues[numpy.isnan(ksvalues)] = numpy.inf

        best_index = argmin(ksvalues)
        self._alpha = best_alpha = alpha_of_xmin[best_index]
        self._xmin = best_xmin = xmins[best_index]
        self._ks = best_ks = ksvalues[best_index]
        best_likelihood = discrete_likelihood(data, best_xmin, best_alpha)

        if finite:
            self._alpha = self._alpha*(n-1.)/n+1./n

        if verbose:
            print "alpha = %f   xmin = %f   ksD = %f   L = %f   (n<x) = %i  (n>=x) = %i" % (
                    best_alpha, best_xmin, best_ks, best_likelihood,
                    (data<best_xmin).sum(), (data>=best_xmin).sum())


        self._ngtx = n = (self.data>=self._xmin).sum()
        self._alphaerr = (self._alpha-1.0)/numpy.sqrt(n)
        if scipyOK: self._ks_prob = scipy.stats.kstwobign.sf(self._ks*numpy.sqrt(n))

        return best_alpha,best_xmin,best_ks,best_likelihood

    def xminvsks(self, **kwargs):
        """
        Plot xmin versus the ks value for derived alpha.  This plot can be used
        as a diagnostic of whether you have derived the 'best' fit: if there are 
        multiple local minima, your data set may be well suited to a broken 
        powerlaw or a different function.
        """
        
        pylab.plot(self._xmins,self._xmin_kstest,'.')
        pylab.plot(self._xmin,self._ks,'s')
        #pylab.errorbar([self._ks],self._alpha,yerr=self._alphaerr,fmt='+')

        ax=pylab.gca()
        ax.set_ylabel("KS statistic")
        ax.set_xlabel("min(x)")
        pylab.draw()

        return ax

    def alphavsks(self,autozoom=True,**kwargs):
        """
        Plot alpha versus the ks value for derived alpha.  This plot can be used
        as a diagnostic of whether you have derived the 'best' fit: if there are 
        multiple local minima, your data set may be well suited to a broken 
        powerlaw or a different function.
        """
        
        pylab.plot(1+self._av,self._xmin_kstest,'.')
        pylab.errorbar(self._alpha,[self._ks],xerr=self._alphaerr,fmt='+')

        ax=pylab.gca()
        if autozoom:
            ax.set_ylim(0.8*(self._ks),3*(self._ks))
            ax.set_xlim((self._alpha)-5*self._alphaerr,(self._alpha)+5*self._alphaerr)
        ax.set_ylabel("KS statistic")
        ax.set_xlabel(r'$\alpha$')
        pylab.draw()

        return ax

    def plotcdf(self,x=None,xmin=None,alpha=None,**kwargs):
        """
        Plots CDF and powerlaw
        """
        if not(x): x=self.data
        if not(xmin): xmin=self._xmin
        if not(alpha): alpha=self._alpha

        x=numpy.sort(x)
        n=len(x)
        xcdf = numpy.arange(n,0,-1,dtype='float')/float(n)

        q = x[x>=xmin]
        fcdf = (q/xmin)**(1-alpha)
        nc = xcdf[argmax(x>=xmin)]
        fcdf_norm = nc*fcdf

        D_location = argmax(xcdf[x>=xmin]-fcdf_norm)
        pylab.vlines(q[D_location],xcdf[x>=xmin][D_location],fcdf_norm[D_location],color='m',linewidth=2)

        #plotx = pylab.linspace(q.min(),q.max(),1000)
        #ploty = (plotx/xmin)**(1-alpha) * nc

        pylab.loglog(x,xcdf,marker='+',color='k',**kwargs)
        #pylab.loglog(plotx,ploty,'r',**kwargs)
        pylab.loglog(q,fcdf_norm,'r',**kwargs)

    def plotpdf(self,x=None,xmin=None,alpha=None,nbins=50,dolog=True,dnds=False,
            drawstyle='steps-post', histcolor='k', plcolor='r', **kwargs):
        """
        Plots PDF and powerlaw.

        kwargs is passed to pylab.hist and pylab.plot
        """
        if not(x): x=self.data
        if not(xmin): xmin=self._xmin
        if not(alpha): alpha=self._alpha

        x=numpy.sort(x)
        n=len(x)

        pylab.gca().set_xscale('log')
        pylab.gca().set_yscale('log')

        if dnds:
            hb = pylab.histogram(x,bins=numpy.logspace(log10(min(x)),log10(max(x)),nbins))
            h = hb[0]
            b = hb[1]
            db = hb[1][1:]-hb[1][:-1]
            h = h/db
            pylab.plot(b[:-1],h,drawstyle=drawstyle,color=histcolor,**kwargs)
            #alpha -= 1
        elif dolog:
            hb = pylab.hist(x,bins=numpy.logspace(log10(min(x)),log10(max(x)),nbins),log=True,fill=False,edgecolor=histcolor,**kwargs)
            alpha -= 1
            h,b=hb[0],hb[1]
        else:
            hb = pylab.hist(x,bins=numpy.linspace((min(x)),(max(x)),nbins),fill=False,edgecolor=histcolor,**kwargs)
            h,b=hb[0],hb[1]
        # plotting points are at the center of each bin
        b = (b[1:]+b[:-1])/2.0

        q = x[x>=xmin]
        px = (alpha-1)/xmin * (q/xmin)**(-alpha)

        # Normalize by the median ratio between the histogram and the power-law
        # The normalization is semi-arbitrary; an average is probably just as valid
        plotloc = (b>xmin)*(h>0)
        norm = numpy.median( h[plotloc] / ((alpha-1)/xmin * (b[plotloc]/xmin)**(-alpha))  )
        px = px*norm

        plotx = pylab.linspace(q.min(),q.max(),1000)
        ploty = (alpha-1)/xmin * (plotx/xmin)**(-alpha) * norm

        #pylab.loglog(q,px,'r',**kwargs)
        pylab.loglog(plotx,ploty,color=plcolor,**kwargs)

        axlims = pylab.axis()
        pylab.vlines(xmin,axlims[2],max(px),colors=plcolor,linestyle='dashed')

        pylab.gca().set_xlim(min(x),max(x))

    def plotppf(self,x=None,xmin=None,alpha=None,dolog=True,**kwargs):
        """
        Plots the power-law-predicted value on the Y-axis against the real
        values along the X-axis.  Can be used as a diagnostic of the fit 
        quality.
        """
        if not(xmin): xmin=self._xmin
        if not(alpha): alpha=self._alpha
        if not(x): x=numpy.sort(self.data[self.data>xmin])
        else: x=numpy.sort(x[x>xmin])

        # N = M^(-alpha+1)
        # M = N^(1/(-alpha+1))
        
        m0 = min(x)
        N = (1.0+numpy.arange(len(x)))[::-1]
        xmodel = m0 * N**(1/(1-alpha)) / max(N)**(1/(1-alpha))
        
        if dolog:
            pylab.loglog(x,xmodel,'.',**kwargs)
            pylab.gca().set_xlim(min(x),max(x))
            pylab.gca().set_ylim(min(x),max(x))
        else:
            pylab.plot(x,xmodel,'.',**kwargs)
        pylab.plot([min(x),max(x)],[min(x),max(x)],'k--')
        pylab.xlabel("Real Value")
        pylab.ylabel("Power-Law Model Value")

    def test_pl(self,niter=1e3, print_timing=False, **kwargs):
        """
        Monte-Carlo test to determine whether distribution is consistent with a power law

        Runs through niter iterations of a sample size identical to the input sample size.

        Will randomly select values from the data < xmin.  The number of values selected will
        be chosen from a uniform random distribution with p(<xmin) = n(<xmin)/n.

        Once the sample is created, it is fit using above methods, then the best fit is used to
        compute a Kolmogorov-Smirnov statistic.  The KS stat distribution is compared to the 
        KS value for the fit to the actual data, and p = fraction of random ks values greater
        than the data ks value is computed.  If p<.1, the data may be inconsistent with a 
        powerlaw.  A data set of n(>xmin)>100 is required to distinguish a PL from an exponential,
        and n(>xmin)>~300 is required to distinguish a log-normal distribution from a PL.
        For more details, see figure 4.1 and section

        **WARNING** This can take a very long time to run!  Execution time scales as 
        niter * setsize

        """
        xmin = self._xmin
        alpha = self._alpha
        niter = int(niter)

        ntail = sum(self.data >= xmin)
        ntot = len(self.data)
        nnot = ntot-ntail              # n(<xmin)
        pnot = nnot/float(ntot)        # p(<xmin)
        nonpldata = self.data[self.data<xmin]
        nrandnot = sum( npr.rand(ntot) < pnot ) # randomly choose how many to sample from <xmin
        nrandtail = ntot - nrandnot         # and the rest will be sampled from the powerlaw

        ksv = []
        if print_timing: deltat = []
        for i in xrange(niter):
            # first, randomly sample from power law
            # with caveat!  
            nonplind = numpy.floor(npr.rand(nrandnot)*nnot).astype('int')
            fakenonpl = nonpldata[nonplind]
            randarr = npr.rand(nrandtail)
            fakepl = randarr**(1/(1-alpha)) * xmin 
            fakedata = numpy.concatenate([fakenonpl,fakepl])
            if print_timing: t0 = time.time()
            # second, fit to powerlaw
            # (add some silencing kwargs optionally)
            for k,v in {'quiet':True,'silent':True,'nosmall':True}.iteritems():
                if k not in kwargs:
                    kwargs[k] = v
            TEST = plfit(fakedata,**kwargs)
            ksv.append(TEST._ks)
            if print_timing: 
                deltat.append( time.time() - t0 )
                print "Iteration %i: %g seconds" % (i, deltat[-1])
        
        ksv = numpy.array(ksv)
        p = (ksv>self._ks).sum() / float(niter)
        self._pval = p
        self._ks_rand = ksv

        print "p(%i) = %0.3f" % (niter,p)
        if print_timing: print "Iteration timing: %g +/- %g" % (numpy.mean(deltat),numpy.std(deltat))

        return p,ksv

    def lognormal(self,doprint=True):
        """
        Use the maximum likelihood estimator for a lognormal distribution to
        produce the best-fit lognormal parameters
        """
        # N = float(self.data.shape[0])
        # mu = log(self.data).sum() / N
        # sigmasquared = ( ( log(self.data) - mu )**2 ).sum() / N
        # self.lognormal_mu = mu
        # self.lognormal_sigma = numpy.sqrt(sigmasquared)
        # self.lognormal_likelihood = -N/2. * log(numpy.pi*2) - N/2. * log(sigmasquared) - 1/(2*sigmasquared) * (( self.data - mu )**2).sum()
        # if doprint:
        #     print "Best fit lognormal is exp( -(x-%g)^2 / (2*%g^2)" % (mu,numpy.sqrt(sigmasquared))
        #     print "Likelihood: %g" % (self.lognormal_likelihood)
        if scipyOK:
            fitpars = scipy.stats.lognorm.fit(self.data)
            self.lognormal_dist = scipy.stats.lognorm(*fitpars)
            self.lognormal_ksD,self.lognormal_ksP = scipy.stats.kstest(self.data,self.lognormal_dist.cdf)
            # nnlf = NEGATIVE log likelihood
            self.lognormal_likelihood = -1*scipy.stats.lognorm.nnlf(fitpars,self.data)

            # Is this the right likelihood ratio?
            # Definition of L from eqn. B3 of Clauset et al 2009:
            # L = log(p(x|alpha))
            # _nnlf from scipy.stats.distributions:
            # -sum(log(self._pdf(x, *args)),axis=0)
            # Assuming the pdf and p(x|alpha) are both non-inverted, it looks
            # like the _nnlf and L have opposite signs, which would explain the
            # likelihood ratio I've used here:
            self.power_lognorm_likelihood = (self._likelihood + self.lognormal_likelihood)
            # a previous version had 2*(above).  That is the correct form if you want the likelihood ratio
            # statistic "D": http://en.wikipedia.org/wiki/Likelihood-ratio_test
            # The above explanation makes sense, since nnlf is the *negative* log likelihood function:
            ## nnlf  -- negative log likelihood function (to minimize)
            #
            # Assuming we want the ratio between the POSITIVE likelihoods, the D statistic is:
            # D = -2 log( L_power / L_lognormal )
            self.likelihood_ratio_D = -2 * (log(self._likelihood/self.lognormal_likelihood))
            
            if doprint: 
                print "Lognormal KS D: %g  p(D): %g" % (self.lognormal_ksD,self.lognormal_ksP),
                print "  Likelihood Ratio Statistic (powerlaw/lognormal): %g" % self.likelihood_ratio_D
                print "At this point, have a look at Clauset et al 2009 Appendix C: determining sigma(likelihood_ratio)"

    def plot_lognormal_pdf(self,**kwargs):
        """
        Plot the fitted lognormal distribution
        """
        if not hasattr(self,'lognormal_dist'):
            return
        
        normalized_pdf = self.lognormal_dist.pdf(self.data)/self.lognormal_dist.pdf(self.data).max()
        minY,maxY = pylab.gca().get_ylim()
        pylab.plot(self.data,normalized_pdf*maxY,'.',**kwargs)

    def plot_lognormal_cdf(self,**kwargs):
        """
        Plot the fitted lognormal distribution
        """
        if not hasattr(self,'lognormal_dist'):
            return

        x=numpy.sort(self.data)
        n=len(x)
        xcdf = numpy.arange(n,0,-1,dtype='float')/float(n)
        lcdf = self.lognormal_dist.sf(x)

        D_location = argmax(xcdf-lcdf)
        pylab.vlines(x[D_location],xcdf[D_location],lcdf[D_location],color='m',linewidth=2)
        
        pylab.plot(x, lcdf,',',**kwargs)


def plfit_lsq(x,y):
    """
    Returns A and B in y=Ax^B
    http://mathworld.wolfram.com/LeastSquaresFittingPowerLaw.html
    """
    n = len(x)
    btop = n * (log(x)*log(y)).sum() - (log(x)).sum()*(log(y)).sum()
    bbottom = n*(log(x)**2).sum() - (log(x).sum())**2
    b = btop / bbottom
    a = ( log(y).sum() - b * log(x).sum() ) / n

    A = exp(a)
    return A,b

def plexp(x,xm=1,a=2.5):
    """
    CDF(x) for the piecewise distribution exponential x<xmin, powerlaw x>=xmin
    This is the CDF version of the distributions drawn in fig 3.4a of Clauset et al.
    """

    C = 1/(-xm/(1 - a) - xm/a + exp(a)*xm/a)
    Ppl = lambda(X): 1+C*(xm/(1-a)*(X/xm)**(1-a))
    Pexp = lambda(X): C*xm/a*exp(a)-C*(xm/a)*exp(-a*(X/xm-1))
    d=Ppl(x)
    d[x<xm]=Pexp(x)
    return d

def plexp_inv(P,xm,a):
    """
    Inverse CDF for a piecewise PDF as defined in eqn. 3.10
    of Clauset et al.  
    """

    C = 1/(-xm/(1 - a) - xm/a + exp(a)*xm/a)
    Pxm = 1+C*(xm/(1-a))
    x = P*0
    x[P>=Pxm] = xm*( (P[P>=Pxm]-1) * (1-a)/(C*xm) )**(1/(1-a)) # powerlaw
    x[P<Pxm] = (log( (C*xm/a*exp(a)-P[P<Pxm])/(C*xm/a) ) - a) * (-xm/a) # exp

    return x

def pl_inv(P,xm,a):
    """ 
    Inverse CDF for a pure power-law
    """
    
    x = (1-P)**(1/(1-a)) * xm
    return x

def test_fitter(xmin=1.0,alpha=2.5,niter=500,npts=1000,invcdf=plexp_inv):
    """
    Tests the power-law fitter 

    Example (fig 3.4b in Clauset et al.)::

        xminin=[0.25,0.5,0.75,1,1.5,2,5,10,50,100]
        xmarr,af,ksv,nxarr = plfit.test_fitter(xmin=xminin,niter=1,npts=50000)
        loglog(xminin,xmarr.squeeze(),'x')

    Example 2::

        xminin=[0.25,0.5,0.75,1,1.5,2,5,10,50,100]
        xmarr,af,ksv,nxarr = plfit.test_fitter(xmin=xminin,niter=10,npts=1000)
        loglog(xminin,xmarr.mean(axis=0),'x')

    Example 3:

        xmarr,af,ksv,nxarr = plfit.test_fitter(xmin=1.0,niter=1000,npts=1000)
        hist(xmarr.squeeze());
        # Test results:
        # mean(xmarr) = 0.70, median(xmarr)=0.65 std(xmarr)=0.20
        # mean(af) = 2.51 median(af) = 2.49  std(af)=0.14
        # biased distribution; far from correct value of xmin but close to correct alpha
    
    Example 4:

        xmarr,af,ksv,nxarr = plfit.test_fitter(xmin=1.0,niter=1000,npts=1000,invcdf=pl_inv)
        print("mean(xmarr): %0.2f median(xmarr): %0.2f std(xmarr): %0.2f" % (mean(xmarr),median(xmarr),std(xmarr)))
        print("mean(af): %0.2f median(af): %0.2f std(af): %0.2f" % (mean(af),median(af),std(af)))
        # mean(xmarr): 1.19 median(xmarr): 1.03 std(xmarr): 0.35
        # mean(af): 2.51 median(af): 2.50 std(af): 0.07

    """
    xmin = numpy.array(xmin)
    if xmin.shape == ():
        xmin.shape = 1
    lx = len(xmin)
    sz = [niter,lx]
    xmarr,alphaf_v,ksv,nxarr = numpy.zeros(sz),numpy.zeros(sz),numpy.zeros(sz),numpy.zeros(sz)
    for j in xrange(lx):
        for i in xrange(niter):
            randarr = npr.rand(npts)
            fakedata = invcdf(randarr,xmin[j],alpha)
            TEST = plfit(fakedata,quiet=True,silent=True,nosmall=True)
            alphaf_v[i,j] = TEST._alpha
            ksv[i,j] = TEST._ks
            nxarr[i,j] = TEST._ngtx
            xmarr[i,j] = TEST._xmin

    return xmarr,alphaf_v,ksv,nxarr




def discrete_likelihood(data, xmin, alpha):
    """
    Equation B.8 in Clauset

    Given a data set, an xmin value, and an alpha "scaling parameter", computes
    the log-likelihood (the value to be maximized) 
    """
    if not scipyOK:
        raise ImportError("Can't import scipy.  Need scipy for zeta function.")
    from scipy.special import zeta as zeta

    zz = data[data>=xmin]
    nn = len(zz)

    sum_log_data = numpy.log(zz).sum()

    zeta = zeta(alpha, xmin)

    L_of_alpha = -1*nn*log(zeta) - alpha * sum_log_data

    return L_of_alpha

def discrete_likelihood_vector(data, xmin, alpharange=(1.5,3.5), n_alpha=201):
    """
    Compute the likelihood for all "scaling parameters" in the range (alpharange)
    for a given xmin.  This is only part of the discrete value likelihood
    maximization problem as described in Clauset et al
    (Equation B.8)

    *alpharange* [ 2-tuple ] 
        Two floats specifying the upper and lower limits of the power law alpha to test
    """
    from scipy.special import zeta as zeta

    zz = data[data>=xmin]
    nn = len(zz)

    alpha_vector = numpy.linspace(alpharange[0],alpharange[1],n_alpha)
    sum_log_data = numpy.log(zz).sum()

    # alpha_vector is a vector, xmin is a scalar
    zeta_vector = zeta(alpha_vector, xmin)

    #xminvec = numpy.arange(1.0,xmin)

    #xminalphasum = numpy.sum([xm**(-alpha_vector) for xm in xminvec])
    #L = -1*alpha_vector*sum_log_data - nn*log(zeta_vector) - xminalphasum

    L_of_alpha = -1*nn*log(zeta_vector) - alpha_vector * sum_log_data

    return L_of_alpha

def discrete_max_likelihood_arg(data, xmin, alpharange=(1.5,3.5), n_alpha=201):
    """
    Returns the *argument* of the max of the likelihood of the data given an input xmin
    """
    likelihoods = discrete_likelihood_vector(data, xmin, alpharange=alpharange, n_alpha=n_alpha)
    Largmax = numpy.argmax(likelihoods)
    return Largmax

def discrete_max_likelihood(data, xmin, alpharange=(1.5,3.5), n_alpha=201):
    """
    Returns the *argument* of the max of the likelihood of the data given an input xmin
    """
    likelihoods = discrete_likelihood_vector(data, xmin, alpharange=alpharange, n_alpha=n_alpha)
    Lmax = numpy.max(likelihoods)
    return Lmax

def most_likely_alpha(data, xmin, alpharange=(1.5,3.5), n_alpha=201):
    """
    Return the most likely alpha for the data given an xmin
    """
    alpha_vector = numpy.linspace(alpharange[0],alpharange[1],n_alpha)
    return alpha_vector[discrete_max_likelihood_arg(data, xmin, alpharange=alpharange, n_alpha=n_alpha)]

def discrete_alpha_mle(data, xmin): 
    """
    Equation B.17 of Clauset et al 2009

    The Maximum Likelihood Estimator of the "scaling parameter" alpha in the
    discrete case is similar to that in the continuous case
    """
    # boolean indices of positive data
    gexmin = (data>=xmin)
    nn = gexmin.sum()
    if nn < 2:
        return 0
    xx = data[gexmin]
    alpha = 1.0 + float(nn) * ( sum(log(xx/(xmin-0.5))) )**-1
    return alpha

def discrete_best_alpha(data, alpharangemults=(0.9,1.1), n_alpha=201, approximate=True, verbose=True):
    """
    Use the maximum L to determine the most likely value of alpha

    *alpharangemults* [ 2-tuple ]
        Pair of values indicating multiplicative factors above and below the
        approximate alpha from the MLE alpha to use when determining the
        "exact" alpha (by directly maximizing the likelihood function)
    """

    xmins = numpy.unique(data)
    if approximate:
        alpha_of_xmin = [ discrete_alpha_mle(data,xmin) for xmin in xmins ]
    else:
        alpha_approx = [ discrete_alpha_mle(data,xmin) for xmin in xmins ]
        alpharanges = [(0.9*a,1.1*a) for a in alpha_approx]
        alpha_of_xmin = [ most_likely_alpha(data,xmin,alpharange=ar,n_alpha=n_alpha) for xmin,ar in zip(xmins,alpharanges) ]
    ksvalues = [ discrete_ksD(data, xmin, alpha) for xmin,alpha in zip(xmins,alpha_of_xmin) ]
    
    best_index = argmin(ksvalues)
    best_alpha = alpha_of_xmin[best_index]
    best_xmin = xmins[best_index]
    best_ks = ksvalues[best_index]
    best_likelihood = discrete_likelihood(data, best_xmin, best_alpha)

    if verbose:
        print "alpha = %f   xmin = %f   ksD = %f   L = %f   (n<x) = %i  (n>=x) = %i" % (
                best_alpha, best_xmin, best_ks, best_likelihood,
                (data<best_xmin).sum(), (data>=best_xmin).sum())

    return best_alpha,best_xmin,best_ks,best_likelihood


def discrete_ksD(data, xmin, alpha):
    """
    given a sorted data set, a minimum, and an alpha, returns the power law ks-test
    D value w/data

    The returned value is the "D" parameter in the ks test
    
    (this is implemented differently from the continuous version because there
    are potentially multiple identical points that need comparison to the power
    law)
    """
    zz = numpy.sort(data[data>=xmin])
    nn = float(len(zz))
    if nn < 2: return numpy.inf
    #cx = numpy.arange(nn,dtype='float')/float(nn)
    #cf = 1.0-(zz/xmin)**(1.0-alpha)
    model_cdf = 1.0-(zz/xmin)**(1.0-alpha)
    data_cdf  = numpy.searchsorted(zz,zz,side='left')/(float(nn))

    ks = max(abs(model_cdf-data_cdf))
    return ks