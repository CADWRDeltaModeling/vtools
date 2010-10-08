#-------------------------------------------------------------------------------
#
#  Helper functions for calculating axis tick related values (i.e. bounds and
#  intervals)
#
#  Written by: Eli Ateljevich (based on similar routines written by Eric Jones and David Morrill)
#
#  Date: 10/10/2006
#
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

#from plot_base import *
from vtools.data.vtime import *
from numpy import *

def _calc_time_unit(tick_intvl,start):
    stime=ticks_to_time(start)
    end = start+tick_intvl
    etime=ticks_to_time(end)
    basic_times=[[ticks_per_second,seconds(1),stime],
                 [ticks_per_minute,minutes(1),stime],
                 [ticks_per_hour,hours(1),stime],
                 [ticks_per_day,days(1),stime],
                 [ticks_per_day*30,months(1),stime],
                 [ticks_per_day*365,time_interval(years=1),stime],
                 [ticks_per_day*3650,time_interval(years=10),stime],
                 [ticks_per_day*365000,time_interval(years=1000),stime],
                 ]
    units = None
    mantissas = None
    
    for i in range(len(basic_times)):
        if (tick_intvl >= basic_times[i][0] and \
            tick_intvl < basic_times[i+1][0]):
            units = basic_times[i][1]
            nintvl=number_intervals(stime,etime,units)
            even_end=increment(stime,units,nintvl)
            even_ticks=ticks(even_end)
            if even_end == etime:
                fraction = 0.
            else:
                unit_tick = float(ticks(even_end+units)-even_ticks)
                fraction=(end - even_ticks)/unit_tick
            break
        
    return units,float(nintvl+fraction)
        

def _create_magic_intervals(units):
    nmagic=6
    # list of intervals plus attractive numbers of these intervals
    mi = {str(seconds(1)):[1,2,5,10,30,60],  \
          str(minutes(1)):[1,2,5,10,30,60],  \
          str(hours(1)):[1,2,6,12,24,48],    \
          str(days(1)):[1,2,7,7,14,30],      \
          str(months(1)):[1,2,3,4,6,12],     \
          str(years(1)):[1,2,5,10,100,1000]  \
          }
    magics = []
    for i in range(len(units)):
        magics.append(mi[str(units[i])])
    magics = numpy.array(magics)
    return magics.transpose()



def auto_time_ticks ( data_low, data_high, bound_low, bound_high, tick_interval,
                 use_endpoints = True):
    """ Finds locations for axis tick marks assuming ticks represent datetimes

		Calculates the location for tick marks on an axis. data_low and data_high 
		specify the maximum and minimum values of the data along this axis. 
		bound_low, bound_high, and tick_interval specify how the axis end points 
		and tick interval are calculated. An array of tick mark locations is 
		returned from the function.  The first and last tick entries are the 
		axis end points.

		Parameters
		----------

		data_low, data_high
			The maximum and minimum values of the data along this axis.
			If any of the bound settings are 'auto' or 'fit', the axis
			traits are calculated automatically from these values.
		bound_low
			Can be 'auto', 'fit' or a number.
		bound_high
			If a number,the axis trait is set to that value.  If the
			value is 'auto', the trait is calculated automatically.
			The value can also be 'fit' in which case the axis end
			point is set equal to the corresponding data_low/data_high value.
		tick_interval
			Can be 'auto' or a positve number specifying the length
			of the tick interval, or a negative integer specifying the
			number of tick intervals.
    """

    is_auto_low  = (bound_low  == 'auto')
    is_auto_high = (bound_high == 'auto')

    if type( bound_low ) is str:
        lower = data_low
    else:
        lower = float( bound_low )
       
    if type( bound_high ) is str:
        upper = data_high
    else:
        upper = float( bound_high )

    if (tick_interval == 'auto') or (tick_interval == 0.0):
        rng = abs( upper - lower )
        if rng == 0.0:
            tick_interval = 0.5
            lower         = data_low  - 0.5
            upper         = data_high + 0.5

        else:
            tick_interval = auto_interval( lower, upper )
    elif tick_interval < 0:
        intervals     = -tick_interval
        tick_interval = tick_intervals( lower, upper, intervals )
        if is_auto_low and is_auto_high:
            is_auto_low = is_auto_high = False
            lower = tick_interval * floor( lower / tick_interval )
            while ((abs( lower ) >= tick_interval) and
                   ((lower + tick_interval * (intervals - 1)) >= upper)):
                lower -= tick_interval
            upper = lower + tick_interval * intervals
    
    # If the lower or upper bound are set to 'auto', 
    # calculate them based on the newly chosen tick_interval:
    if is_auto_low or is_auto_high:
        #todo ignored this case delta = 0.01 * tick_interval * (data_low == data_high)
        auto_lower, auto_upper = auto_bounds( ticks_to_time(data_low), 
                                              ticks_to_time(data_high),
                                              tick_interval )
         
        if is_auto_low:
            lower = ticks(auto_lower)
            bound_low = lower

        if is_auto_high:
            upper = ticks(auto_upper)
            bound_high = upper
            end = upper

        
    start = ticks(align(ticks_to_time(lower),tick_interval,-1))            
    end = ticks(align(ticks_to_time(upper),tick_interval,+1))    
    # Compute the range of ticks values:
    #start = floor( lower / tick_interval ) * tick_interval
    #end   = floor( upper / tick_interval ) * tick_interval
    # If we return the same value for the upper bound and lower bound, the
    # layout code will not be able to lay out the tick marks (divide by zero).
    if start == end:
        lower = start = start - tick_interval
        upper = end = start - tick_interval
        
    if upper > end:
        end += tick_interval

    stime = ticks_to_time(start)
    etime = ticks_to_time(end)
    nticks = number_intervals(stime, etime, tick_interval)
    tickrange = time_sequence(stime,tick_interval,nticks)
    ticktimes = map(ticks_to_time,tickrange)

    if len( tickrange ) < 2:
        tickrange = array( ( ( lower - lower * 1.0e-7 ), lower ) )
    if (not is_auto_low) and use_endpoints:
        tickrange[0] = lower
    if (not is_auto_high) and use_endpoints:
        tickrange[-1] = upper
    tlist=[tick for tick in tickrange if tick >= bound_low and tick <= bound_high]

    return [tick for tick in tickrange if tick >= bound_low and tick <= bound_high]

           
