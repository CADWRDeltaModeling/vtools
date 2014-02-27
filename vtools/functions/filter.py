""" Module contains filter used in tidal time series analysis. 
"""

## Python libary import.
from numpy import abs
## Scipy import.
from scipy import array as sciarray
from scipy import nan, isnan,add,convolve, \
transpose
from scipy import pi, sin
from scipy import where,arange,clip
from scipy.signal import lfilter,firwin,filtfilt
from scipy.signal import fftconvolve,freqz
from scipy.signal.filter_design import butter
from numpy import sqrt
## Vtool vtime import.

from vtools.data.vtime import *
from vtools.data.timeseries import rts
from vtools.data.constants import *

__all__=["boxcar","butterworth","daily_average","godin","cosine_lanczos","lowpass_cosine_lanczos_filter_coef"]



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
    
    if (not (interval in _butterworth_interval)) and (cutoff_period == None) and (cutoff_frequency==None):
        raise ValueError("time interval is not supported by butterworth if no cuttoff period/frequency given.")

    if (cutoff_frequency!=None) and (cutoff_period!=None):
        raise ValueError("cutoff_frequency and cutoff_period can't be specified simultaneously")
    
    cf=cutoff_frequency
    if (cf==None):
        if (cutoff_period !=None):
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
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    time_interval
    return rts(d2,ts.start,ts.interval,prop)
    

def cosine_lanczos(ts,cutoff_frequency=None,cutoff_period=None,m=20):
    """ low-pass cosine lanczos squared filter on a regular time series.
      
        
    Parameters
    -----------
    
    ts : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    m  : int
        Size of lanczos window, default is 20.
        
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
        If input timeseries is not regular, 
        or, cutoff_period and cutoff_frequency are given at the same time,
        or, neither cutoff_period nor curoff_frequence is given.
        
    """
    
    if not ts.is_regular():
        raise ValueError("Only regular time series are supported.")
        
    
    interval=ts.interval
    

    if (cutoff_frequency!=None) and (cutoff_period!=None):
        raise ValueError("cutoff_frequency and cutoff_period can't be specified simultaneously")
        
        
    ##find out nan location and fill with 0.0. This way we can use the
    ## signal processing filtrations out-of-the box without nans causing trouble
    idx=where(isnan(ts.data))[0]
    data=sciarray(ts.data).copy()
    
    ## figure out indexes that will be nan after the filtration,which
    ## will "grow" the nan region around the original nan by 2*m-1 
    ## slots in each direction
    if  len(idx)>0:
        data[idx]=0.0
        shifts=arange(-2*m+2,2*m-1)
        result_nan_idx=clip(add.outer(shifts,idx),0,len(ts)-1).ravel()
    
    cf=cutoff_frequency
    if (cf==None):
        if (cutoff_period !=None):
            ## convert it to ticks
            if not (is_interval(cutoff_period)):
                cutoff_period=parse_interval(cutoff_period)
            cutoff_frequency_in_ticks = 1.0/float(ticks(cutoff_period))
            nyquist_frequency  = 0.5/float(ticks(interval))
            cf = cutoff_frequency_in_ticks/nyquist_frequency
        else:
            raise ValueError("you must give me either cutoff_frequency or cutoff_period")
        
    ## get filter coefficients.
    coefs=_lowpass_cosine_lanczos_filter_coef(cf,m)
#    d1=lfilter(coefs, 1.0, ts.data,axis=0)
#    d1=d1[len(d1)::-1]
#    d2=lfilter(coefs,1.0,d1,axis=0)
#    d2=d2[len(d2)::-1]
    d2=filtfilt(coefs,[1.0],data,axis=0)

    if(len(idx)>0):
        d2[result_nan_idx]=nan
        
    prop={}
    for key,val in ts.props.items():
        prop[key]=val
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL
    time_interval
    return rts(d2,ts.start,ts.interval,prop)
    
   


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
    
    
from pylab import *

def mfreqz(b,a=1):
    w,h = freqz(b,a)
    ## is the response of squred filter, just squre response h
    h2=h*h
    hdb = 20 * log10 (abs(h))
    subplot(211)
    #plot(w/max(w),h_dB)
    plot(w/max(w),abs(h),label="cosine_lanczos")
    plot(w/max(w),abs(h2),label="squared_cosine_lanczos")
    legend()
    ylim(-.2,1.5)
    #ylim(-150, 5)
    ylabel('Magnitude')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Frequency response')
    subplot(212)
    h_phase = unwrap(arctan2(imag(h),real(h)))
    h_phase2 = unwrap(arctan2(imag(h2),real(h2)))
    plot(w/max(w),h_phase,label="consine_lanczos")
    plot(w/max(w),h_phase2,label="squared_consine_lanczos")
    legend(loc="lower left")
    ylabel('Phase (radians)')
    xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
    title(r'Phase response')
    subplots_adjust(hspace=0.5) 
    
