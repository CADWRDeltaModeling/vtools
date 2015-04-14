
Timeseries concepts and manipulation
====================================


Datetime and ticks
------------------
Vtools uses the Python standard library class :py:class:`datetime.datetime` to represent time. The term "ticks" refers to the numerical representation of time in an application-dependent unit (seconds) from a starting time datum. 
Ticks are currently long integers, but you shouldn't count on this because
it may change to floats.

Creating and parsing times
^^^^^^^^^^^^^^
Creating datetimes is done with the datetime constructor, which takes arguments in decreasing order of length (year, month, day, hour, etc.). Seldom do you go out to microseconds ... you can simplify by using as many or as few arguments as you want: 
::
    import datetime as dtm
    dt1 = dtm.datetime(2012,4)       # April 1, 2012, 00:00
    dt2 = dtm.datetime(2012,4,10,16) # April 10, 2012, 4:00PM
    
Python date and time classes have methods (:py:meth:`datetime.datetime.strptime`) for parsing dates from strings and :py:meth:`datetime.datetime.isoformat`. Note the "T" between the date and time in the ISO standard, which is convenient when parsing data in columns because you don't have to deal with recombining date and time.

Here are some examples using strftime, isotime and strptime. Note that these functions are both part of the datetime class, which is inside the datetime module:
::
    >>> import datetime as dtm
    >>> t = dtm.datetime(1990, 1, 21, 0, 30)
    >>> t.isoformat()
    '1990-01-21T00:30:00'    
    >>> t.strftime("%Y-%m-%d %H:%M")
    '1990-01-21 00:30'
    >>> dtm.datetime.strptime('2/21/02 00:30',"%m/%d/%y %H:%M")
    datetime.datetime(2002, 2, 21, 0, 30)


The function `dateutil.parse` in the `dateutil` module can guess at a lot of formats. Vtools provides :func:`~vtools.data.vtime.parse_time` if you have the format '12MAR2005 23:00' or just '12MAR2005':
::
    >>> from vtools.data.vtime import *
    >>> parse_time("21JAN1990 00:30")
    datetime.datetime(1990, 1, 21, 0, 30)

        
    
Rounding times
^^^^^^^^^^^^^^
There are routines to do the equivalent of round (nearest neat value), floor and ceiling to produce neat times. See :func:`~vtools.data.vtime.round_time`, :func:`~vtools.data.vtime.align` and :func:`~vtools.data.vtime.round_ticks`

Here are some examples:
::
    # Aligning an interval to make it "neat"
    t=datetime(1994,1,1,1,17)       # 01JAN1994 01:17
    floor   = -1                    # align takes -1 to indicate floor, +1 to indicate ceiling
    ceiling =  1                    #
    t=align(t,minutes(15),floor)    # 01JAN1994 01:15
    t=align(t,minutes(15),ceiling)  # 01JAN1994 01:30, 
    t=align(t,days(1),floor)        # 01JAN1994 00:00
    t=round_time(t,days(1))         # 01JAN1994 00:00 rounding goes down in this case

.. _time_interval:
    
Ticks
^^^^^

Ticks are the minimum representation of time, and are used in some interpolation and plotting routines. Routines for parsing and manipulating times are in in :mod:`vtools.data.vtime`. Vtools uses a long integer representing ticks since a basetime, which harks back to DSS and IBM Informix conventions. The time resolution in ticks per second (currently 1 per second, which seems kind of underresolved) is obtainable using the function :py:func:`~vtools.data.vtime.resolution`.

You can convert ticks to time using :func:`~vtools.data.vtime.ticks`
::
    from vtools.data.vtime import *
    # Convert between datetime and a numerical value used, say,
    # in a time series.
    t=datetime(1994,1,1)
    tk=ticks(t)

Note that you don't usually have to work with ticks for basic analyses and you should not ever work with the base time. The reverse conversion :func:`~vtools.data.vtime.ticks_to_time` is also available:
::
    >>> from vtools.data.vtime import *
    >>> import datetime
    >>> dt = datetime.datetime(2005,3,12)
    >>> ticks(dt)
    63246182400L
    >>> ticks_to_time(63246183600L)  # incremented by 1200s
    datetime.datetime(2005, 3, 12, 0, 20)
    

.. _time_intervals:

Time intervals
--------------
A time_interval in vtools refers to either a length of time or the sampling period (dt) of a time series. Under the hood, we actually have a different representation for truly regular fixed intervals (datetime.timedelta) and for calendar dependent longer than a month (dateutils). Both have a similar interface for many chores, and we have ensured that you can pass either of these around as a 'time_interval' in vtools interchangeably.

