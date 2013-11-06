""" Draws several line plots """
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from enthought.chaco2.api import VPlotContainer


# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()
palette=get_palette("default")

# Simple time series plot. Note you don't really have to put
# plot_area=None. This is the default, and it means that the output
# will be a new plot area.
p0 = ts_plot(ts0,"ts0",plot_area=None,color=palette[0])


# Now we are reusing the plot area and plotting another time series on
# top of the first.
p0 = ts_plot(ts1,"ts1",plot_area=p0,color=palette[1])
p1 = ts_plot(ts2,"ts2",color=palette[0])
p1.index_range = p0.index_range
p0.padding_bottom=30
p1.padding_top=0


vpc = VPlotContainer(stack_order="top_to_bottom")
vpc.add(p0)
vpc.add(p1)
# Now get a frame to display it live
fig=default_frame(vpc,size=(600,400))
display_frame(fig)
# Things you can do:
# z: enter/exit zoom mode
# esc: reset to original scale
# cntrl-c: copy to clipboard
# cntrl-s: save to image file



# EOF
