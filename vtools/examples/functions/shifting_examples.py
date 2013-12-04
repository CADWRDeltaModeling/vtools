# -*- coding: utf-8 -*-

from vtools.functions.shift import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts=synthetic_tide_series()
ts_shifted=shift(ts,"1day")
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts.times,ts.data,color='g',linewidth=1.0)
p1=ax0.plot(ts_shifted.times,ts_shifted.data,color='r',linewidth=1.0)
plt.legend(["Surface","Shifted"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

