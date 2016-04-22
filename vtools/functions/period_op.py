""" Period operation over a regular time series, the returned new time
    series are aligned with operation interval( e.g. monthly data
    will start on the first day of the month).
"""



## Python libary import.
import datetime

## Scipy import.
from scipy import maximum as scimaximum
from scipy import minimum as sciminimum
from scipy import add as sciadd
from scipy import equal as sciequal
from scipy import subtract as scisubtract
from scipy import int64 as sciint64
from scipy import array as sciarray
from scipy import nan, isnan,zeros
from scipy import alltrue,isfinite,inf,sometrue,where

## Vtool vtime import.
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,is_interval\
     ,parse_interval,align,is_calendar_dependent

from vtools.data.timeseries import rts,its
from vtools.data.constants import *
#from vtools.debugtools.timeprofile import debug_timeprofiler

########################################################################### 
## Public interface.
###########################################################################

__all__=["period_op","period_min","period_max","period_ave"\
         ,"period_sum","TRAPEZOID","RECT"]



## Operators dic used to do actual operations.
operator_dic={MAX:scimaximum,MIN:sciminimum,MEAN:sciadd,SUM:sciadd}

TRAPEZOID="trapezoid"
LEFTSUM="leftsum" ## TEMPORARY NAME
RECT=LEFTSUM

def period_op(ts,interval,op,method=None):
    """Apply a period operation on a time series.
    
    .. note:: 
        Only valid data of input 'ts' will be considered.
        The 'method' input is only meaningful for averaging operation, if not
        given, function will select one method based
        on the timestamp property of time seris.
        
     Parameters
     ----------
     ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be operated.
        
     interval : :ref:`time_interval <time_intervals>` 
        Interval of operation.
        
     op: string
        three optiona are avaible, MAX,MIN and MEAN (in :mod:`vtools.data.constants` )
            
     method : string, optional
        the averaging method going to be used, Two option avaiable, TRAPEZOID and RECT
        
     Returns
     -------    
     Result : :class:`~vtools.data.timeseries.TimeSeries`
         a new time series with period interval that is the result
         of applying op consecutively over calendar periods
        
     Raises
     --------
     error : :py:class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
          
    """
    
    if not is_interval(interval):
        interval=parse_interval(interval)
    
    ## Check if input ts is regular ts.
    #if not(ts.is_regular()):
    #    raise ValueError("Input timeseries is not a regular" 
    #                     " interval time series")

    ## Check ts interval is compatible with opertional interval.
    if not (_check_interval_compatible(ts.interval,interval)):
        raise ValueError("Period operation by %s on a regular"
                         " timeseries with interval of %s is" 
                         " undefined"%(interval,ts.interval))

    
    ## select mean method if doing mean.
    if op==MEAN:
        if not method:
            if TIMESTAMP in ts.props.keys() and \
               ts.props[TIMESTAMP]==INST:
                method=TRAPEZOID
            else:
                method=LEFTSUM
    
    ## Align time calendar first by finding 
    ## valid starting time point.
    ts_start=ts.start
    ts_end=ts.end
    if (TIMESTAMP in ts.props.keys()) and (ts.props[TIMESTAMP]==PERIOD_START):
        ts_end=ts_end+ts.interval
        
    aligned_start=align(ts_start,interval,1)

    if not (aligned_start==ts_start):        
        if aligned_start>ts_end or (aligned_start+interval)>ts_end:
            raise ValueError("Input timeseries is not long enough " \
                  "to apply operation.")

    
    num=number_intervals(aligned_start,ts_end,interval)
    aligned_start_ticks=ticks(aligned_start)
    ndx_after=ts.index_after(aligned_start_ticks)  
    start_index=sciint64(ndx_after)
    
    if not (op in operator_dic.keys()):
        raise ValueError("Invalid operation %s,it must be" \
                         " one of %s."%(op,operator_dic.kyes()))

    ##operator= operator_dic[op]    
    ## ts property dic
    prop={}
    prop[TIMESTAMP]=PERIOD_START
    prop[AGGREGATION]=op
    for key,val in ts.props.items():
        if (not (key==TIMESTAMP)) and (not (key==AGGREGATION)):
            prop[key]=val
        
    ## Depending on the calendar dependence of interval,
    ## two methods are chosen to perform operation, first
    ## one is adapted from code by Alexander Ross from
    ## ASPN, which is faster.
    if is_calendar_dependent(interval):
        ntt= _calendar_dependent_op(ts,op,interval,\
                             aligned_start,start_index,\
                             num,prop,method)
    else:
        ntt=_calendar_independent_op(ts,op,interval,\
                             aligned_start,start_index,\
                             num,prop,method)
    return ntt

