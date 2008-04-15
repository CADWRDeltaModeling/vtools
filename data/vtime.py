""" Basic ops for creating, testing and manipulating times and time intervals.
    This module contains factory and helper functions for working with
    times and time intervals.

    The module will import the name datetime and is
    designed to work exclusively with python datetimes. In addition, datetimes
    are convertible to long integer timestamps called ticks. The resolution
    of 1 tick in ticks per second may be obtained using the resolution()
    function or certain utility constants such as ticks_per_day. Never
    code with hard wired numbers.

    For time intervals (or deltas), VTools requires a time and time
    interval system that is consistent (e.g. time+n*interval makes sense)
    and that can be applied to both calendar dependent
    and calendar-independent intervals. Because this requirement
    is not met by any one implementation it is recommended that
    you always use the factory functions in this module
    for creating intervals or testing whether an interval is valid.
"""

import numpy
import datetime as _datetime
#from datetime import datetime
#import dateutil.relativedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from time import strptime
from string import lower,strip
import re #,pdb

def resolution():
    return 1L

ticks_per_second=resolution()
ticks_per_minute=resolution()*60L
ticks_per_hour=ticks_per_minute*60L
ticks_per_day=24L*ticks_per_hour
time_base=_datetime.datetime.min

def ticks(time,base=time_base):
    """ Convert a datetime to a long integer.
        The long integer is a number of units since a
        time base. The actual value depends on resolution.
    """
    if time==None:
        raise TypeError("ticks not provided")
    if isinstance(time,_datetime.timedelta):
        return time.days*ticks_per_day + time.seconds*ticks_per_second
    elif isinstance(time,_datetime.datetime):
        rel=time-base
        return rel.days*ticks_per_day + rel.seconds*ticks_per_second
    else:
        raise ValueError("ticks not defined for relative delta")


def time_interval(years=0,months=0,days=0,hours=0,minutes=0,seconds=0):
    """Create a time interval.
       Create a time interval representing the inputs that is appropriate for VTools.
       This function is the 'hard way' to create a time interval. However, it is useful
       when the interval is not known in advanced and must be created programatically.
    """
    if(years == 0 and months == 0):
        return _datetime.timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
    else:
        return relativedelta(years=years,months=months,days=days,minutes=minutes)

def increment(time,interval,nintvl=1):
    """ Increment a time by an interval.
    Safely increment time by interval ninterval times. This function
    helps resolve a bug in dateutil.
    Arguments:
       time: time to be incremented
       interval: the interval to use
       nintvl: number of times to increment it
    """
    if int(nintvl)==0:
        return time   
    if (isinstance(interval,relativedelta)):
        dt=interval*nintvl
        dt.years=long(dt.years)
        dt.months=long(dt.months)
        dt.days=long(dt.days)
        dt.hours=long(dt.hours)
        dt.minutes=long(dt.minutes)
        dt.seconds=long(dt.seconds)
        dt.microseconds=0L
    else:
         dt=nintvl*interval
    return time+dt


def number_intervals(start,end,dt):
    """
    Calculate the number of intervals dt between start and end time.
    The result is the max number_intervals such that
     start + number_intervals*dt <= end.
    """	
    if start==end:
        return 0
    if isinstance(dt,_datetime.timedelta):
        intvl=end-start
        secs_intvl=ticks(intvl)
        secs_dt=ticks(dt)
        return secs_intvl//secs_dt
    if isinstance(dt,relativedelta):
        est_intvl=ticks(increment(start,dt))-ticks(start)
        est_rng=ticks(end)-ticks(start)
        est_n=est_rng//est_intvl
        while (increment(start,dt,(est_n+1)) <= end):
            est_n += 1
        while (increment(start,dt,est_n) > end):
            est_n -= 1            
        return est_n

def seconds(s):
    """ Create a time interval representing s seconds"""
    return _datetime.timedelta(seconds=s)

def minutes(m):
    """ Create a time interval representing m minutes"""    
    return _datetime.timedelta(minutes=m)

def hours(h):
    """ Create a time interval representing h hours"""    
    return _datetime.timedelta(hours=h)

def days(d):
    """ Create a time interval representing d days"""
    return _datetime.timedelta(days=d)

def months(m):
    """ Create a time interval representing m months"""
    return relativedelta(months=m)

def years(y):
    """ Create a time interval representing y years"""
    return relativedelta(years=y)

