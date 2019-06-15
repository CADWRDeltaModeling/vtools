# Import VTools and numpy array creation function
from vtools.data.api import *
import datetime as dtm
from numpy import arange,sin,pi
DATUM="datum"

# Create the times and data. The its function accepts
# lists or arrays. Here lists and "append" are used,
# because in the typical situation you
# can't predict the number of times.
# Where performance is an issue (say >10000 entries),
# consider using numpy arrays instead of lists
times=[]
data=[]

times.append(dtm.datetime(1990,1,1,0,0))
data.append(1.)
times.append(dtm.datetime(1990,1,2,13,30))
data.append(10.)
times.append(dtm.datetime(1990,1,4,10,15))
data.append(7.)
times.append(dtm.datetime(1990,1,5,12,20))
data.append(1.)

# create the attribute dictionary, optional
props={DATUM:"NGVD88"}

# create the series
ts=its(times,data,props)

print(ts[0])                          # todo: time series elements don't print
print(ts[1])
