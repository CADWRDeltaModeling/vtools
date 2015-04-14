

from vtools.data.timeseries import *

from numpy import array, nan, isnan
from itertools import groupby



def group_by_nan(data,compress_size):
    
    group_start_end=[]
    group_count=-1
    group_start=0
    group_end  =0
    new_group= True
    pre_group_end =-1
    pre_group_count=-1
    #pdb.set_trace()
    for a,b in groupby(data,isnan):
        a_group_size = sum(1 for x in b)
        if(a) and (a_group_size>=compress_size):
            if (group_count>=0):
                pre_group_end = group_start_end[group_count][1]
            #group_count = group_count+1
            group_start = pre_group_end + a_group_size+1
            new_group = True
        else:
            i = group_count
            if (new_group==False):
                group_end =  group_start_end[group_count][1]
                group_start_end[group_count][1] = group_end+a_group_size
            else:
                group_end = group_start+a_group_size-1
                group_start_end.append([group_start,group_end])
                pre_group_end = group_end
                pre_group_count = group_count
                group_count =group_count+1
                new_group=False
    return group_start_end
    

    
def ts_group(ts,gap_size=1000):
    """
    Split a time sereies with gaps to a group time series with
    gap large then nan_size remvoed.

    input:
      ts:        instance of timeseries, regular or irregular.
      gap_size:  integer specify the size of gap to be splitted
      
    output:
       A number of time series
    """
    group_indexs = group_by_nan(ts.data,gap_size)
    ts_group=[]
    if ts.is_regular():
        for (start,end) in group_indexs:
            data  = ts.data[start:end+1]
            start = ts.times[start]
            a_ts = rts(data,start,ts.interval,ts.props)
            ts_group.append(a_ts)
    else:
        for (start,end) in group_indexs:
            data  = ts.data[start:end+1]
            times = ts.times[start:end+1]
            a_ts = its(times,data,ts.props)
            ts_group.append(a_ts)
    return ts_group
    
    
    
