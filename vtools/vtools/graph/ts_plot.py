""" Draws several overlapping line plots """
import sys

# Enthought library imports

from enthought.chaco2.axis import PlotAxis,AbstractTickGenerator
from enthought.chaco2.tools.api import SimpleZoom,LineSegmentTool,PanTool
from enthought.chaco2.grid import PlotGrid
from enthought.chaco2.api import ArrayPlotData,Plot,VPlotContainer
                            
from vtools.data.vtime import *
from numpy import repeat,concatenate,array
import wx

## local import
import time_ticks
from zoom_connect import zoom_connect
from palette import get_palette
from frame_base import BaseVTFrame

__all__=["ts_plot","time_axis","ts_line_data", \
         "default_frame","display_frame", \
         "zoom_plot_frame","ts_plot_frame","zoom_plot_frame"]

class DateFormatter(object):
    def __init__(self,date_format="%d%b%Y\n    %H:%M"):
        self.date_format=date_format
 
    def __call__(self,ticks):
        return self.format(ticks)

    def update_context(self):
        pass
    
    def format(self,ticks):
        self.update_context()
        t=ticks_to_time(long(ticks))
        if (ticks<=1000): return '%s'% ticks
        return t.strftime(self.date_format)
        


class DateTimeTickGenerator(AbstractTickGenerator):
    def get_ticks(self, data_low, data_high, bounds_low, bounds_high, interval,use_endpoints,scale):
        return time_ticks.auto_time_ticks(data_low,data_high,bounds_low, \
                                    bounds_high,interval,False)


def _add_tools(plot):
    plot.overlays.append(SimpleZoom(plot,tool_mode="box",always_on=False))


def time_axis(axis):
    """Convert an existing axis into a time axis"""
    axis.tick_label_formatter=DateFormatter()
    axis.tick_generator=DateTimeTickGenerator()
    return axis



def ts_flat_data(ts,name,plot_data=None,period=True):
    """Create a chaco-compatible PlotData object from a series
       The resulting Plot Data will repeat values in
       such a way that the plot will appear as a series
       of flat lines between values in the time series.
       This can be a good way of visualizing period valued
       data.
    """
    if not plot_data:
        plot_data=ArrayPlotData(index=ts.ticks)
    if not name:
        if (plot_data.list_data()):
            n=len(plot_data.list_data())/2
        else:
            n=0            
        name="Series%s" % n
    else:
        index_name="%s_index" % name
    if period:
        if (not ts.is_regular):
            raise ValueError("Period flattening not valid for irregular timeseries")
        
        new_end=array([ticks(ts.end+ts.interval)])
        t=concatenate((repeat(ts.ticks,2)[1:],new_end)) # fixme: not multivariate
        plot_data.set_data(index_name, t)
        plot_data.set_data(name, repeat(ts.data,2))                         
    else:
        plot_data.set_data(index_name,repeat(ts.ticks,2)[1:])
        plot_data.set_data(name,repeat(ts.data,2)[:-1])
    return index_name,name,plot_data

def ts_line_data(ts,name,plot_data=None):
    if not plot_data:
        plot_data=ArrayPlotData(index=ts.ticks)
    if not name:
        if (plot_data.list_data()):
            n=len(plot_data.list_data())/2
        else:
            n=0            
        name="Series%s" % n
    else:
        index_name="%s_index" % name
    plot_data.set_data(index_name,ts.ticks)
    plot_data.set_data(name,ts.data)
    return index_name,name,plot_data

def ts_plot(series,name=None,plot_area=None,flat=False,**kwds):
    if kwds.has_key("add_axis"):
       add_axis=kwds["add_axis"]
       del kwds["add_axis"]
    else:
       add_axis=True

    if kwds.has_key("add_grid"):
       add_grid=kwds["add_grid"]
       del kwds["add_grid"]
    else:
       add_grid=True

    if plot_area:
        pd=plot_area.data
    else:
        pd=None

    if flat:
        index_name,name,pd=ts_flat_data(series,name,pd,period=(flat=="period"))
    else:
        index_name,name,pd=ts_line_data(series,name,pd)
        
    if plot_area == None:
       plot_area = Plot(pd,add_grid=False)
    plot_area.plot((index_name,name),name=name,**kwds)
    if add_grid:
          add_ts_grids(plot_area)

    if add_axis:
       plot_area.index_axis=time_axis(plot_area.index_axis)

    plot_area.bgcolor="white"
    _add_tools(plot_area)
    return plot_area


