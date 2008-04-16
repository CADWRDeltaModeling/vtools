

# Standard library imports.
import os,pdb


# Enthought library imports.
from enthought.envisage.workbench.api import View
#from enthought.envisage.ui.view import View
from enthought.logger.api import logger

# Local imports.
from file_system import FileSystem, Folder
from file_system_tree_view import file_system_tree_view


class FileSystemExplorer(View):


    ###########################################################################
    # 'View' interface.
    ###########################################################################

    #def _create_contents(self, parent):
    def _create_contents(self, parent):
        """ Create the toolkit-specific control that represents the view.
        'parent' is the toolkit-specific control that is the view's parent.
        """

        file_system = FileSystem(root=Folder(path=os.path.abspath(os.curdir)))
        ui = file_system.edit_traits(
            parent=parent, kind='subpanel', view=file_system_tree_view
        )

        return ui.control
    
#### EOF ######################################################################
    

