""" Sample script for creating time series
 The steps for creating an irregular time series are:
 0. Import VTools
 1. Create the times
 2. Create the data
 3. Create a dictionary of attributes
 4. Use its to create the time series
"""
# Import VTools and numpy array creation function
from vtools.data.vtime import *        # todo: review import statement, vtools.data or vtools.data.api
from vtools.data.timeseries import *   # todo: review import statement "
from datetime import datetime          # todo: should import datetime.datetime as part of vtools
from numpy import arange,sin,pi
DATUM="datum"                          # todo: central place for dictionary of property keys


# Create the times and data. The its function accepts
# lists or arrays. Here lists and "append" are used,
# because in the typical situation you
# can't predict the number of times.
# Where performance is an issue (say >10000 entries),
# consider using numpy arrays instead of lists
times=[]
data=[]

times.append(datetime(1990,1,1,0,0))
data.append(1.)
times.append(datetime(1990,1,2,13,30))
data.append(10.)
times.append(datetime(1990,1,4,10,15))
data.append(7.)
times.append(datetime(1990,1,5,12,20))
data.append(1.)

# create the attribute dictionary, optional
props={DATUM:"NGVD88"}

# create the series
ts=its(data,start,dt,props)

print ts[0]                          # todo: time series elements don't print
print ts[1]
