""" Draws several overlapping line plots """
from vtools.data import sample_series
from vtools.data.timeseries import TimeSeries
from ts_plot import ts_plot

from enthought.enable2.wx_backend import Window
from demo_base import DemoFrame, demo_main
from enthought.chaco2.base import arg_find_runs
from enthought.chaco2.api import VPlotContainer,ArrayDataSource
from enthought.chaco2.tools.api import RangeSelection,RangeSelectionOverlay
from enthought.traits.api import HasTraits,Instance,List
from numpy import nan,invert,isnan,array,concatenate,shape
import scipy.interpolate

class DataEdit(object):
    def __init__(self,series,selection):
        self.start_ndx,self.end_ndx= \
           self._selection_to_slice(series,selection)
        print "st %s end %s" % (self.start_ndx,self.end_ndx)

    def modify(self,series):
        pass

    def _selection_to_slice(self,series,selection):
        return    (series.indexes_after(selection[0]),
                   series.index_before(selection[1]))

    def _render_dict(self):
        return {"line_style":"dash","color":"yellow","type":"line","line_width":2.00}

    def render(self,container):
        n=len([a for a in container.datasources.keys() if a.startswith("edit_index")])-1
        edit_index="edit_index%s" % n
        edit_value="edit_value%s" % n
        container.datasources[edit_index]=ArrayDataSource(self.index)
        container.datasources[edit_value]=ArrayDataSource(self.values)
        container.plot((edit_index,edit_value),**self._render_dict())
        container.plots["plot1"][0].request_redraw() 



class SetNan(DataEdit):
    def modify(self,series):
        self.index=series.ticks[self.start_ndx:self.end_ndx].copy()
        self.values=series.data[self.start_ndx:self.end_ndx].copy()
        series.data[self.start_ndx:self.end_ndx] = nan
        return series.data

    def _render_dict(self):
        return {"line_style":"dash","color":"red","type":"line","line_width":2.00}


class LinearInterpolationEdit(DataEdit):
    def modify(self,series):
        self.index=series.ticks[self.start_ndx:self.end_ndx].copy()
        self.values=series.data[self.start_ndx:self.end_ndx].copy()
        non_na_blocks=non_nan_blocks(self.index,self.values)
        x=self.index[non_na_blocks[0][0]:non_na_blocks[0][1]]
        y=self.values[non_na_blocks[0][0]:non_na_blocks[0][1]]
        if len(non_na_blocks) > 1:
            for b in non_na_blocks[1:]:
                appx=self.index[b[0]:b[1]]
                appy=self.values[b[0]:b[1]]
                x=concatenate((x,appx))
                y=concatenate((y,appy))

        interpolator=scipy.interpolate.interp1d(x,y)
        self.values=interpolator(self.index)
        series.data[self.start_ndx:self.end_ndx] = self.values
        return series.data


def non_nan_blocks(index,value):
    # Split the index and value raw data into non-NaN chunks
    nan_mask = invert(isnan(value))
    non_na_blocks = [b for b in arg_find_runs(nan_mask, "flat") if nan_mask[b[0]] != 0]
    return non_na_blocks

def add_edit_to_series(edit,series):
    if hasattr(series,"edits"):
        series.edits.append(edit)
    else:
        series.edits=[edit]


class DataEditorRangeSelection(RangeSelection):
    series=Instance(TimeSeries)
    edit_class=SetNan

    def selected_key_pressed(self, event):
        if event.character == "Enter":
            self.complete_edit(event)
        if event.character == "i":
            self.edit_class=LinearInterpolationEdit
        if event.character == "s":
            print self.selection
        return

    def complete_edit(self,event):
        print self.selection
        print self._get_selection() - self.series.ticks[0]
        edit=self.edit_class(self.series,self.selection)
        self.deselect(event)
        add_edit_to_series(self.series,edit)
        self.component.value.set_data(edit.modify(self.series))
        edit.render(self.container)


class PlotFrame(DemoFrame):
    def _create_window(self):
        ts0,ts1=sample_series.create_sample_series()[0:2]

        p=ts_plot(ts1)
        p0=p.plots["plot0"][0]

        rs=DataEditorRangeSelection(p0,
                                    left_button_selects = True,
                                    series=ts0)
        rs.deselect()
        rs.container=p
        p0.active_tool=rs
        p0.overlays.append(RangeSelectionOverlay(component=p0))
        p0.value.set_data(ts1.data)
        #container = VPlotContainer(resizable = "hv", bgcolor="lightgray",
        #                           fill_padding=True, padding = 10)        
        
        #container.add(p)
        self.container = p #container
        return Window(self, -1, component=p)
        




# EOF

