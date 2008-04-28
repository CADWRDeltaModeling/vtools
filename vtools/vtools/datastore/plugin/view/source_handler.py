
#envisage import
from enthought.envisage.repository.repository_handler \
     import RepositoryImportHandler
     
#vtools import
from vtools.datastore.plugin.plugin_constants import ICATALOGMANAGER
     
class SourceImportHandler(RepositoryImportHandler):

    #---------------------------------------------------------------------------
    #  Handles the selected datasource  being changed:
    #---------------------------------------------------------------------------

    def _selection_changed ( self ):
        """ Handles the selection being modified.
        """
        cm = self.repository.application.get_service(ICATALOGMANAGER)
        cm.current_selection=str(self.selection)