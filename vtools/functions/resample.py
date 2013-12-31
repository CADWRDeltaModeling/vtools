""" Resample operation over a time series, a new time series with the desired interval
   and corresponding ticks will be returned. 
"""

import pdb

## Python lib import.
from operator import add,sub


## Vtool vtime import.
from vtools.data.vtime import number_intervals,\
ticks,ticks_to_time,is_calendar_dependent,\
parse_interval,is_interval,align
from vtools.data.timeseries import rts,its
from vtools.data.constants import *

## scipy import.
from scipy.signal import resample as sciresample
from scipy.signal import cheby1, firwin, lfilter



__all__=["resample","decimate","resample_ftt"]
         
left_to_decide=["BLACKMAN","HAMMING","BARTLETT","HANNING","KAISER",
"GAUSSIAN","GENERALGAUSS","BOXCAR","TRIANG","PARZEN","BOHMAN",
"BLACKMANHARRIS","NUTTALL","BARTHANN","SLEPIAN",]

BLACKMAN='blackman'   
HAMMING='hamming'        
BARTLETT='bartlett'    
HANNING='hanning'
KAISER='kaiser'
GAUSSIAN='gaussian'
GENERALGAUSS='general gauss'
BOXCAR="boxcar"
TRIANG="triang"
PARZEN="parzen"
BOHMAN="bohman"
BLACKMANHARRIS="blackmanharris"
NUTTALL="nuttall"
BARTHANN="barthann"
SLEPIAN="slepian"

def resample_ftt(ts,interval,window=BOXCAR):
    """ Do a resample operation on a time series "ts".
        A wrapper of scipy.signal.resample function.
        
     .. note::  resample provides those windowing method options:  
        
        BOXCAR\n
        TRIANG\n
        PARZEN\n
        BOHMAN\n
        BLACKMANHARRIS\n
        NUTTALL\n
        BARTHANN\n
        TRIANG\n
        BLACKMAN\n   
        HAMMING\n        
        BARTLETT\n  
        SLEPIAN    # needs (width) \n  
        HANNING    # requires parameter (beta) \n
        KAISER     # requires parameter (beta) \n
        GAUSSIAN   # requires parameter (std.) \n
        GENERALGAUSS # Needs parameter (power, width)\n
       
       To use window without parameter input window
       as a constant: BOXCAR, etc.
       
       To use windows with parameter input
       window as a tuple: (GAUSSIAN,0.5)
       (GENERALGAUSS,2,1024),etc.
       
       if a single float point used as window, 
       KAISER window will be used with input
       value as beta of KAISER window.     
       
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be resampled.
        
    interval : :ref:`time_interval <time_intervals>`  
        Interval of resampled time series.
        
    window: string, tuple,or float
        windowing method option.
        
   
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    Raises
    --------
    error : :py:class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent.

          
       
    """
    
    # Resampling regular time series with calendar dependent 
    # interval is not allowed for the time being.
    
    if ts.is_regular():
        tsdelta=ts.interval
        if is_calendar_dependent(tsdelta):
            raise ValueError("Resampling of a regular time series \
            with calendar dependent interval is not defined.")
    else:
        raise ValueError("input timeseris for resampling operation \
            must be regualr timeserise with calendar independent interval.")

    if not is_interval(interval):
        interval=parse_interval(interval)
        
    num=number_intervals(ts.start,ts.end,interval) 
    (nt,t)=sciresample(ts.data,num,t=ts.ticks,axis=0,window=window)

    st=ticks_to_time(t[0])
    prop={}
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    new_ts=rts(nt,st,interval,prop)               
    return new_ts

