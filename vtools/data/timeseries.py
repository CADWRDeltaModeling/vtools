""" Time series module
Module contains the TimeSeries class and the factory functions
for creating regular and irregular time series, as well as
some helper functions.
"""
import sys
from vtime import *
import datetime as _datetime
import numpy as np
import copy
import itertools
import scipy
import bisect
all = ["TimeSeries","TimeSeriesElement","prep_binary","range_union","rts","its"]

# python standard lib import.
from operator import isNumberType,isSequenceType
#from vtools.debugtools.timeprofile import debug_timeprofiler

def range_union(ts0,ts1):
    """Union of time ranges of two series.
       
       Parameters
       ----------
       ts0,ts1 : :class:`~vtools.data.timeseries.TimeSeries`
              The series whose union is to be found
       
       Returns
       ------- 
       range : (:py:class:`datetime.datetime`, :py:class:`datetime.datetime`)
              A tuple representing the start and end of the union of time
              ranges of ts0 and ts1, as determined by the earliest start and the latest end.
    """
      
    union_start=min(ts0.start,ts1.start)
    union_end=max(ts0.end,ts1.end)
    return (union_start,union_end)

def range_intersect(ts0,ts1):
    """Intersection of time ranges of two series.
    
      .. note::
         may return result with union_start > union_end,
         in which case there is no intersection.
    
       Parameters
       ----------
       ts0,ts1 : :class:`~vtools.data.timeseries.TimeSeries`
              The series whose union is to be found
       
       Returns
       ------- 
       range : (:py:class:`datetime.datetime`, :py:class:`datetime.datetime`)
              A tuple representing the start and end of the intersect of time ranges of ts0 and ts1
            
    """
    intersect_start=max(ts0.start,ts1.start)
    intersect_end=min(ts0.end,ts1.end)
    return (intersect_start,intersect_end)

def index_after(seq,tm):
    """Return the integer index of a time sequence that is on or after tm
    
    Parameters
    ----------
    seq : :ref:`time_sequence<time_sequence>`
    The sequence whose index will be searched
    
    tm : :py:class:`datetime.datetime`
    Time whose index is sought
    
    Returns
    -------
    The integer index in the sequence that fall on or after tm.
    
    """
    return bisect.bisect_right(seq,ticks(tm))

def indexes_after(seq,tm):
    """Return an array of indexes representing the index of seq that is on or after each
       member of tm.
       
    Parameters
    ----------
    seq : :ref:`time_sequence<time_sequence>`
    The sequence whose index will be searched
    
    tm : list of  :py:class:`datetime.datetime`
    List of times whose index is sought
    """

    return scipy.searchsorted(seq,tm)


def index_before(seq,tm):
    """Return the integer index of a time sequence that is on or before tm
    
    Parameters
    ----------
    seq : :ref:`time_sequence<time_sequence>`
    The sequence whose index will be searched
    
    tm : :py:class:`datetime.datetime`
    Time whose index is sought
    
    Returns
    -------
    The integer index in the sequence that fall on or before tm.
    
    """
    return bisect.bisect_left(seq,ticks(tm))
    
def prep_binary(ts1,ts2):
    """Create data for time-aligned op binary operation between two series
       Returns data holders and selections required to carry out
       index-aligned binary operations on two series. Mostly of interest to programmers.
       
       Parameters
       ----------
       ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
           Two regular time series with similar time intervals

       Returns
       -------
       seq : :ref:`time_sequence<time_sequence>`
           Representing the union of times from the series

       start : py:class:`datetime.datetime`
           The start of the sequence as a datetime
       
       slice0 : slice 
           Indexing slice within seq covered by ranges of both ts1 and ts2
       
       slice1 : slice
           Indexing slice within ts1 representing the region intersecting ts2
       
       slice2 : slice
           Indexing slice within ts2 representing the region intersecting ts1
    """
    if not ts1.is_regular() or not ts2.is_regular():
        raise ValueError("Time series in binary operations must be regular")
    if (ts1.interval != ts2.interval):
        raise ValueError("Series have different time interval")
    tm_union=range_union(ts1,ts2)
    tm_sect=range_intersect(ts1,ts2)
    n=number_intervals(tm_union[0],tm_union[1],ts1.interval)+1
    start=tm_union[0]
    seq=time_sequence(tm_union[0],ts1.interval,n)
    slice0=slice(index_before(seq,tm_sect[0]),index_before(seq,tm_sect[1]))
    slice1=slice(ts1.index_before(tm_sect[0]),ts1.index_before(tm_sect[1]))
    slice2=slice(ts2.index_before(tm_sect[0]),ts2.index_before(tm_sect[1]))
    return (seq,start,slice0,slice1,slice2)


