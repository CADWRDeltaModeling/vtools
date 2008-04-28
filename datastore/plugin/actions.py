""" 
The plugin action definition for the datastore plugin.

"""

# Enthought library imports
from enthought.envisage.action.action_plugin_definition import \
    Action, Group, Location, Menu
from enthought.envisage.workbench.action.action_plugin_definition import \
    WorkbenchActionSet

##from enthought.envisage.ui.ui_plugin_definition import \
##     Action, Group, Menu, UIActions, UIViews, View


##############################################################################
# Constants
##############################################################################

# The plugin's globally unique identifier (also used as the prefix for all
# identifiers defined in this module).

ID = 'vtools.datastore.plugin'

##############################################################################
# Action set for workbench.
##############################################################################
workbench_action_set = WorkbenchActionSet(
    id=ID+'.DataToolActionSet',
    name='DataToolSet',
    groups=[
#        Group(
#            id='PerspectiveGroup',
#            location=Location(path='ToolBar')
#            ),
        Group(
            id='CatalogGroup',
            location=Location(path='ToolBar')
            ),
        Group(
            id='DataTool',
            location=Location(path='MenuBar',before='ViewMenuGroup')
            ),
        ],
    menus=[
        Menu(
            groups=[
                Group(id='CatalogGroup'),
                Group(id='MathFuncGroup'),
                Group(id='EditGroup'),
                ],
            id='DataToolMenu',
            location=Location(path='MenuBar/DataTool'),
            name='&DataTool',
            ),
        Menu(
            id='CatalogToolMenu',
            groups=[Group(id='alltool'),],
            location=Location(path='MenuBar/DataToolMenu/CatalogGroup'),
            name='&Catalog',
            ),
        Menu(
            id='MathToolMenu',
            groups=[Group(id='alltool'),],
            location=Location(path='MenuBar/DataToolMenu/MathFuncGroup'),
            name='&Math',
            ),       
        
        ],
    actions=[
        # Action(
            # locations=[
                # Location(path='ToolBar/CatalogGroup'),
                # Location(path='MenuBar/DataToolMenu/CatalogToolMenu/alltool'),
                # ],
            # id=ID+".action.data_action.CatalogAction",
            # class_name=ID+".action.data_action.DataCatalogingAction",
            # name="&Cataloging",
            # image="action/images/do_it",
            # description="Catalog a source selected in data explorer",
            # tooltip="Click it to catalog a source selected in data explorer",
            # ),
        Action(
            locations=[
                Location(path='MenuBar/DataToolMenu/CatalogToolMenu/alltool'),
                ],
            id=ID+".action.data_action.EditCatalogAction",
            name="&Edit catalog",
            description="Edit the catalog of a source selected",
            ),
            
        Action(
            locations=[
                Location(path='MenuBar/DataToolMenu/MathToolMenu/alltool'),
                ],
            id=ID+".action.data_action.TimeAverageTS",
            name="Time &Averaging",
            description="Averaging a time series selected",
            ),
            
        ],
    )


