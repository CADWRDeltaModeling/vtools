""" Draws several line plots """
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from enthought.chaco2.api import OverlayPlotContainer

# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()

# Simple time series plot.
# Note you don't really have to put
# plot_area=None. This is the default, and it means that the output
# will be a new plot area.
p0 = ts_plot(ts0,"ts0",plot_area=None,color="red",line_style="long dash")


# Now we are reusing the plot area and plotting another time series on
# top of the first.
p0 = ts_plot(ts1,"ts1",plot_area=p0,color="blue")
p0.legend.visible = True

# Now save the plot to a file
# The format is inferred from the extension
# A *.gif name is used here, but recommend
# *.png, which is widely used in applications
# (if lesser known), and efficient for plots
# JPEG (jpg) and encapsulated postscript (eps)
# and bitmap (bmp) are also supported
save_image_file(p0,"ts_line.pdf")
#save_image_file(p0,"ts_line.pdf")

# Now get a frame to display it live

fig=default_frame(p0,size=(600,400))
display_frame(fig)
# Things you can do:
# z: enter/exit zoom mode
# esc: reset to original scale
# cntrl-c: copy to clipboard
# cntrl-s: save to image file



# EOF
