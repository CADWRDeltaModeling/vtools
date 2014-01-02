from vtools.functions.filter import *
from vtools.data.sample_series import *
import matplotlib.pyplot as plt

ts_1day=example_data("pt_reyes_tidal_6min")
ts_butt=butterworth(ts_1day,cutoff_period="1hour")
boxcar_aver_interval = parse_interval("1hour")
ts_box=boxcar(ts_1day,boxcar_aver_interval,boxcar_aver_interval)
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
p0=ax0.plot(ts_1day.times,ts_1day.data,color='g',linewidth=1.2)
p1=ax0.plot(ts_butt.times,ts_butt.data,color='r',linewidth=1.)
p2=ax0.plot(ts_box.times,ts_box.data,color='b',linewidth=0.5)
plt.legend(["Surface","Butterworth","Boxcar"])
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

