""" Sample script for creating time series
 The steps for creating a regular time series are:
 0. Import VTools
 1. Create the time specifications.
 2. Create the data
 3. Create a dictionary of attributes
 4. Use rts to create the time series
"""
# Import VTools and numpy array creation function
from vtools.data.vtime import *        # todo: review import statement, vtools.data or vtools.data.api
from vtools.data.timeseries import *   # todo: review import statement "
from datetime import datetime          # todo: should import datetime.datetime as part of vtools
from numpy import arange,sin,pi
DATUM="datum"                          # todo: central place for dictionary of property keys


# Create the start time and interval
start=datetime(1990,1,1,0,0) # 01JAN1990 00:00
dt = hours(1)

# Size the data to fit the period of interest
end=datetime(1998,1,1,0,0)  #
n=number_intervals(start,end,dt)
print "number of data: %s" % n

# Create the data (see create_numpy_array.py for more examples)
# These two statements could be combined to
# data=sin(2.*pi*arange(n)/24.)
x=arange(n)
data=sin(2*pi*x/24.)  

# create the attribute dictionary, optional
props={DATUM:"NGVD88"}

# create the series
ts=rts(data,start,dt,props)

print ts[0]                          # todo: time series elements don't print
print ts[1]
