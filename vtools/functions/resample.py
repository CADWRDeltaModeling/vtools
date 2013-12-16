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

## local import.
from _decimate import decimate as _decimate

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
    
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be resampled.
        
    interval: :ref:`time_interval <time_interval>` 
        Interval of resampled time series.
        
    window: string, tuple,or float
        windowing method option.
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    Raise
    --------
    ValueError
        If input time series is not regular, or regular interval is calendar
        dependent.

    ..note :: Those windowing method option  are available:    
        BOXCAR
        TRIANG
        PARZEN
        BOHMAN
        BLACKMANHARRIS
        NUTTALL
        BARTHANN
        TRIANG
        BLACKMAN   
        HAMMING        
        BARTLETT  
        SLEPIAN    # needs (width)  
        HANNING    # requires parameter (beta)
        KAISER     # requires parameter (beta)
        GAUSSIAN   # requires parameter (std.)
        GENERALGAUSS # Needs parameter (power, width)
       
       To use window without parameter input window
       as a constant: BOXCAR, etc.
       
       To use windows with parameter input
       window as a tuple: (GAUSSIAN,0.5)
       (GENERALGAUSS,2,1024),etc.
       
       if a single float point used as window, 
       KAISER window will be used with input
       value as beta of KAISER window.           
       
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
        
    interval: :ref:`time_interval <time_interval>` 
        Interval of resampled time series.
        
    aligned: boolean
        Default is true which means aligning result' time with input 'interval'.
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    Raise
    --------
    ValueError
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

def decimate(ts,interval,**dic):
    """ Downsample timeseries by decimating.
        A wrapper of GNU Octave function decimate.m function.
        This will remove the influence of aliasing on downsampled
        ts.
        
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be resampled.
        
    interval: :ref:`time_interval <time_interval>` 
        Interval of resampled time series.
        
    **dic : Dictionary
        Dictonary of extra parameters to be passed in. For instance , input
        'align_calendar'  as boolean to align resampled timeseries with the
        downsampling interval. 
    
    Returns
    -------    
    Resampled : :class:`~vtools.data.timeseries.TimeSeries`
        A new resampled time series if success.
        
    Raise
    --------
    ValueError
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
        
    """
    
    if ts.is_regular():
        tsdelta=ts.interval
        if is_calendar_dependent(tsdelta):
            raise ValueError("Resampling of a regular time series \
            with calendar dependent interval is not defined.")
    else:
        raise ValueError("input timeseris for resampling operation \
            must be regualr timeserise with calendar independent interval.")
            
    
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
        
        
        
    
        
    
    
    







