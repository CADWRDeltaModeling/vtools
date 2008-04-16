
# Standard python import.
from os.path import isfile
import pdb
from enthought.logger import logger

# Enthought library imports.
from enthought.traits.api import Dict,HasTraits,Trait,Str
from enthought.envisage.workbench.api import WorkbenchApplication

# vtools import
from vtools.datastore.dimension import ChannelDimension
from plugin_constants import IDSS,IHDF5
from vtools.datastore.service import Service
    
class CatalogManager(HasTraits):
    """ Class manages a number of catalog
        models contained in a number of data source.
    """

    ###########################################################################
    # private traits.
    ###########################################################################    
    _model_dict=Dict({})
    _catalog_dict=Dict({})
    _application=Trait(WorkbenchApplication)
    current_selection=Str('')
    ###########################################################################
    # 'object' interface.
    ###########################################################################     
    def __init__(self,application):
        self._application=application
        #self.current_selection=r'D:\delta\models\vtools\src\vtools\datastore\dss\test\testfile.dss'
    ###########################################################################
    # public interface.
    ###########################################################################     
    def current_models(self):
        """ Return current selected datasoruce cataloggrid models"""

        if self.current_selection in self._model_dict.keys():
            return self._model_dict[self.current_selection]

    def current_catalog(self):
        """ Return current selected datasoruce cataloggrid models"""

        if self.current_selection in self._catalog_dict.keys():
            return self._catalog_dict[self.current_selection]

    def add_datasource(self,datasource):
        """ Add the catalog models of a datasource into manager by
            cataloging it. datasoruce will be used as key to identify
            its models,should be in string.
        """
        if not (datasource in self._model_dict.keys()):
            catalog=self._cataloging_datasource(datasource)
            if catalog:               
##                models=generate_models_from_schema_entries(catalog.entries(),\
##                                                           catalog.schema())
##                self._model_dict[datasource]=models
                self._catalog_dict[datasource]=catalog
         
    def remove_datasource(self,datasource):
        """ remove the catalog models of a datasource from manager by
            cataloging it. datasoruce will be used as key to identify
            its models.
        """

        if datasource in self._model_dict.keys():
            del self._model_dict[datasource]

    def get_model_dic(self):

        """ debug only,remove soon """

        return self._model_dict
         

    ###########################################################################
    # protected interface.
    ###########################################################################

    def _current_selection_changed(self,old,new):
        """ Whennever current datasource changed, if it is a new one, add it."""
        if not (new==old):
            self.add_datasource(new)

    ###########################################################################
    # private interface.
    ########################################################################### 

    def  _cataloging_datasource(self,datasource):
        """ Cataloging a datasoruce based on its type and return catalog."""

        service=None
        for cls in Service.all_service.values():
           if cls.serve(datasource):
              service=self._application.get_service(cls.identification)
             
        logger.debug("got service")
        
        if service:
            catalog=service.get_catalog(datasource)
            
            ## Here intentionaly add a channeldimension to every entry
            ## in catalog. for test gui only.
            
#            channels=ChannelDimension(['flow','stage','EC','Temp'])
#            channels.name='physical_variable'
#            channels.label="physical_variable"
#            channels.dimension_index=1
#            logger.debug("done with adding entries")
#            for entry in catalog.entries():
#                entry.add_dimension(channels)
                
                

            return catalog

        
        
