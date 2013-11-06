""" Module contains filter used in tidal time series analysis. 
"""

## Python libary import.

## Scipy import.
from scipy import array as sciarray
from scipy import nan, isnan,add,convolve, \
transpose
from scipy.signal import lfilter
from scipy.signal.filter_design import butter

## Vtool vtime import.

from vtools.data.vtime import *
from vtools.data.timeseries import rts
from vtools.data.constants import *

__all__=["tide_butterworth"]



## This dic saves the missing points for different intervals. 
first_point={time_interval(minutes=15):48,time_interval(hours=1):36}

## This dic store tide butterworth filter' cut-off frequencies for 
## tide time series analysis, here set cutoff frequency at 0.8 cycle/day
## ,but it is represented as a ratio to Nyquist frequency for two
## sample intervals.
butterworth_cutoff_frequecies={time_interval(minutes=15):0.4/(48),\
                               time_interval(hours=1):0.4/12}

## supported interval
_butterworth_interval=[time_interval(minutes=15),time_interval(hours=1)]

########################################################################### 
## Public interface.
###########################################################################

def tide_butterworth(ts,order=2,cutoff_frequence=None):
    
    """ low-pass butterworth filter on a regular time series.
        default order is 4, if no cutoff_frequence
        is given, default will be used.

        input:
            ts: regular time series to be filtered.
            order: order of the filter,int.
            cutoff_frequence: cut_off frequence represented
            by ratio of Nyquist frequency, should within (0,1).
        output:
           a new regular time series with the same 
           interval of ts.
    """

    if not ts.is_regular():
        raise ValueError("Only regular time series can be filtered.")
    
    interval=ts.interval
    
    if not interval in _butterworth_interval:
        raise ValueError("time interval is not supported by butterworth.")
    
    cf=cutoff_frequence
    if cf==None:
        cf=butterworth_cutoff_frequecies[interval]
        
    ## get butter filter coefficients.
    [b,a]=butter(order,cf)
    d1=lfilter(b, a, ts.data,0)
    dr=d1[::-1].copy()
    d2=lfilter(b,a,dr,0)
    d2r=d2[::-1].copy()
    
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    return rts(d2r,ts.start,ts.interval,prop)
    
   




def steps_per_interval(ts,averaging_interval):
    """
       number of ts interval over a averaging interval.
    """
    
    return int(ticks(averaging_interval)/ticks(ts.interval))


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
