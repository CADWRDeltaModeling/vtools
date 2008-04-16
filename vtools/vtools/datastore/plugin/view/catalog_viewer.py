""" The datasource catalog explorer view. """

import pdb

# Enthought library imports.
from enthought.envisage.workbench.api import View
#from enthought.envisage.ui.view import View
from enthought.traits.api import Any,Instance
from enthought.logger import logger

# Major package imports.
import wx

# vtools import.
from vtools.datastore.ui.catalog_adapter import create_catalog_editor_view
    
from vtools.datastore.catalog import Catalog
from vtools.datastore.plugin.catalog_manager import \
     CatalogManager
     
from vtools.datastore.plugin.plugin_implementation import \
ICATALOGMANAGER

class CatalogViewer(View):
    """ A view containing catalog view of a data source """
    ###########################################################################
    # Private traits.
    ###########################################################################   
    current_catalog=Instance(Catalog)
    _catalog_manager=Instance(CatalogManager)
    
    # The pointer to the panel contain catalog table.
    view_panel=Any
    
    ###########################################################################
    # Public interface.
    ###########################################################################
    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the view.
        'parent' is the toolkit-specific control that is the view's parent.
        """
        
        self.control = self._create_catalog_explorer(parent)        
        return self.control
    
    def update_catalog(self):
        """ Update the content of catalog view after current data
            source changed.
        """
        self.current_catalog=self._catalog_manager.current_catalog()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_catalog_explorer(self, parent):
        """ Creates the datasoruce catalog explorer.
        This is the combination of identity entries and other metadata.
        """
        
        self._catalog_manager=self.application.get_service\
        (ICATALOGMANAGER)        
        current_catalog=self._catalog_manager.current_catalog()
        
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        self.view_panel=panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        # Create grid panel.
        if current_catalog:
            catalog_table_control = self._create_catalog_table(panel,current_catalog)
            sizer.Add(catalog_table_control, 1, wx.EXPAND)
        # Resize the panel to match the sizer's minimum size.
        sizer.Fit(panel)
        return panel

    def _create_catalog_table(self, parent,current_catalog=None):
        """ Creates the catalog table. """
                
        if current_catalog:    
            pdb.set_trace()
            table_view=create_catalog_editor_view(current_catalog) 
            logger.debug("created tableview %s",table_view)           
            ui =  current_catalog.edit_traits(
                parent=parent, kind='subpanel',view=table_view)
            logger.debug("created control %s,%s",ui,ui.control)
            return ui.control
        
    def _current_catalog_changed(self,old,new):
               
        if not(old==new): 
            sizer=self.control.GetSizer() 
            try:
                sizer.Remove(0)
            finally:
                catalog_table_control = self._create_catalog_table\
                (self.control,self.current_catalog)
                logger.debug("created control %s",catalog_table_control)
                sizer.Add(catalog_table_control, 1, wx.EXPAND)
                sizer.Layout()
            #logger.debug("lay out control.")
            
#### EOF ######################################################################


