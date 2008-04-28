""" The datastore plugin. """

## Standard library imports.
from os.path import join
import pdb

## Enthought library imports.
from enthought.envisage.api import Plugin
from enthought.envisage.repository.api import Repository
from enthought.envisage.repository.repository_root\
import RepositoryRoot

## Vtools import.
from vtools.datastore.data_service_manager import DataServiceManager
import vtools.datastore.dss
import vtools.datastore.hdf5
import vtools.datastore.excel

## Local import.
from catalog_manager import CatalogManager
from plugin_constants import IDSS,IHDF5,ICATALOGMANAGER,IREPOSITORY


## Load possible avaiable data source service plugins
try:
    for plugin in  __import__('pkg_resources').iter_entry_points(group="vtools.datastore",name=None):
        pe=plugin.parse(str(plugin))
        pe.load(False)
        
except Exception, e:
    raise ImportError("fail to load required data source serice plugin %s due to %s"%(str(plugin),str(e)))

class DataStorePlugin(Plugin):
    """ The datastore plugin. """

    ###########################################################################
    # 'Plugin' interface.
    ###########################################################################

    def start(self, application):
        """ Starts the plugin. """
        
        ## Create a service manager.
        dm=DataServiceManager()

        ## Create dss service.
        self.dss_service=dm.get_service("vtools.datastore.dss.DssService")
        ## Create HDF5 service.
        self.hdf5_service=dm.get_service("vtools.datastore.hdf5.HDF5Service")

        # Register the dss service.
        self.register_service("vtools.datastore.dss.DssService", self.dss_service)
        # Register the dss service.
        self.register_service("vtools.datastore.hdf5.HDF5Service", self.hdf5_service)

        ## Create models service.
        self.model_manager=CatalogManager(application)
        # Register the catalog manager service.
        self.register_service(ICATALOGMANAGER, self.model_manager)
        
        ## Create repository service.
        #rr1=RepositoryRoot(name='DiskD',path="D:")
        #self.repository=Repository(roots=[rr1,],application=application)
        #self.register_service(IREPOSITORY,self.repository)
        
        
        
        return

    def stop(self, application):
        """ Stops the plugin. """

        print 'Stopping the datastore plugin'

        return

#### EOF ######################################################################
