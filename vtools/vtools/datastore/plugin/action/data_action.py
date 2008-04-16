""" Actions for data cataloging. """


# Enthought library imports.
from enthought.logger import logger
from enthought.traits.api import Bool, List, Str

from enthought.envisage.workbench.action import WorkbenchAction

# Vtools lib import
from vtools.datastore.plugin.plugin_implementation import \
ICATALOGMANAGER

import pdb

class DataCatalogingAction(WorkbenchAction):
    """ The action to fire cataloging of a data source. """

    ##########################################################################
    # 'Action' interface.
    ##########################################################################

    #### public interface ####################################################

    def perform(self, event):
        """ Performs the action.
            Cause catalog_table of viewer to udpate.
        """        
       
       ## Tempory demo code here to make code below works
       ## it set the current data source
        app=self.window.application
        cm=app.get_service(ICATALOGMANAGER)
        logger.debug("cm begin to change.")

        if not cm.current_selection:
            cm.current_selection=r'D:\temp\hist.h5'
            #cm.current_selection=r"D:\delta\models\vtools\src\vtools\datastore\hdf5\test\hist.h5"
        logger.debug("cm changed")
        vs=self.window.views        
        # A ugly way findout the catalog viewer
        # any better one?
        for v in vs:
            if hasattr(v,"update_catalog"):
                logger.debug("begin updating.")
                v.update_catalog()
            
    def refresh(self):
        """ Refresh the enabled/disabled state of this action.
        """
        return True 

#### EOF #####################################################################

