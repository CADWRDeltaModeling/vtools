
Time series concepts and manipulation
====================================

Time series class
----------------------------
The :class:`vtools.data.timeseries.TimeSeries` class it the fundamental data structure for both regular and irregular time series. The class supports a number of slicing and querying methods, as well as simple index-aligned arithmetic.


Creating time series
--------------------
The time series class has a constructor, but the preferred "guaranteeed backward compatible" way to create a time series is with the factory functions :func:`~vtools.data.timeseries.rts` for regular time series or :func:`~vtools.data.timeseries.its` for irregular.  

Regular vs irregular
--------------------
In vtools, a regular time series is one that has a non-None value for the interval. You correct way to test this in the programming interface (ie, the one that will be kept stable) is the :py:meth:`~vtools.data.timeseries.TimeSeries.is_regular` method.  

Properties: metadata about the series
-------------------------------------
Every time series has an attribute called :attr:`~vtools.data.timeseries.TimeSeries.props` that stores some basic metadata about the series. These include some fairly universal quantities (e.g units or type of period averaging) as well as some attributes that are data source specific. The exact names used for properties does matter if you are going to be interacting with data sources.


Timestamp conventions for period aggregated (e.g. ave) data
-----------------------------------------------------------
HEC-DSS and some real time storage programs have a convention of storing period-averaged data at the end of each period. This hard to work with in terms of labels and quality control. Vtools interacts with data sources using their own conventions, but converts it on import/export so that in the vtools environment the timestamp is at the beginning of the period. So, for instance, if you import DSS period averaged data the data will be translated from period-end to period-start on import and the reverse on export.

For plotting or cell-centered numerical work, it can also be convenient to have times and ticks that are period centered. The :meth:`TimeSeries.centered(copy_data=[True,False]) <vtools.data.timeseries.TimeSeries.centered>` method will created a shared or copied-data version of the parent time series.

Indexing, slicing and shifting
------------------------------

Iterating and TimeSeriesElement
-------------------------------
Occasionally (if you follow good programming practices and emphasize functional programming) it is necessary to march through the elements of a time series. Time series do provide their own iterator:
::
    for elem in ts:
        print elem

The element in this case is an object of type :class:`vtools.data.timeseries.TimeSeriesElement', which has just three attributes:

.. autoclass:: vtools.data.timeseries.TimeSeriesElement
    :members:
    :noindex:

There is no connection back to the parent series, so mostly you can just use this for read-only access to data at one time step. A TimeSeriesElement can also be used to set data in the time series. 

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