def _get_span(ts,start,end,left,right):
    """ Return span of index within ts according to input start and end
    """

    if (start==None):
        start=ts.start
    elif isinstance(start,int) or isinstance(start,str):
        start=parse_time(start)
    elif not isinstance(start,_datetime.datetime):
        raise TypeError("input start must be None,integer ticks,time string or datetime")
    if (end==None):
        end=ts.end
    elif isinstance(end,int) or isinstance(end,str):
        end=parse_time(end)
    elif not isinstance(end,_datetime.datetime):
        raise TypeError("input end must be None,integer ticks,time string or datetime")

    if start>end:
        raise ValueError("Requested end of window is after time series end.")
       
    start_index=ts.index_before(start)
    start=ticks(start)

    if (start_index==0) and (not(start==ts.ticks[start_index])) and left:
        raise ValueError("Requested start of window is before time series start.")
    
    if (not(start_index==0)) and (not(start==ts.ticks[start_index])):
        if left:
          start_index-=1;
    
    end_index=ts.index_before(end)
    end=ticks(end)

    if (end_index==(len(ts)-1)) and (not(end==ts.ticks[end_index])) and right:
        raise ValueError("Requested end of window is after time series end.")   
    
    if (not(end_index==(len(ts)-1))) and (not(end==ts.ticks[end_index])):
        if not right:
          end_index-=1;
          
    assert end_index>start_index 
    
    return (start_index,end_index)

class TimeSeriesElement(object):
    def __init__(self,time_data):
        self.time_data=time_data

    def _get_value(self):
        return self.time_data[1]

    def _get_ticks(self):
        return self.time_data[0]

    def _get_time(self):
        return ticks_to_time(self.ticks)
    
    value = property(_get_value,None,None,"Value at element")
    ticks = property(_get_ticks,None,None,"Time point in long integer ticks of element")
    time = property(_get_time,None,None,"Time at element")

    def __str__(self):
        return "%s %s" % (self.time, self.value)



