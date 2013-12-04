"""Examples of performing interplation over time
   series.
"""

## load necessary libs.
from vtools.functions.interpolate import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt


ts_with_nan=example_data("pt_reyes_tidal_with_gaps")
## fill the invalid (nan) data points within a time
## series by linear interpolation.
ts_new=interpolate_ts_nan(ts_with_nan,method=LINEAR,max_gap=4)

fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts_with_nan.times,ts_with_nan.data,color='g',linewidth=1.,)
p1=ax0.plot(ts_new.times,ts_new.data,color='r',linestyle="none",marker=".")
plt.legend(["original","gap_filled"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()