def add_ts_grids(plot, orientation="normal"):
    """
    Creates horizontal and vertical gridlines for a plot.  Assumes that the
    index is horizontal and value is vertical by default; set orientation to
    something other than "normal" if they are flipped.
    """
    if orientation in ("normal", "h"):
        v_mapper = plot.index_mapper
        h_mapper = plot.value_mapper
    else:
        v_mapper = plot.value_mapper
        h_mapper = plot.index_mapper
    
    vgrid = PlotGrid(mapper=v_mapper, orientation='vertical',
                     component=plot,
                     line_color="lightgray", line_style="dot",
                     tick_generator=DateTimeTickGenerator()
                     )

    hgrid = PlotGrid(mapper=h_mapper, orientation='horizontal',
                     component=plot,
                     line_color="lightgray", line_style="dot"
                     )
    plot.x_grid=vgrid
    plot.y_grid=hgrid
    return hgrid, vgrid


def _display(frame,display):
    
    if display and frame:
        app = wx.PySimpleApp()  
        frame.main_app=app  
        app.SetTopWindow(frame)
        app.MainLoop()
        
def display_frame(frame):
    return _display(frame,True)
        

def default_frame(container=None,size=(600,500),title=""):
    """returns a standalone frame with saving and copying
       functionality.
       Inputs:
       container layout container displayed in plot(Plot,VPlotContainer,...)
       size      width and height of frame
       title     title displayed at top of frame

       Output:
       frame with container installed
    """
    return BaseVTFrame(None,size=size,title=title,\
                       plot_window=container)

def figure_plot_area(frame,container,display=True):
    """adds the given container to the frame. If the frame already
       has a top level container it is replaced
    """
    # see if display above
    pass
  

def ts_plot_frame(tss,ts_names=[],types=None,title="",size=(600,500)):
    """fast plotting function for normal python shell that plots series
       on a single set of axes and puts it in a frame for display
    """
    (tss,ts_names)=_check_ts_inputs(tss,ts_names)    
    p1=_create_ts_plot(tss,ts_names,"time series",types=types)
    frame = default_frame(size=size,title=title,\
                       container=p1)
    _display(frame,True)

def zoom_plot_frame(tss,ts_names=[],size=(600,500),title="",types=None):
    """fast zoom plotting function for normal python shell that plots series
       on a single set of axes and puts it in a frame for display
    """
    (tss,ts_names)=_check_ts_inputs(tss,ts_names)    
    source=ts_names[0]
    dest=ts_names[0]
    p1=_create_ts_plot(tss,ts_names,"time series",types=types)
    p2=_create_ts_plot(tss,ts_names,"zoomed plot",types=types)
    container = VPlotContainer()
    container.stack_order="top_to_bottom"
    container.add(p1)
    container.add(p2)
    zoom_overlay=zoom_connect(p1,p2,source,dest)
    container.overlays.append(zoom_overlay)
    frame = default_frame(size=size,title=title,\
                       container=container)    
    _display(frame,True)
    
###############################################################################
##                 private helper funcs                                     ###
###############################################################################
COLOR_PALETTE=get_palette("default")
def _create_ts_plot(tss,ts_names,title,types=None):
    i=0
    p1=None
    if not types:
        types=['line']*len(tss)
    for ts,ts_name,type in zip(tss,ts_names,types):
        if type=="scatter":
            if i==0:
                p1=ts_plot(ts,name=ts_name,color=tuple(COLOR_PALETTE[i]),\
                           type=type,marker="dot")
            else:
                p1=ts_plot(ts,plot_area=p1,name=ts_name,\
                             color=tuple(COLOR_PALETTE[i]),\
                           type=type,marker="dot")
        else:
            if i==0:
                p1=ts_plot(ts,name=ts_name,color=tuple(COLOR_PALETTE[i]),type=type)
            else:
                p1=ts_plot(ts,plot_area=p1,name=ts_name,\
                             color=tuple(COLOR_PALETTE[i]),type=type)

            
        i=i+1        
    p1.title=title
    p1.legend.visible = True        
    return p1

def _check_ts_inputs(tss,ts_names):
    if len(tss)==0:
        raise ValueError("No input timeseries.")
    if len(ts_names)==0:
        ts_names=_create_ts_names(len(tss))

    if not len(ts_names)==len(tss):
        raise ValueError("input number of data is not equal to"+\
                         "number of data names")
    return tss,ts_names

def _create_ts_names(tss_num):
    """ if no input names,create a default one."""
    tss_names=[]
    for i in range(tss_num):
        tss_names.append("ts"+str(i))
    return tss_names


#######################################################################################




# EOF