class TimeSeries(object):
    """ Fundamental class for both regular and irregular time series. 
       The preferred way to create a time series is with the rts or its factory functions,
       not with the constructor. The member attributes include the times and data in the series (which
       are paired) as well as methods of querying the time series properties (start, end, interval) of the time series.       
    """

    def __init__(self, times, data, props,header=None):
        """ Avoid using the constructor for client programming.
            Use the factory functions rts and its instead.
        """
        if (len(times) != len(data)):
            raise ValueError("times not same length as data")
            # fixme: what is the correct exception?
        
        # are times input as times or as a sequence
        # of ticks?
        if(len(times)>0):
            if isinstance(times[0],_datetime.datetime):
                self._ticks = scipy.array(map(ticks,times))
            else:
                self._ticks = times
        else:
            self._ticks=[]
        self._data = data    # must validate data sequence properties
        self._props = props  # must validate props        
        self._len = len(times)
        self._len = len(data)
       

    def is_regular(self):
        """Returns true if the time series is regular
           A regular series is considered regular if it has a sampling interval. This interval may
           or may not be calendar dependent. 
        """
        if hasattr(self,'interval'): 
            return not self.interval is None
        else:
            return False 
    
    def __len__(self):
        return len(self._ticks)

    def index_before(self,tm):
        """
        Return the index of the time series at point tm
        """
        return index_before(self._ticks,tm)

    def index_after(self,tm):
        """ return the indexes of the time series at/after points
            given by tm.

            Input tm maybe a single datetime or list/array datetime, or
            single ticks or list/array of ticks.
            Accordingly, return will be a single index or array of indexes
            
            If points are found, corresponding indexes will be return,
            if not, indexes whose time are directly after points will 
            be returned.

            Performance of this method is better if tm is given by ticks
            if this is convenient; otherwise, if given a sequence of times,
            the method will convert the sequence to ticks automatically.
        """
        
        ## Decsion about time type of tm, is it
        ## ticks or datetime.
 
        issequence=False
        if isSequenceType(tm):
            test_tm=tm[0]
            issequence=True
        else:
            test_tm=tm
        
        if isinstance(test_tm,_datetime.datetime):
            if issequence:
                   tm=map(ticks,tm)
            else:
                   tm=ticks(tm)
            return indexes_after(self._ticks,tm)
        elif isNumberType(test_tm):
            return indexes_after(self._ticks,tm)
        else:
            raise TypeError("Timeseries class can only"
                            " search time given as datetime"
                            " or ticks")
       


    def __iter__(self):
        ts_iter = itertools.izip(self._ticks,self._data)
        for item in ts_iter:
            yield TimeSeriesElement(item)

    # slicing/subsetting API
    def __getitem__(self,key):
        if type(key)==int:
            # return element
            return TimeSeriesElement( (self._ticks[key],self.data[key]))
        elif isinstance(key,_datetime.datetime):
            ndx = self.index_before(key)
            if self._ticks[ndx] == ticks(key):
                return TimeSeriesElement( (self._ticks[ndx],self._data[ndx]))
            else:
                raise ValueError("Subscript date must exactly match date in series")
        else:
            begndx=key.start
            endndx=key.stop
            if key.start:
                if not (type(key.start) == int or
                        isinstance(key.start,_datetime.datetime)):
                    raise TypeError("slice index start must be integer or datetime")
                if isinstance(key.start,_datetime.datetime):
                    begndx = self.index_after(key.start)
            if key.stop:
                if not(type(key.stop) == int or
                       isinstance(key.stop,_datetime.datetime)):
                    raise TypeError("slice index stop must be integer or datetime")
                if isinstance(key.stop,_datetime.datetime):
                    endndx = self.index_after(key.stop)
            props2=copy.copy(self._props)
            props2["sliced_from"]=(self.start,self.end)
            # to do: what is this header
            ts = TimeSeries(self._ticks[begndx:endndx], \
                              self._data[begndx:endndx], \
                              props2) #header=self.header)
            if self.is_regular(): ts.interval = self.interval
            return ts


    def __setitem__(self,key,item):
        if type(key) == int:
            self.data[key] = item
        elif isinstance(key,_datetime.datetime):
            ndx = self.index_before(key)
            if self._ticks[ndx] == ticks(key):
                self.data[ndx] = item
            else:
                raise IndexError("Subscript date must exactly match existing date in series")
        else:
            raise KeyError("Key not understood")
    # 
    def __delitem__(self, index):
        if( self.is_regular()):
            raise ValueError("Elements may not be deleted from a regular time series")
        else:
            del(_ticks[index])
            del(_data[index])

    def has_gap(self):
        """ find out if timeseries has nan data"""
        
        return np.any(np.isnan(self.data))

    def copy(self,start=None,end=None,left=False,right=False):
        """ Perform a copy of this series, optionally with clipped start and end
        
        Parameters
        ----------
        start : :py:class:`datetime.datetime`
            Start time of copy
        
        end : :py:class:`datetime.datetime`
            End time of copy
        
        left : boolean, optional
            Overlap so that the copy catches the value previous to the given start time (useful for irregular)

        right : boolean, optional
            Overlap so that the copy catches the next value after the given end time (useful for irregular)
        
        Returns
        -------
        result : :class:`~vtools.data.timeseries.TimeSeries`
            Copy of the series. No shared data with the original, so you can manipulate it without fear of overwriting the original series.
        
        See also
        --------
        window : Same concept but with shared data.
        """
        (startindex,endindex)=_get_span(self,start,end,left,right)
        newdata=numpy.copy(self.data[startindex:endindex+1])
        newprops=copy.copy(self.props)
        if(self.is_regular()):
            newstart=ticks_to_time(self._ticks[startindex])
            interval=copy.copy(self.interval)
            return rts(newdata,newstart,interval,newprops)
        else:
            newticks=numpy.copy(self._ticks[startindex:endindex+1])
            return its(newticks,newdata,newprops)
    
    # 
    # 
    def window(self,start=None, end=None, left=False, right=False):
        """Provide a shared-memory ts (shared data and props) with a reduced time window 
        
           .. note::
               if left=True, the first time point will be at or before the given start time
               otherwise, the first time will be at or after the given start. same for right.
               
        Parameters
        ----------
        start : :py:class:`datetime.datetime`
            Start time of window
        
        end : :py:class:`datetime.datetime`
            End time of window
        
        left : boolean, optional
            Overlap so that the copy catches the value previous to the given start time (useful for irregular)

        right : boolean, optional
            Overlap so that the copy catches the next value after the given end time (useful for irregular)
        
        Returns
        -------
        result : :class:`~vtools.data.timeseries.TimeSeries`
            Copy of the series,shared data with the original.
        
        See also
        --------
        copy : Same concept but with copied data.
        
        """
        (startindex,endindex)=_get_span(self,start,end,left,right)
        newdata=self.data[startindex:endindex+1]
        newprops=self.props
        if(self.is_regular()):
            newstart=ticks_to_time(self._ticks[startindex])
            interval=self.interval
            return rts(newdata,newstart,interval,newprops)
        else:
            newticks=self._ticks[startindex:endindex+1]
            return its(newticks,newdata,newprops)        
 
    def centered(self,copy_data=False,neaten=True):
        """ Return a time series with times centered between the timestamps of the original series.
        
        Parameters
        ----------
        copy_data : boolean,optional
            If True, the result is an entirely new series with deep copy of all data and properties. Otherwise, it will share data and properties ... more like a window than a new series.
        
        neaten : boolean, optional
        
        Returns
        -------
        result : :class:`~vtools.data.timeseries.TimeSeries`
            New series with shared or copied data with time centered between the timestamps of the original series. Note the new series has length one shorter than the original.
        """
        
        new_data=self.data[0:-1]
        if copy_data:
            new_data = numpy.copy(self.data[0:-1])
        new_props=self.props
        if copy_data:
            new_props = copy.deepcopy(self.props)
        if (self.is_regular())and(not(is_calendar_dependent(self.interval))):
            new_start=ticks_to_time(self._ticks[0]+ticks(self.interval)/2)
            interval=self.interval
            return rts(new_data,new_start,interval,new_props)
        elif (self.is_regular())and(is_calendar_dependent(self.interval)):
            dt=self.times[1]-self.times[0]
            assert(dt.seconds==0)
            interval_days=dt.days
            ##flooring to the below of half interval
            half_interval_days=interval_days//2
            if (half_interval_days==int(interval_days/2)):
                half_interval_days=half_interval_days-1
            new_start=self.times[0]+days(half_interval_days)
            interval=self.interval
            return rts(new_data,new_start,interval,new_props)
        else:
            ticks1=self._ticks[0:-1]
            ticks2=self._ticks[1:]
            interval_ticks = [t2-t1 for t1,t2 in zip (ticks1,ticks2)]
            half_interval  = [t/2 for t in interval_ticks]
            new_ticks = [t+dt for t,dt in zip(ticks1,half_interval)]
            return its(new_ticks,new_data,new_props)
            
    def shift(self,interval,copy_data=False):
        """ Return a time series with the timestamps shifted by a interval.
        
        Parameters
        ----------
        interval : :py:class:`dateutil.relativedelta`, :py:class:`datetime.timedelta`, string 
  
        copy_data : boolean,optional
            If True, the result is an entirely new series with deep copy of all data and properties. Otherwise, it will share data and properties.
    
        Returns
        -------
        result : :class:`~vtools.data.timeseries.TimeSeries`
            New series with shared or copied data with  the  shfited timestamps of the original series by inpute interval.
        """    
        
        new_data=self.data
        if copy_data:
            new_data = numpy.copy(self.data)
        new_props=self.props
        if copy_data:
            new_props = copy.deepcopy(self.props)   
 
        if not is_interval(interval):
            interval=parse_interval(interval)
               
        if self.is_regular():
            return rts(new_data,increment(self.start,interval,1),self.interval,new_props) 
        else:
            new_times=[]
            if is_calendar_dependent(interval):
               new_times=self.times + interval
            else:
               new_times=self.ticks + ticks(interval)
      
            return its(new_times,new_data,new_props)
            
    def ts_inplace_binary(f):
        def b(self,other):
            if( isinstance(other,TimeSeries) ):
                raise ValueError("In place ops not implemented for two time series")
            else:
                if (other is None): return None
                f(self._data,other)
                return self
        b.__name__=f.__name__
        return b


    # built in math
    def ts_unary(f):     
        def u(self):
            data=f(self._data)
            if self.is_regular():
                return rts(data,self.start,self.interval,None)
            else:
                return TimeSeries(self._ticks,data,None)
        u.__name__=f.__name__
        return u

    def ts_binary(f):
        def b(self,other):
            if( isinstance(other,TimeSeries) ):
                tm_seq,start,slice0,slice1,slice2 = prep_binary(self,other)
                data=scipy.ones(len(tm_seq),'d')*scipy.nan #@todo: correct the size for non-univariate
                data[slice0.start:slice0.stop+1:slice0.step]=f(self.data[slice1.start:slice1.stop+1:slice1.step],
                                                             other.data[slice2.start:slice2.stop+1:slice2.step])
                return rts(data,start,self.interval,None)
            else:
                if (other is None): return None
                data=f(self._data,other)
                if self.is_regular():
                    return rts(data,self.start,self.interval,None)
                else:
                    return TimeSeries(self._ticks,data,None)
        b.__name__=f.__name__
        return b

    @ts_binary
    def __add__(self, other):
        return self + other

    @ts_binary
    def __sub__(self, other):
        return self - other

    @ts_binary
    def __mul__(self, other):
        return self * other
    
    @ts_binary    
    def __div__(self, other):
        return self / other

    @ts_binary
    def __mod__(self, other):
        return self % other

    @ts_binary
    def __divmod__(self, other):
        return divmod(self,other)

    @ts_binary
    def __radd__(self, other):
        return other+self

    @ts_binary
    def __rsub__(self, other):
        return other-self

    @ts_binary
    def __rmul__(self, other):
        return self*other

    @ts_binary
    def __rdiv__(self, other):
        return other/self

    @ts_binary
    def __rmod__(self, other):
        return other % self

    @ts_binary
    def __pow__(self, other):
        return other % self
        
    def __rdivmod__(self, other):
        raise NotImplementedError

