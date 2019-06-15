""" Some data interpolating over gaps within a time series.
"""


# python standard lib import.
import datetime
import numbers,collections
from copy import deepcopy
from numpy import ones,searchsorted

## scipy import.
from scipy.interpolate import interp1d
from scipy.interpolate import splrep,splev
from scipy import array,logical_not,compress,\
  isnan,zeros,zeros_like,put,transpose,where,take,alltrue,\
  greater,less,arange,nan,resize,array

## vtools import.
from vtools.data.vtime import ticks,time_sequence,\
number_intervals,parse_interval,align,is_interval
from vtools.data.timeseries import its,rts
from vtools.data.constants import *

## local import.
from _monotonic_spline import _monotonic_spline
#from _rational_hist import *
from rhist import rhist_bound

__all__=["linear","spline","monotonic_spline","nearest_neighbor","gap_size",\
         "previous_neighbor","next_neighbor","interpolate_ts_nan",\
         "NEAREST","PREVIOUS","NEXT","LINEAR","SPLINE","MONOTONIC_SPLINE",\
         "interpolate_ts","rhistinterp","RATIONAL_HISTOSPLINE","MSPLINE","RHIST"]

NEAREST="nearest"
PREVIOUS="previous"
NEXT="next"
LINEAR="linear"
SPLINE="spline"
MONOTONIC_SPLINE='mspline'
RATIONAL_HISTOSPLINE='rhist'
MSPLINE='mspline'
RHIST = 'rhist'

###########################################################################
## Public interface.
###########################################################################

def interpolate_ts_nan(ts,method=LINEAR,max_gap=0,**args):
    """ Estimate missing values within a time series by interpolation.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        The time series to be interpolated. Must be univariate.

    method : {LINEAR,NEAREST,PREVIOUS,NEXT,SPLINE,MSPLINE,RHIST}
        You can use our constants or the equivalent string as indicated below.

        LINEAR or 'linear'
            Linear interpolation
        NEAREST or 'nearest'
            Nearest value in time
        PREVIOUS or 'previous'
            Previous step with data
        NEXT or 'next'
            Next step with data
        SPLINE or 'spline'
            numpy 1D spline
        MSPLINE or 'mspline'
            Monotonicity (shape) preserving spline
        RHIST or 'rhist'
            Rational histospline that conserves area under the curve.

    max_gap: int,optional
        The maximum number of continous nan data to allow interpolation. By default
        0, which means doing interpolation no matter how big is the continous nan block.

    **args : dictonary
        Extra keyword parameters required by the `method`.

    Returns
    -------
    filled : :class:`~vtools.data.timeseries.TimeSeries`
        New series with missing values filled using `method`


    """
    if not(ts.has_gap()):
        return ts

    tst=deepcopy(ts)

    if max_gap > 0:
        gaps = gap_size(tst.data)
        indexes = where((gaps > 0) & (gaps <= max_gap))
    else:
        indexes=where(isnan(tst.data))

    ## no nan just return
    if(len(indexes[0])<1):
        return ts

    ## indexes turn out to be a tuple
    ## only the first element is what
    ## needed.
    times=take(tst.ticks,indexes[0])
    values=_interpolate_ts2array(tst,times,method,filter_nan=True,**args)
    put(tst.data,indexes,values)
    return tst


def interpolate_ts(ts,times,method=LINEAR,filter_nan=True,**dic):
    """ Interpolate a time series to a new time sequence.

    Parameters
    -----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to interpolate. Must has data of one dimension, regular or irregular.
    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.
    method : string, optional
        See :func:`interpolate_ts_nan` for a list of methods
    filter_nan : boolean, optional
        True if nan should be omitted or not. If retained,
        nan values in the source series will be used in interpolation algorithm, which may cause new nan points in resulting ts.
    **dic : dictonary
        Extra parameters.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular or irregular series with times based on times and values interpolated from ts.

    See Also
    --------
    interpolate_ts_nan : Fill internal nan values using interpolation

    """
    from vtools.data.api import TimeSeries
    if type(times) == TimeSeries:
        if times.start < ts.start or times.end > ts.end:
            raise ValueError("Time series used to provide requested interpolation times is outside the original series")
        interval=times.interval if times.is_regular() else None
        seq = times.times
        data=_interpolate_ts2array(ts,seq,method=method,\
                                  filter_nan=filter_nan,**dic)
        if interval:
            return rts(data,seq[0],interval)
        else:
            return its(times,data)
    elif not(type(times)==str) and hasattr(times,'__getitem__'):
       data=_interpolate_ts2array(ts,times,method=method,\
                                  filter_nan=filter_nan,**dic)
       ts=its(times,data,{})
    else:
       # interval
       ts=_interpolate2rts(ts,times,method=method,\
                           filter_nan=filter_nan,**dic)
    return ts


