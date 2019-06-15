""" 
Module for data interpolation using rational histosplines.
The main algorithm is a numpy re-implementation of rhist2 in 
    One Dimensional Spline Interpolation Algorithms
    by Helmuth Spath (1995).
The benefit of histosplines is that they are designed to
conserve the integral under the curve, and so they are good
for period averaged data when you want the
interpolator to conserve mass.
"""

import numpy as np

def rhist_bound(x,y,xnew,y0,yn,p,lbound=None,
                maxiter=5,pfactor=2,floor_eps=1e-3):
    """
    Histopline for arrays with lower bound enforcement.
    This routine drives rhist() but tests that the output
    array observes the lower bound and adapts the tension parameters as needed. 
       
    This will not work exactly if the input
    array has values right on the lower bound. In this case,
    the parameter floor_eps allows you to specify a tolerance
    of bound violation to shoot for ... and if it isn't met in maxiter iterations the value is simply floored.
       
    Parameters
    ----------
    x : array-like
        Abscissa array of original data to be interpolated,
        of length n
        
    y : array-like, dimension (n-1)
        Values (mantissa) of original data giving the rectangle (average) values between x[i] and x[i+1] 

    xnew : array-like
        Array of new locations at which to interpolate.
        
    y0,yn : float
        Initial and terminal values
         
    p: float
        Tension parameter. This starts out as a global scalar, but will be converted to an array and adapted locally. 
        The higher this goes for a particular x interval, the more rectangular the interpolant will look and the more 
        positivity and shape preserving it is at the expense
        of accuracy. A good number is 1, and for this routine,
        p > 0 is required because the adaptive process multiplies it by pfactor each iteration on the expectation that it will get bigger.
        
    lbound: float
        Lower bound to be enforced. If the original y's are strictly above this value, the output has the potential to also be strictly above. If the original y's lie on the lower bound, then the lower bound can only be enforced within a tolerance using the Spath algorithm ...
        and once the values reach that tolerance they are floored. If lbound = None, this function behaves like rhist()
        
    maxiter : integer
        Number of times to increase p by multiplying it by pfactor before giving up on satisfying floor_eps.
        
    pfactor : float
        Factor by which to multiply individual time step p
        
    floor_eps : float 
        Tolerance for lower bound violation at which the algorithm will be terminated and the bounds will be enforced by flooring.

    Returns
    -------    
    ynew : array-like
        Array that interpolates the original data, on a curve that conserves mass and strictly observes the lower bound.

    """
    if type(p) == float:
        p = ones_like(y)*p
    q=p
    ynew = rhist(x,y,xnew,y0,yn,p,q)
    if lbound != None:
        iter = 0
        bound_viol = lbound - ynew.min()
        while(bound_viol > floor_eps and iter < maxiter):
            iter += 1
            print("Iteration %s" % iter)
            print(ynew.min() - lbound)
            xbad = xnew[ynew < lbound]
            bad_ndx_left = np.minimum(np.searchsorted(x,xbad,side="right"),len(x)-1) -1 
            p[bad_ndx_left] *= pfactor
            q[bad_ndx_left] *= pfactor
            ynew = rhist(x,y,xnew,y0,yn,p,q)
            bound_viol = lbound - ynew.min()
        if bound_viol <= floor_eps:
            if bound_viol < 0.: 
                return ynew
            else:
                return np.maximum(ynew,lbound)
        else:
            raise Exception("Failed to meet lower bound criterion within maxiter iterations")
    return ynew


def rhist(x,y,xnew,y0,yn,p,q):
    """
    Histopline for arrays with tension.
    Based by an algorithm rhist2 in 
    One Dimensional Spline Interpolation Algorithms
    by Helmuth Spath (1995).
           
    Parameters
    ----------
    x : array-like
        Abscissa array of original data,
        of length n
        
    y : array-like, dimension (n-1)
        Values (mantissa) of original data giving the rectangle (average) values between x[i] and x[i+1] 

    xnew : array-like
        Array of new locations at which to interpolate.
        
    y0,yn : float
        Initial and terminal values
         
    p,q: array-like, dimension (n-1)
        Tension parameter, p and q are almost always the same. The higher p and q are for a particular x interval, the more rectangular the interpolant will look and the more 
        positivity and shape preserving it is at the expense
        of accuracy. For this routine any number p,q > -1 is allowed, although the bound routine doesn't use vals less
        than zero. 
    Returns
    -------    
    ynew : array-like
        Array that interpolates the original data.
    """
    if not xnew[0] >= x[0] and xnew[-1] <= x[-1]:
        raise ValueError("Range of xnew must lie in range of original abscissca values (x)")    
    a,b,c = rhist_coef(x,y,y0,yn,p,q)
    return rhist_val(xnew,x,p,q,a,b,c)

