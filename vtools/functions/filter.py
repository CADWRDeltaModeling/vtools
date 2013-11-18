""" Module contains filter used in tidal time series analysis. 
"""

## Python libary import.

## Scipy import.
from scipy import array as sciarray
from scipy import nan, isnan,add,convolve, \
transpose
from scipy.signal import lfilter
from scipy.signal.filter_design import butter
from numpy import sqrt
## Vtool vtime import.

from vtools.data.vtime import *
from vtools.data.timeseries import rts
from vtools.data.constants import *

__all__=["boxcar","butterworth","daily_average","godin"]



## This dic saves the missing points for different intervals. 
first_point={time_interval(minutes=15):48,time_interval(hours=1):36}

## This dic store tide butterworth filter' cut-off frequencies for 
## tide time series analysis, here set cutoff frequency at 0.8 cycle/day
## ,but it is represented as a ratio to Nyquist frequency for two
## sample intervals.
butterworth_cutoff_frequencies={time_interval(minutes=15):0.8/(48),\
                               time_interval(hours=1):0.8/12}

## supported interval
_butterworth_interval=[time_interval(minutes=15),time_interval(hours=1)]

########################################################################### 
## Public interface.
###########################################################################

def butterworth(ts,order=4,cutoff_frequency=None,cutoff_period=None):
    
    """ low-pass butterworth filter on a regular time series.
        default order is 4, if no cutoff_frequency
        is given, default will be used.

        input:
            ts: regular time series to be filtered.
            order: order of the filter,int.
            cutoff_frequency: cut_off frequency represented
            by ratio of Nyquist frequency, should within (0,1).
            cutoff_period   : period of cutoff frequency represented by hours,
                              cutoff_frequency and cutoff_period can't be
                              specified at the same time.
        output:
           a new regular time series with the same 
           interval of ts.
    """
    if (order%2):
        raise ValueError("only even order is accepted")
        
    if not ts.is_regular():
        raise ValueError("Only regular time series can be filtered.")
    
    interval=ts.interval
    
    if (not (interval in _butterworth_interval)) and (cutoff_period == None) and (cutoff_frequency==None):
        raise ValueError("time interval is not supported by butterworth if no cuttoff period/frequency given.")

    if (cutoff_frequency!=None) and (cutoff_period!=None):
        raise ValueError("cutoff_frequency and cutoff_period can't be specified simultaneously")
    
    cf=cutoff_frequency
    if (cf==None):
        if (cutoff_period !=None):
            ## convert it to days
            cutoff_frequency_in_ticks = 1.0/float(ticks(parse_interval(cutoff_period)))
            nyquist_frequency  = 0.5/float(ticks(interval))
            cf = cutoff_frequency_in_ticks/nyquist_frequency
        else:
            cf=butterworth_cutoff_frequencies[interval]
        
    ## get butter filter coefficients.
    [b,a]=butter(order/2,cf)
    d1=lfilter(b, a, ts.data,0)
    d1=d1[len(d1)::-1]
    d2=lfilter(b,a,d1,0)
    d2=d2[len(d2)::-1]
    #d2=sqrt(d2)
    
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    
    return rts(d2,ts.start,ts.interval,prop)
    
   


def boxcar(ts,before,after):
    """ moving averaging over ts with before- 
        and after- interval/number
        about sampling points.
       
       input:
          ts: timeseries to be processed.
          
          before:length of averging interval 
                 before the sampling 
                 points.
                 
          after: length of averging interval 
                after the sampling 
                points.
                
       output:
           a new smoothed regular time series.
    """
    
    t=time_interval(minutes=15)
    len_before=0
    len_after=0
    
    if not ts.is_regular():
        raise ValueError("Only regular time series are accpted by"
                         "boxcar function")
    
    if type(before)==type(1) and type(after)==type(1):
        len_before=before
        len_after=after
    elif type(before)==type(t) and type(after)==type(t):
        len_before= steps_per_interval(ts,before)
        len_after= steps_per_interval(ts,after)
    elif type(before)==type(" ") and type(after)==type(" "):
        before=parse_interval(before)
        after=parse_interval(after)
        if is_calendar_dependent(before) or\
           is_calendar_dependent(after):
            raise ValueError("before and after arguments of  boxcar"+\
                             "must be calendar independent.")
        len_before= steps_per_interval(ts,before)
        len_after= steps_per_interval(ts,after)
    else:
        raise ValueError("before and after arguments of  boxcar"+\
                         "should be integer or calendar independent"+\
                         "time intervals or interval strings")
        
    new_data=_boxcar(ts.data,len_before,len_after)
    
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    return rts(new_data,ts.start,ts.interval,prop)

def daily_average(ts):
    """
       Classic moving average over 24 hours.
    """
    before=parse_interval("1day")
    after=parse_interval("0min")   
    return boxcar(ts,before,after)
    
    
## This dic saves the points involves in half summations 
## for different intervals
godin_interval={time_interval(minutes=15):(48,49),\
                time_interval(hours=1):(12,12)} 


def godin(ts):
    
    """ Godin filtering method on a regular time series.
        input:
            ts: regular time series to be filtered
        output:
            new regular time series with the same interval of ts.
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series can be filtered.")
    
    interval=ts.interval
    
    if not interval in godin_interval.keys():
        raise ValueError("Not supported time interval by godin filter")
    
    num_1=godin_interval[interval][0]
    num_2=godin_interval[interval][1]   
    ## use boxcar averging fuction 3 times to 
    ## achieve final values.
    
    d1=_boxcar(ts.data,num_1-1,num_1)
    d1=_boxcar(d1,num_1,num_1-1)
    d1=_boxcar(d1,num_2,num_2)
    
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
        
    return rts(d1,ts.start,ts.interval,prop)

        
########################################################################### 
## Private interface.
###########################################################################

def _boxcar(data,nbefore,nafter):
    """ Inside boxcar averaging function doing real
        works.
        
        input: 
            data: data samples at regular intervals, must be 
                  array.
            nbefore: number of samples before the point
                     to be averaged (not including this 
                     point).
            nafter: number of samples after the point
                     to be averaged (not including this 
                     point).
         output:
            a new averaged data samples.
            
    """
    ntotal=nbefore+nafter+1
    b=[1.0/ntotal]*ntotal
    a=1.0
    size_data=data.size
    
    ## Using linear filter doing averaging 
    ## of ntotal samples.
    ##dd=lfilter(b,a,data)
    ##dd=[add.reduce(data[i-nbefore:i+nafter+1]) for i in range(nbefore,len_data-nafter)]
    if data.ndim==1:
        dim2_size=1
        dd=convolve(data,b,mode=0) 
    elif data.ndim==2: ## for multi-dimension data,convolve can't handle it directly
        dim2_size=data.shape[1]
        dd=[convolve(data[:,i],b,mode=0) for i in range(dim2_size)]
        dd=sciarray(dd)
        dd=transpose(dd)            
    else:
        raise "_boxcar function can't process data with dimension more than 2"
    
    ## convole first dimension length.
    dd_len=dd.shape[0]     
    ## Based on the nbefore and nafter, do a
    ## sample result shifting.
    dt=sciarray([nan]*size_data)
    dt=dt.reshape(data.shape)

    #dt[nbefore:len_data-nafter]=dd[nbefore+nafter:len_data]
    dt[nbefore:dd_len+nbefore,]=dd[0:dd_len,]
    return dt


def steps_per_interval(ts,averaging_interval):
    """
       number of ts interval over a averaging interval.
    """
    
    return int(ticks(averaging_interval)/ticks(ts.interval))


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