def monotonic_spline(ts,times,filter_nan=True):
    """Interpolation by monotonicity (shape) preserving spline.
    The spline will fit the data points exactly, derivatives are
    subject to slope limiters. The name 'monotonicity-preserving'
    can be a little deceptive -- this is an excellent all around
    choice for interpolating continuous data.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.
    filter_nan: if nan points should be omitted or not.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series if second input is time interval, or irregular time series otherwise.
    """

    return interpolate_ts(ts,times,method=MONOTONIC_SPLINE,filter_nan=filter_nan)

def linear(ts,times,filter_nan=True):
    """Interpolate a time series by linear interpolation.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.
    filter_nan : boolean, optional
        Should nan points should be omitted or not.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series if `times` is a `time_interval`, or irregular time series if `times` is a `time_sequence`.
    """
    return interpolate_ts(ts,times,method=LINEAR,filter_nan=filter_nan)

def nearest_neighbor(ts,times,filter_nan=True,**dic):
    """
       Interpolating series using nearest valid neighbor.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.
    filter_nan : boolean, optional
        True if NaN point should be ommitted or not.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
    A regular time series if second input is time interval,
             or irregular time series otherwise.
    """
    return interpolate_ts(ts,times,method=NEAREST,filter_nan=filter_nan,**dic)

def previous_neighbor(ts,times,filter_nan=True,**dic):
    """Interpolate at time series using value at the previous valid neighbor

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.
    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
    A regular time series if second input is time interval,
             or irregular time series otherwise.
    """
    return interpolate_ts(ts,times,method=PREVIOUS,filter_nan=filter_nan,**dic)

def rhistinterp(ts,interval,**dic):
    """ Interpolating a regular time series (rts) to a finer rts by rational histospline.

    The rational histospline preserves area under the curve. This is a good choice of spline for period averaged data where an interpolant is desired
    that is 'conservative'. Note that it is the underlying continuous interpolant
    that will be 'conservative though, not the returned discrete time series which
    merely samples the underlying interpolant.

    Parameters
    ----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated, typically period averaged

    interval : :ref:`time_interval <time_intervals>`

    p : float, optional
        Spline tension, usually between 0 and 20. Must >-1. For a 'sufficiently large' value of p, the interpolant will be monotonicity-preserving and will maintain strict positivity (always being strictly > `lowbound`.

    lowbound : float, optional
        Lower bound of interpolated values.

    tolbound : float, optional
        Tolerance for determining if an input is on the bound.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series with instantaneous values
    """
    return interpolate_ts(ts,interval,method=RATIONAL_HISTOSPLINE,**dic)

def next_neighbor(ts,times,filter_nan=True,**dic):
    """Interpolate by next (forward in time) valid neighbors.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.

    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series if `times` is time interval or irregular time series otherwise.


    """
    return interpolate_ts(ts,times,method=NEXT,filter_nan=filter_nan,**dic)

def spline(ts,times,filter_nan=True,**dic):
    """Interpolating gaps using cubic spline.
       The spline does not need to pass data point. The closeness
       can be controlled by parameter s.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_interval <time_intervals>`  or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval.

    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    s : float, optional
        Smoothing parameter. s=1.0e-3 by default. The lower s is, the closer the fitted curve will be to the data points, and the less smoother the filter will be. This is different from monotonic spline, currently a bit slower and perhaps more robust.

    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series if second input is time interval, or irregular time series otherwise.

    """
    return interpolate_ts(ts,times,method=SPLINE,filter_nan=filter_nan,**dic)

