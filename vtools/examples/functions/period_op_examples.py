# -*- coding: utf-8 -*-

from vtools.functions.period_op import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts=synthetic_tide_series()
ts_max=period_max(ts,"1hour")
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts.times,ts.data,color='g',linewidth=1.0)
p1=ax0.step(ts_max.times,ts_max.data,color='r',linewidth=1.0,where="post")
plt.legend(["Surface","Max"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

