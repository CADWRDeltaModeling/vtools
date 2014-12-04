
Time series concepts and manipulation
=====================================

Time series class
----------------------------
The :class:`vtools.data.timeseries.TimeSeries` class it the fundamental data structure for both regular and irregular time series. The class supports a number of slicing and querying methods, as well as simple index-aligned arithmetic.

.. _reg_irreg:

Regular vs irregular
--------------------

We use the term *regular* when the times correspond to an organized sampling interval. In the implementation, a regular time series is simply one that has a non-None value for the :attr:`~vtools.data.timeseries.TimeSeries.interval` attribute. Rather than relying on this implementation, the preferred way to test this is the :py:meth:`~vtools.data.timeseries.TimeSeries.is_regular` method. 

Creating time series
--------------------
The time series class has a constructor, but the preferred "guaranteeed backward compatible" way to create a time series is with the factory functions :func:`~vtools.data.timeseries.rts` for regular time series or :func:`~vtools.data.timeseries.its` for irregular. 
These terms are clarified in section :ref:`reg_irreg`.

The function :func:`~vtools.data.timeseries.rts` creates a time series from a a start date, interval and array:

.. literalinclude:: ../../vtools/examples/data/create_regular_time_series.py

The function :func:`~vtools.data.timeseries.its` creates a time series from a regular time series is from a start date, interval and array:

.. literalinclude:: ../../vtools/examples/data/create_irregular_time_series.py

If what you have is a start and end time, there are two options. One is to use :func:`~vtools.data.timeseries.rts_constant`, which creates a time series initialized to a constant. You can then access the :attr:`~vtools.data.timeseries.TimeSeries.data` attribute if you want to alter it.

Properties: metadata about the series
-------------------------------------
Every time series has an attribute called :attr:`~vtools.data.timeseries.TimeSeries.props` that stores some basic metadata about the series. These include some fairly universal quantities (e.g units or type of period averaging) as well as some attributes that are data source specific. The exact names used for properties does matter if you are going to be interacting with data sources.


Timestamp conventions for period aggregated (e.g. ave) data
-----------------------------------------------------------
HEC-DSS and some real time storage programs have a convention of storing period-averaged data at the end of each period. This hard to work with in terms of labels and quality control. Vtools interacts with data sources using their own conventions, but converts it on import/export so that in the vtools environment the timestamp is at the beginning of the period. So, for instance, if you import DSS period averaged data the data will be translated from period-end to period-start on import and the reverse on export.

For plotting or cell-centered numerical work, it can also be convenient to have times and ticks that are period centered. The :meth:`TimeSeries.centered(copy_data=[True,False]) <.centered>` method will created a shared or copied-data version of the parent time series.

Indexing, slicing
-----------------

You can index or slice a series using integers or datetime objects. Indexing with a single index will return a single :class:`~vtools.data.timeseries.TimeSeriesElement`. 
If the index is a slice  using a start and stop index separated 
by a colon, the operation will return
a :class:`~vtools.data.timeseries.TimeSeries` with shared data. 
A slice in VTools follows the Python convention for the stop index -- it is not
included in the resulting slice. The behavior is demonstrated by this example:

.. literalinclude:: ../../vtools/examples/data/slice_series.py


This can be inconvenient, in which case you
may want to consider using the :meth:`.TimeSeries.window` 
for a shared memory copy or the :meth:`.TimeSeries.copy` method for a deep copy. If what you will be doing is replacing the contents of the series with another series of the same interval, use the :meth:`~vtools.data.timeseries.TimeSeries.replace` method.


Shifting series and centering period averaged data
--------------------------------------------------
A series can be shifted forward and back in time using the member function 
:meth:`.shift`, which also lets you decide whether 
you want to use copied data or a copy. 
The :meth:`.centered` method is a special case that
returns interval-centered data for period averaged time series. For instance, daily
average data in vtools will be stamped at the beginning of the period by convention
(see time stamping conventions). The appropriate centering for analysis is noon. This
is the shifting that is returned by :meth:`.centered`


Iterating through time
----------------------
Occasionally it is necessary to march through the elements of a time series. 

Not often. You should avoid stepwise iteration as much as possible. Vtools, numpy and python in general recommend "functional programming" on entire arrays or time series, and
besides not being "pythonic" the speed penalty of iterating is big at least in relative terms. When necessary, though, time series do provide their own iterator so this will work to traverse through a series by time steps:
::
    for elem in ts:
        print elem

The element in this case is an object of type TimeSeriesElement, which has just three attributes:

.. autoclass:: vtools.data.timeseries.TimeSeriesElement
    :members:
    :noindex:

There is no connection back to the parent series, so mostly you can just use this for read-only access to data at one time step. A TimeSeriesElement can also be used to set data in the time series::

    ts[element] = 7.0

although the use cases for this are few and if you are using one series to replace another
you should consider using :class:`~vtools.data.timeseries.TimeSeries.replace'.

One example where iteration is very useful is when coordinating the traversal of a coarse
and fine time series using itertools. The following comes from an 
example that coordinates the traversal of a two minute regular time series (gate_rts) and two daily series (gate_daily,qts) based on date::

    from itertools import groupby
    def elday(el):
        return dtm.datetime.combine(el.time.date(),dtm.datetime.min.time())

    ...
    
    # on entry, gate_rts is an indicator (1,0) of whether gate is open    
    for i,(k,g) in enumerate( groupby(gate_rts,elday)):
        gtot = gate_daily[k].value
        daily_pump_ave = qts[k].value
        for el in g:
            if not np.isnan(el.value):
                # on exit, a daily pumping value has been distributed
                # over the times when the gate is open, and the (1,0) indicator
                # is replaced with the value
                gate_rts[el.time] = el.value*daily_pump_ave/gtot

       


Time series arithmetic
----------------------
Most unary and binary operators that works in numpy work in vtools, only in an index aligned way:

::
    ts3 = ts1 + ts2    # ts3[ some_time ] = ts1[ some_time ] + ts2[ some_time ]  
    
The time range of the output (ts3 in the above example) will be the union of the input time series. 

Unary operators and binary operators with scalars work the same way, except there is no need for time alignment:

:: 
    is_pos = ts >= 0.    # produces a time series of boolean (True/False) values.
    ts23 = ts**(2./3.)   # each element raised to the two thirds power