def rhist_coef(x,y,y0,yn,p,q):
    """ Routine that produces coefficients for the histospline"""
    n = len(x)
    nintvl = n-1
    if n < 3:
        raise ValueError("Minimum input array size is 3")
    if len(y) != nintvl:
        raise ValueError("Argument y should have len equal to the number of intervals, one smaller than x")
    if len(p) != nintvl:
        raise ValueError("Argument p should have len equal to the number of intervals, one smaller than x")
    if len(q) != nintvl:
        raise ValueError("Argument q should have len equal to the number of intervals, one smaller than x")
    # calculate cumulative sum of values of y
    xdiff=np.ediff1d(x,to_begin=[0.])    
    ycum= xdiff.copy()
    ycum[1:] *= y
    ycum = np.cumsum(ycum)
    
    a,b,c,d = _ratsp1(x,ycum,p,q,y0,yn)
    
    h=1./xdiff[1:]
    a = h*(b-a)
    b = h*c
    c = -h*d
      
    return a,b,c

def _ratsp1(x,y,p,q,y0,yn):
    """RATSP1 in Spath (1995)"""
    n = len(x)
    nintvl = n-1
    if n < 3: 
        raise ValueError("Input array must have len > 3")
    
    if len(p) != nintvl:
        raise ValueError("Input argument p must be equal to the number of intervals in the series (one smaller than x)")
    if len(q) != nintvl:
        raise ValueError("Input argument p must be equal to the number of intervals in the series (one smaller than x)")
    a = np.zeros(nintvl,dtype='d')
    b = np.zeros_like(a)
    c = np.zeros_like(a)
    d = np.zeros_like(a)
    y1 = np.zeros_like(x) # work array, larger
    
    
    y1[0]  = y0
    y1[-1] = yn
    
    xdiff=np.ediff1d(x)
    ydiff=np.ediff1d(y)  
    h=1./xdiff
    pk2=p*(p+3.)+3.
    qk2=q*(q+3.)+3.
    p22=2.+p
    q22=2.+q
    
    if (np.any(p < -1) or np.any(q < -1)):
        raise ValueError("p and q arguments must be >= -1")
    
    print("n=%s len(a)=%s len(xdiff)=%s" % (n,len(a),len(xdiff))) 
    a = 1./(p22*q22-1.)
    g2=h*a
    r2=h*g2*ydiff
    p21=p22[:-1]
    qk1=qk2[:-1]
    g1=g2[:-1]
    r1=r2[:-1]
    p22s=p22[1:]
    q22s=q22[1:]
    qk2s=qk2[1:]
    g2s=g2[1:]
    r2s=r2[1:]
    pk2s=pk2[1:]
    # b is lower diagonal, so padded with 0
    b[1:] = qk2[1:]*g2[1:] 
    c = qk1*p21*g1 + pk2s*q22s*g2s
    d[:-1] = pk2s*g2s
    y1[0:-2]=r1*qk1*(1.+p21) + r2s*pk2s*(1.+q22s)
    y1[0] -= qk1[1]*g1[1]*y0
    y1[-3] -= pk2[-1]*g2[-1]*yn
    x = tridiagonal(b[:-1],c,d[:-1],y1[0:-2])
    y1[1:-1] = x
    y1[0]=y0
    y1[-1]=yn
    h = a*ydiff
    z = a*xdiff
    d=-(1.+p22)*h+z*(p22*y1[1:]+y1[:-1])
    c= (1.+q22)*h-z*(y1[1:]+q22*y1[:-1])
    b=y[1:]-d
    a=y[:-1]-c
    return a,b,c,d


## Tri-diagonal matrix Algorithm(a.k.a Thomas algorithm) solver
def tridiagonal(a, b, c, d):
    '''
    a is the lower band (with leading zero)
    b is the center diagonal (length == nrow)
    c is upper band (trailing zero)
    d is right hand side
    '''
    nf = len(a)     # number of equations
    ac, bc, cc, dc = list(map(np.array, (a, b, c, d)))     # copy the array
    for it in range(1, nf):
        mc = ac[it]/bc[it-1]
        bc[it] = bc[it] - mc*cc[it-1] 
        dc[it] = dc[it] - mc*dc[it-1]
    xc = ac
    xc[-1] = dc[-1]/bc[-1]
    for il in range(nf-2, -1, -1):
        xc[il] = (dc[il]-cc[il]*xc[il+1])/bc[il]
    del bc, cc, dc  # delete variables from memory
    return xc

def rhist_val(xnew,x,p,q,a,b,c):
    """ Evaluate a histospline at new x points"""
    n = len(x)
    nintvl = n-1
    if n < 3: raise ValueError("Length of array x must be > 3")
    if len(a) != nintvl: 
        raise ValueError("Length of array a must be same as number of intervals (one less than x)")
    ndx_right = np.minimum(np.searchsorted(x,xnew,side="right"),n-1)
    ndx_left = ndx_right-1
    t = (xnew-x[ndx_left])/(x[ndx_right] - x[ndx_left])
    u=1.- t
    p_left = p[ndx_left]
    q_left = q[ndx_left]
    h1=p_left*t+1.
    h2=q_left*u+1.
    val= a[ndx_left] \
         + b[ndx_left]*u*u*(2.*p_left*u-3.*(1.+p_left))/(h1*h1) \
         + c[ndx_left]*t*t*(2.*q_left*t-3.*(1.+q_left))/(h2*h2)
    return val 


    
    
