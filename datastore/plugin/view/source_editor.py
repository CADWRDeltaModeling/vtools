#-------------------------------------------------------------------------------
#
#  Traits UI repository editor
#
#  Written by: David C. Morrill
#
#  Date: 05/17/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

from enthought.traits.api \
     import List, Str, Enum, Instance

from enthought.traits.ui.api \
     import InstanceEditor, View, VGroup, HFlow, HSplit, Item

from enthought.traits.ui.wx.editor \
     import Editor

from enthought.traits.ui.wx.basic_editor_factory \
     import BasicEditorFactory
     
from enthought.envisage.repository.repository_tree_editor \
     import repository_tree_editor     

from source_handler \
     import SourceImportHandler



#-------------------------------------------------------------------------------
#  '_SourceEditor' class:
#-------------------------------------------------------------------------------

class _SourceEditor ( Editor ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Indicate that the editor is scrollable (default override):
    scrollable = True 

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Initialize the repository handler:
        self._handler = handler = SourceImportHandler( 
                                      repository = self.value,
                                      view       = factory.view,
                                      types      = factory.types )
        handler.set_resource_types()
        handler.set_root_node()

        # Create the view definition based on the factory settings:
        content = [ VGroup(
                        HFlow(
                            Item( 'add_root@',
                                  tooltip = 'Add a new repository root' ),
                            Item( 'create_folder@',
                                  tooltip = 'Create a new repository folder' ),
                            Item( 'delete_item@',
                                  tooltip = 'Delete the selection' ),
                            show_labels = False
                        ),
                        Item( 'root_node',
                              show_label = False,
                              style      = 'custom',
                              editor     = repository_tree_editor )
                    ) ]
        if factory.view != '':
            content.append( Item( 'selection',
                                  show_label = False,
                                  id         = 'selection',
                                  editor     = InstanceEditor(),
                                  style      = 'custom',
                                  resizable  = True ) )
        view = View( 
                   HSplit( id          = 'splitter', 
                           orientation = factory.orientation,
                           *content ),
                   id        = factory.id,
                   kind      = 'subpanel',
                   resizable = True )

        # Create the actual view and set the view's control as our control:
        self._ui = self.edit_traits( view    = view, 
                                     parent  = parent,
                                     context = handler,
                                     handler = handler )
        self.control = self._ui.control

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._ui.dispose()
        super( _RepositoryEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        pass
    
#-------------------------------------------------------------------------------
#  'RepositoryEditor' class:
#-------------------------------------------------------------------------------

class SourceEditor ( BasicEditorFactory ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Class of editor to be instantiated (override)
    klass = _SourceEditor
    
    # Resource types to be edited:
    types = List( Str )
    
    # Name of view to use for browsing selected repository items:
    view = Str( 'enthought.envisage.repository' )
    
    # Orientation of the tree and browser sub-views relative to each other:
    orientation = Enum( 'vertical', 'horizontal' )
    
    # Persistence id for the editor's sub-view:
    id = Str( 'enthought.envisage.repository.repository_editor.'
              'RepositoryEditor' )
                             
