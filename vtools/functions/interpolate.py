""" Some data interpolating over gaps within a time series.
"""


# python standard lib import.
from operator import isNumberType,isSequenceType
import datetime,pdb
from copy import deepcopy

## scipy import.
from scipy.interpolate import interp1d
from scipy.interpolate.fitpack import splrep,splev
from scipy import array,logical_not,compress,\
isnan,zeros,put,transpose,where,take,alltrue,\
greater,less,arange,nan,resize

## vtools import. 
from vtools.data.vtime import ticks,time_sequence,\
number_intervals,parse_interval,align,is_interval
from vtools.data.timeseries import its,rts
from vtools.data.constants import *

## local import.
from _monotonic_spline import _monotonic_spline
from _rational_hist import *

__all__=["linear","spline","monotonic_spline","nearest_neighbor",\
         "previous_neighbor","next_neighbor","interpolate_ts_nan",\
         "NEAREST","PREVIOUS","NEXT","LINEAR","SPLINE","MONOTONIC_SPLINE",\
         "interpolate_ts","rhistinterp","RATIONAL_HISTOSPLINE"]

NEAREST="nearest"
PREVIOUS="pre"
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

def interpolate_ts_nan(ts,method=LINEAR,**args):
    
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
    **args : dictonary 
        Extra keyword parameters required by the `method`.

    Returns
    -------    
    filled : vtools.data.time_series.TimeSeries
        New series with missing values filled using `method`

        
    """
    tst=deepcopy(ts)
    indexes=where(isnan(tst.data))
    ## indexes turn out to be a tuple
    ## only the first element is what
    ## needed.
    times=take(tst.ticks,indexes[0])    
    values=_interpolate_ts2array(tst,times,method,filter_nan=True,**args)       
    put(tst.data,indexes,values)
    return tst


def interpolate_ts(ts,intime,method=SPLINE,filter_nan=True,**dic):
    """ Interpolate a time series to a new time sequence.

    Parameters
    -----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to interpolate. Must has data of one dimension, regular or irregular.
    times : :ref:`time_interval <time_interval>` or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval. 
    method : string, optional
        See interpolate_ts_nan
    filter_nan : boolean, optional
        True if nan should be omitted or not. If retained, 
        nan values in the source series will be used in interpolation algorithm, which may cause new nan points in resulting ts.
    **dic : dictonary
        Extra parameters.

    Returns
    -------
    result : vtools.data.time_series.TimeSeries
        A regular or irregular series with times based on intime and values interpolated from ts.
        
    See Also
    --------
    interpolate_ts_nan : Fill internal nan values using interpolation
    
    """
    
    if not(type(times)==str) and isSequenceType(times):
       data=_interpolate_ts2array(ts,times,method=method,\
                                  filter_nan=filter_nan,**dic)
       ts=its(intime,data,{})
    else:
       ts=_interpolate2rts(ts,times,method=method,\
                           filter_nan=filter_nan,**dic)
    return ts


def monotonic_spline(ts,times,filter_nan=True):
    """Interpolation by monotonicity (shape) preserving spline.
    The spline will fit the data points exactly, derivatives are
    subject to slope limiters
       
    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_interval>` or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval. 
    filter_nan: if nan points should be omitted or not.

    Returns
    -------
    result : `vtools.data.time_series.TimeSeries`
        A regular time series if second input is time interval, or irregular time series otherwise. 
    """

    return interpolate_ts(ts,times,method=MONOTONIC_SPLINE,filter_nan=filter_nan)  

def linear(ts,times,filter_nan=True):
    """Interpolate a time series by linear interpolation.

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Series to be interpolated
    times : :ref:`time_interval <time_interval>` or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval. 
   
    filter_nan : boolean, optional
        Should nan points should be omitted or not.
    
    Returns
    -------
    result : `TimeSeries`
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
    times : :ref:`time_interval <time_interval>` or :ref:`time_sequence <time_sequence>`
        The new times to which the series will be interpolated. Can also be a string that can be parsed into a time interval. 
    filter_nan : boolean, optional 
        True if NaN point should be ommitted or not.
    
    Returns
    -------
    result : TimeSeries
    A regular time series if second input is time interval,
             or irregular time series otherwise. 
    """
    return interpolate_ts(ts,times,method=NEAREST,filter_nan=filter_nan,**dic)  

def previous_neighbor(ts,times,filter_nan=True,**dic):
    """
       Interpolating gaps by previous valid neighbors.

       Input:
             ts: timeseries to be interpolated
             times: time interval or string which can be parsed into
                    time interval, or sequence of datetime or integer
                    ticks.
        Optional input:
             filter_nan:if NaN point should be ommitted or not.
        Output:
              a regular time series if second input is time iterval,
              or irregular time series otherwise.        
    """
    return interpolate_ts(ts,times,method=PREVIOUS,filter_nan=filter_nan,**dic)

def rhistinterp(ts,interval,**dic):
    """ Interpolating rts to a new rts with input interval by rational histospline

        User may specify several optional paramters as keyward inputs:

           p: spline tension, usually between 0 and 20. Must >-1
           lowbound: lower bound of interpolated values.
           tolbound: tolerance for determinign an input is on the bound.
    """
    return interpolate_ts(ts,interval,method=RATIONAL_HISTOSPLINE,**dic)

def next_neighbor(ts,times,filter_nan=True,**dic):
    """
       Interpolating gaps by next valid neighbors.

       Input:
             ts: timeseries to be interpolated
             times: time interval or string which can be parsed into
                    time interval, or sequence of datetime or integer
                    ticks.
        Optional input:
             filter_nan:if NaN point should be ommitted or not.
        Output:
              a regular time series if second input is time iterval,
              or irregular time series otherwise. 
    """
    return interpolate_ts(ts,times,method=NEXT,filter_nan=filter_nan,**dic)

def spline(ts,times,filter_nan=True,**dic):    
    """
       Interpolating gaps by next valid neighbors.
       spline method is not necessary to pass data point, the closeness
       can be controlled by parameter s, s=1.0e-3 by default. the lower s is
       , the closer is the fitted curve to data point, and less smoother.
       this is different from monotonic spline.
       Input:
             ts: timeseries to be interpolated
             times: time interval or string which can be parsed into
                    time interval, or sequence of datetime or integer
                    ticks.
        Optional input:
             filter_nan:if NaN point should be ommitted or not.
        Output:
              a regular time series if second input is time iterval,
              or irregular time series otherwise. 
    """
    return interpolate_ts(ts,times,method=SPLINE,filter_nan=filter_nan,**dic)

def _interpolate2rts(ts,interval,method=SPLINE,filter_nan=True,**dic):
    
    """ Interpolate on a ts to get a regular
        ts with input interval.

        usage: ts=interpolate_its_rts(it,interval,
        method,filter_nan,**dic)
        
        input:
             ts: timeseries, must has data of rank one
             at the moment, can be regular time series
             or irregular time series.
        optional input:
             method: what interpolation method used.
             **dic: dictonary of extra parameters.        
    
        A regular ts will be returned if succeed.
     """
    if type(interval)==type(" "):
        interval=parse_interval(interval)
        
    if not is_interval(interval):
        raise TypeError("second input must be a time interval or can be "
                        "parsed as time interval")
    
    if ts.is_regular():
        if ts.start+interval>ts.start+ts.interval:
            raise ValueError("interpolating interval is wider than"
                             "input time series' interval")
        
    rt_start=align(ts.start,interval,1)
    num=number_intervals(rt_start,ts.end+interval,interval)
    times=time_sequence(rt_start,interval,num)
    values=_interpolate_ts2array(ts,times,method,filter_nan,**dic)
    
    prop=deepcopy(ts.props)
    prop[AGGREGATION]=INDIVIDUAL
    prop[TIMESTAMP]=INST
    rt=rts(values,rt_start,interval,prop)
    return rt
    
def _interpolate_ts2array(ts,times,method=LINEAR,filter_nan=True,**dic):
    
    """ Interpolate on given times within ts,
        a array of interpolated values
        will be return if succeed.
    """
    
    if method==LINEAR:
        values=_linear(ts,times,filter_nan=filter_nan)
    elif method==SPLINE:
        values=_spline(ts,times,filter_nan=filter_nan,**dic)
    elif method==NEXT or method==PREVIOUS or method==NEAREST:
        values=_flat(ts,times,method,filter_nan=filter_nan,**dic)
    elif method==MONOTONIC_SPLINE:
        values=_inner_monotonic_spline(ts,times,filter_nan=filter_nan)
    elif method==RATIONAL_HISTOSPLINE:
        values=_inner_histospline(ts,times,**dic)
    else:
        raise ValueError("Not supported interpolation method.")  
    return values


def _inner_histospline(ts,times,**dic):
    """ inner histospline funcs, depends on wether tolbound is given or not
        _rhistinterpbound or _rhisterinterp will be used.
    """
    p=10
    if "p" in dic.keys():
        p=dic["p"]
        
    lowbound=0
    if "lowbound" in dic.keys():
        lowbound=dic["lowbound"]
        
    if "tolbound" in dic.keys():
        totlbound=dic["tolbound"]
        return _rhistinterpbound(ts,times,p=p,lowbound=lowbound,tolbound=tolbound)
    else:
        return _rhistinterp(ts,times,p=p,lowbound=lowbound)


def _rhistinterp(ts,times,p=10,lowbound=0):
    """ Wrapper of the histospline rhistinerp from _rational_hist.
 
         It only accept ts with time averaged values which is stamped at
         begining of period.If no such props is given in ts, function
         will assume input ts has such property.

         Input:
              times must be array of ticks.
              p is spline tension.
    """

    if not ts.is_regular():
        raise ValueError("Only regular time series can be"
                        " interpolated by histospline")
    
    if AGGREGATION in ts.props.keys():
        if not ts.props[AGGREGATION]==MEAN:
            raise ValueError("Only time series with averaged values can be"
                             " interpolated by histospline")
    if TIMESTAMP in ts.props.keys():
        if not ts.props[TIMESTAMP]==PERIOD_START:
            raise ValueError("Input time series values must be stamped at start"
                              " of individual period")
    x=ts.ticks
    extra_x=ticks((ts[-1].time+ts.interval))
    x=resize(x,len(x)+1)
    x[-1]=extra_x
    y=ts.data    
    q=p
    y0=y[0]
    yn=y[-1]
    (ynew,iflag)=rhistinterpbound(x,y,times,p,lowbound,[y0,yn,q])

    if iflag==1:
        raise ValueError("Input time series must be longer than 3")
    if iflag==2:
        raise ValueError("Error in solving the linear system (TRIDIU)")
    if iflag==3:
        raise ValueError("Lowbound violation")
    if iflag==12:
        raise ValueError("Spline tension parameter must be larger than -1")

    return ynew


def _rhistinterpbound(ts,times,p=10,lowbound=0,tolbound=1.e-4):
    """ Wrapper of the histospline rhistinerp from _rational_hist.
 
         It only accept ts with time averaged values which is stamped at
         begining of period.If no such props is given in ts, function
         will assume input ts has such property.

         Input:
              times must be array of ticks.
              p is spline tension.
    """
    if not ts.is_regular():
        raise ValueError("Only regular time series can be"
                        " interpolated by histospline")
    
    if AGGREGATION in ts.props.keys():
        if not ts.props[AGGREGATION]==MEAN:
            raise ValueError("Only time series with averaged values can be"
                             " interpolated by histospline")
    if TIMESTAMP in ts.props.keys():
        if not ts.props[TIMESTAMP]==PERIOD_START:
            raise ValueError("Input time series values must be stamped at start"
                              " of individual period")
    x=ts.ticks
    extra_x=x[-1]+ticks(ts.interval)
    x=resize(x,len(x)+1)
    x[-1]=extra_x
    y=ts.data    
    q=p
    y0=y[0]
    yn=y[-1]
    (ynew,iflag)=rhistinterpbound(x,y,times,p,lowbound,[y0,yn,q,tolbound])
    if iflag==1:
        raise ValueError("Input time series must be longer than 3")
    if iflag==2:
        raise ValueError("Error in solving the linear system (TRIDIU)")
    if iflag==3:
        raise ValueError("Lowbound violation")
    if iflag==12:
        raise ValueError("spline tension must be larger than -1")

    return ynew    

    
def _inner_monotonic_spline(ts,times,filter_nan=True):
    # todo: none of our public API should return arrays
    """ Wrapped monotonic spline function for time
        series operation.

        input:
             ts: timeseries
             times: a single datetime or list/array
                    of datetime, or ticks.
             filter_nan: if null data points of ts
                         are omitted. 
        output:
            a array of interpolated vlaues is returned.        
    """

    if isSequenceType(times) and len(times)==0:
        raise ValueError(" invalid time sequence input.")

    if filter_nan and ts.data.ndim>1:
        raise ValueError(" filtering nan is only defined for"
                          " one dimensional time series data.")
    
    tticks=_check_input_times(times)
        
    ts_ticks=ts.ticks
    ts_data=ts.data
    
    if filter_nan:
        ts_data,ts_ticks=filter_nana(ts_data,ts_ticks)

    if ts.data.ndim==1:
        new_data=_monotonic_spline(ts_ticks,ts_data,tticks)
    else:
        l=len(tticks) ## length of data
        n=ts.data.shape[1] ## num of data elements
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
    
        
def _linear(ts,times,filter_nan=True):
    
    """ Estimate values within ts data by linear
        interploate at given times.
        
        input:
             ts: timeseries
             times: a single datetime or list/array
                    of datetime, or ticks.
             filter_nan: if null data points of ts
                         are omitted. 
        output:
            a array of interpolated vlaues is returned.
    """
    
    if isSequenceType(times) and len(times)==0:
        return

    if filter_nan and ts.data.ndim>1:
        raise ValueError( " filtering nan is only defined for"+  
                          " one dimensional time series data." )    
    
    tticks=_check_input_times(times)
        
    ts_ticks=ts.ticks
    ts_data=ts.data
    
    if filter_nan:
        ts_data,ts_ticks=filter_nana(ts_data,ts_ticks)

    interpolator=interp1d(ts_ticks,ts_data,axis=0,\
                          copy=False, bounds_error=False)
    new_data=interpolator(tticks)
    return new_data


def _flat(ts,times,method=NEAREST,filter_nan=True,**dic):
    """ 
        Estimate timeseries values at given times by
        flat methods (previous known value, next known 
        vlaue, and nearest known value)
        
        input:
           ts: timeseries
           times: single or list of datetime or ticks
           method: optional, choice PREVIOUS,NEXT,NEAREST
           filter_nan: to filter out invalid data or not
           extroplate: input as integer (num of interval,whether
                       or not do a number of extra extroplation
                       at the end of new ts data. 
        return:
           a array of interpolated values 
    """    

    if isSequenceType(times) and len(times)==0:
        return
    
    if filter_nan and ts.data.ndim>1:
        raise ValueError( " filtering nan is only defined for"+ 
                          " one dimensional time series data." )
        
    tticks=_check_input_times(times)
    
    ## Filter out nan from data
    if filter_nan:
        ts_data,ts_ticks=filter_nana(ts.data,ts.ticks)
        tss=its(ts_ticks,ts_data)
    else:
        tss=ts

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
    if "extrapolate" in dic.keys():
        new_ts_len=len(vals2)
        extrapolate_num=dic["extrapolate"]
        dum_val2=zeros(new_ts_len+extrapolate_num)
        dum_val2[0:new_ts_len]=vals2[0:new_ts_len]
        last_val=vals2[new_ts_len-1]
        dum_val2[new_ts_len:new_ts_len+extrapolate_num]=last_val
        vals2=dum_val2        
    return vals2


def _spline(ts,times,time_begin=None,time_end=None,\
            k=3,s=1.0e-3,filter_nan=True,per=0):
    
    """ Estimate missing values within ts data by
        B-spline interpolation.
        
        input:
            ts: time series
            
            times: the time points on which interpolation wanted.
            
            time_begin, time_end: the boundary of approximating, must
                                  be given as ticks or datetime.
                                  if not set, whole time series will
                                  be fitted.
            
            k:  The order of the spline fit.  It is recommended 
                to use cubic splines.Even order splines should be
                avoided especially with small s values.
                1 <= k <= 5.
                
            s:  A smoothing condition.  The amount of smoothness
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
                
           filter_nan: if null data points of ts are omitted. 
                         
           per: If non-zero, data points are considered periodic with
                period x[m-1] - x[0] and a smooth periodic spline 
                approximation is returned.Values of y[m-1] and w[m-1]
                are not used.
                
        output:
            a array of interpolated vlaues is returned.               
               
    """

    if isSequenceType(times) and len(times)==0:
        return
    
    if k<1 or k>5:
        raise ValueError("Unsupported spline interpolation order.")
    
    tticks=_check_input_times(times)
    
    (start_i,end_i)=_check_fitting_bounds(ts,time_begin,time_end)
    
    if not(start_i==0) or not(end_i==(len(ts.data)-1)):
        ## Sliceing is needed
        ts_ticks=ts.ticks[start_i:end_i]
        ts_data=ts.data[start_i:end_i]
    else:
        ts_ticks=ts.ticks
        ts_data=ts.data
   
    if filter_nan:
        ts_data,ts_ticks=filter_nana(ts_data,ts_ticks)
    
    ## splrep cann't hanle multi-rank data directly.
    ## so,it needes to be done here.    
    if ts_data.ndim==1:
        ## Generate spline representation.
        tck=splrep(ts_ticks,ts_data,s=s,per=per,k=k) 
        ## Calculate values.
    
        v=splev(tticks,tck,der=0)
        if not isSequenceType(v):
            v=array([v])
        return v
     
    elif ts_data.ndim>1: 
        l=len(tticks)      
        values=zeros([ts_data.shape[1],l])+nan
        ## transpose orginal data for speed up
        temp_data=transpose(ts_data)
        for i in range(ts_data.shape[1]):
            tck=splrep(ts_ticks,temp_data[i,:],s=s,per=per,k=1)
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
    if isSequenceType(times):
        ## Here assume sequence contains
        ## elements of same type.
        test_tm=times[0]
        issequence=True
    else:
        test_tm=times

    if not issequence:
        times=[times]
        
    if isinstance(test_tm,datetime.datetime):
        tticks=map(ticks,times)
        tticks=array(tticks,float)           
    elif isNumberType(test_tm):      
        tticks=array(times,float)
    else:
        raise TypeError("Second input for interpolation functions" \
        " must be list/array of number or datatime, or single" \
        " number or datetime")

    return tticks

def _check_fitting_bounds(ts,time_begin,time_end):
    
    # If boundary is given findout boundary index within ts.    
    begin_index=0
    end_index=len(ts.data)-1

    if type(time_begin)==datetime.datetime:
        time_begin=ticks(time_begin)

    if type(time_end)==datetime.datetime:
        time_end=ticks(time_end)    
    
    if time_begin:
        begin_index=ts.index_after(time_begin)
        if begin_index>len(ts.data)-3+k:
            raise ValueError(" Fitting interval is out of available timesers data."+ 
                             " Move interval begining time backward.")

    if time_end:
        end_index=ts.index_after(time_end)-1
        if end_index>len(ts.data)-3+k:
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
