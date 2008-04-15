"""
The 24-24-25 hour filter from Godin's Analysis of Tides book
"""

from vtools.data.api import *

from vtools.data.constants import *

# Local import
from filter import *
from filter import _boxcar
all=["godin"]

## This dic saves the points involves in half summations 
## for different intervals
godin_interval={time_interval(minutes=15):(48,49),\
                time_interval(hours=1):(12,12)} 


def godin(ts):
    
    """ Godin filtering method on a regular time series.
        input:
            ts: regular time series to be filtered
        output:
            new regular time series with the same interval of ts.
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series can be filtered.")
    
    interval=ts.interval
    
    if not interval in godin_interval.keys():
        raise ValueError("Not supported time interval by godin filter")
    
    num_1=godin_interval[interval][0]
    num_2=godin_interval[interval][1]   
    ## use boxcar averging fuction 3 times to 
    ## achieve final values.
    
    d1=_boxcar(ts.data,num_1-1,num_1)
    d1=_boxcar(d1,num_1,num_1-1)
    d1=_boxcar(d1,num_2,num_2)
    
    prop={}
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    
    for key,val in ts.props.items():
        prop[key]=val
        
    return rts(d1,ts.start,ts.interval,prop)