def period_min(ts,interval):
    """Find a period minimum values on a time series.

     Parameters
     ----------
     ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be operated.
        
     interval : :ref:`time_interval <time_intervals>` 
        Interval of operation.
    
        
     Returns
     -------    
     Result : :class:`~vtools.data.timeseries.TimeSeries`
         a new time series with period interval that is the result
         of applying min operation consecutively over calendar periods
        
     Raises
     --------
     error : :py:class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
    """
    
    
    return period_op(ts,interval,MIN)

def period_max(ts,interval):
    """Find a period maximum on a time series.
 
     Parameters
     ----------
     ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be operated.
        
     interval : :ref:`time_interval <time_intervals>` 
        Interval of operation.
    
        
     Returns
     -------    
     Result : :class:`~vtools.data.timeseries.TimeSeries`
         a new time series with period interval that is the result
         of applying min operation consecutively over calendar periods
        
     Raises
     --------
     error : :class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
    """
    
    
    return period_op(ts,interval,MAX)

def period_ave(ts,interval,method=None):
    """Find a period mean on a time series.
    
     Parameters
     ----------
     ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be operated.
        
     interval : :ref:`time_interval <time_intervals>` 
        Interval of operation.
    
        
     Returns
     -------    
     Result : :class:`~vtools.data.timeseries.TimeSeries`
         a new time series with period interval that is the result
         of applying average operation consecutively over calendar periods
        
     Raises
     --------
     error : :class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
    """    
    return period_op(ts,interval,MEAN,method)

def period_sum(ts,interval):
    """Find a period sum on a time series.

     Parameters
     ----------
     ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be operated.
        
     interval : :ref:`time_interval <time_intervals>` 
        Interval of operation.
    
        
     Returns
     -------    
     Result : :class:`~vtools.data.timeseries.TimeSeries`
         a new time series with period interval that is the result
         of applying sum operation consecutively over calendar periods
        
     Raises
     --------
     error : :py:class:`ValueError`
        If input time series is not regular, or regular interval is calendar
        dependent, or input downsampling interval is narrower than original
        one.
    """
    return period_op(ts,interval,SUM)

########################################################################### 
## Private interface.
###########################################################################

def _calendar_independent_op(ts,op,interval,\
                             aligned_start,start_index,\
                             num,prop,method):
    """ if op interval is independent of calendar, use this
        function to do operation.
    """
    tsdata=ts.data
    interval_ticks=ticks(interval)
    stepsize=int(interval_ticks/(ts.ticks[1]-ts.ticks[0]))
    end_index=sciint64(start_index+num*stepsize)
    data=tsdata[start_index:end_index,]
    if data.ndim==2:
        data=data.reshape(num,stepsize,-1)
    elif data.ndim==1:
        data=data.reshape(num,stepsize)
    else:
        raise StandardError("Time series data has dimension size larger than 2.")
    
    operator= operator_dic[op] 
    if operator==sciadd and op==MEAN:
        if method==LEFTSUM:
            data=operator.reduce(data,1)
        elif method==TRAPEZOID:
            dhalf1=data[0:num,0,]*0.5
            
            ## this handling is to include last
            ## value point into calculation.
            if tsdata.ndim==2:                
                dhalf2=zeros((num,tsdata.shape[1]))
            elif tsdata.ndim==1:
                dhalf2=zeros(num)
                
            dhalf2[0:num-1,]=data[1:num,0,]*0.5
            dhalf2[num-1,]=tsdata[end_index,]*0.5        
            data=operator.reduce(data,1)
            data=data[0:num]-dhalf1+dhalf2            
        data=data/float(stepsize)               
    else:
        data=operator.reduce(data,1)        
    return rts(data,aligned_start,interval,prop)    

def _calendar_dependent_op(ts,op,interval,\
                             aligned_start,start_index,\
                             num,prop,method):
    
    """ if op interval is dependent of calendar, use this
        function to do operation.
    """
    ## why put num+1 here, for num is number of interval
    ## contained within ts, then total points marks all
    ## the intervals must be num+1, time_sequence gen
    ## time sequence by the number of time points, not
    ## number of itervals. To make a more complete
    ## operation over the ts data, all the points are
    ## needed, check some sub func below.
    times=time_sequence(aligned_start,interval,num+1)
    operation_index=ts.index_after(times)
    tsdata=ts.data
    
    if not operation_index.any():
        raise StandardError("Error in building operation" 
                            " indexs in period operation funcs.")
    
    operator= operator_dic[op]
    
    if operator==sciadd and op==MEAN:
        if method==LEFTSUM:
            data=_calendar_dependent_mean_leftsum(operation_index,tsdata)
        elif method==TRAPEZOID:
            data=_calendar_dependent_mean_trapezoid(operation_index,ts)
    else: #operator==sciminimum or operator==scimaximum or:
        data=_calendar_dependent_ops(operation_index,operator,tsdata)
        
    out=rts(data,aligned_start,interval,prop)
    return out


