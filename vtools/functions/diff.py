""" Calculates left side derative of time series
    of input order.
"""

from scipy import diff
from copy import deepcopy


from vtools.data.constants import *
from vtools.data.timeseries import its,rts

__all__=["time_diff"]


def time_diff(ts,order=1):
    """ Generate left side derative of a ts of input orders.

    Parameters
    -----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to interpolate. Must has data of one dimension, and regular.
    
    order : int
        Order of derative.
    

    Returns
    -------
    result : vtools.data.time_series.TimeSeries
        A regular series with derative.
        
    Raise
    --------
    
    ValueError
        If input time series is shorter than order+1 or is not regular.
    """
    

    if len(ts)<order+1:
        raise ValueError("input timeseries is not"
                         "long enough.")
    if not ts.is_regular():
        raise ValueError("time_diff only support regular"
                         "time series for the time being.")
    
    delta_data=diff(ts.data,order)
    rt_start=ts.times[order]
    interval=ts.interval
    
    prop=deepcopy(ts.props)
    prop[AGGREGATION]=INDIVIDUAL
    prop[TIMESTAMP]=INST
    
    rt=rts(delta_data,rt_start,interval,prop)
    return rt    
