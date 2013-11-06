# Enthought library imports required for pan and zoom
from enthought.chaco2.tools.api import PanTool, SimpleZoom

#Numpy functions needed to create sample data
from numpy import arange,sin
from numpy.random import random

#Vtools imports required for scatter plots
from vtools.data.api import *
from vtools.graph.api import *

def create_scatter_data():
    """Create sample time series"""
    numpts = 5000
    x=arange(numpts)
    y0 = sin(x)+random(numpts)
    y1 = 1+0.8*y0+0.00006*random(numpts)+0.05*y0**2.
    start0=datetime(1994,1,10)
    start1=datetime(1994,1,14)
    dt=minutes(15)
    ts0=rts(y0,start0,dt)
    ts1=rts(y1,start1,dt)
    return ts0,ts1


ts0,ts1 = create_scatter_data()



plot=ts_scatter(ts0,ts1,["x_name","y_name"],
                    color=(.2,.44,.802),   # fractional RGB, see plot_format.py
                    marker="diamond",
                    marker_size=3)
# Tweak some of the plot properties
plot.title = "Scatter Plot"
plot.x_axis.title="X axis title"
plot.y_axis.title="Y axis title"
save_image_file(plot,"ts_scatter.png")

#EOF
