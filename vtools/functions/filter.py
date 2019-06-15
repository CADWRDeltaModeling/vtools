""" Module contains filter used in tidal time series analysis. 
"""

## Python libary import.
from numpy import abs
## Scipy import.
from scipy import array as sciarray
from scipy import nan, isnan,add,convolve,transpose
from scipy import pi, sin
from scipy import where,arange,clip
from scipy.signal import lfilter,firwin,filtfilt
from scipy.signal import fftconvolve
from scipy.signal.filter_design import butter
from scipy.ndimage.filters import gaussian_filter 
from numpy import sqrt
## Vtool vtime import.

from vtools.data.vtime import *
from vtools.data.timeseries import rts
from vtools.data.constants import *

__all__=["boxcar","butterworth","daily_average","godin","cosine_lanczos",\
         "lowpass_cosine_lanczos_filter_coef","ts_gaussian_filter"]



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

def butterworth(ts,order=4,cutoff_period=None,cutoff_frequency=None):
    """ low-pass butterworth-squared filter on a regular time series.
      
        
    Parameters
    -----------
    
    
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    order: int ,optional
        The default is 4.
        
    cutoff_frequency: float,optional
        Cutoff frequency expressed as a ratio of a Nyquist frequency,
        should within the range (0,1). For example, if the sampling frequency
        is 1 hour, the Nyquist frequency is 1 sample/2 hours. If we want a
        36 hour cutoff period, the frequency is 1/36 or 0.0278 cycles per hour. 
        Hence the cutoff frequency argument used here would be
        0.0278/0.5 = 0.056.
                      
    cutoff_period : string  or  :ref:`time_interval<time_intervals>`
         Period of cutting off frequency. If input as a string, it must 
         be  convertible to :ref:`Time interval<time_intervals>`.
         cutoff_frequency and cutoff_period can't be specified at the same time.
           
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts.
        
    Raise
    --------
    ValueError
        If input order is not even, or input timeseries is not regular, 
        or neither cutoff_period and cutoff_frequency is given while input
        time series interval is not 15min or 1 hour, or  cutoff_period and cutoff_frequency 
        are given at the same time.
        
    """
    
    if (order%2):
        raise ValueError("only even order is accepted")
        
    if not ts.is_regular():
        raise ValueError("Only regular time series can be filtered.")
    
    interval=ts.interval
    
    if (not (interval in _butterworth_interval)) and (cutoff_period is None) and (cutoff_frequency is None):
        raise ValueError("time interval is not supported by butterworth if no cuttoff period/frequency given.")

    if (not (cutoff_frequency is None)) and (not(cutoff_period is None)):
        raise ValueError("cutoff_frequency and cutoff_period can't be specified simultaneously")
    
    cf=cutoff_frequency
    if (cf is None):
        if  (not(cutoff_period is None)):
            ## convert it to ticks
            if not (is_interval(cutoff_period)):
                cutoff_period=parse_interval(cutoff_period)
            cutoff_frequency_in_ticks = 1.0/float(ticks(cutoff_period))
            nyquist_frequency  = 0.5/float(ticks(interval))
            cf = cutoff_frequency_in_ticks/nyquist_frequency
        else:
            cf=butterworth_cutoff_frequencies[interval]
        
    ## get butter filter coefficients.
    [b,a]=butter(order/2,cf)
#    d1=lfilter(b, a, ts.data,0)
#    d1=d1[len(d1)::-1]
#    d2=lfilter(b,a,d1,0)
#    d2=d2[len(d2)::-1]
    d2=filtfilt(b,a,ts.data,axis=0)
    
    prop={}
    for key,val in list(ts.props.items()):
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    time_interval
    return rts(d2,ts.start,ts.interval,prop)
    

