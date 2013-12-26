# -*- coding: utf-8 -*-


from vtools.functions.filter import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt



ts_1week=example_data("pt_reyes_tidal_1hour")
ts_butt=butterworth(ts_1week,cutoff_period=hours(36))
boxcar_aver_interval = hours(25)
ts_box=boxcar(ts_1week,boxcar_aver_interval,hours(25))
ts_god=godin(ts_1week)
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts_1week.times,ts_1week.data,color='green',linewidth=1.2)
p1=ax0.plot(ts_butt.times,ts_butt.data,color='red',linewidth=0.5)
p2=ax0.plot(ts_box.times,ts_box.data,color='blue',linewidth=0.5)
p2=ax0.plot(ts_god.times,ts_god.data,color='black',linewidth=0.5)
plt.legend(["Surface","Butterworth","Boxcar","Godin"])
plt.grid(b=True, which='both', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()