""" UI classes for a local file system. """


# Enthought library imports.
from enthought.traits.ui.api import Group, Item, TreeEditor, TreeNode, View

# Local imports.
from file_system import File, Folder

    
file_system_tree_editor = TreeEditor( 
    editable    = False,
    nodes       = [
        TreeNode(
            node_for = [File],
            label    = 'name',
        ),

        TreeNode(
            node_for = [Folder],
            children = 'children',
            label    = 'name',
            add      = [File, Folder]
        ),
        
    ]
)

file_system_tree_view = View(
    Group(
        Item(
            name      = 'root', 
            editor    = file_system_tree_editor, 
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

##### EOF #####################################################################