def cosine_lanczos(ts,cutoff_period=None,cutoff_frequency=None,filter_len=None,
                   padtype=None,padlen=None,fill_edge_nan=True):
    """ squared low-pass cosine lanczos  filter on a regular time series.
      
        
    Parameters
    -----------
    
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    filter_len  : int, time_interval
        Size of lanczos window, default is to number of interval within filter_period*1.25.
        
    cutoff_frequency: float,optional
        Cutoff frequency expressed as a ratio of a Nyquist frequency,
        should within the range (0,1). For example, if the sampling frequency
        is 1 hour, the Nyquist frequency is 1 sample/2 hours. If we want a
        36 hour cutoff period, the frequency is 1/36 or 0.0278 cycles per hour. 
        Hence the cutoff frequency argument used here would be
        0.0278/0.5 = 0.056.
                      
    cutoff_period : string  or  :ref:`time_interval<time_intervals>`
         Period of cutting off frequency. If input as a string, it must 
         be  convertible to :ref:`Time interval<time_intervals>`.
         cutoff_frequency and cutoff_period can't be specified at the same time.
         
     padtype : str or None, optional
         Must be 'odd', 'even', 'constant', or None. This determines the type
         of extension to use for the padded signal to which the filter is applied. 
         If padtype is None, no padding is used. The default is None.

     padlen : int or None, optional
          The number of elements by which to extend x at both ends of axis 
          before applying the filter. This value must be less than x.shape[axis]-1. 
          padlen=0 implies no padding. If padtye is not None and padlen is not
          given, padlen is be set to 6*m.
    
     fill_edge_nan: bool,optional
          If pading is not used and fill_edge_nan is true, resulting data on 
          the both ends are filled with nan to account for edge effect. This is
          2*m on the either end of the result. Default is true.
  
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts. If no pading 
        is used the beigning and ending 4*m resulting data will be set to nan
        to remove edge effect.
        
    Raise
    --------
    ValueError
        If input timeseries is not regular, 
        or, cutoff_period and cutoff_frequency are given at the same time,
        or, neither cutoff_period nor curoff_frequence is given,
        or, padtype is not "odd","even","constant",or None,
        or, padlen is larger than data size
        
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series are supported.")
        
    
    interval=ts.interval
    m=filter_len
    if (not (cutoff_frequency is None)) and (not (cutoff_period is None)):
        raise ValueError("cutoff_frequency and cutoff_period can't\
        be specified simultaneously")
        
    if ( (cutoff_frequency is None)) and ((cutoff_period is None)):
         print("neither cutoff_frequency nor cutoff_period is given, 40 hours is used by defualt")
         cutoff_period = hours(40)
        
    cf=cutoff_frequency
    if (cf is None):
        if (not (cutoff_period is None)):
            ## convert it to ticks
            if not (is_interval(cutoff_period)):
                cutoff_period=parse_interval(cutoff_period)
            cutoff_frequency_in_ticks = 1.0/float(ticks(cutoff_period))
            nyquist_frequency  = 0.5/float(ticks(interval))
            cf = cutoff_frequency_in_ticks/nyquist_frequency
        else:
            raise ValueError("you must give me either cutoff_frequency or cutoff_period")
    
    if is_interval(m):
        m=int(ticks(m)/ticks(ts.interval))
    ## if m is none set it to number of interval within filter_period*1.25
    elif  (m is None):
        ## cf reverse is half of the interval within filtering period
        m=int(1.25*2.0/cf)
    elif type(1)==type(m):
        ## nothing to do
        m=m
    else:
        raise TypeError("unkown filter length type")

   
        
        
    ##find out nan location and fill with 0.0. This way we can use the
    ## signal processing filtrations out-of-the box without nans causing trouble
    idx=where(isnan(ts.data))[0]
    data=sciarray(ts.data).copy()
    
    ## figure out indexes that will be nan after the filtration,which
    ## will "grow" the nan region around the original nan by 2*m
    ## slots in each direction
    if  len(idx)>0:
        data[idx]=0.0
        shifts=arange(-2*m,2*m+1)
        result_nan_idx=clip(add.outer(shifts,idx),0,len(ts)-1).ravel()
    
    if m<1:
        raise ValueError("bad input cutoff period or frequency")
        
    if not(padtype is None):
        if (not padtype in ["odd","even","constant"]):
            raise ValueError("unkown padtype :"+padtype)
    
    if (padlen is None) and (not(padtype is None)):
        padlen=6*m
        
    if padlen>len(data):
        raise ValueError("Padding length is more  than data size")
        
    ## get filter coefficients. sizeo of coefis is 2*m+1 in fact
    coefs=_lowpass_cosine_lanczos_filter_coef(cf,m)
    
    
    d2=filtfilt(coefs,[1.0],data,axis=0,padtype=padtype,padlen=padlen)

    if(len(idx)>0):
        d2[result_nan_idx]=nan
    
    ## replace edge points with nan if pading is not used
    if (padtype is None) and (fill_edge_nan==True):
        d2[0:2*m]=nan
        d2[len(d2)-2*m:len(d2)]=nan
        
    prop={}
    for key,val in list(ts.props.items()):
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    time_interval
    return rts(d2,ts.start,ts.interval,prop)
    

def ts_gaussian_filter(ts,sigma,order=0,mode="reflect",cval=0.0):
    """ wrapper of scipy gaussian_filter.
    
    Parameters
    -----------
    ts: :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    sigma: int or :ref:`time_interval<time_intervals>`
          Standard deviation for Gaussian kernel presented as number of
          samples, or time interval.
          
    order: int,optional
          Order of the gaussian filter. Must be one of 0,1,2,3. Default 0.
          
    mode : {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}, optional
         This input determines how the array borders are handled, 
         where cval is the value when mode is 'constant'. 
         Default is 'reflect'

    cval : scalar, optional
        Value to fill past edges of input if mode is 'constant'.
        Default is 0.0

       
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts.
        
    Raise
    --------
    ValueError
        If input timeseries is not regular, 
        or input order is not 0,1,2,3.
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series are supported by\
                         guassian filter")

    sigma_int=1
    if is_interval(sigma):
        ticks_sigma=ticks(sigma)
        ticks_interval=ticks(ts.inteval)
        sigma_int=int(ticks_sigma/ticks_interval)
    elif type(sigma)==type(1):
        sigma_int=sigma
    else:
        raise ValueError("sigma must be int or timeinterval")
        
    filtered_data=gaussian_filter(ts.data,sigma_int,order=order,\
                  mode=mode,cval=cval)
    filtered_ts=rts(filtered_data,ts.start,ts.interval)
    return filtered_ts    

