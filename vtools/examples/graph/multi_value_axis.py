# Example of how to create a time series plot with two value axes,
# one on the right and one on the left

# Enthought library imports

from vtools.data.api import *
from vtools.graph.api import *
from vtools.data.sample_series import *

# Obtain some sample data
ts0,ts1 = create_sample_series()[0:2]

# Create the plots with right and left value axes as completely
# independent plots (ie, do not use the "plot_area" argument)
p0=ts_plot(ts0,"ts0",color="red")
p1=ts_plot(ts1*1000,"ts1",color="blue")

# Call multi_value_axis. The first argument will be on the left axis.
# It (p0) will become the "main" plot. The next plot (p1) will be added as
# an overlay to the left plot and can be reached using the
# right_plot attribute.
p0 = multi_value_axis(p0,p1) # The "p0 =" clarifies that p1 is added to p0,
                             # but you don't need the "p0 =" part for it to work
p0.legend.visible=True       # The legend material of p1 has been added to p0's legend
p0.right_plot.value_range.high=p0.value_range.high*1000
p0.right_plot.value_range.low=p0.value_range.low*1000 # If you can make the second plot scale
                                       # differ from that of the left plot by orders of magnitude,
                                       # it will help make the grid lines line up with both
                                       # axes, not just the left one.

f = default_frame(container=p0)
display_frame(f)

# EOF