def _interpolate2rts(ts,interval,method=SPLINE,filter_nan=True,**dic):

    """ Interpolate a time series to get a regular series with input `interval`.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    method : string, optional
        See :func:`interpolate_ts_nan` for a list of methods

    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    **dic : Dictionary
        Dictonary of extra parameters to be passed to `method`

    Returns
    -------
    result: :class:`~vtools.data.timeseries.TimeSeries`
        A regular time series.

    """

    if type(interval)==type(" "):
        interval=parse_interval(interval)

    if not is_interval(interval):
        import pdb; pdb.set_trace()
        raise TypeError("second input must be a time interval or can be "
                        "parsed as time interval")

    #if ts.is_regular():
    #    if ts.start+interval>ts.start+ts.interval:
    #        raise ValueError("interpolating interval is wider than"
    #                         "input time series' interval")

    rt_start=align(ts.start,interval,1)
    rt_end = align(ts.end,interval,-1)
    num=number_intervals(rt_start,rt_end,interval)+1
    times=time_sequence(rt_start,interval,num)
    values=_interpolate_ts2array(ts,times,method,filter_nan,**dic)

    prop=deepcopy(ts.props)
    prop[AGGREGATION]=INDIVIDUAL
    prop[TIMESTAMP]=INST
    rt=rts(values,rt_start,interval,prop)
    return rt

def _interpolate_ts2array(ts,times,method=LINEAR,filter_nan=True,**dic):
    """ Interpolate a time series to input 'times'.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    method : string, optional
        See :func:`interpolate_ts_nan` for a list of methods.

    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    **dic : Dictionary
        Dictonary of extra parameters to be passed to `method`

    Returns
    -------
     result: array
        interpolated values.

    Raise
    --------
    ValueError
        If interpolate method is not supported, or input time sequence is
        not a subset of input timeseries datetime range.

    """
    ## do a check of extrapolation, which is not allowed
    ts_start=ts.ticks[0]
    ts_end=ts.ticks[-1]
    tticks=_check_input_times(times)

    if not ((ts_start<=(tticks[0])) and (ts_end>=(tticks[-1]))):
        raise ValueError("Interpolation time sequence is not subset of \
        input timeseries valid time range")

    if filter_nan and ts.data.ndim>1:
        raise ValueError( " filtering nan is only defined for"+
                          " one dimensional time series data." )
    valid_ts_data=ts.data
    valid_ts_ticks=ts.ticks
    if filter_nan:
        valid_ts_data,valid_ts_ticks=filter_nana(ts.data,ts.ticks)
    valid_start=valid_ts_ticks[0]
    valid_end=valid_ts_ticks[-1]

    ## find out the indexes within tticks that can be interpolated by
    ## valid ts data
    indexes1=where(tticks>=valid_start)
    indexes2=where(tticks<=valid_end)

    if (len(indexes1[0])==0) or (len(indexes2[0])==0):
        raise ValueError("interpolation point is out of valid data range")

    s1=indexes1[0][0]
    s2=indexes2[0][-1]

    valid_tticks=tticks[s1:s2+1]

    if hasattr(valid_tticks,'__getitem__') and len(valid_tticks)==0:
        raise ValueError(" interpolation point sequence is out of valid data range")

    if ts.data.ndim==1:
        values=array([nan]*len(tticks))
    elif ts.data.ndim==2:
        values=array([[nan]*ts.data.shape[1]]*len(tticks))
    else:
        raise ValueError("interpolation over data with dimension more than 2 is not supported")


    if method==LINEAR:
        temp=_linear(valid_ts_data,valid_ts_ticks,valid_tticks,**dic)
    elif method==SPLINE:
        temp=_spline(valid_ts_data,valid_ts_ticks,valid_tticks,**dic)
    elif method==NEXT or method==PREVIOUS or method==NEAREST:
        temp=_flat(valid_ts_data,valid_ts_ticks,valid_tticks,method,**dic)
    elif method==MONOTONIC_SPLINE:
        temp=_inner_monotonic_spline(valid_ts_data,valid_ts_ticks,valid_tticks,**dic)
    elif method==RATIONAL_HISTOSPLINE:
        if not ts.is_regular():
            raise ValueError("Only regular time series are"
                        " supported by histospline")

        if AGGREGATION in list(ts.props.keys()):
            if not ts.props[AGGREGATION]==MEAN:
                raise ValueError("Only time series with averaged values can be"
                             " interpolated by histospline")
        if TIMESTAMP in list(ts.props.keys()):
            if not ts.props[TIMESTAMP]==PERIOD_START:
                raise ValueError("Input time series values must be stamped at start"
                              " of individual period")
        temp=_rhistinterpbound(valid_ts_data,valid_ts_ticks,valid_tticks,**dic)
    else:
        raise ValueError("Not supported interpolation method.")

    assert(len(temp)==len(valid_tticks))
    if ts.data.ndim==1:
        put(values,arange(s1,s2+1),temp)
    else:
        for index in arange(0,ts.data.shape[1]):
            put(values[:,index],arange(s1,s2+1),temp[:,index])
    return values




