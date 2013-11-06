from numpy import *

# Interpolating spline
# Eli Ateljevich 9/27/99


#
def _minmod(x,y):
    return where(x*y>0,
        sign(x)*minimum(abs(x),abs(y)),
        0.)
#
def _monotonic_spline(x,y,xnew):
    """
    Third order (M3-A) monotonicity-preserving spline
    Usage:          interpolate.spline(x,y,xnew)

	where
	    x are the sorted index values of the original data
	    y are the original dataxnew
	    xnew are new locations for the spline


   	Reference: Huynh, HT <<Accurate Monotone Cubic Interpolation>>,
   	SIAM J. Numer. Analysis V30 No. 1 pp 57-100 
   	All equation numbers refer to this paper. The variable names are 
   	also almost the same. Double letters like "ee" to indicate 
   	that the subscript should have "+1/2" added to it and a number after
   	the variable to show the "t" that the first member applies to.
   	"""

    diffx=diff(x)
    dbl_diff1=x[2:]-x[:-2]     
    ss0=diff(y)/diffx         # [2.1]
    
    # d1 is paddedis the following right? seems like a boundary condition
    n=len(x)-1
    d0=zeros(n+1,'d')
    d0[1:-1]=diff(ss0)/dbl_diff1      # [3.1]
    d0[0]=d0[1]
    d0[n]=d0[n-1]

    # minmod-based estimates
    s1 = _minmod(ss0[:-1],ss0[1:])  #[2.8]
    dd0 = _minmod(d0[:-1],d0[1:])


    #polynomial slopes
    dpp_left1 = ss0[:-1] + dd0[:-1]*diffx[:-1]   #theorem 1 (from 3.5)
    dpp_right1 = ss0[1:] - dd0[1:]*diffx[1:]     #theorem 1 (from 3.13)
    t1 = _minmod(dpp_left1,dpp_right1)
    fdot=zeros(n+1,'d')
    fdot[1:-1]=0.5*(dpp_left1+dpp_right1)
    fdot[1:-1]=_minmod(fdot[1:-1],t1)

    #boundary [5.1]
    fdot[0]=ss0[0]+d0[1]*(x[0]-x[1])
    fdot[n]=ss0[n-1]+d0[n-1]*(x[n]-x[n-1])

    #perform interpolation
    ssort=searchsorted(x,xnew)-1
    left=clip(ssort,0,len(x)-2)

    
    #left=searchsorted(x,xnew)
    xdist=xnew-x[left]
    c2=(3.*ss0-2.*fdot[:-1] - fdot[1:])/diffx
    c3=(fdot[:-1]+fdot[1:]-2.0*ss0)/(diffx**2.)
    out=y[left] + fdot[left]*xdist + +c2[left]*xdist**2. + c3[left]*xdist**3.;
    return out

if __name__ == "__main__":
    x=arange(0.,20.,2.)
    y=sin(x/4.)
    xnew=arange(0.,18,.5)
    out=spline(x,y,xnew)

