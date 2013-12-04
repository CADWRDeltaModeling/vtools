# -*- coding: utf-8 -*-

from vtools.functions.resample import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts=synthetic_tide_series()
ts_resample=decimate(ts,"1hour")
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts.times,ts.data,color='g',linewidth=1.2)
p1=ax0.plot(ts_resample.times,ts_resample.data,color='r',marker=".",linestyle="none",markersize=3)
plt.legend(["Surface","Decimated"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

