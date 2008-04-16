
""" Defines the vtool table editor and the table editor factory, for the Vtool Catalog
user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.ui.wx.table_editor import ToolkitEditorFactory \
as wxToolkitEditorFactory
from enthought.traits.ui.wx.table_editor import TableEditor \
as wxTableEditor

     


#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class VTToolkitEditorFactory(wxToolkitEditorFactory):
    """ vtool editor factory for table editors.
    """
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        return VTTableEditor( parent,
                            factory     = self,
                            ui          = ui,
                            object      = object,
                            name        = name,
                            description = description )

    def readonly_editor ( self, ui, object, name, description, parent ):
        self.editable = False
        return VTTableEditor( parent,
                            factory     = self,
                            ui          = ui,
                            object      = object,
                            name        = name,
                            description = description )

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------


#-------------------------------------------------------------------------------
#  'VTTableEditor' class:
#-------------------------------------------------------------------------------

class VTTableEditor(wxTableEditor):
    """ Editor that presents data in a table. Optionally, tables can have
    a set of filters that reduce the set of data displayed, according to their
    criteria.
    """

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the currently selected object being changed:
    #---------------------------------------------------------------------------

    def _selected_changed ( self, selected ):
        """ Handles the currently selected object being changed.
            load record in full for selected entry if it is incomplete.
        """

        self.set_selection( selected )
        
        if not hasattr(selected,"__iter__"):
            if hasattr(selected,"load_full"):
                selected.load_full()
        else:
            for sel in selected:
                if hasattr(sel,"load_full"):
                    sel.load_full()
                    
                    
    #---------------------------------------------------------------------------
    #  Handles the user selecting a row in the table when an editor view is
    #  associated with the table:
    #---------------------------------------------------------------------------

    def _selection_updated ( self, event ):
        """ Handles the user selecting a row in the table when an editor view
            is associated with the table.
        """

        toolbar   = self.toolbar
        no_filter = (self.filter is None)
        if len( event ) > 0:
            start, end = event[0][0], event[1][0]
            if start == end:
                self.selected_index = start
                self.selected       = self.model.get_filtered_item( start )
                if toolbar is not None:
                    delete = toolbar.delete
                    n      = len( self.model.get_filtered_items() ) - 1
                    if self.auto_add:
                        n -= 1
                        delete.enabled = (start <= n)
                    else:
                        delete.enabled = True
                    if delete.enabled and callable( self.factory.deletable ):
                        delete.enabled = self.factory.deletable( self.selected )
                    toolbar.search.enabled    = toolbar.add.enabled = True
                    toolbar.move_up.enabled   = (no_filter and (start > 0))
                    toolbar.move_down.enabled = (no_filter and (start < n))

                # Invoke the user 'on_select' handler:
                self.ui.evaluate( self.factory.on_select, self.selected )
                return

        self.selected_index = -1
        if toolbar is not None:
            toolbar.add.enabled     = no_filter
            toolbar.search.enabled  = toolbar.delete.enabled    = \
            toolbar.move_up.enabled = toolbar.move_down.enabled = False


