"""Examples of performing interplation over time
   series.
"""

## load necessary libs.
from vtools.functions.api import *

## to fill the invalid data points within time
## sereis ts by linear method.
ts_new=interpolate_ts_nan(ts,method=LINEAR)

## to fill the invalid data points within time
## sereis ts by spline method.
ts_new=interpolate_ts_nan(ts,method=SPLINE)

## to fill the invalid data points within time
## sereis ts by monotonic spline method.
ts_new=interpolate_ts_nan(ts,method=MONOTONIC_SPLINE)

## to create a regular time series with time step of
## 1day from a irregular time series irts by linear
## interploation.
regularTS=interpolate_its_rts(irts,"1day",method=LINEAR)

## to create a regular time series with time step of
## 1hour from a irregular time series irts by SPLINE
## interploation.
regularTS=interpolate_its_rts(irts,"1hour",method=SPLINE)

## to create a regular time series with time step of
## 1month from a irregular time series irts by monotonic
## spline interploation.
regularTS=interpolate_its_rts(irts,"1month",method=MONOTONIC_SPLINE)

