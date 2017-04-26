# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 09:17:56 2017

@author: qshu
"""

""" Bind two a couple time series of univariate into a multivariate one.
"""
## vtools import. 
from vtools.data.vtime import ticks,time_sequence,\
number_intervals,parse_interval,align,is_interval
from vtools.data.timeseries import its,rts
from vtools.data.constants import *


import numpy as np
import pdb
__all__=["ts_bind","ts_split"]

def ts_bind(ts0,ts1,*other_ts):
    """ bind a number of timeseries of univarate together along time diemension and return a new ts
        of multivariabe.
    
    Parameters
    ----------
    ts0  :  :class:`~vtools.data.timeseries.TimeSeries`
        Regular or Irregular time series.
              
    ts1  :  :class:`~vtools.data.timeseries.TimeSeries`
        Regular or Irregular time series.
              
    
    *other_ts : :class:`~vtools.data.timeseries.TimeSeries`
        Additional time series arguments (number of args is variable)
        

    Returns
    -------    
    binded : :class:`~vtools.data.timeseries.TimeSeries`
        A new time series with time extent the union of the inputs.
        If the series are all regular, the output will be regular 
        with an interval of the smallest constituent intervals.
        
    """

   

    ts=_bind(ts0,ts1)
    
    if len(other_ts)>0:
        for i in range(len(other_ts)):
            ts=_bind(ts,other_ts[i])

    return ts
    
def _bind(ts1,ts2): 
    """ bind data from timeseries ts1 and ts2.
    
    Parameters
    ----------
    ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
        Two  timeseries

    Returns
    -------    
    merged : :class:`~vtools.data.timeseries.TimeSeries`
        A new binded time series if success. 

    """
    
    if (not((ts1.data.ndim==1) and (ts2.data.ndim==1))):
        raise ValueError("bind only support time series of univariate")
    ts=None
    ts_is_regular = False
    new_ts_time_sequence = []
    new_start = None
    new_interval = None
    if ((ts1.is_regular()) and (ts2.is_regular())):
        ts1_start = ts1.times[0]
        ts1_end   = ts1.times[-1]
        ts2_start = ts2.times[0]
        ts2_end   = ts2.times[-1]
        new_start = ts1_start
        if new_start>ts2_start:
            new_start = ts2_start
        new_end = ts1_end
        if new_end<ts2_end:
            new_end = ts2_end
        new_interval = ts1.interval
        ts2_interval = ts2.interval
        if new_interval>ts2_interval:
            new_interval = ts2_interval
        num_data = number_intervals(new_start,new_end,new_interval)+1
        new_ts_time_sequence = time_sequence(new_start,new_interval,num_data)
        ts_is_regular = True
    else:
        new_ts_time_sequence = np.union1d(ts1.ticks,ts2.ticks)
        
    
    new_ts_len = len(new_ts_time_sequence)
    new_data = np.array([[np.nan]*new_ts_len,[np.nan]*new_ts_len])
    
    ts1_data_id = np.searchsorted(new_ts_time_sequence,ts1.ticks)
    ts2_data_id = np.searchsorted(new_ts_time_sequence,ts2.ticks)
    new_data[0,ts1_data_id] = ts1.data
    new_data[1,ts2_data_id] = ts2.data 
    
    new_data = new_data.transpose()
    
    if ts_is_regular:
        ts = rts(new_data,new_start,new_interval)
    else:
        ts = its(new_ts_time_sequence,new_data)
        
    return ts
    
def ts_split(ts, shared=True):
    """ Splits a 2D multivariate series into constituent univariate series.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
    shared :: Boolean
         Return time sereis share or copy data array of input one
    
    Returns
    -------    
    out1,out2 : :class:`~vtools.data.timeseries.TimeSeries`
        Two comonent time series.     
    
    """
    
    
    data1 = ts.data[:,0]
    if shared==False:
        data1 = np.copy(ts.data[:,0])
    data2 = ts.data[:,1]
    if shared==False:
        data2 = np.copy(ts.data[:,1])
        
    if ts.is_regular():
        ts1=rts(data1,ts.start,ts.interval)
        ts2=rts(data2,ts.start,ts.interval)
    else:
        ts1=its(ts.ticks,data1)
        ts2=its(ts.ticks,data2)
        
    return ts1,ts2
