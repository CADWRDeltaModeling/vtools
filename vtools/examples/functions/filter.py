from vtools.functions.filter import *
from vtools.data.sample_series import *

import matplotlib.pyplot as plt

## 1 day of tide at point reyes 
ts_1day=example_data("pt_reyes_tidal_6min")
ts_butt=butterworth(ts_1day,cutoff_period="1hour")
boxcar_aver_interval = parse_interval("1hour")
ts_box=boxcar(ts_1day,boxcar_aver_interval,boxcar_aver_interval)
ts_cos=cosine_lanczos(ts_1day,cutoff_period=hours(1),filter_len=10)
fig=plt.figure()
ax0 = fig.add_subplot(111)
ax0.set_ylabel("surface (feet)")
lwidth=0.8
p0=ax0.plot(ts_1day.times,ts_1day.data,color='green',\
            linewidth=lwidth,label="Surface")
p1=ax0.plot(ts_butt.times,ts_butt.data,color='red',\
            linewidth=lwidth,label="Butterworth")
p2=ax0.plot(ts_box.times,ts_box.data,color='black',\
            linewidth=lwidth,label="Boxcar")
p3=ax0.plot(ts_cos.times,ts_cos.data,color='brown',\
            linewidth=lwidth,label="Cosine")
plt.legend(loc="lower center",prop={'size':12})
plt.grid(b=True, which='major', color='0.9', linestyle='-', linewidth=0.5)
fig.autofmt_xdate()
plt.show()