# Implement the inplace operators (currently only with scalar)
    @ts_inplace_binary
    def __iadd__(self,other):
        self+=other

    @ts_inplace_binary
    def __isub__(self,other):
        self-=other
        
    @ts_inplace_binary
    def __imul__(self,other):
        self*=other

    @ts_inplace_binary
    def __idiv__(self,other):
        self/=other

        
# Called to implement the unary arithmetic operations (-, +, abs()  and ~). 
    @ts_unary
    def __neg__(self):
        return -self

    def __pos__(self):
        raise NotImplementedError

    @ts_unary
    def __abs__(self) :
        return abs(self)

    def __invert__(self):
        raise NotImplementedError

# Comparisons
    @ts_binary
    def __gt__(self, other):
        return self > other

    @ts_binary
    def __lt__(self, other):
        return self < other        

    @ts_binary
    def __le__(self, other):
        return self <= other

    @ts_binary
    def __ge__(self, other):
        return self >= other                

    @ts_binary
    def __eq__(self, other):
        return self == other 

    @ts_binary
    def __ne__(self, other):
        return self != other             
        
    @ts_binary
    def __and__(self,other):
        return numpy.logical_and(self,other) 

    @ts_binary
    def __or__(self,other):
        return numpy.logical_or(self,other) 
        
