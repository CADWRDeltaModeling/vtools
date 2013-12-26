# -*- coding: utf-8 -*-

from vtools.functions.resample import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts=synthetic_tide_series()
ts_decimate=decimate(ts,hours(1))
ts_ftt_resample=resample_ftt(ts,hours(1))
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts.times,ts.data,color='g',linewidth=1.2)
p1=ax0.plot(ts_decimate.times,ts_decimate.data,color='r',\
marker=".",linestyle="none",markersize=3)
p2=ax0.plot(ts_ftt_resample.times,ts_ftt_resample.data,\
color='b',marker="*",linestyle="none",markersize=3)
plt.legend(["Surface","Decimated","Ftt"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

