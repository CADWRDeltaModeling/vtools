""" Draws several line plots """
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from enthought.chaco2.api import OverlayPlotContainer

# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()

# Simple time series plot. 
p0 = ts_plot(ts0,"ts0",plot_area=None,color="red",line_style="long dash")
# Now we are reusing the plot area and plotting another time series on
# top of the first.
p0 = ts_plot(ts1,"ts1",plot_area=p0,color="blue")

# Now lets isolate 1994
p0.index_range.set_bounds(ticks(datetime(1994,1,1)),
                          ticks(datetime(1995,1,1)))
p0.value_range.set_bounds(-0.2,0.2)

# Now save the plot to a file
save_image_file(p0,"ts_line.gif")

# Now get a frame to display it live
fig=default_frame(p0,size=(600,400))
display_frame(fig)




# EOF
