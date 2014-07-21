# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 13:17:21 2014

@author: qshu
"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from vtools.functions.filter import *
from scipy.signal import freqz

from pylab import *

def compare_response(cutoff_period,interval):
    """ plot frequence response of squared cosine_lanczos,godin filter
        boxcar
        cutoff_period and interval are input as hours
    """
    data_interval=interval
    cf=2.0*data_interval/cutoff_period
    
    ## C_L of size 70hours
    m0=int(70.0/interval)
    a=1
    b0 = lowpass_cosine_lanczos_filter_coef(cf,m0,normalize=True)
    worN=4096
    w0,h0 = freqz(b0,a,worN=worN)
    h0=h0*h0
    ## C_L of default size,which is 1.25 times number of 
    ## interval within cutoff period
    m2= int(1.25*2.0/cf)
    b2 = lowpass_cosine_lanczos_filter_coef(cf,m2,normalize=True)
    w2,h2 = freqz(b2,a,worN=worN)
    h2=h2*h2
    
    
    ## godin response is computed by multiplying responses of 
    ## three boxcar filter on hourly data (23,23,24)
    ## correct for nonhourly data
    l1=int(23.0/interval)
    l2=int(23.0/interval)
    l3=int(24.0/interval)
    b3_1 = [1.0/l1]*l1
    b3_2 = [1.0/l2]*l2
    b3_3 = [1.0/l3]*l3
    w3_1,h3_1 = freqz(b3_1,a,worN=worN)
    w3_2,h3_2 = freqz(b3_2,a,worN=worN)
    w3_3,h3_3 = freqz(b3_3,a,worN=worN)
    h3=h3_1*h3_2*h3_3
      
    ## compute boxcar coefficients for 24 and 25 hours
    num_intervl=int(24/interval)
    b4=[1.0/num_intervl]*num_intervl
    w4,h4=freqz(b4,a,worN=worN)
    h4=h4*h4
    
    num_intervl=int(25/interval)
    b5=[1.0/num_intervl]*num_intervl
    w5,h5=freqz(b5,a,worN=worN)
    h5=h5*h5
    
    
    pw=w0[1:]
   ## convert frequence to period in hours
    period=1.0/pw
    period=2.0*pi*period*interval
    
    fig = plt.figure(figsize=(6,6),dpi=300)
    
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim(-.2,1.5)
    ax.set_xlim(0.1,400)
    
    legend_font = FontProperties()
    legend_font.set_family("sans-serif")
    legend_font.set_size(11)
    axis_font = FontProperties()
    axis_font.set_family("sans-serif")
    axis_font.set_size(11)
    ticks_font = FontProperties()
    ticks_font.set_family("sans-serif")
    ticks_font.set_size(11)
    
    ax.plot(period,abs(h0[1:]),color="black",linewidth=1,label="C_L,size=70 hours") 
    ax.plot(period,abs(h2[1:]),color="r",linewidth=1,label="C_L,size=%s default"%m2)
  
    ax.plot(period,abs(h3[1:]),color="blue",linewidth=1,label="godin")
    ax.plot(period,abs(h4[1:]),color="green",linewidth=1,label="boxcar 24hours")
    ax.plot(period,abs(h5[1:]),color="orange",linewidth=1,label="boxcar 25hours")
    ax.axvline(x=cutoff_period,ymin=-0.2,linewidth=1,color='r')
    ax.annotate("cutoff period=%f h"%cutoff_period,(cutoff_period,1.2),xycoords='data',\
                xytext=(50, 50), textcoords='offset points',\
               arrowprops=dict(arrowstyle="->"))
    ax.set_ylabel(r'Magnitude',fontproperties=axis_font)
    ax.set_xlabel(r'Period(hours)',fontproperties=axis_font)
    
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)

    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
      
  
    plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=0.5)
    plt.tight_layout()
  
    legend(loc="lower right", prop=legend_font)

if __name__=="__main__":


    ## compare response for data with 15min interval 
    compare_response(40,0.25)
    plt.savefig('frequency_response',bbox_inches=0)
    
