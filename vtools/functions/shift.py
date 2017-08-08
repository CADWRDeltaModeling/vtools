""" Shift operations over a time series, original time series with shifted
    start_time,end_time and times is return.
"""

# Python lib import.
from copy import deepcopy

import numpy

# Vtool vtime import.
from vtools.data.vtime import *
from vtools.data.timeseries import rts, its

__all__ = ["shift"]


###########################################################################
# Public interface.
###########################################################################

def shift(ts, interval, copy_data=True):
    """ Shift entire time series by a given interval

    Parameters
    ----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        A regular timeseries to be shifted.

    interval : :ref:`time_interval <time_intervals>`
        Interval of the shifting.

    copy_data : boolean,optional
            If True, the result is an entirely new series with deep copy of all data and properties. Otherwise, it will share data and properties.

    Returns
    -------
    shifted : :class:`~vtools.data.timeseries.TimeSeries`
        A new time series with shifted times.

    """

    if copy_data:
        new_data = numpy.copy(ts.data)
        new_props = deepcopy(ts.props)
    else:
        new_data = ts.data
        new_props = ts.props

    if not is_interval(interval):
        interval = parse_interval(interval)

    if ts.is_regular():
        return rts(new_data, increment(ts.start, interval, 1),
                   ts.interval, new_props)
    else:
        if is_calendar_dependent(interval):
            tms = ts.times + interval
        else:
            tms = ts.ticks + ticks(interval)
            # ts._ticks=scipy.array(map(ticks,time_op(ts.times,interval)))
        return its(tms, new_data, new_props)