def _rhistinterpbound(ts_data,ts_ticks,tticks,p=10,lowbound=None,\
                     floor_eps=1.e-4,maxiter=5,pfactor=2):
    """ Wrapper of the histospline rhistinerp from _rational_hist.
        It only accept ts with time averaged values which is stamped at
        begining of period.If no such props is given in ts, function
        will assume input ts has such property.


    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    filter_nan : boolean,optional
        True if nan points should be omitted or not.

    p : float,optional
        spline tension, must >-1.

    lowbound: float,optional
        lower bound for the data

    tolbound:float,optional
        lower bound tolerance for the data

    Returns
    -------
     result: array
        interpolated values.


    .. note::
        In piecewise intervals the data are treated as follows:
        1. If the input data lie above lobound for the interval,
        the spline will be forced (using parameters p and q)
        to lie above the bound
        2. If the input data lie along lobound (within a distance
        tolobound), the spline will be a flat line on lobound.
        3. If the input data lie more than a distance tolobound below
        lobound, an error occurs and the routine aborts.


    """
    if len(ts_ticks)<2:
        raise ValueError("data length is too short to do interpolation")

    x=ts_ticks
    ts_interval_ticks=x[1]-x[0]
    extra_x=x[-1]+ts_interval_ticks
    x=resize(x,len(x)+1)
    x[-1]=extra_x
    y=ts_data
    p=ones(len(x)-1,dtype='d')*p
    q=p
    y0=y[0]
    yn=y[-1]
    ynew=rhist_bound(array(x).astype("float"),array(y),tticks.astype("float"),\
                            y0,yn,p,lbound=lowbound,\
                            maxiter=maxiter,pfactor=pfactor,\
                            floor_eps=floor_eps)
    return ynew


def _inner_monotonic_spline(ts_data,ts_ticks,tticks):
    """ Wrapper of monotonic spline function.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    filter_nan:boolean,optional
        if true, null data points of input timeseries are omitted.

    Returns
    -------
     result: array
        interpolated values.

    """

    if ts_data.ndim==1:
        new_data=_monotonic_spline(ts_ticks,ts_data,tticks)
    else:
        l=len(tticks) ## length of data
        n=ts_data.shape[1] ## num of data elements
        ## a nan matrix with shape of n*l,
        new_data=zeros([n,l])+nan
        ## transpose original data to speed up
        temp_data=transpose(ts_data)

        for i in range(0,n):
            indices=arange(i*l,(i+1)*l)
            subdata=_monotonic_spline(ts_ticks,temp_data[i,:],tticks)
            put(new_data,indices,subdata)

        new_data=transpose(new_data)

    ## in case only single data returned.
    if not(type(new_data)==type(array([1,2]))):
        new_data=array([new_data])

    return new_data


def _linear(ts_data,ts_ticks,tticks):

    """ Estimate values within ts data by linear interploate at given times.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    filter_nan:boolean,optional
        if true, null data points of input timeseries are omitted.

    Returns
    -------
     result: array
        interpolated values.

    """

    interpolator=interp1d(ts_ticks,ts_data,axis=0,\
                          copy=False, bounds_error=False)
    new_data=interpolator(tticks)
    return new_data


