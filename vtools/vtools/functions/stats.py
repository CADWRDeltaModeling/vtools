from vtools.data.timeseries import rts,its
from numpy import add as numpyadd, maximum as numpymaximum

all=["ts_apply","ts_accumulate","ts_reduce","ts_sum","ts_max","ts_maximum","ts_mean"]

def _prepare(f):
    def decoratedf(ts,ufunc,window=None,other=None):
        if not window:
            window=(ts.start,ts.end)
        nt=ts.window(window[0],window[1])
        return f(nt,ufunc,other) 
    return decoratedf

@_prepare    
def ts_apply(ts,ufunc,other=None,window=None):
    
    if other:
        ndata=ufunc(ts.data,other)
    else:
        ndata=ufunc(ts.data)
    if ts.is_regular():
        return rts(ndata,ts.start,ts.interval,ts.props)
    else:
        return its(ts.ticks,ndata,ts.props)
    
@_prepare
def ts_accumulate(ts,ufunc,window=None):
    if ts.is_regular():
        return rts(ts.start,ufunc.accumulate(ts.data),ts.interval,ts.props)
    else:
        return its(ts.ticks,ufnc.accumulate(ts.data),ts.props)
    
@_prepare
def ts_reduce(ts,ufunc,window=None):
    return ufunc.reduce(ts.data)


def ts_sum(ts,window=None,time_weight=False):
    """ Return the sum of the time series from start to end
        todo: figure out time weights, figure out trapezoidal part
    """
    return ts_reduce(ts,numpyadd,window)


def ts_max(ts,window=None):
    """ Return the global (scalar) maximum value of ts"""
    return ts_reduce(ts,numpymaximum,window)


def ts_maximum(ts,other,window=None):
    """ Return the pointwise maximum of the ts and a scalar or
        another time series
    """
    return ts_apply(ts,maximum,window,other)

# todo: minimum also


def ts_mean(ts,window=None):
    """ todo: figure out time weight"""
    if window:
        ntlen=len(ts.window(window[0],window[1]))
    else:
        ntlen=len(ts)
    return ts_reduce(ts,numpyadd,window)/ntlen



    