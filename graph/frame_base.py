"""
 The basic frame class for time series plot.
"""



## graphic lib import 
import wx,os,pdb
from enthought.enable2.wx_backend.api import Window
from enthought.chaco2.api import PlotGraphicsContext
from enthought.chaco2.api import BasePlotContainer
from enthought.logger import logger as en_logger

## trait import
from enthought.traits.api import Instance,Bool

WILDCARD = "Portable Network Graphics file (*.png)|*.png|Bitmap (*.bmp)|*.bmp|"\
           "JPEG (*.jpg)|*.jpg|Encapsulated Postscript (*.eps)|*.eps|"\
           "GIF (*.gif)|*.gif|All files (*.*)|*.*"

class BaseVTFrame(wx.Frame):
    
    main_app=Instance(wx.App)

    def __init__ ( self, *args, **kw ):

        if "plot_window" in kw.keys():
            container=kw["plot_window"]
            del kw["plot_window"]
        else:
            container=args[0]
        
        if not isinstance(container,BasePlotContainer):
            raise ValueError("TSFrame' container input must be"+\
                             "initialized by a Chaco BasePlotContainer")
        

        
        wx.Frame.__init__( *(self,) + args, **kw )
        self.SetAutoLayout( True )
    
        # Create the subclass's window
        # self.plot_window = self._create_window()
        self.plot_window=Window(self,-1,component=container)
        self.container=container
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Show( True )

        ## event binding
        self.plot_window.control.Bind(wx.EVT_CHAR,self.OnChar)
        #self.Bind(wx.EVT_CLOSE,self.OnClose)
        return

    def _create_window(self):
        "Subclasses should override this method and return an enable.wx.Window"
        raise NotImplementedError
    
############################################################################
##  Event handling func
############################################################################
    
    def OnChar(self,event):

        ## keycode is not ascii code as said in wxptyhon doc,
        ## it is 1-26 for a-z in fact.
        keycode=event.KeyCode
        
        if event.ControlDown():
            if keycode==3: ## ctrl+c
                self._copy()
            elif keycode==19: ## ctrl+s
                self._save()
            else:
                event.Skip()
        else:
            event.Skip()

    def OnClose(self,event):
        
        self.main_app.exit()
            
############################################################################
##   Private funcs
#############################################################################

    def _copy(self):
        
        plot_gc = PlotGraphicsContext(self.container.outer_bounds)
        plot_gc.render_component(self.container)
        ashape=plot_gc.bmp_array.shape
        bm=wx.BitmapFromBufferRGBA(ashape[1],ashape[0],plot_gc.bmp_array)
        bitmapdata=wx.BitmapDataObject(bm)
        
        if wx.TheClipboard.Open():
            wx.TheClipboard.UsePrimarySelection(False)
            wx.TheClipboard.SetData(bitmapdata)
            wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
        else:
            dlg = wx.MessageDialog(self,"Couldn't open clipboard!\n",wx.OK)
            wx.Bell()
            dlg.ShowModal()
            dlg.Destroy()

    def _save(self):

        plot_gc = PlotGraphicsContext(self.container.outer_bounds)
        plot_gc.render_component(self.container)

        dlg = wx.FileDialog(self, "Save plot as...", defaultDir=os.getcwd(),
                            defaultFile="", wildcard=WILDCARD,
                            style=wx.SAVE | wx.CHANGE_DIR | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()        
            print "Saving plot to", path, "..."
            try:
                plot_gc.save(path)               
            except:
                print "Error saving!"
                raise
            print "Plot saved."
        dlg.Destroy()
        return        
        
        

    def _create_popmenu(self):
        
        return wx.Menu()
        



# EOF
