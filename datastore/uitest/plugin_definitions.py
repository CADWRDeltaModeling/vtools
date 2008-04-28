""" The absolute filenames of the plugin definitions used in the application.

"""


# Enthought library imports.
from os.path import abspath, dirname,join

# We use this package to find the absolute location of the plugin definition
# files.
import enthought.envisage
import enthought.plugins.python_shell
import vtools.datastore.plugin

envisage=abspath(dirname(enthought.envisage.__file__))
pythonshell=abspath(dirname(enthought.plugins.python_shell.__file__))
vtools_datastore_plugin=abspath(dirname(vtools.datastore.plugin.__file__))

# The plugin definitions that make up the application.
PLUGIN_DEFINITIONS = [
    # Envisage plugins.
    join(envisage, 'core/core_plugin_definition.py'),
    join(envisage, 'resource/resource_plugin_definition.py'),
    join(envisage, 'action/action_plugin_definition.py'),
    join(envisage, 'workbench/workbench_plugin_definition.py'),
    join(envisage, 'workbench/action/action_plugin_definition.py'),
    join(envisage, 'repository/repository_plugin_definition.py'),
    join(envisage, 'resource/resource_plugin_definition.py'),
    #join(envisage, 'ui/ui_plugin_definition.py'),
    #join(envisage, 'ui/preference/preference_plugin_definition.py'),

    
    # Enthought plugins.
    #join(pythonshell, 'python_shell_plugin_definition.py' ),
    
    # datastore plugins.
    join(vtools_datastore_plugin, 'plugin_definition.py'),
    
    
]

#### EOF ######################################################################
