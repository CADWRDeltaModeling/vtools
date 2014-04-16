# -*- coding: utf-8 -*-

from vtools.functions.period_op import *
from vtools.data.vtime import days
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts_week=synthetic_tide_series()
## get 2 days of data
ts=ts_week.window(ts_week.times[0],ts_week.times[0]+days(2))
ts_max=period_max(ts,hours(1))
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts.times,ts.data,color='g',linewidth=1.0)
p1=ax0.step(ts_max.times,ts_max.data,color='r',linewidth=1.0,where="post")
p2=ax0.plot(ts_max.centered().times,ts_max.centered().data,color='black',\
linewidth=1.0,linestyle="--")
plt.legend(["Surface","Max_step","Max_centered"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

