"""Examples of merging several time series.
"""


## loading necessary lib
from vtools.functions.api import *

## shift a timeseries by interval of 1hour forward
shift(ts,"1hour")
## shift a timeseries by interval of 1hour backward
shift(ts,"1hour",forward=False)