# Private accessors for properties

    def _get_start(self):
        return ticks_to_time(self._ticks[0])        

    def _get_end(self):
        return ticks_to_time(self._ticks[-1])

    def _get_data(self):
        return self._data
        
    def _set_data(self,data):
        if type(data) == type(self._data):
            self._data = data

    def _get_ticks(self):
        return self._ticks

    def _get_props(self):
        return self._props
    
    def _get_times(self):
        return scipy.array(map(ticks_to_time,self._ticks))

    def _get_name(self):

        if type(self._props)==dict:
            if 'name' in self._props.keys():
                return self._props['name']
            else:
                return 'no name'
        else:
            return 'no name'
    
#   public properties
    start = property(_get_start,None,None,"Time at first element of series")
    end = property(_get_end,None,None,"Time at last element of series") 
    data=property(_get_data,_set_data,None,"Data component of series (for all time)")
    ticks=property(_get_ticks,None,None,"Array of long integer ticks representing the time index of the series")
    times=property(_get_times,None,None,"Array of datetimes represented by series")    
    props=property(_get_props,None,None,"Dictionary containing attributes, metadata and user properties")


    
def rts(data,start,interval,props=None):
    """ Create a regular or calendar time series from data and time parameters

        Parameters
        ----------
        data : array_like
            Should be a array/list of values. There is no restriction on data 
             type, but not all functionality like addition or interpolation will work on all data.
        
        start : :py:class:`datetime.datetime`
            Can also be a string representing a datetime.
        
        interval : :ref:`time_interval<time_intervals>`
            Can also be a string representing an interval that is
            understood by :func:`vools.vtime.parse_interval`. 

        Returns
        -------
        result :  :class:`~vtools.data.timeseries.TimeSeries`
            A regular time series.
    """
    
    if type(start)==type(' '):
        start=parse_time(start)
    if type(interval)==type(' '):
        interval=parse_interval(interval)
    timeseq=time_sequence(start,interval,len(data))
    if type(data)==list:
        data=scipy.array(data)
    if props == None: props = {}
    ts=TimeSeries(timeseq,data,props)
    ts.interval=interval
    return ts