def impz(b,a=1):
    l = len(b)
    impulse = repeat(0.,l); impulse[0] =1.
    x = arange(0,l)
    response = lfilter(b,a,impulse)
    subplot(211)
    stem(x, response)
    ylabel('Amplitude')
    xlabel(r'n (samples)')
    title(r'Impulse response')
    subplot(212)
    step = cumsum(response)
    stem(x, step)
    ylabel('Amplitude')
    xlabel(r'n (samples)')
    title(r'Step response')
    subplots_adjust(hspace=0.5)
    
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
def compare_response():
    """ plot frequence response of cosine_lanczos and godin filter"""
    ## cosin_lanczos cut off period is set at 40h
    ## the normailzed cutoff frequence is 2/40=0.05 for hourly data
    cf=0.05
    m1=40
    a=1
    b1 = _lowpass_cosine_lanczos_filter_coef(cf,m1,normalize=True)
    m2=60
    b2 = _lowpass_cosine_lanczos_filter_coef(cf,m2,normalize=True)
    w1,h1 = freqz(b1,a)
    w2,h2 = freqz(b2,a)
    
    ## godin response is computed by multiplying responses of 
    ## three boxcar filter on hourly data (23,23,24)
    b3_1 = [1.0/23]*23
    b3_2 = [1.0/23]*23
    b3_3 = [1.0/24]*24
    w3_1,h3_1 = freqz(b3_1,a)
    w3_2,h3_2 = freqz(b3_2,a)
    w3_3,h3_3 = freqz(b3_3,a)
    
    fig = plt.figure(figsize=(6,6),dpi=300)
    
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim(-.2,1.5)
    ax.set_xlim(0,0.2)
    
    legend_font = FontProperties()
    legend_font.set_family("sans-serif")
    legend_font.set_size(11)
    axis_font = FontProperties()
    axis_font.set_family("sans-serif")
    axis_font.set_size(11)
    ticks_font = FontProperties()
    ticks_font.set_family("sans-serif")
    ticks_font.set_size(11)
    
    ax.plot(w1/max(w1),abs(h1),color="black",linewidth=1,label="cosine size=40") 
    ax.plot(w1/max(w1),abs(h2),color="r",linewidth=1,label="cosine size=60")
    ax.plot(w3_1/max(w3_1),abs(h3_1*h3_2*h3_3),color="blue",linewidth=1,label="godin")
    
    ax.set_ylabel(r'Magnitude',fontproperties=axis_font)
    ax.set_xlabel(r'Normalized Frequency (x$\pi$rad/sample)',fontproperties=axis_font)
    
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)

    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
    plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=0.5)
    plt.tight_layout()
  
    legend()
   
import pdb
def compare_response2():
    """ plot frequence response of boxcar times godin filter"""
    ## cosin_lanczos cut off period is set at 40h
    
    cf=0.05
    m1=40
    a=1.0
    cb1 = _lowpass_cosine_lanczos_filter_coef(cf,m1,normalize=True)
    cf=0.005
    m2=480
    cb2 = _lowpass_cosine_lanczos_filter_coef(cf,m2,normalize=True)
    cw1,ch1 = freqz(cb1,a)
    cw2,ch2 = freqz(cb2,a)
    
    ## godin response is computed by multiplying responses of 
    ## three boxcar filter on hourly data (23,23,24)
    gb1 = [1.0/23]*23
    gb2 = [1.0/23]*23
    gb3 = [1.0/24]*24
    gw1,gh1 = freqz(gb1,a)
    gw2,gh2 = freqz(gb2,a)
    gw3,gh3 = freqz(gb3,a)
    gw=gw3
    gh=gh1*gh2*gh3 ## godin response
    
    
    ## three boxcar coeffice for hourly data
    p1=int(15*24) ## 15day
    p2=int(15*24+12) ## 15.5day
    p3=int(16*24) ## 16day
    
    b1=[1.0/p1]*p1
    b2=[1.0/p2]*p2
    b3=[1.0/p3]*p3
    
    bw1,bh1=freqz(b1,a)
    bw2,bh2=freqz(b2,a)
    bw3,bh3=freqz(b3,a)
    
        
    
    
    fig = plt.figure(figsize=(6,6),dpi=300)
    
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim(-.1,1.1)
    ax.set_xlim(1,10000)
    ax.set_xscale('log')
    
    legend_font = FontProperties()
    legend_font.set_family("sans-serif")
    legend_font.set_size(11)
    axis_font = FontProperties()
    axis_font.set_family("sans-serif")
    axis_font.set_size(11)
    ticks_font = FontProperties()
    ticks_font.set_family("sans-serif")
    ticks_font.set_size(11)
    pdb.set_trace()
    
    gw[0]=0.00001
    period=1.0/gw
    
#    ax.plot(period,abs(gh*bh1),color="black",linewidth=1,label="godin*box_15day") 
#    ax.plot(period,abs(gh*bh2),color="red",linewidth=1,label="godin*box_15.5day")
#    ax.plot(period,abs(gh*bh3),color="green",linewidth=1,label="godin*box_16day")
#    ax.plot(period,abs(ch2*bh1),color="black",linestyle="-",linewidth=1,label="cl_480*box_15day") 
#    ax.plot(period,abs(ch2*bh2),color="red",linestyle="-",linewidth=1,label="cl_480*box_15.5day")
    ax.plot(period,abs(ch2),color="green",linestyle="-",linewidth=1,label="cl_480_16day")
   
    
    ax.set_ylabel(r'Magnitude',fontproperties=axis_font)
    ax.set_xlabel(r'period(hours)',fontproperties=axis_font)
    
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)

    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
    plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=0.5)
    plt.tight_layout()
  
    legend(loc="upper left")
   
    
    
    
if __name__=="__main__":

    #b=_lowpass_cosine_lanczos_filter_coef(0.4,10)
    #mfreqz(b)
    #show()
#    compare_response()
#    plt.savefig('frequency_response',bbox_inches=0)
   # compare_response2()
   # plt.savefig('frequency_response2',bbox_inches=0)
    #plt.show()
    
    
    
    
    
    
    
    
