"""  Handy utility functions to read data from or save data to dss source.
"""
## python import
import sys,os,time #,pdb

## vtools import
from vtools.datastore.dss.dss_constants import DSS_DATA_SOURCE
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.data.vtime import parse_time,parse_interval
from vtools.data.timeseries import rts,its
from vtools.data.constants import *
from vtools.datastore.data_reference import DataReferenceFactory


__all__=["dss_retrieve_ts","dss_store_ts","dss_catalog",\
         "visual_dss_format","dss_delete_ts","is_valid_dss"]


dsm=DataServiceManager()
_catalog_buffer={}

##############################################           
## Public function.
##############################################

def dss_retrieve_ts(dss_file,selector,time_window=None,unique=False,overlap=None):
    """
       retrieve timesereies from a dss file on from
       specified paths within the same time_window.


    usage: rt=retrieve_dss_data(dss_file,selector)

    input:    
         dss_file: path of dss file (relative or abs).
         selector: data record paths within dss file, might
                   be a single path, or a wildcard path.
         time_window: time window of selection, can be string
                   like "(10/1/1997 12:00, 2/14/2001 11:45)", or
                   tuple of datetime (start,end) or tuple of time
                   string like ("10/1/1997 12:00","2/14/2001 11:45").
                   if not given, all data will be retrieved.
        overlap: a tuple, like (0,0),(0,1),(1,0),(1,1) or None
                 This tuple set the option of retrieving a data just preceding or
                 following time window early and late side for irregular timeseries
                 (0,0): only retrieve data within time window
                 (1,0): retrieve a data preceding time window early side in addition to data within
                 (0,1): retrieve a data following time window late side in addition to data within
                 (1,1): retrieve a data preceding and following in addition to data within
                 If early or late sides exactly coincide with data point, the data preceding or
                 following the earyl or late side will still be returned when the corresponding overlap
                 is set.
                 dss service will raise ValueError if overlap is not None in reading regular timeseries.
                
    ouput:
          one or more time series if succeed.
    """    

    if os.path.isfile(dss_file):
       dss_file=os.path.abspath(dss_file)

    ##### time profile ####
    ##debug_timeprofiler.mark("create dss service")
    ######################
    dss_service=dsm.get_service(DSS_DATA_SOURCE)

    ##### time profile ####
    ##print 'time at begining catalog',\
    ##      debug_timeprofiler.timegap()
    ######################
    
    lt=os.stat(dss_file)
   
    if dss_file in _catalog_buffer.keys():
        if not(lt[9]==lt[8]) and (lt[7]>lt[8]): ## to do, is it a enough conditon to
            c=_catalog_buffer[dss_file]         ## decide the source dss has not been changed?
        else:
            c=dss_service.get_catalog(dss_file)
            _catalog_buffer[dss_file]=c                        
    else:
        c=dss_service.get_catalog(dss_file)
        _catalog_buffer[dss_file]=c

    ##### time profile ####
    ##print 'time at done with catalog',\
    ##      debug_timeprofiler.timegap()
    ######################      

    data_ref=[df for df in c.data_references(selector,time_window)]
    
    if len(data_ref)==0:
       raise Warning("Warning:selection criteria "
       "return no data records from source."
       " no data was retrieved")

    if unique:
        if len(data_ref)>1:
            raise Warning("your selecting criteria for unique ts"
                          " matches more than one timeseries,"
                          "check it.")
    
    if len(data_ref)==1:
        return dss_service.get_data(data_ref[0],overlap)
    else:
        return map(dss_service.get_data,data_ref,overlap)


def dss_store_ts(ts,dss_file,path):
    """"
       Save a timeseris object into specficed path
       within a dss file.

    input:    
         dss_file: path of dss file (relative or abs).
         path: a data record path within dss file.
         ts: a instance of timeseris class.
    ouput:
          None       

    """
    if(len(ts)==0):
        raise ValueError("timeseries to be written is empty")
    ref=DataReferenceFactory(DSS_DATA_SOURCE,\
                             source=dss_file,\
                             selector=path)
    dss_service=dsm.get_service(DSS_DATA_SOURCE)
    dss_service.add_data(ref,ts)
    
    ## update catalog buffer
    if dss_file in _catalog_buffer.keys():
        del _catalog_buffer[dss_file] 

   
    
def dss_catalog(dss_source,selection=None):
    """ return catalog of a dss file."""    

    dss_service=dsm.get_service(DSS_DATA_SOURCE)
    cat=dss_service.get_catalog(dss_source)
    if selection:
        cat_filtered=cat.filter_catalog(selection)
        cat_filtered.set_editable()
        return cat_filtered
    else:
        return cat


def is_valid_dss(dss_file):
    """ Decide if the string dss_file point to a valid dss file."""
    if not os.path.isfile(dss_file):
        return False
    dss_file=dss_file.strip()
    if not dss_file.endswith(".dss"):
        return False
    return True

def dss_delete_ts(dssfile='',selection=''):
   """ delete selected time series from dss file."""
   
   if not is_valid_dss(dssfile):
       raise ValueError("DSS file name must point to valid dss file")
   if selection=="":
       raise ValueError("Selection for deletion may not be empty")

   cat=dss_catalog(dssfile,selection)
   lcat=len(cat)
   
   for i in range(lcat):
       cat.remove(cat.entries()[0])


def visual_dss_format(selection,write_times="all"):
    """ return a formatting string in dss style. """
    selection=selection.strip(",")
    return selection+",name=${A}_${B},unit=${unit},"\
           +"write_times="+write_times 



        
    
    
    
    
