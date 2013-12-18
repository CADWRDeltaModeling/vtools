""" Shift operation over a time series, orginal time series with shifted
    star_time,end_time and times is return.
"""

import pdb
## Python lib import.
from operator import add,sub
from copy import deepcopy

## Vtool vtime import.
from vtools.data.vtime import *
from vtools.data.timeseries import rts,its

## scipy import.
import scipy

__all__=["shift"]


########################################################################### 
## Public interface.
###########################################################################

def shift(ts,interval):
    
    """Shift entire time series by a given interval
    
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be shifted.
        
    interval : :ref:`time_interval <time_intervals>` 
        Interval of the shifting. 
        
    
    Returns
    -------    
    shifted : :class:`~vtools.data.timeseries.TimeSeries`
        A new time series with shifted times.
    
    """
    
    if not is_interval(interval):
        interval=parse_interval(interval)
               
    if ts.is_regular():
        return rts(ts.data,increment(ts.start,interval,1),ts.interval,deepcopy(ts.props)) 
    else:
        if is_calendar_dependent(interval):
           tms=ts.times + interval
        else:
           tms=ts.ticks + ticks(interval)
           #ts._ticks=scipy.array(map(ticks,time_op(ts.times,interval)))
        return its(tms,ts.data,deepcopy(ts.props))
        
        
        
    
        
    
    
    







