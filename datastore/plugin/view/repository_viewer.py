""" The datasource catalog explorer view. """

import pdb


# Enthought library imports.
from enthought.envisage.workbench.api import View as WorkBenchView
from enthought.traits.ui.view import View 
from enthought.traits.ui.group import Group
from enthought.traits.ui.item import Item
from enthought.traits.ui.api import UIInfo
from enthought.traits.api import HasTraits,Instance


 
from enthought.envisage.repository.repository \
    import Repository, REPOSITORY_METADATA
    
from enthought.envisage.repository.repository_editor \
    import RepositoryEditor

from enthought.envisage.repository.repository_tree_editor  import RepositoryNode,RepositoryRootNode,repository_tree_editor
	
from enthought.envisage.repository.repository_handler import RepositoryHandler,RepositoryImportHandler

# vtools import
from vtools.datastore.plugin.resource.default_resource_type import DefaultResourceType

# Major package imports.
import wx

#local import 
from source_editor import SourceEditor

class RepositoryViewer(WorkBenchView):
    """ A view containing a repository of data sources """
    repositorynode = Instance( RepositoryNode )
    root=Instance(RepositoryRootNode)
    repository=Instance(Repository)
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
       
        self.repository=self.application.get_service('enthought.envisage.repository.IRepository')
        resource_manager=self.application.get_service('enthought.envisage.resource.IResourceManager')
        
        ## find out the avilable source type plugin 
        typelist=[]
        try:
            for plugin in  __import__('pkg_resources').iter_entry_points(group="vtools.datastore.plugin.resource",name=None):
                pe=plugin.parse(str(plugin))
                resourcetype=pe.load(False)() 
                typelist.append(resourcetype.id)                
                resource_manager.add_resource_type(resourcetype)                
        except Exception, e:
            raise ImportError("fail to load required resource plugin %s due to %s"%(str(plugin),str(e)))
            

        repository_tree_view = View(
                                    Group(
                                        Item(
                                            name      = 'repository', 
                                            editor    = SourceEditor(types=typelist), 
                                            resizable = True
                                            ),

                                        show_labels = False,
                                        show_border = False,
                                        orientation = 'vertical',
                                    ),
                                help   = False,
                                width  = .3,
                                height = .3)  
        
        if self.repository:   
            #hd=RepositoryImportHandler(repository=repository)
            #hd=RepositoryHandler(repository=repository)
            #self.repositorynode=RepositoryNode(repository=repository,handler=hd)   
            #self.root=self.repositorynode.roots[0]
            #self.root.tno_get_children(self.root)     
            #respository_tree_view.handler=RepositoryHandler()
            #ui =  self.edit_traits(parent=parent, kind='subpanel',view=repository_tree_view)
            ui = self.edit_traits(parent=parent,kind='subpanel',view=repository_tree_view)
            
            return ui.control
        else:
            raise StandardError("Error in retrieve serive 'vtools.datastore.IRepsitory' ")
            
        
        

        


#### EOF ######################################################################