#--------------------------------------------------------------------------------
#  Compute the best tick interval for a specified data range:
#--------------------------------------------------------------------------------

def auto_interval ( data_low, data_high ):
    """ Calculates the tick intervals for a graph axis.

        Description
        -----------
        The boundaries for the data to be plotted on the axis are::
        
            data_bounds = (lower,upper)
                
        The function chooses the number of tick marks, which can be between
		3 and 9 marks (including end points), and chooses tick intervals at 
		1, 2, 2.5, 5, 10, 20, ...
        
        Returns
        -------
        interval : float
			tick mark interval for axis
    """    
    range = float( data_high ) - float( data_low )
    
    # We'll choose from between 2 and 8 tick marks.
    # Preference is given to more ticks:
    #   Note reverse order and see kludge below...
    divisions = numpy.arange( 7.0, 2.0, -1.0 ) # (8, 7, 6, ..., 3 )
    
    # Calculate the intervals for the divisions:
    candidate_intervals = range / divisions
    
    # Get base_unit and number of intervals for each candidate:
    calcs = map(lambda x: _calc_time_unit(x,data_low),candidate_intervals)
    base_units,mantissas = [x[0] for x in calcs],[x[1] for x in calcs]
    
    # List of "pleasing" intervals between ticks on graph.
    # These depend on the base_unit. Nrows is number of pleasing
    # possibilities. Ncols is the number of candidates
    magic_intervals = _create_magic_intervals(base_units)
    
    # Calculate the absolute differences between the candidates
    # (with magnitude removed) and the magic intervals:
    differences = abs( magic_intervals - mantissas ) 

    # Find the division and magic interval combo that produce the
    # smallest differences:

    # KLUDGE: 'argsort' doesn't preserve the order of equal values,
    # so we subtract a small, index dependent amount from each difference
    # to force correct ordering.
    sh    = shape( differences )
    small = 2.2e-16 * numpy.arange( sh[1] ) * arange( sh[0] )[:,numpy.newaxis]
    small = small[::-1,::-1] #reverse the order
    differences = differences - small
   
    # ? Numeric should allow keyword "axis" ? comment out for now
    #best_mantissa = minimum.reduce(differences,axis=0)    
    #best_magic = minimum.reduce(differences,axis=-1)
    best_mantissa  = minimum.reduce( differences,  0 )    
    best_magic     = minimum.reduce( differences, -1 )
    magic_index    = argsort( best_magic )[0]
    mantissa_index = argsort( best_mantissa )[0]

    # The best interval is the magic_interval multiplied by the magnitude
    # of the best mantissa:
    interval  = magic_intervals[ magic_index, mantissa_index ]
    result =  base_units[ mantissa_index ] * int(interval)
    
    if result == 0.0:
        result = limits.float_epsilon
    return result
           
#--------------------------------------------------------------------------------
#  Compute the best tick interval length to achieve a specified number of tick
#  intervals:
#--------------------------------------------------------------------------------

def tick_intervals ( data_low, data_high, intervals ):
    range     = float( data_high - data_low )
    if range == 0.0:
        range = 1.0 
    interval  = range / intervals
    factor    = 10.0 ** floor( log10( interval ) )
    interval /= factor

    if interval < 2.0:
        interval = 2.0
        index    = 0
    elif interval < 2.5:
        interval = 2.5
        index    = 1
    elif interval < 5.0:
        interval = 5.0
        index    = 2
    else:
        interval = 10.0
        index    = 3

    while True:
        result = interval * factor 
        if ((floor( data_low / result ) * result) + (intervals * result) >=
             data_high):
            return result
        index     = (index + 1) % 4
        interval *= ( 2.0, 1.25, 2.0, 2.0 )[ index ]
           
#-------------------------------------------------------------------------------
#  Compute the best lower and upper axis bounds for a range of data:
#-------------------------------------------------------------------------------

def auto_bounds ( data_low, data_high, tick_interval ):
    """ Calculates an appropriate upper and lower bounds for the axis from
        the the data_bounds (lower, upper) and the given axis interval.  The
        boundaries will either hit exactly on the lower and upper values
        or on the tick mark just beyond the lower and upper values.
    """    
    return (
             calc_bound( data_low,  tick_interval, False ),
             calc_bound( data_high, tick_interval, True  ) )
           
#-------------------------------------------------------------------------------
#  Compute the best axis endpoint for a specified data value:
#-------------------------------------------------------------------------------

def calc_bound ( end_point, tick_interval, is_upper ):
    """ Finds an axis end point that includes the value 'end_point'.  If the
        tick mark interval results in a tick mark hitting directly on the 
        end_point, end_point is returned.  Otherwise, the location of the tick
        mark just past the end_point is returned. end is 'lower' or 'upper' to
        specify whether end_point is at the lower or upper end of the axis.
    """
    if is_upper:
        return align(end_point,tick_interval,+1)
    else:
        return align(end_point,tick_interval,-1)

def is_interval(interval):
    return (isinstance(interval,datetime.timedelta) or \
            isinstance(interval,dateutil.relativedelta.relativedelta) )
        

