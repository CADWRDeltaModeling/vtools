""" Merge multiple time series ts1,ts2 ..., a new time series with combination of 
    ts1,ts2 data will be returned. 
"""


## Vtool vtime import.
from vtools.data.vtime import ticks_to_time
from vtools.data.timeseries import rts,prep_binary
from vtools.data.constants import AGGREGATION,TIMESTAMP

## scipy 
from scipy import nan,zeros,where,isnan

__all__=["merge",]

########################################################################### 
## Public interface.
###########################################################################
def merge(ts0,ts1,*other_ts):
    """ merge a number of timeseries together and return a new ts.
    
    Parameters
    ----------
    ts0  :  :class:`~vtools.data.timeseries.TimeSeries`
        Highest priority time series.
              
    ts1  :  :class:`~vtools.data.timeseries.TimeSeries`
        Next highest priority time series, used to replace nans in ts0.
              
    
    *other_ts : :class:`~vtools.data.timeseries.TimeSeries`
        Additional regular time series arguments (number of args is variable)
        to merge with ts0 to cover nan data. Each must have
        with the same interval and should be listed in decreasing priority

    Returns
    -------    
    merged : :class:`~vtools.data.timeseries.TimeSeries`
        A new time series with time interval same as the inputs, time extent
        the union of the inputs, and filled first with ts1, then with remaining
        gaps filled with ts2, then ts3....
        
    """

    ts=_merge(ts0,ts1)
    
    if len(other_ts)>0:
        for i in range(len(other_ts)):
            ts=_merge(ts,other_ts[i])

    return ts

def _merge(ts1,ts2): 
    """ Merge data from timeseries ts1 and ts2.
    
    Parameters
    ----------
    ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
        Two or more regular timeseries (number of args is variable). 
        Each with the same interval with the highest priority time
        series listed first

    Returns
    -------    
    merged : :class:`~vtools.data.timeseries.TimeSeries`
        A new merged time series if success. In the intersection zone
        of two ts, ts1 data take priority unless it is nan. Time extent of
        output ts will be union of two ts' extent.

    """
    
    if not (ts1.is_regular() and ts2.is_regular()):      
        raise ValueError("two input time series for merge operation"
            "must be regular time series.")
        
        if not(ts1.interval==ts2.interval):
            
            raise ValueError("Input timeseries for merge operation"
            "must have the same time interval.")
        
        if not(ts1.data.shape==ts2.data.shape):           
            raise ValueError("Input timeseries for merge operation"
            "must have data of identical shape.")
                
    (seq,start,slice0,slice1,slice2)=prep_binary(ts1,ts2)
    
    tss=(ts1,ts2)
    len_ts=len(seq)
    
    if len(ts1.data.shape)==1:
        data=zeros(len_ts)+nan
    else:
        data=zeros((len_ts,ts1.data.shape[1]))+nan

    if slice1.start>slice2.start:
        first=0
        second=1
        first_slice=slice1
        second_slice=slice2
    else:
        first=1
        second=0
        first_slice=slice2
        second_slice=slice1
         
         
    len1=len(tss[first].data)
    len2=len(tss[second].data)
    ## for situation without intersection, slice0 
    ## will be returned as slice0[0] > slice0[1].
    if slice0.start>slice0.stop:    
         data[0:len1,]=tss[first].data
         data[(len_ts-len2):len_ts,]=tss[second].data
    else:  ## There existes union of two ts.
        data[0:slice0.start,]=tss[first].data[0:first_slice.start,]
        if second_slice.stop+1<len2:
            data[slice0.start:slice0.stop+1,]=tss[0].data[slice1.start:slice1.stop+1]
            data[slice0.stop+1:len_ts,]=tss[second].data[second_slice.stop+1:len2,]
        else:
            ##data[0:len_ts]=tss[first].data
            data[slice0.start:slice0.stop+1,]=tss[0].data[slice1.start:slice1.stop+1,]
            data[slice0.stop+1:len_ts,]=tss[first].data[first_slice.stop+1:len1,]
            
        x=data[slice0.start:slice0.stop+1,]
        y=tss[1].data[slice2.start:slice2.stop+1,]
        temp_data=where(isnan(x),y,x)
        data[slice0.start:slice0.stop+1,]=temp_data
 
    
    return rts(data,ticks_to_time(seq[0]),ts1.interval,{})    
     
        
        
        
    
        
    
    
    







