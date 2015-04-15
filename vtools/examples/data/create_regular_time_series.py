# Import VTools and numpy array creation function
from vtools.data.api import *
import datetime as dtm
import numpy as np
DATUM="datum"  

# Create the start time and interval
start=dtm.datetime(1990,1,1,0,0) # 01JAN1990 00:00
dt = hours(1)
n = 2400

# Create the data (see create_numpy_array.py for more examples)
x=np.arange(n)
data=np.cos(2.*np.pi*x/24.) + np.cos(2.*np.pi*x/12.5)

# Create the attribute dictionary, optional
props={DATUM:"NGVD88"}

# Create the series
ts=rts(data,start,dt,props)


