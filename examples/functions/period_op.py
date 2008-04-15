"""Examples of performing period operation over time
   series.
"""

## loading necessary libary.
from vtools.functions.api import *


## get 1day minimal values of a timeseris
ts_min=period_min(ts,"1day")

## get 1day maximum values of a timeseris
ts_max=period_max(ts,"1day")

## get 1day average values of a timeseris
ts_min=period_aver(ts,"1day")

## get 1day average values of a timeseris
## using SQUARE method
ts_min=period_aver(ts,"1day",SQUARE)

## get 1day average values of a timeseris
## using TRAPEZOID method
ts_min=period_aver(ts,"1day",TRAPEZOID)
