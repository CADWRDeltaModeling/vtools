import sys
import datetime
from numpy import arange,loadtxt
from scipy import nan
from scipy.special import jn
from matplotlib.dates import num2date,datestr2num

## vtools import
from timeseries import *
from  constants import *



def create_sample_series():
    numpoints=100000
    arr=arange(numpoints)
    low = -5
    high = 85.0
    x = arange(low, high+0.001, (high-low)/numpoints)

    stime1=datetime(1992,3,7)
    stime2=datetime(1992,3,7,1,0)
    dt=time_interval(minutes=15)
    ts1=rts(jn(1,x),stime1,dt,None)
    ts1.data[11100:13900] = nan
    ts1.data[18300:19800] = nan
    ts1.data[34000:37000] = nan
    ts2=rts(jn(2,x),stime2,dt,None)
    ts3=rts(jn(3,x),stime1,dt,None)
    ts4=rts(jn(4,x),stime1,dt,None)
    return (ts1,ts2,ts3,ts4)


#"tidal_no_gap"
#"pt_reyes_tidal_with_gap"
#"tidal_obs_vs_model"
#"irreg_off_on"
            

def example_data(name):
  
    if (name=="pt_reys_tidal_6min"):
	     return pt_reys_tidal_6min_interval()
    elif (name=="pt_reys_tidal_1hour"):
	     return pt_reys_tidal_1hour_interval()
    else:
	    raise ValueError("invalid example series name")

def pt_reys_tidal_6min_interval():
    """ Sea surface level at Point Reys from NOAA with 6 min interval from 11/24/2013-11/25/2013
	
	"""
	
    raw_data=loadtxt("CO-OPS__9415020__wl_6min.txt",skiprows=1,converters={0:datestr2num},delimiter=",")
    start=num2date(raw_data[:,0])[0].replace(tzinfo=None)
    interval=num2date(raw_data[:,0])[1]-num2date(raw_data[:,0])[0]
    props={AGGREGATION:INDIVIDUAL,TIMESTAMP:INST,UNIT:"feet"}
    return rts(raw_data[:,1],start,interval,props)
	

def pt_reys_tidal_1hour_interval():
    """ Sea surface level at Point Reys from NOAA downsampled to 1hour interval from 11/01/2013-11/08/2013
	
	"""
	
    raw_data=numpy.loadtxt("CO-OPS_9415020_wl_1hour.txt",skiprows=1,converters={0:datestr2num},delimiter=",")
    start=num2date(raw_data[:,0])[0].replace(tzinfo=None)
    interval=num2date(raw_data[:,0])[1]-num2date(raw_data[:,0])[0]
    props={}
    return rts(raw_data[:,1],start,interval,props)
    
    



    
    
    


    
