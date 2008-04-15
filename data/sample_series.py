import sys

    
import datetime
from timeseries import *
from enthought.util.numerix import arange
from scipy.special import jn,nan

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



            
        
    
    
    



    
    
    


    