########################################################################### 
## Public interface.
###########################################################################
def resample(ts,interval,aligned=True): 
    """ Do a resampling operation on a time series.
        
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be resampled.
        
    interval : :ref:`time_interval <time_intervals>` 
        Interval of resampled time series.
        
    aligned: boolean
        Default is true which means aligning result' time with input 'interval'.
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    Raises
    --------
    error : :py:class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent.
    
     .. note::This is a simple resample method with side effect of
        aliasing.
        
    """
    
    # Resampling regular time series with calendar dependent 
    # interval is not allowed for the time being.
    
    if ts.is_regular():
        tsdelta=ts.interval
        if is_calendar_dependent(tsdelta):
            raise ValueError("Resampling of a regular time series \
            with calendar dependent interval is not defined.")
    else:
        raise ValueError("input timeseris for resampling operation \
            must be regualr timeserise with calendar independent interval.")

    if not is_interval(interval):
        interval=parse_interval(interval)     

    if aligned:
        aligned_start=align(ts.start,interval,1)
        return resample(ts.window(aligned_start,ts.end),interval,False)
    else:
        num=number_intervals(ts.start,ts.end,interval) 
        steps=int(ticks(interval)/ticks(ts.interval))   
        nt=ts.data[0:num*steps+1:steps,]
        st=ts.start
        prop={}
       
        for key,val in ts.props.items():
            prop[key]=val
        prop[TIMESTAMP]=INST
        prop[AGGREGATION]=INDIVIDUAL
    
        new_ts=rts(nt,st,interval,prop)                
        return new_ts

def _decimate(x, q, n=None, ftype='iir', axis=-1):
    """downsample the signal x by an integer factor q, using an order n filter
    
    By default, an order 8 Chebyshev type I filter is used or a 30 point FIR 
    filter with hamming window if ftype is 'fir'.

    (port to python of the GNU Octave function decimate.)

    Inputs:
        x -- the signal to be downsampled (N-dimensional array)
        q -- the downsampling factor
        n -- order of the filter (1 less than the length of the filter for a
             'fir' filter)
        ftype -- type of the filter; can be 'iir' or 'fir'
        axis -- the axis along which the filter should be applied
    
    Outputs:
        y -- the downsampled signal

    """

    if type(q) != type(1):
        raise ValueError, "q should be an integer"

    if n is None:
        if ftype == 'fir':
            n = 30
        else:
            n = 8
    if ftype == 'fir':
        b = firwin(n+1, 1./q, window='hamming')
        y = lfilter(b, 1., x, axis=axis)
    else:
        (b, a) = cheby1(n, 0.05, 0.8/q)

        y = lfilter(b, a, x, axis=axis)

    return y.swapaxes(0,axis)[::q].swapaxes(0,axis)

def decimate(ts,interval,**dic):
    """ Downsample timeseries by decimating.
        A wrapper of GNU Octave function decimate.m function.
        This will remove the influence of aliasing on downsampled
        ts.
        
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be resampled.
        
    interval : :ref:`time_interval <time_intervals>` 
        Interval of resampled time series.
        
    **dic : Dictionary
        Dictonary of extra parameters to be passed in. For instance , input
        'align_calendar'  as boolean to align resampled timeseries with the
        downsampling interval. 
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    """
    
    
    if "align_calendar" in dic.keys():
        align_calendar=dic["align_calendar"]
        del dic["align_calendar"]
    else:
        align_calendar=False
    
        
    if not is_interval(interval):
        interval=parse_interval(interval)

    if align_calendar:
        resample_start=align(ts.start,interval,1)
    else:
        resample_start=ts.start
     
    new_num=number_intervals(resample_start,ts.end,interval)
    len_ts=number_intervals(resample_start,ts.end,ts.interval)
    n=int(len_ts/new_num)
    
    if n<1:
        raise ValueError("Input downsampling interval \
    is narrower than orginal timeseries,try a wider one.")
    
    if ts.data.ndim==1:
        data=_decimate(ts.data,n,**dic)
        d1=data[::-1].copy()
        d2=_decimate(d1,1,**dic)
        data=d2[::-1].copy()
    elif ts.data.ndim==2:
        data=_decimate(ts.data,n,axis=0,**dic)
        d1=data[::-1].copy()
        d2=_decimate(d1,1,axis=0,**dic)
        data=d2[::-1].copy()
        
    ll=data.shape[0]    
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    new_rts=rts(data,resample_start,interval,prop)
    
    return new_rts
        
        
        
    
        
    
    
    







