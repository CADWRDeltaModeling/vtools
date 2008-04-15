""" Draws several overlapping line plots """
import sys

# Enthought library imports

from enthought.chaco2.axis import PlotAxis,AbstractTickGenerator
from enthought.chaco2.tools.api import SimpleZoom,BroadcasterTool,PanTool
from enthought.chaco2.api import OverlayPlotContainer
      
from vtools.data.api import *
from vtools.graph.api import *
from vtools.data.sample_series import *


## local import
__all__=["multi_value_axis"]


def multi_value_axis(left_plot,right_plot):
    if not (isinstance(left_plot, Plot) and
            isinstance(right_plot,Plot)):
        raise TypeError("Left and right arguments must be instances of Plot")

    right_plot.index_range = left_plot.index_range
    right_plot.padding = 0
    right_plot.value_axis.orientation = "right"
    right_plot.index_axis.orientation = "top"
    right_plot.index_axis.visible=False
    right_plot.value_grid.visible=False
    
    left_plot.right_plot=right_plot
    left_plot.add(right_plot)

    # Attach some tools to the plot
    broadcaster = BroadcasterTool()

    for c in (left_plot, right_plot):
        zoom = SimpleZoom(component=c, tool_mode="box", always_on=False)
        broadcaster.tools.append(zoom)
        
    left_plot.tools.append(broadcaster)
    left_plot.legend.plots.update(right_plot.legend.plots)

    return left_plot
        


# EOF


