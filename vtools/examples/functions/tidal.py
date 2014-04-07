# -*- coding: utf-8 -*-


from vtools.functions.filter import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt
import datetime

ts=example_data("pt_reyes_tidal_1hour")
## only plot part of result 
window_start=datetime.datetime(2013,11,25)
window_end=datetime.datetime(2013,12,2)
ts_cosine=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=30,padtype="constant")
#ts_cosine=temp.window(window_start,window_end)
ts_butt=butterworth(ts,cutoff_period=hours(60),order=4)
#ts_butt=temp.window(window_start,window_end)
boxcar_aver_interval = hours(12)
ts_box=boxcar(ts,boxcar_aver_interval,boxcar_aver_interval)
#ts_box=temp.window(window_start,window_end)
ts_god=godin(ts)
#ts_god=temp.window(window_start,window_end)
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
#ts=ts.window(window_start,window_end)
lwidth=0.8
p0=ax0.plot(ts.times,ts.data,color='green',\
           linewidth=1.2,label="Pt Reyes Water Level")
p1=ax0.plot(ts_butt.times,ts_butt.data,color='red',\
           linewidth=lwidth,label="Butterworth")
p2=ax0.plot(ts_box.times,ts_box.data,color='blue',\
           linewidth=lwidth,label="Boxcar")
p3=ax0.plot(ts_god.times,ts_god.data,color='black',\
           linewidth=lwidth,label="Godin")
p4=ax0.plot(ts_cosine.times,ts_cosine.data,color='brown',\
           linewidth=lwidth,label="Cosine-Lanczos")
plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=lwidth)
plt.legend(loc="lower left",ncol=2)
fig.autofmt_xdate()
plt.show()