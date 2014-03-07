# -*- coding: utf-8 -*-


from vtools.functions.filter import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt
import datetime

ts=example_data("oldriver_flow")
ts_lowpass=cosine_lanczos(ts,cutoff_period=days(28),m=480)
boxcar_aver_interval = days(14)
ts_box=boxcar(ts,boxcar_aver_interval,boxcar_aver_interval)
ts_box_god=godin(ts_box)
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("flow (cfs)")
lwidth=0.8
p0=ax0.plot(ts.times,ts.data,color='green',linewidth=1.2,label="Flow")
p2=ax0.plot(ts_box.times,ts_box.data,color='blue',linewidth=lwidth,label="Boxcar")
p3=ax0.plot(ts_box_god.times,ts_box_god.data,color='black',linewidth=lwidth,label="Boxcar+Godin")
p4=ax0.plot(ts_lowpass.times,ts_lowpass.data,color='red',linewidth=lwidth,label="Cosine-Lanczos")
plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=lwidth)
plt.legend(loc="lower left",ncol=2)
fig.autofmt_xdate()
plt.show()