def _flat(ts_data,ts_ticks,tticks,method=NEAREST):

    """  Estimate timeseries values at given times by flat methods
         use previous known value, next known vlaue, and nearest known value to
         fill missed data.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    method: int,optional
        Choice of PREVIOUS,NEXT,NEAREST

    filter_nan:boolean,optional
        if true, null data points of input timeseries are omitted.

    **dic : Dictionary
        Dictonary of extra parameters to be passed in. For instance , input
        'extroplate'  as integer (num of interval,whether or not do a number
        of extra extroplation at the end of new ts data).

    Returns
    -------
     result: array
        interpolated values.

    """

    tss=its(ts_ticks,ts_data)


    ## find out index of interpolating points that exists in
    ## in original ts, thus orginal value can be reused in
    ## interpolated ts.
    ts_len=len(tss)
    index1=tss.ticks.searchsorted(tticks)
    index2=where(index1<ts_len,index1,ts_len-1)
    tticks2=take(tss.ticks,index2)
    same_points_index=where(tticks2==tticks,index1,ts_len)

    indexes=tss.index_after(tticks)

##    if not(alltrue(greater(indexes,0))) or not(alltrue(less(indexes,len(tss.data)))):
##        raise ValueError("interpolation list has time points falling out of input "+
##              "timeseries range.")

    ## removed the exception above, that will by default make interpolating point
    ## locate on boundary points using boundary values (value before take first order).
    indexes1=where(indexes<1,1,indexes)
    indexes2=where(indexes>len(tss.data)-1,len(tss.data)-1,indexes1)
    indexes=indexes2

    if method==PREVIOUS:
        indexes=indexes-1
    elif method==NEXT:
        indexes=indexes
    else:
        pre=indexes-1
        after=indexes
        interval_to_pre=abs(tticks-take(tss.ticks,pre))
        interval_to_after=abs(tticks-take(tss.ticks,after))
        indexes=where(interval_to_pre<=interval_to_after,pre,after)

    vals1=take(tss.data,indexes)
    dum_index=where(same_points_index<ts_len,same_points_index,0)
    dum_val=take(tss.data,dum_index)
    vals2=where(same_points_index<ts_len,dum_val,vals1)


    ## if is required by user, do some extra extrapolation at the
    ## end of new ts using last value, thus new ts will be longer
#    for keyword in dic.keys():
#        if not(keyword=="extrapolate"):
#            raise TypeError("unexpected keyword %s"%keyword)
#
#    if "extrapolate" in dic.keys():
#        new_ts_len=len(vals2)
#        extrapolate_num=dic["extrapolate"]
#        dum_val2=zeros(new_ts_len+extrapolate_num)
#        dum_val2[0:new_ts_len]=vals2[0:new_ts_len]
#        last_val=vals2[new_ts_len-1]
#        dum_val2[new_ts_len:new_ts_len+extrapolate_num]=last_val
#        vals2=dum_val2
    return vals2


def _spline(data,ticks,tticks,time_begin=None,time_end=None,\
            k=3,s=1.0e-3,filter_nan=True,per=0):
    """ Estimate missing values within ts data by B-spline interpolation.

    Parameters
    -----------

    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated

    times : :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated.

    time_begin, time_end: int or datetime,optional
        the boundary of approximating, Default means whole time series will
        be fitted.

    k: int,optional
       The order of the spline fit.

    s:  float,optional
       A smoothing condition.

    filter_nan:boolean,optional
        If true, null data points of input timeseries are omitted.

    per:int,optional
        If non-zero, data points are considered periodic.

    Returns
    -------
     result: array
        interpolated values.




    ..note::

    k:  It is recommended
    to use cubic splines.Even order splines should be
    avoided especially with small s values.
    1 <= k <= 5.

    s:  The amount of smoothness
    is determined by satisfying the conditions:
    sum((w * (y - g))**2,axis=0) <= s where g(x) is
    the smoothed interpolation of (x,y).  The user can
    use s to control the tradeoff between closeness and
    smoothness of fit.  Larger s means more smoothing
    while smaller values of s indicate less smoothing.
    Recommended values of s depend on the weights, w.
    If the weights represent the inverse of the
    standard-deviation of y, then a good s value should
    be found in the range (m-sqrt(2*m),m+sqrt(2*m))
    where m is the number of datapoints in x, y, and w.
    default : s=m-sqrt(2*m).

    per: If non-zero, data points are considered periodic with
    period x[m-1] - x[0] and a smooth periodic spline
    approximation is returned.Values of y[m-1] and w[m-1]
    are not used.

    """

    if k<1 or k>5:
        raise ValueError("Unsupported spline interpolation order.")



    (start_i,end_i)=_check_fitting_bounds(ticks,k,time_begin,time_end)

    if not(start_i==0) or not(end_i==(len(data)-1)):
        ## Sliceing is needed
        ts_ticks=ticks[start_i:end_i]
        ts_data=data[start_i:end_i]
    else:
        ts_ticks=ticks
        ts_data=data



    ## splrep cann't hanle multi-rank data directly.
    ## so,it needes to be done here.
    if ts_data.ndim==1:
        ## Generate spline representation.
        tck=splrep(ts_ticks,ts_data,s=s,per=per,k=k)
        ## Calculate values.
        v=splev(tticks,tck,der=0)
        if not hasattr(v,'__getitem__'):
            v=array([v])
        return v

    elif ts_data.ndim>1:
        l=len(tticks)
        values=zeros([ts_data.shape[1],l])+nan
        ## transpose orginal data for speed up
        temp_data=transpose(ts_data)
        for i in range(ts_data.shape[1]):
            tck=splrep(ts_ticks,temp_data[i,:],s=s,per=per,k=k)
            v=splev(tticks,tck,der=0)
            indices=arange(i*l,(i+1)*l)
            put(values,indices,v)
        values=transpose(values)
        return values


