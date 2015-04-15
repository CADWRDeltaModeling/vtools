from vtools.data.timeseries import rts,its
from numpy import add as numpyadd, maximum as numpymaximum,minimum as numpyminimum

all=["ts_apply","ts_accumulate","ts_reduce","ts_sum","ts_max","ts_maximum","ts_mean"]


    
def ts_apply(ts,ufunc,other=None):
    """Apply a numpy ufunc to the data and produce a neatened time series
       The function will be applied pointwise to the data.
       The argument other must be a scalar and serves as the
       second argument to a binary operator or function.
       
       So... ts_apply(ts, add, 5) will add 5 to every data member 
    """
    if other:
        ndata=ufunc(ts.data,other)
    else:
        ndata=ufunc(ts.data)
    if ts.is_regular():
        return rts(ndata,ts.start,ts.interval,ts.props)
    else:
        return its(ts.ticks,ndata,ts.props)
    

def ts_accumulate(ts,ufunc):
    """Apply ufunc.accumulate to the data and produce a neatened time series
       The function will be applied cumulatively to the data.
       So... ts_apply(ts, add) will produce a time series, where each entry 
       is the cumulative sum up to that index.
    """
    if ts.is_regular():
        return rts(ufunc.accumulate(ts.data),ts.start,ts.interval,ts.props)
    else:
        return its(ts.ticks,ufunc.accumulate(ts.data),ts.props)
    

def ts_reduce(ts,ufunc):
    """Reduce the data by applying ufunc.reduce and produce a neatened time series
       The function will be applied cumulatively to the data, producing
       a "total". The output of ts_reduce is the same as the size of one 
       element in the time series.
       So... ts_reduce(ts, add) will produce the sum of a time series. Some
       convenience functions such as ts_sum, ts_mean, ts_max, ts_min are 
       provided that rely on this function.
    """
    return ufunc.reduce(ts.data)


def ts_sum(ts,time_weight=False):
    """ Return the sum of the time series from start to end
        todo: figure out time weights, figure out trapezoidal part
    """
    if (time_weight):
        raise NotImplementedError
    return ts_reduce(ts,numpyadd)


def ts_max(ts):
    """ Return the global (scalar) maximum value of ts"""
    return ts_reduce(ts,numpymaximum)


def ts_maximum(ts,other):
    """ Return the pointwise maximum of the ts and a scalar or
        another time series
    """
    return ts_apply(ts,numpymaximum,other)

# todo: minimum also
def ts_min(ts):
    """ Return the global (scalar) minimum value of ts"""
    return ts_reduce(ts,numpyminimum)


def ts_minimum(ts,other):
    """ Return the pointwise minimum of the ts and a scalar
    """
    return ts_apply(ts,numpyminimum,other)

def ts_mean(ts):
    """ todo: figure out time weight"""
    ntlen=len(ts)
    return ts_reduce(ts,numpyadd)/ntlen



    