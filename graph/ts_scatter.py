# Chaco imports
from enthought.chaco2.api import ArrayPlotData, Plot

# Enthought library imports
from enthought.chaco2.tools.api import PanTool, SimpleZoom
from vtools.data.api import prep_binary

all = ["ts_scatter_data","ts_scatter"]

def ts_scatter_data(ts1,ts2,names=["x","y"]):
    seq,start,slice0,slice1,slice2=prep_binary(ts1,ts2)
    pd = ArrayPlotData()
    pd.set_data("index",seq)
    pd.set_data(names[0],ts1[slice1])
    pd.set_data(names[1],ts2[slice2])
    return pd

def _add_tools(plot_area):
    pass

def ts_scatter(ts1,ts2,names=["x","y"],plot_area=None,**kwds):
    """Create a scatter plot from two time series.
       Inputs:
          ts1: time series that will go on the x axis
          ts2: time series that will go on the y axis
          names: names of the two series (e.g., for legend)
          plot_area: container or plot on which scatter will be
                     added as an overlay
          other arguments: any other chaco plotting style parameter
                Some useful ones are:
                marker_size: an integer
                color: 
                marker: circle,cross,diamond,dot,inverted_triangle,
                        pixel,plus,square,triangle
    """

    if plot_area:
        pd=plot_area.data
    else:
        pd=None

    pd=ts_scatter_data(ts1,ts2,names)
        
    if plot_area == None:
       plot_area = Plot(pd,add_grid=False)
    plot_area.plot(names,name="scatter%s_%s" % tuple(names),
                   type="scatter",**kwds)
    plot_area.bgcolor="white"
    _add_tools(plot_area)
    return plot_area



#EOF