def boxcar(ts,before,after):
    """ low-pass butterworth filter using moving average.
        
    Parameters
    -----------
    ts1 : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    before : :ref:`time_interval<time_intervals>`, int
          Length of averging interval before the sampling points or number of points.
          

    after : :ref:`time_interval<time_intervals>`, int
          Length of averging interval after the sampling points or number of points..
       
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts.
        
    Raise
    --------
    ValueError
        If input timeseries is not regular, 
        or before and after are not integer, time_interval or string,
        or before and after is time interval calendar dependent.
        
    """
    
    t=time_interval(minutes=15)
    len_before=0
    len_after=0
    
    if not ts.is_regular():
        raise ValueError("Only regular time series are accpted by\
                         boxcar function")
    
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
    for key,val in list(ts.props.items()):
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    return rts(new_data,ts.start,ts.interval,prop)

def daily_average(ts):
    """Classic moving average over 24 hours.
    
    Parameters
    -----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
     
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts.
        
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
    
    Parameters
    -----------
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
     
    Returns
    -------
    result : :class:`~vtools.data.timeseries.TimeSeries`
        A new regular time series with the same interval of ts.
        
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series is supported.")
    
    interval=ts.interval
    
    if not interval in list(godin_interval.keys()):
        raise ValueError("Not supported time interval by godin filter")
    
    num_1=godin_interval[interval][0]
    num_2=godin_interval[interval][1]   
    ## use boxcar averging fuction 3 times to 
    ## achieve final values.
    
    d1=_boxcar(ts.data,num_1-1,num_1)
    d1=_boxcar(d1,num_1,num_1-1)
    d1=_boxcar(d1,num_2,num_2)
    
    prop={}
    for key,val in list(ts.props.items()):
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
        
    return rts(d1,ts.start,ts.interval,prop)

        
########################################################################### 
## Private interface.
###########################################################################

def _boxcar(data,nbefore,nafter):
    """ Inside boxcar averaging function doing real works.
        
    Parameters
    -----------
    
    data: array
        data samples at regular intervals.
                  
    nbefore: int
        number of samples before the point to be averaged
        (not including this point).
        
    nafter: int
        number of samples after the point to be averaged 
        (not including this point).
        
    Returns
    --------
    
    Results: array
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
        dd=convolve(data,b,mode="valid") 
    elif data.ndim==2: ## for multi-dimension data,convolve can't handle it directly
        dim2_size=data.shape[1]
        dd=[convolve(data[:,i],b,mode="valid") for i in range(dim2_size)]
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
    """ number of ts interval over a averaging interval.
       
    """
    
    return int(ticks(averaging_interval)/ticks(ts.interval))



def lowpass_cosine_lanczos_filter_coef(cf,m,normalize=True):
    """For test purpose only
    """
    return  _lowpass_cosine_lanczos_filter_coef(cf,m,normalize)
    

def _lowpass_cosine_lanczos_filter_coef(cf,m,normalize=True):
    """return the convolution coefficients for low pass lanczos filter.
      
    Parameters
    -----------
    
    Cf: float
      Cutoff frequency expressed as a ratio of a Nyquist frequency.
                  
    M: int
      Size of filtering window size.
        
    Returns
    --------
    pdb.set_trace()
    Results: list
           Coefficients of filtering window.
    
    """
    
    coscoef=[cf*sin(pi*k*cf)/(pi*k*cf) for k in range(1,m+1,1)]
    sigma=[sin(pi*k/m)/(pi*k/m) for k in range(1,m+1,1)]
    prod= [c*s for c,s in zip(coscoef,sigma)]
    temp = prod[-1::-1]+[cf]+prod
    res=sciarray(temp)
    if normalize:
        res = res/res.sum()
    return res
    
    

    
    
    
    
    
    
    
