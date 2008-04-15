## example of using boxcar and butterworth filter
## remember: boxcar and butterworth filter
## can only be used on regular time series.

## import necessary lib
from vtools.functions.api import *
from vtools.data.vtime import *


## use boxcar filter do a centered moving average
## over 24 hours
intl=parse_interval("12hour")
ts_24=boxcar(ts,intl,intl)


## use boxcar filter do a forward moving average
## over 24 hours
intl_after=parse_interval("24hour")
intl_before=parse_interval("0min")
ts_24=boxcar(ts,intl,intl)


## use butterworth filter to low passing a series.
ts_new=butterworth(ts)