def its(times,data,props=None):
    """ Create an irregular time series from time and data sequences
        
        Parameters
        ----------
        times : :ref:`time_sequence<time_sequences>`
            An array or list of datetimes or ticks
        
        data : array or list of values
            An array/list of values. No restriction on data type,
            but not all functionality will work on every data type.
        
        Returns
        -------
        result :  :class:`~vtools.data.timeseries.TimeSeries`
            An irregular TimeSeries instance
    """
    # convert times to a tick sequence
    if type(data)==list:
        data=scipy.array(data)
    if props == None: props = {}        
    ts=TimeSeries(times,data,props)

    return ts


def its2rts(its,interval,original_dates=True):
   """ Convert an irregular time series to a regular.
   
       .. note::
       This function assumes observations were taken at "almost regular" intervals with some 
       variation due to clocks/recording. It nudges the time to "neat" time points to obtain the
       corresponding regular index, allowing gaps. There is no correctness checking, 
       The dates are stored at the original "imperfect" time points if original_dates == True,
       otherwise at the "nudged" regular times.
       
        Parameters
        ----------
        its : :class:`~vtools.data.timeseries.TimeSeries`
             A irregular time series.
             
        
        interval : :ref:`time_interval<time_intervals>`
            Interval of resulting regular timeseries,Can also be a string 
            representing an interval that is understood by :func:`vools.vtime.parse_interval`. 

        original_dates:boolean,optional
            Use original datetime or nudged regular times.
        
        Returns
        -------
        result :  :class:`~vtools.data.timeseries.TimeSeries`
            A regular time series.
       
   """
   if not isinstance(interval, _datetime.timedelta): 
       raise ValueErrror("Only exact regular intervals (secs, mins, hours, days)\
                        accepted in its2rts")
   start = round_ticks(its.ticks[0],interval)
   stime = ticks_to_time(start)
   end = round_ticks(its.ticks[-1],interval)
   interval_seconds = ticks(interval)
   its_ticks = its.ticks   
   n = (end - start)/interval_seconds
   tseq = time_sequence(stime, interval, n+1)   
   data = np.ones_like(tseq,dtype='d')*np.nan
   vround = np.vectorize(round_ticks)
   tround = vround(its.ticks,interval)   
   ndx = np.searchsorted(tseq,tround)
   if any(ndx[1:] == ndx[:-1]):
        badndx = np.extract(ndx[1:] == ndx[:-1],ndx[1:])
        badtime = tseq[badndx]
        for t in badtime:
            print "Warning multiple time steps map to a single \
                   neat output step near: %s " % ticks_to_time(t)
   data[ndx]=its.data
   if original_dates:
       tseq[ndx]=its.ticks
   ts = TimeSeries(tseq,data,its.props)
   ts.interval = interval
   return ts


