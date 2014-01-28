import sys
import datetime as _datetime
import os
from numpy import arange,loadtxt,put
from numpy import nan,cos,pi
from scipy.special import jn
from timeseries import *
from constants import *
from vtime import *


def create_sample_series():
    numpoints=100000
    arr=arange(numpoints)
    low = -5
    high = 85.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    stime1=_datetime.datetime(1992,3,7)
    stime2=_datetime.datetime(1992,3,7,1,0)
    dt=time_interval(minutes=15)
    ts1=rts(jn(1,x),stime1,dt,None)
    ts1.data[11100:13900] = nan
    ts1.data[18300:19800] = nan
    ts1.data[34000:37000] = nan
    ts2=rts(jn(2,x),stime2,dt,None)
    ts3=rts(jn(3,x),stime1,dt,None)
    ts4=rts(jn(4,x),stime1,dt,None)
    return (ts1,ts2,ts3,ts4)

def _synthetic_tide(t):
    principal_tide_components=[ \
    ##O1
    (6.759775e-05 ,1.12898 ,7.95342),\
    ##K1
    (7.292117e-05,1.07731,206.56352),\
    ##Q1
    (6.495457e-05,1.15212,282.20352),\
    ##P1
    (7.251056e-05, 0.99465 ,40.40973),\
    ##K2
    (1.458423e-04,1.19194,233.73387),\
    ##N2
    (1.378797e-04,0.97487,131.77513),\
    ##M2
    (1.405189e-04,0.97799,217.03899),\
    ##S2
    (1.454441e-04,1.00142,239.89972)]
    
    tide=0.0
    
    for freq,amp,phase in  principal_tide_components:
        tide=tide+amp*cos(freq*t+phase*pi/180)
    return tide
    

def synthetic_tide_series():
    """ Return a week long synthetic tide
	
    """
    
    a_week_seconds=24*7*3600
    step=15*60
    times = arange(0,a_week_seconds,step)
    data=map(_synthetic_tide,times)
    start_time=_datetime.datetime(1992,1,1)
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"meter"}
    dt=time_interval(minutes=15)
    ts=rts(data,start_time,dt,props)
    return ts
        
    
    

def example_data(name):
    
    if (name=="pt_reyes_tidal_6min"):
	     return pt_reyes_tidal_6min_interval()
    elif (name=="pt_reyes_tidal_1hour"):
	     return pt_reyes_tidal_1hour_interval()
    elif (name=="pt_reyes_tidal_with_gaps"):
	     return pt_reyes_tidal_with_gaps()
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
 
    data_file=os.path.join(os.path.split(__file__)[0],"CO-OPS__9415020__wl_6min.txt")
    raw_data=loadtxt(data_file,converters={0:_datetime_convertor},skiprows=1,delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    return rts(raw_data[:,1],start,interval,props)
	

def pt_reyes_tidal_1hour_interval():
    """ Sea surface level at Point Reyes from NOAA downsampled to 1hour interval from 11/01/2013-11/08/2013
	
    """
    
    data_file=os.path.join(os.path.split(__file__)[0],"CO-OPS_9415020_wl_1hour.txt")
    raw_data=numpy.loadtxt(data_file,converters={0:_datetime_convertor},skiprows=1,delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    return rts(raw_data[:,1],start,interval,props)
	
def pt_reyes_tidal_with_gaps():
    """ Sea surface level at Point Reys with gaps of different length"
	
	"""

    data_file=os.path.join(os.path.split(__file__)[0],"CO-OPS__9415020__wl_6min.txt")
    raw_data=loadtxt(data_file,skiprows=1,converters={0:_datetime_convertor},delimiter=",")
    start=ticks_to_time(raw_data[:,0][0])
    interval=ticks_to_interval(raw_data[:,0][1]-raw_data[:,0][0])
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    put(raw_data[:,1],range(12,14),nan)
    put(raw_data[:,1],range(20,23),nan)
    put(raw_data[:,1],range(26,45),nan)
    return rts(raw_data[:90,1],start,interval,props)
    
    
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


    
    
    


    