###########################################################################
## Private interface.
###########################################################################
def _check_data_length(x,k):

    if len(x)< k+2:
        raise ValueError("time series is too short to do interpolation.")

def _check_input_times(times):

    issequence=False
    if hasattr(times,'__getitem__'):
        ## Here assume sequence contains
        ## elements of same type.
        test_tm=times[0]
        issequence=True
    else:
        test_tm=times

    if not issequence:
        times=[times]

    if isinstance(test_tm,datetime.datetime):
        tticks=list(map(ticks,times))
        tticks=array(tticks,float)
    elif isinstance(test_tm,numbers.Number):
        tticks=array(times,float)
    else:
        raise TypeError("Second input for interpolation functions" \
        " must be list/array of number or datatime, or single" \
        " number or datetime")

    return tticks

def _check_fitting_bounds(ts_ticks,k,time_begin,time_end):

    # If boundary is given findout boundary index within ts.
    begin_index=0
    end_index=len(ts_ticks)-1

    if type(time_begin)==datetime.datetime:
        time_begin=ticks(time_begin)

    if type(time_end)==datetime.datetime:
        time_end=ticks(time_end)

    if time_begin:
        begin_index=searchsorted(ts_ticks,time_begin,side='right')
        if begin_index>(len(ts_ticks)-3+k):
            raise ValueError(" Fitting interval is out of available timesers data."+
                             " Move interval begining time backward.")

    if time_end:
        end_index=searchsorted(ts_ticks,time_end,side='right')-1
        if end_index>(len(ts_ticks)-3+k):
            raise ValueError(" Fitting interval is out of available timesers data."+
                             "Move interval begining time backward.")

    return begin_index,end_index


def filter_nana(ts_data,ts_ticks):

    if ts_data.ndim>1:
        raise ValueError( "filtering-NaN is only defined for"+
                        "one dimensional time series data." )
    ts_ticks=compress(logical_not(isnan(ts_data)),ts_ticks)
    ts_data=compress(logical_not(isnan(ts_data)),ts_data)


    return ts_data,ts_ticks


def gap_size(x):
    from itertools import groupby

    """Find the size of gaps (blocks of nans) for every point in an array.
    Parameters
    ----------
    x : array_like
    an array that possibly has nans

    Returns
    gaps : array_like
    An array the values of which represent the size of the gap (number of nans) for each point in x, which will be zero for non-nan points.
    """
    isgap = zeros_like(x)
    isgap[isnan(x)] = 1
    gaps = []
    for a, b in groupby(isgap, lambda x: x == 0):
        if a: # Where the value is 0, simply append to the list
            gaps.extend(list(b))
        else: # Where the value is one, replace 1 with the number of sequential 1's
            l = len(list(b))
            gaps.extend([l]*l)
    return array(gaps)
