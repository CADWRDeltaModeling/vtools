"""  Handy utility functions to read data from or save data to dss source.
"""
## python import
import sys,os #,pdb

## vtools import
from vtools.datastore.hdf5.hdf5_constants import HDF5_DATA_SOURCE
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.data.vtime import parse_time,parse_interval
from vtools.data.timeseries import rts,its
from vtools.data.constants import *
from vtools.datastore.data_reference import DataReferenceFactory

__all__=["hdf_retrieve_ts","hdf_store_ts","hdf_catalog"]

dsm=DataServiceManager()

##############################################           
## Public function.
##############################################

def hdf_retrieve_ts(hdf_file,selector,extent=None):
    """
       retrieve timesereies from a hdf source on from
       specified paths within the same time_window.


    usage: rt=hdf_retrieve_ts(hdf_file,path,extent)

    input:    
         hdf_file: path to hdf5 source (relative or abs).
                    given as string,i.e."test.h5"

         selector: path to data record, given as string,i.e.
               "/hydro/data/channel_flow"
         
         extent:   data extent selection criteria, may contain data channel
                   setting, may contain time window setting (default is
                   to retrieve all the time extent). i.e. "channel_number
                   =1;channel_location=upstream;time_window=(12/11/1991
                   01:00,04/02/1992 21:50)" or "reservoir_name=clifton;
                    connection_no=2"
    ouput:
          one time series if succeed.
    """    

    if os.path.isfile(hdf_file):
       hdf_file=os.path.abspath(hdf_file)
       
    hdf_service=dsm.get_service(HDF5_DATA_SOURCE)
    c=hdf_service.get_catalog(hdf_file)
    extent=extent.rstrip(';')
    extent=extent+";"
    data_refs=c.data_references(selector,extent)
    
##    if not data_ref:
##       print """ Warning:selection criteria 
##       return no data records from source.
##       no data was retrieved."""
##       return  None
    ts=[]
    for data_ref in data_refs:
       tss=hdf_service.get_data(data_ref)
       ts.append(tss)
    if len(ts)==1:
       return ts[0]
    else:
       return ts


    
def hdf_store_ts(hdf_file,path,datachannel,ts):

    """
       save a data with time to path in a existing dss file.


    usage: hdf_save_ts(hdf_file,path,data,times)

    input:    
         hdf_file: path of hdf file (relative or abs).
                   given as string,i.e. "test.h5"
                   
         path: a data record path within hdf file.
               given as string,i.e. "/hydro/data/channel_flow".
               Must be existing path for the moment.
               
         datachannel:data channel within the path
                     given as string, i.e. "channel_location=
                     upstream;channel_number=1". 
                     
         ts: a instance of timeseries. ts must has same interval
             as hdf array and its time extent must be contained
             within the latter', or error will be raised.
    
    ouput:
          None
    """
    
    if os.path.isfile(hdf_file):
       hdf_file=os.path.abspath(hdf_file)
    else:
       raise ValueError("Not existing hdf file %s"%hdf_file)

    datachannel=datachannel.strip(";")
    datachannel=datachannel.strip()

    time_extent=";time_window=("+ts.start.strftime('%m/%d/%Y %H%M')\
                 +","+ts.end.strftime('%m/%d/%Y %H%M')+")"
    
    ref=DataReferenceFactory(HDF5_DATA_SOURCE,\
                             source=hdf_file,\
                             selector=path,extent\
                             =datachannel+time_extent)
    
    hdf_service=dsm.get_service(HDF5_DATA_SOURCE)
    hdf_service.modify_data(ref,ts)   
    

## cataloging function.
    
def hdf_catalog(hdf5_source):
    """ return catalog of a dss file."""    

    hdf5_service=dsm.get_service(HDF5_DATA_SOURCE)
    ## tempory return first catalog only.
    return hdf5_service.get_catalog(hdf5_source)
    



        
    
    
    
    