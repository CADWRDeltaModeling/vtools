""" The main datasotre plugin. """


# Enthought library imports.
from enthought.envisage.api import PluginDefinition

# Plugin definition imports (extension points etc).
from enthought.envisage.workbench.workbench_plugin_definition\
     import Perspective,Branding, View, Workbench

from enthought.envisage.repository.repository_extensions import ExportableObject
from enthought.envisage.repository.repository_extensions import RepositoryRootFactory

##from enthought.envisage.ui.ui_plugin_definition import \
##      UIBranding, UIViews, View

     
#from enthought.envisage.workbench.action.action_plugin_definition import \
#     WorkbenchActionSet
#from enthought.envisage.action.action_plugin_definition import \
#     Action, Group, Menu
     
     
# Local import
from vtools.datastore.plugin.actions import workbench_action_set

# The plugin's globally unique identifier (also used as the prefix for all
# identifiers defined in this module).
ID = 'vtools.datastore.plugin'
ID_CATALOGVIWER='Time Series Catalog'
ID_REPOSITORYVIWER='DataSources Explorer'


###############################################################################
# Extensions.
###############################################################################

#### Branding #################################################################

branding =  Branding(
    # The about box image.
    about_image = 'about.png',

    # The application icon.
    application_icon = 'application.ico',

    # The application name.
    application_name = 'DataStore'
)


#### Workbench ################################################################

workbench = Workbench(
    views = [
        View(
            class_name  = ID + '.view.repository_viewer.RepositoryViewer',
            name        = ID_REPOSITORYVIWER,
            position    = 'top'
        ),

        View(
            class_name  =ID + '.view.catalog_viewer.CatalogViewer',
            name        = ID_CATALOGVIWER,
            position    = 'left'
          ),
        #View(
        #    class_name  =ID + '.view.file_system_explorer.FileSystemExplorer',
        #    name        = "File vier",
        #    position    = 'left'
        #  )
        
    ],
    
    perspectives = [
        Perspective(
            id = ID + '.perspective.catalog',
            name = 'catalog',

            contents = [                
                Perspective.Item(
                    id = ID + '.view.repository_viewer.RepositoryViewer',
                    position = 'right'
                ),
                Perspective.Item(
                    id = ID + '.view.catalog_viewer.CatalogViewer',
                    #id ='catalog_viewer.CatalogViewer',
                    position = 'left',
                    relative_to = ID + '.view.repository_viewer.RepositoryViewer'
                ),
                #Perspective.Item(
                #    id = ID + '.view.file_system_explorer.FileSystemExplorer',
                #    #id ='catalog_viewer.CatalogViewer',
                #    position = 'left',
                #    relative_to = ID + '.view.repository_viewer.RepositoryViewer'
                #)
                
            ]
        )
    ],

    default_perspective = ID + '.perspective.catalog'
)


exportable_dss = ExportableObject(
    class_name = 'vtools.datastore.plugin.data.dssfile.DssFile',
    id = 'vtools.datastore.plugin.DssFile',
    label = 'dss file Template',
    )

###############################################################################
# The plugin definition.
###############################################################################

class DataStorePluginDefinition(PluginDefinition):
    """ The main datastore plugin. """
    
    # The plugin's globally unique identifier.
    id = ID

    # The name of the class that implements the plugin.
    class_name = ID + '.plugin_implementation.DataStorePlugin'

    # General information about the plugin.
    name          = 'catalog'
    version       = 'alpha'
    provider_name = 'bay delta office, Department of water resources'
    provider_url  = 'www.water.ca.gov'
    autostart     = True

    # The Id's of the plugins that this plugin requires.
    requires = ['enthought.envisage.workbench']


    # The extension points offered by this plugin.
    extension_points = []

    # The contributions that this plugin makes to extension points offered by
    # either itself or other plugins.
    extensions = [branding,workbench,workbench_action_set,
    RepositoryRootFactory(class_name='vtools.datastore.plugin.root_factories.BuiltInRootFactory'),
	exportable_dss]

#### EOF ######################################################################