def _allocate_data_array(first_dim_size,tsdata):
    """ allocate a nan array for the use of operation
        according to time series data tsdata, this array
        will has size of first_dim_size*tsdata.shape[1] for
        2 dimensional tsdata, for one dimensional its size is
        first_dim_size.
    """
    if tsdata.ndim==1:
        data=zeros(first_dim_size)+nan
    elif tsdata.ndim==2:
        data=zeros(first_dim_size,tsdata.shape[1])+nan
    
    return data

def _calendar_dependent_ops(operation_index,operator,tsdata):
    """ calendar dependent of min, max except add.
        consistently return data with size of number of interval,
        this is num in _calendar_dependent_op' input.
    """

    data=_allocate_data_array(len(operation_index)-1,tsdata)

    ## here to see the effect of start and end points
    ## as metioned in _calendar_dependent_op, when
    ## ei move to last operation index, it it used as a
    ## indicator of slice only.
    for i in range(len(operation_index)-1):
        si=operation_index[i]
        ei=operation_index[i+1]
        val=operator.reduce(tsdata[si:ei,],0)    
        data[i]=val        
    return data

def _calendar_dependent_mean_leftsum(operation_index,tsdata):
    """ calendar dependent op of mean leftsum only.
        consistently return data with size of number of interval,
        this is num in _calendar_dependent_op' input.
    """

    data=_allocate_data_array(len(operation_index)-1,tsdata) 
    for i in range(len(operation_index)-1):
        si=operation_index[i]
        ei=operation_index[i+1]
        val=sciadd.reduce(tsdata[si:ei,],0)
        val=val/float((ei-si))
        data[i]=val
    return data
       
def _calendar_dependent_mean_trapezoid(operation_index,ts):
    """ calendar dependent op of mean trapezoid only."""

    data=_allocate_data_array(len(operation_index)-1,ts.data)
  
    for i in range(len(operation_index)-1):
        si=operation_index[i]
        ei=operation_index[i+1]
        val=sciadd.reduce(ts.data[si:ei,],0)
        #if ei<len(tsdata): 
        val=val-0.5*ts.data[si,]+0.5*ts.data[ei,]
        val=val/float((ei-si))
        data[i]=val
    #pdb.set_trace()

    return data

def _check_interval_compatible(ts_interval,op_interval):

    """ Check whether time series interval is compatible with
        operational interval.

        For non calendar dependent operational interval, such as
        1hour,2day,3hours,etc., its ticks must be integer times of
        ts time interval ticks.

        For calendar dependent operational interval, such as 1 year,
        2 month, ts time interval ticks must be smaller than 1 day and
        can be divided by 1day ticks without remainder, if ts time
        interval is calendar independent. If both are calendar dependent,
        neither can contain interval of days,hours,minutes and seconds.
        and the months of ts interval must be divided by op interval months
        without remainder.

        input:
            ts_interval_ticks: regular ts time interval as timedelta or relativedelta.
            op_interval: operation time interval in timedelta or
            relativedelta.
    """

    if not is_calendar_dependent(op_interval):

        if is_calendar_dependent(ts_interval):
            return False

        op_ticks=ticks(op_interval)
        ts_interval_ticks=ticks(ts_interval)
        if ts_interval_ticks>= op_ticks:
            return False
        else:
            if (op_ticks%ts_interval_ticks):
                return False
    else:
        
        if not (is_calendar_dependent(ts_interval)):
            day_ticks=ticks(datetime.timedelta(days=1))
            ts_interval_ticks=ticks(ts_interval)
            if ts_interval_ticks>day_ticks:
                return False
            else:
                if day_ticks%ts_interval_ticks:
                    return False
                
        else:
            mt=ts_interval.months
            yt=ts_interval.years
            dt=ts_interval.days
            ht=ts_interval.hours
            mit=ts_interval.minutes
            st=ts_interval.seconds

            yo=op_interval.years
            mo=op_interval.months
            do=op_interval.days
            ho=op_interval.hours
            mio=op_interval.minutes
            so=op_interval.seconds

            if dt or ht or mit or st \
               or do or ho or mio or so:
                return False
            else:
                myt=mt+yt*12
                myo=mo+yo*12
                if myo%myt:
                    return False                   
    return True    
     
            