def time_sequence(start,dt,n):
    """ Create ticks sequence based on provided start datetime, and timedelta/relativedelta dt
        start must be instance of datetime.
        input:
            start: must be a instance of datetime,
            dt: maybe timedelta or relativedelta.
            n: number of time points, not number of intervals.
        return:
            A time sequence array in ticks.
    """

    if not isinstance(start,_datetime.datetime):
        raise TypeError("1st argument of time_sequence"
        "must be type of datetime")
    
    if start.day>28:
        if type(dt)==type(years(1)):
            if dt.months or dt.years:
                raise ValueError("Time sequence "
                "starting after 28th day by interval %s"
                "is not defined"%str(dt))
    
    if isinstance(dt,_datetime.timedelta):
        start=(start-time_base)
        sticks=ticks(start)
        dticks=ticks(dt)
        tseq=numpy.arange(long(n))*(dticks) + sticks
    elif isinstance(dt,relativedelta):
        tseq=numpy.arange(long(n))
        for i in range(n):
            rel=increment(start,dt,i) - time_base
            tseq[i]=ticks(rel)
    else:
        raise  TypeError("2st argument of time_sequence must be\
        datetime.timedelta or dateutil.relativedelta.relativedelta") 
    return tseq

    
def ticks_to_time(ticks,base=time_base):
    """Convert a number of ticks to a datetime"""
    return base+_datetime.timedelta(seconds=long(ticks)/ticks_per_second)

def ticks_to_interval(ticks,base=time_base):
    """Convert a number of ticks to a time interval."""
    d=ticks//ticks_per_day
    s=(ticks - d*ticks_per_day)//ticks_per_second
    return timedelta(days=d,seconds=s)


def is_interval(intvl):
    """Determine whether the argument is a time interval.
       This is the safe way to determine whether the input is a time
       interval class understood by Vtools.
    """
    if not intvl:
        return False
    return isinstance(intvl,_datetime.timedelta) or \
           isinstance(intvl,relativedelta)

def is_calendar_dependent(intvl):
    """Determine whether the input is a calendar dependent time interval.
       Returns true if the length of the interval does not depend on
       the calendar, currently implemented by determining whether the interval
       includes months or years.
    """
    if not is_interval(intvl): raise TypeError("intvl must be a time interval")
    if isinstance(intvl,relativedelta):
        assert intvl.years != 0 or intvl.months != 0
        if intvl.years==0 and intvl.months==0:
            return False
        else:
            return True
    else:
        return False

def parse_interval(interval_string):
    """ Parse interval expressed as string and return a valid time interval
        input:
           interval_string: a string containing the interval to be parsed. May
                            contain spaces, numbers, and abbreviations:
                            s,sec,second
                            m,min,minute
                            h,hr,hour
                            d,day
                            mon,month
                            y,yr,year
        output: time interval of appropriate class for vtools depending on
        calendar dependence
    """
    if not(type(interval_string)==str):
        raise TypeError("parse_interval only accept string input.")
    
    interval_string=strip(lower(interval_string))
    interval=None
    
    time_pattern=re.compile(r'(-?\d+)(\D+)')
    matches=time_pattern.findall(interval_string)

    if not(matches):
        print interval_string
        raise ValueError("invalid time interval string %s" % interval_string )

    units={"s":"seconds","sec":"seconds","seconds":"seconds",
          "m":"minutes","min":"minutes","minute":"minutes","minutes":"minutes",
          "h":"hours","hr":"hours","hour":"hours","hours":"hours",
          "d":"days","day":"days","days":"days",
          "mon":"months","month":"months",
          "y":"years","yr":"years","year":"years","years":"years"}

    args={}
    for t in matches:
        n=int(strip(t[0]))
        ss=strip(t[1])
        ## for time_delta funciton don't honor week input, convert week into days.
        if ss.lower()=="week" or ss.lower()=="weeks":
            ss="days"
            n=n*7
        unit=units[ss]
        args[unit]=n

    return time_interval(**args)

                           
                
def align(timepoint,interval,side):
    """ Finds a neat time point that is calendar aligned with the given
        interval either to the right (+1) or the left (-1) of the arg
        timepoint. E.g., align(01Jan1992 00:"""
    if (not isinstance(timepoint,_datetime.datetime)):
        raise TypeError("timepoint argument must be a datetime")
    if (not is_interval(interval)):
        raise TypeError("interval argument not a valid interval")

    nintvl = number_intervals(time_base,timepoint,interval)
    left =  increment(time_base,interval,nintvl)
    if (side == -1):
        return left
    else:
        if (left == timepoint): return left
        else: return increment(left,interval)


def parse_time(t):
    """ Given a input as ticks or string
        try to return its datetime equivalent.
    """
    try:
        try:
            return _datetime.datetime(*strptime(t, "%d%b%Y %H:%M")[0:6])
        except:
            return _datetime.datetime(*strptime(t, "%d%b%Y")[0:6])
    except:
        if type(t)==str:
           t=t.strip()
           return parse(t)


    
    
    
    
    


            
    
    

    

