import sys
import datetime
from numpy import arange,loadtxt,put
from numpy import nan
from scipy.special import jn
from timeseries import *
from  constants import *
from vtime import *


def create_sample_series():
    numpoints=100000
    arr=arange(numpoints)
    low = -5
    high = 85.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    stime1=datetime(1992,3,7)
    stime2=datetime(1992,3,7,1,0)
    dt=time_interval(minutes=15)
    ts1=rts(jn(1,x),stime1,dt,None)
    ts1.data[11100:13900] = nan
    ts1.data[18300:19800] = nan
    ts1.data[34000:37000] = nan
    ts2=rts(jn(2,x),stime2,dt,None)
    ts3=rts(jn(3,x),stime1,dt,None)
    ts4=rts(jn(4,x),stime1,dt,None)
    return (ts1,ts2,ts3,ts4)


def example_data(name):
  
    if (name=="pt_reyes_tidal_6min"):
	     return pt_reyes_tidal_6min_interval()
    elif (name=="pt_reyes_tidal_1hour"):
	     return pt_reyes_tidal_1hour_interval()
    elif (name=="pt_reys_tidal_with_gaps"):
	     return pt_reys_tidal_with_gaps()
    else:
	    raise ValueError("invalid example series name")
		
		
def _datetime_convertor(time_str):
    """ Convert input datetime string into vtools ticks
	
	"""
	
    a_t=parse_time(time_str)
    return ticks(a_t)
	

def pt_reyes_tidal_6min_interval():
    """ Sea surface level at Point Reyes from NOAA with 6 min interval from 11/24/2013-11/25/2013
	
	"""
	
    raw_data=loadtxt("CO-OPS__9415020__wl_6min.txt",converters={0:_datetime_convertor},skiprows=1,delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    return rts(raw_data[:,1],start,interval,props)
	

def pt_reyes_tidal_1hour_interval():
    """ Sea surface level at Point Reyes from NOAA downsampled to 1hour interval from 11/01/2013-11/08/2013
	
	"""
	
    raw_data=numpy.loadtxt("CO-OPS_9415020_wl_1hour.txt",converters={0:_datetime_convertor},skiprows=1,delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    return rts(raw_data[:,1],start,interval,props)
	
def pt_reys_tidal_with_gaps():
    """ Sea surface level at Point Reys with gaps of different length"
	
	"""
	
    raw_data=loadtxt("CO-OPS__9415020__wl_6min.txt",skiprows=1,converters={0:_datetime_convertor},delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    put(data[:,1],range(12,14),nan)
    put(data[:,1],range(150,160),nan)
    put(data[:,1],range(300,303),nan)
    return rts(raw_data[:,1],start,interval,props)
    
    
def arma(phi,theta,sigma,n,discard=0,verbose=0):

    """ Generate a Gaussian ARMA(p,q) series. 
    This was obtained from stack exchange and is not written in terms of 
    a time series ... however it can be used as an ingredient in a time series
    providing correlated random noise

    Parameters
    ----------

    phi : array
    An array of length p with the AR coefficients (the AR part of the ARMA model).

    theta : array
    An array of length q with the MA coefficients (the MA part of the ARMA model).

    sigma : float
    Standard deviation of the Gaussian noise.

    n :        Length of the returned series.

    discard:   Number of data points that are going to be discarded (the higher 
          the better) to avoid dependence of the ARMA time-series on the initial values.
          
    Returns
    -------
    Numpy array from an ARMA(p,q) process
    
    """ 
    from numpy import append,array
    from numpy.random import normal

    l=max(len(phi),len(theta))
    if(discard==0):
      discard=10*l # Burn-in elements!
    w=normal(0,sigma,n+discard)
    arma=array([])
    s=0.0
    l=max(len(phi),len(theta))
    for i in range(n+discard):
        if(i<l):
          arma=append(arma,w[i])
        else:
          s=0.0
          for j in range(len(phi)):
              s=s+phi[j]*arma[i-j-1]
          for j in range(len(theta)):
              s=s+theta[j]*w[i-j-1]
          arma=append(arma,s+w[i])
    if(verbose!=0):
      print 'Measured standard deviation: '+str(sqrt(var(w[discard:])))
    return arma[discard:]


    
    
    


    
