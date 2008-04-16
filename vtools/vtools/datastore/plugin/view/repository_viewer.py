""" The datasource catalog explorer view. """

import pdb


# Enthought library imports.
from enthought.envisage.workbench.api import View as WorkBenchView
from enthought.traits.ui.view import View 
from enthought.traits.ui.group import Group
from enthought.traits.ui.item import Item
from enthought.traits.api import HasTraits,Instance


 
#from enthought.envisage.repository.repository \
#    import Repository, REPOSITORY_METADATA

from repository_tree_editor  import RepositoryNode,RepositoryRootNode,repository_tree_editor
	
from enthought.envisage.repository.repository_handler import RepositoryHandler,RepositoryImportHandler


# Major package imports.
import wx

repository_tree_view = View(
    Group(
        Item(
            name      = 'repositorynode', 
            editor    = repository_tree_editor, 
            resizable = True
        ),

        show_labels = False,
        show_border = False,
        orientation = 'vertical',
    ),
    
    help   = False,
    width  = .3,
    height = .3
)


class RepositoryViewer(WorkBenchView):
    """ A view containing a repository of data sources """
    repositorynode = Instance( RepositoryNode )
    root=Instance(RepositoryRootNode)
    ###########################################################################
    # 'View' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the view.

        'parent' is the toolkit-specific control that is the view's parent.

        """
        
        import wx
        control = self._create_data_repository_panel(parent)        
        return control


    def _create_data_repository_panel(self, parent):
    
        """ Creates the datasoruce catalog explorer.
        This is the combination of identity entries and other metadata.
        """        
        
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        
        # Create grid panel.
        repository_control = self._create_repository_control(panel)
        sizer.Add(repository_control, 1, wx.EXPAND)

        # Resize the panel to match the sizer's minimum size.
        sizer.Fit(panel)
        return panel

    def _create_repository_control(self, parent):
        """ Creates the datasource chooser. """
       
        repository=self.application.get_service('enthought.envisage.repository.IRepository')
		
        if repository:   
            #hd=RepositoryImportHandler(repository=repository)
            hd=RepositoryImportHandler(repository=repository)
            pdb.set_trace() 
            self.repositorynode=RepositoryNode(repository=repository,handler=hd)   
            print "hello"
            self.root=self.repositorynode.roots[0]
            print "hello again"
            self.root.tno_get_children(self.root)            
            ui =  self.edit_traits(parent=parent, kind='subpanel',view=repository_tree_view)
            return ui.control
        else:
            raise StandardError("Error in retrieve serive 'vtools.datastore.IRepsitory' ")
            
        
        

        


#### EOF ######################################################################