def rts_constant(start,end,interval,val=np.nan):
    
    """ Create a regular or calendar time series filled with constant value

        Parameters
        ----------
        start : :py:class:`datetime.datetime`
            Starting time, can also be a string representing a datetime.
        
        end : :py:class:`datetime.datetime`
            Ending time,can also be a string representing a datetime.
        
        interval : :ref:`time_interval<time_intervals>`
            Can also be a string representing an interval that is 
            understood by :func:`vools.vtime.parse_interval`. 
            
        val : float,int
            Constant will be filled into the time series.
            Optional, default is nan.
            
        Returns
        -------
        result :  :class:`~vtools.data.timeseries.TimeSeries`
            A regular time series wiht constant values
    """
    
    
    num_data=number_intervals(start,end,interval)+1
    data=np.empty(num_data)
    data.fill(val)
    ts=rts(data,start,interval,{})
    return ts
        

def extrapolate_ts(ts,start=None,end=None,method="constant",val=np.nan):
    
    """ Extend a regular time series with newer start/end 

        Parameters
        ----------
        start : :py:class:`datetime.datetime`
            The starting time to be extended to.Optional, default no extension.
        
        end : :py:class:`datetime.datetime`
           The ending time to be extended to.Optional,default no extension.
        
        method : :string
            Method to fill the extended part of resulting series. either
            "taper" or"constant". default constant.
            
        val : float
            Constant will be filled or the value that the last non-nan
            gets tapered to.
            
        Returns
        -------
        result :  :class:`~vtools.data.timeseries.TimeSeries`
           An new time series extended to the input start and end.
    """
    if start==None:
        start=ts.start
    if end==None:
        end=ts.end
        
    head_extended=number_intervals(start,ts.start,ts.interval)
    tail_extended=number_intervals(ts.end,end,ts.interval)
    
    new_len=len(ts)+head_extended+tail_extended
    data=np.empty(new_len)
    old_len=len(ts)
    data[head_extended:head_extended+old_len]=ts.data[:]
    

    if method=="constant":
        data[0:head_extended]=val
        data[head_extended+old_len:new_len-1]=val
    elif method=="taper":
        if np.isnan(val):
            raise ValueError("You must input a valid value for taper method")
        ## find out first and last non val
        temp=ts.data[~np.isnan(ts.data)]
        begin_taper_to=temp[0]
        end_taper_from=temp[-1]
        
        head_taper_step=(begin_taper_to-val)/(head_extended)
        tail_taper_step=(val-end_taper_from)/(tail_extended)
        data[0:head_extended]=np.arange(start=val,\
                                stop=begin_taper_to,step=head_taper_step)
        data[old_len+head_extended:new_len]=np.arange(start=end_taper_from+tail_taper_step,\
                                stop=val+tail_taper_step,step=tail_taper_step)
        
    else:
        raise ValueError("Unkonw filling method:"+method)
        
    new_ts=rts(data,start,ts.interval,{})
    return new_ts
        
    
    
    



    
    
    


    
