""" Draws several line plots using a user defined palette for colors.
    A palette file is a file with the name of the palette on the first
    line and then the colors listed one per line after that. You can
    use names of chaco colors (see the bottom of plot_format.py)
    or you can use RGB values (see the file chaco/graph/default_palette.txt
"""
from vtools.graph.api import *
from vtools.data.api import *
from vtools.data.sample_series import create_sample_series
from enthought.chaco2.api import OverlayPlotContainer

# Obtain sample data
ts0,ts1,ts2,ts3 = create_sample_series()

# Read the palette
read_palette("primary_palette.txt")
palette=get_palette("primary")

# Simple time series plot with the first color in the palette
p0 = ts_plot(ts0,"ts0",plot_area=None,color=palette[0])

# Two more, advancing within the palette
p0 = ts_plot(ts1,"ts1",plot_area=p0,color=palette[1])
p0 = ts_plot(ts2,"ts2",plot_area=p0,color=palette[2])

# Now save the plot to a file
save_image_file(p0,"palette.jpg")


# EOF

