""" Merge two time series ts1,ts2, a new time series with combination of 
    ts1,ts2 data will be returned. 
"""

import pdb

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
def merge(*lts):
    """ merge a number of timeseries together and return a new ts.
        Input:
        ts1,ts2... two or more regular timeseries (number of args is variable),
                   each with the same interval, with the
                   highest priority time series listed first

        Output:
        A new time series with time interval same as the inputs, time extent
        the union of the inputs, and filled first with ts1, then with remaining
        gaps filled with ts2, then ts3....
        
    """

    if len(lts)<2:
        raise ValueError("Merge require at least two input timeseries.")
    ts=_merge(lts[0],lts[1])
    
    if len(lts)>2:
        for i in range(2,len(lts)):
            ts=_merge(ts,lts[i])

    return ts

def _merge(ts1,ts2):
    
    """ 
        Merge data from timeseries ts1 and ts2.

        input:
           ts1: regular time series.
           ts2: regular time series with same interval as ts1
                
        returns:
            a new merged time series if success.
    
    """
    
    if not (ts1.is_regular() and ts2.is_regular()):      
        raise ValueError("two input timeseris for merge operation"
            "must be regualr timeserise.")
        
        if not(ts1.interval==ts2.interval):
            
            raise ValueError("Input timeseris for merge operation"
            "must have the same time interval.")
        
        if not(ts1.data.shape==ts2.data.shape):           
            raise ValueError("Input timeseris for merge operation"
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
        if second_slice.stop+1<len2:
            data[slice0.stop+1:len_ts,]=tss[second].data[second_slice.stop+1:len2,]
            data[0:slice0.stop+1,]=tss[first].data
        else:
            data[0:len_ts]=tss[first].data
        
        x=data[slice0.start:slice0.stop+1,]
        y=tss[second].data[second_slice.start:second_slice.stop+1,]
        temp_data=where(isnan(x),y,x)
        data[slice0.start:slice0.stop+1,]=temp_data
 
    
    return rts(data,ticks_to_time(seq[0]),ts1.interval,{})    
     
        
        
        
    
        
    
    
    







