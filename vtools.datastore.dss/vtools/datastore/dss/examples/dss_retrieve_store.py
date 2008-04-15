"""Examples of retrieve and strore time series from or into
   a dss data source.
"""

## import necessary vtools lib.
from vtools.datastore.dss.api import *

###########################################################
### examples to retrieve time series from a dss source ####
###########################################################

## giving a existing datasource.
source="mustbeexist.dss"

## to retrieve a whole time series stored at a specific path
## within dss source
selector="/Apart/Bpart/Cpart//Epart/Fpart/"
ts=dss_retrieve_ts(source,selector)

## to retrieve part of a time series within time window
## i.e.10/1/1991 13:30-2/3/1992 10:45, from a dss source
selector="/Apart/Bpart/Cpart//Epart/Fpart/"
time_window="(10/1/1991 13:30, 2/3/1992 10:45)"
## or use datetime tuple
from datetime import datetime
time_window=(datetime(1991,10,1,13,30),datetime(1992,2,3,10,45))
## or string tuples is also fine
time_window=("10/1/1991 13:30", "2/3/1992 10:45")
ts=dss_retrieve_ts(source,selector,time_window)

## to retrieve all time series whose A_part of path is 'HIST+CHAN' and
## F_part is 'USGS' within time window, from a dss source
selector="A=HIST+CHAN,F=USGS"
time_window=(datetime(1994,5,5,11,15),datetime(1998,7,4,1,45))
## If there are more than one path qualifing selection criteria
## tss is a list of timeseris, if there is only one qualifing path,
## tss is single timeseris. If no one qualifing, warning message will
## be raised.
tss=dss_retrieve_ts(source,selector,time_window)


## to retreive all time series whose A_part begins with 'RLTM'
## and B part starts with RSA.
selector="A=RLTM+*,B=RSA*"
tss=dss_retrieve_ts(source,selector)

## to retrieve all time series stored in a dss source.
selector=""
tss=dss_retrieve_ts(source,selector)


###########################################################
### examples to store time series into a dss source     ####
###########################################################

## user can only save a timeseris into a sepcified path
## within a dss source each time.
path="A/B/C//E/F/"
## assume ts is a instance of timeseries.
dss_store_ts(ts,source,path)