Creating and parsing intervals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We provide utilities for creating and parsing time_intervals.
There are several ways to create time intervals. When you know in advance the unit of the interval you want, the simplest functions are named after the interval
::
    intvl = minutes(15)
    intvl_hr = hours(1)  # etc

but there is also a parameterized version that can create an interval of any length (:func:`~vtools.data.vtime.time_interval`)
::
    # Creating a time interval using the time_interval function
    # time_interval(years=0,months=0,days=0,hours=0,minutes=0,seconds=0)
    intvl=time_interval(months=1)
    intvl=time_interval(0,0,1)      # 1 day

There is also a parsing function for string representations (:func:`~vtools.data.vtime.parse_interval`) that can be used as follows
::
    # Creating a time interval using a strings
    intvl=parse_interval("1sec")
    intvl=parse_interval("1SEC")
    intvl=parse_interval("1min")
    intvl=parse_interval("1hour")
    intvl=parse_interval("1day")
    intvl=parse_interval("1mon")
    intvl=parse_interval("1year")
Vtools function usually accepts string representation of time interval, such as "1hour", "15min" and so on.

Verifying an interval
^^^^^^^^^^^^^^^^^^^^^
Because time_intervals are a concept represented by several classes, there is a need sometimes to verify that an object meets the requirements of a vtools time interval. This is done safely by passing it to the :func:`~vtools.data.vtime.is_interval` function:
::
    >>> from vtools.data.vtime import *
    intvl = "a string"
    >>> is_interval(intvl)
    False
    >>>intvl2 = months(6)
    >>> is_interval(intvl2)
    True

Calendar-dependence
^^^^^^^^^^^^^^^^^^^
Units up to a day always have the same length. Months (28-31 days) and years (365-366 days) have slightly different lengths depending on the calendar month or year. If you want to query whether an interval is calendar dependent or not, the safest and shortest way to do it is with the utility `is_calendar_dependent`
::
    >>> from vtools.data.vtime import *
    >>> is_calendar_dependent(months(1))
    True
    >>> is_calendar_dependent(hours(13))
    False

Ticks
^^^^^
You can also pass a (calendar-independent) interval into :func:`~vtools.data.vtime.ticks`, and it will return the (constant) number of ticks represented by that interval. The function :func:`~vtools.data.vtime.ticks_to_interval` inverts that conversion.

Datetime and time interval arithmetic
-------------------------------------
Datetimes can be incremented or decremented by intervals as you would expect:
::
    >>> import datetime
    >>> tm = datetime.datetime(2009,3,10,4,0)
    >>> tm
    datetime.datetime(2009, 3, 10, 4, 0)
    >>> from vtools.data.vtime import *
    >>> tm + days(1)
    datetime.datetime(2009, 3, 11, 4, 0)
    >>> tm - time_interval(hours=3)
    datetime.datetime(2009, 3, 10, 1, 0)
    
See also the examples in :ref:`vtime_examples`

    
.. _time_sequence:

Time sequence
-------------
A time sequence is the variable that orders a time series. You may also see contexts like interpolation that specifically ask for a time_sequence. In vtools, this is a concept rather than a class ... a time sequence is a numpy array or python list of unique datetimes in ascending order. You can create a time sequence manually.
::
    >>> from datetime import datetime
    >>> import numpy as np
    >>> dts = [datetime(2013,1,1),datetime(2013,1,1,12),datetime(2013,1,2,2)]
    >>> dts # dts is an 'array-like' list of times ... which makes it a time_sequence
    [datetime.datetime(2013, 1, 1, 0, 0), datetime.datetime(2013, 1, 1, 12, 0), datetime.datetime(2013, 1, 2, 2, 0)]
    >>> tseq = np.array(dts)
    >>> tseq
    array([datetime.datetime(2013, 1, 1, 0, 0),
           datetime.datetime(2013, 1, 1, 12, 0),
           datetime.datetime(2013, 1, 2, 2, 0)], dtype=object)

It is not common to create time_sequences from scratch. More often, you will get them by querying a time series using the :attr:`vtools.data.timeseries.TimeSeries.times` property of a `TimeSeries`:
::
    seq = ts.times

.. _time_window:

Time windows
------------
Vtools does not have any special object to represent a time window. Where a time_window is requested it is delineated with a simple tuple showing its start and end time:
::
    tw = (datetime(1990,10,1), datetime(2011,10,1))









