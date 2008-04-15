"""Examples of retrieve time series from
   a hdf data source. Comment, hdf source
   only support one time sereis retrieving
   a time for the momnent.
"""

## import necessary vtools lib.
from vtools.datastore.hdf5.api import *

###########################################################
### examples to retrieve time series from a hdf source ####
###########################################################

## giving a existing datasource.
source="mustbeexist.h5"

## to retrieve a time series stored at a specific path
## without time window, at specified location
selector="/hydro/data/channel_flow"
extent="channel_number=201;channel_location=upstream"

ts=hdf_retrieve_ts(source,selector,extent)

## to retrieve part of a time series within time window
## i.e.10/1/1991 13:30-2/3/1992 10:45, from a dss source
selector="/hydro/data/channel_flow"
extent="channel_number=201;channel_location=upstream;\
time_window=(10/1/1991 13:30, 2/3/1992 10:45)"
ts=hdf_retrieve_ts(source,selector,extent)



