#-------------------------------------------------------------------------------
#
#  Traits UI repository tree editor
#
#  Written by: David C. Morrill
#
#  Date: 03/22/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir, remove, rmdir, mkdir, makedirs, rename, access, W_OK

from os.path \
    import join, isfile, isdir, basename, dirname, splitext, exists

from enthought.traits.api \
    import Instance, Property, Str, Regex, List, true, false

from enthought.traits.ui.api \
     import View, Item, TreeEditor,  Handler,TreeNodeObject, ObjectTreeNode,TreeNode

from enthought.envisage.resource.resource_type \
    import ResourceType

from enthought.pyface.api \
    import error, confirm, YES

from enthought.logger.api \
    import logger

from enthought.envisage.repository.repository \
    import Repository, REPOSITORY_METADATA

from enthought.envisage.repository.repository_root \
    import RepositoryRoot




#-------------------------------------------------------------------------------
#  'RepositoryBaseNode' class:
#-------------------------------------------------------------------------------

class RepositoryBaseNode ( TreeNodeObject ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The handler for this tree:
    handler = Instance( 'enthought.envisage.repository.repository_handler.'
                        'RepositoryHandler' )

    # Event fired when a node is modified:
    modified = Property

    #---------------------------------------------------------------------------
    #  Returns whether chidren of this object are allowed or not:
    #---------------------------------------------------------------------------

    def tno_allows_children ( self, node ):
        """ Returns whether chidren of this object are allowed or not.
        """
        return True

    #---------------------------------------------------------------------------
    #  Returns whether a specified path allows any of a set of specified types:
    #---------------------------------------------------------------------------

    def allows_type ( self, path, types ):
        """ Returns whether or not the specified path allows any of the
            specified list of resource type ids. The possible results:
            - True:  Definitely allows
            - False: Definitely does not allow
            - None:  Unknown whether it allows any of the types or not
        """
        return self.handler.repository.allows_type( path, types )

    #---------------------------------------------------------------------------
    #  Implementation of the 'modified' property:
    #---------------------------------------------------------------------------

    def _set_modified ( self, value ):
        self.handler.repository.modified = value

#-------------------------------------------------------------------------------
#  'RepositoryNode' class:
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
#  'RepositoryRootNodeHandler' class:
#-------------------------------------------------------------------------------

class RepositoryRootNodeHandler ( Handler ):

    #---------------------------------------------------------------------------
    #  Handles a request to close a dialog-based user interface by the user:
    #---------------------------------------------------------------------------

    def close ( self, info, is_ok ):
        """ Handles a user request to close a dialog-based user interface.
        """
        if not is_ok:
            return True

        root   = info.object.root
        parent = info.ui.control
        if root.name.strip() == '':
            error( parent,
                   'Please specify a name for the new repository root.' )
            return False

        path = root.path
        if path.strip() == '':
            error( parent,
                   'Please specify a path for the new repository root.' )
            return False

        if not isdir( path ):
            if exists( path ):
                error( parent, ("'%s' is the name of a file, not a directory.\n"
                                "Please specify a directory.") % path )
                return False

            if confirm( parent, ("'%s' does not exist.\n"
                                 "Do you wish to create it?") % path ) != YES:
                return False
            try:
                makedirs( path )
            except:
                error( parent, "Could not create the '%s' directory." % path )
                return False

        return True

#-------------------------------------------------------------------------------
#  'RepositoryRootNode' class:
#-------------------------------------------------------------------------------

class RepositoryRootNode ( RepositoryBaseNode ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The RepositoryRoot this is a node for:
    root = Instance( RepositoryRoot, { 'persistent': True } )

    # The file path associated with this node:
    path = Property

    # The name of the node:
    name = Property

    # The child nodes of this node:
    children = List

    # Has the node been completely initialized yet?
    initialized = false

    # Does this node represent a valid path?
    valid = true

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    view = View(
        Item( 'root',
              style      = 'custom',
              show_label = False
        ),
        buttons = [ 'OK', 'Cancel' ],
        title   = 'New Repository Root',
        handler = RepositoryRootNodeHandler
    )

    #---------------------------------------------------------------------------
    #  Gets the resource type (if any) for a specified file:
    #---------------------------------------------------------------------------

    def _resource_type_for ( self, path ):
        """ Gets the resource type (if any) for a specified file.
        """
        for rt in self.handler.resource_types:
            if rt.serializer.can_load( path ):
                return rt

        return None

    #---------------------------------------------------------------------------
    #  Returns the type metadata for a specified directory:
    #---------------------------------------------------------------------------

    def _get_metadata ( self, path ):
        """ Returns the type metadata for a specified directory.
        """
        return self.handler.repository.get_metadata( path )

    #---------------------------------------------------------------------------
    #  Saves the type metadata for a specified directory:
    #---------------------------------------------------------------------------

    def _set_metadata ( self, path, types ):
        """ Saves the type metadata for a specified directory.
        """
        return self.handler.repository.set_metadata( path, types )

    #---------------------------------------------------------------------------
    #  Handles changes to the 'children' trait:
    #---------------------------------------------------------------------------

    def _children_items_changed ( self, event ):
        """ Handles changes to the 'children' trait.
        """
        for child in event.added:
            if not isinstance( child, DirectoryNode ):
                continue

            new_path = join( self.path, child.dir_name )
            if isfile( new_path ):
                error( self.handler.parent,
                       ("Cannot create the directory '%s'.\nThere is already a "
                        "file with that name.") % child.dir_name )
                return

            if not isdir( new_path ):
                try:
                    mkdir( new_path )
                    self.modified = True
                except:
                    error( self.handler.parent, ("An error occurred creating "
                           "the directory '%s'") % child.dir_name )
                    return

            # Update the directory metadata:
            self.handler.repository.update_metadata( new_path, self.handler.types )

            child.set( path = new_path, handler = self.handler )

            self.initialized = False

    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    #---------------------------------------------------------------------------

    def _has_children ( self, node ):
        """ Returns whether or not the object has children.
        """
        if not self.initialized:
            self._get_children( node )

        return (len( self.children ) > 0)

    #---------------------------------------------------------------------------
    #  Gets the object's children:
    #---------------------------------------------------------------------------

    def tno_get_children ( self, node ):
        """ Gets the object's children.
        """

        if not self.initialized:
            self.initialized = True
            handler          = self.handler
            types            = handler.types
            resource_types   = handler.resource_types
            path             = self.path
            root             = self.root
            dirs             = []
            files            = []

            # Convert each eligible file/directory into its corresponding node:
            try:
                for file in listdir( path ):
                    fn = join( path, file )
                    if isfile( fn ):
                        rt = self._resource_type_for( fn )
                        if True: #rt is not None:
                            files.append( FileNode( path          = fn,
                                                    resource_type = rt,
                                                    handler       = self.handler,
                                                    root          = root ) )
                    elif isdir( fn ): #and (self.allows_type( fn, types ) == True):
                        dirs.append( DirectoryNode( path    = fn,
                                                    handler = handler,
                                                    root    = root ) )
            except:
                self.valid = False
                logger.exception( "Error accessing the repository root with "
                                  "path: '%s'" % path )

                # Fake a label change to force the icon to be updated:
                if self._when_label_changed is not None:
                    self._when_label_changed( self, '', '' )

            # Sort the directories and files separately:
            dirs.sort(  lambda l, r: cmp( l.name, r.name ) )
            files.sort( lambda l, r: cmp( l.name, r.name ) )

            # Returns the combined list of objects:
            self.children = dirs + files

        return self.children

    #---------------------------------------------------------------------------
    #  Gets the label to display for a specified object:
    #---------------------------------------------------------------------------

    def tno_get_label ( self, node ):
        """ Gets the label to display for a specified object.
        """
        return self.root.name

    #---------------------------------------------------------------------------
    #  Sets the label for a specified node:
    #---------------------------------------------------------------------------

    def tno_set_label ( self, node, label ):
        """ Sets the label for a specified object.
        """
        self.root.name = label

    #---------------------------------------------------------------------------
    #  Returns whether or not the object's children can be renamed:
    #---------------------------------------------------------------------------

    def tno_can_rename ( self, node ):
        """ Returns whether or not the object's children can be renamed.
        """
        return ((not self.root.locked) and access( self.path, W_OK ))

    #---------------------------------------------------------------------------
    #  Returns whether or not the object can be renamed:
    #---------------------------------------------------------------------------

    def tno_can_rename_me ( self, node ):
        """ Returns whether or not the object can be renamed.
        """
        return (not self.root.permanent)

    #---------------------------------------------------------------------------
    #  Returns whether or not the object's children can be deleted:
    #---------------------------------------------------------------------------

    def tno_can_delete ( self, node ):
        """ Returns whether or not the object's children can be deleted.
        """
        return ((not self.root.locked) and access( self.path, W_OK ))

    #---------------------------------------------------------------------------
    #  Returns whether or not the object can be deleted:
    #---------------------------------------------------------------------------

    def tno_can_delete_me ( self, node = None ):
        """ Returns whether or not the object can be deleted.
        """
        return (not self.root.permanent)

    #---------------------------------------------------------------------------
    #  Confirms that a specified object can be deleted or not:
    #  Result = True:  Delete object with no further prompting
    #         = False: Do not delete object
    #         = other: Take default action (may prompt user to confirm delete)
    #---------------------------------------------------------------------------

    def tno_confirm_delete ( self, node = None ):
        """ Confirms that a specified object can be deleted or not.
        """
        return (confirm( self.handler.parent,
               "Delete '%s' from the repository?\n\nNote: No files will be "
               "deleted." % self.root.name,
               'Delete Repository Root' ) == YES)

    #---------------------------------------------------------------------------
    #  Deletes a child at a specified index from the object's children:
    #---------------------------------------------------------------------------

    def tno_delete_child ( self, node, index ):
        """ Deletes a child at a specified index from the object's children.
        """
        # fixme: This doesn't work right for a cut/paste operation, since it
        # will delete the object, then try to paste the now non-existent
        # file/directory somewhere else...
        self.children[ index ].delete()
        del self.children[ index ]

    #---------------------------------------------------------------------------
    #  Appends a child to the object's children:
    #---------------------------------------------------------------------------

    def tno_append_child ( self, node, child ):
        """ Appends a child to the object's children.
        """
        super( RepositoryRootNode, self ).tno_append_child( node, child )

        self.tno_get_children( node )

    #---------------------------------------------------------------------------
    #  Returns the list of classes that can be added to the object:
    #---------------------------------------------------------------------------

    def tno_get_add ( self, node ):
        """ Returns the list of classes that can be added to the object.
        """
        if ((not self.root.locked) and access( self.path, W_OK )):
            return [ ( DirectoryNode, True ) ]

        return []

    #---------------------------------------------------------------------------
    #  Returns the icon for a specified object:
    #---------------------------------------------------------------------------

    def tno_get_icon ( self, node, is_expanded ):
        """ Returns the icon for a specified object.
        """
        if not self.valid:
            return 'folder_forbidden'

        return super( RepositoryRootNode, self ).tno_get_icon( node,
                                                               is_expanded )

    #---------------------------------------------------------------------------
    #  Sets up/Tears down a listener for 'label changed' on a specified object:
    #---------------------------------------------------------------------------

    def tno_when_label_changed ( self, node, listener, remove ):
        """ Sets up/Tears down a listener for 'label changed' on a specified
            object.
        """
        super( RepositoryRootNode, self ).tno_when_label_changed( node,
                                                              listener, remove )
        if remove:
            listener = None
        self._when_label_changed = listener

    #---------------------------------------------------------------------------
    #  Implementation of the 'path' property:
    #---------------------------------------------------------------------------

    def _get_path ( self ):
        return self.root.path

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return basename( self.path )
     
class RepositoryNode ( RepositoryBaseNode ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The repository this is a node for:
    repository = Instance( Repository )

    # The valid repository roots:
    roots = List ( RepositoryRootNode )

    # Should 'locked' roots be shown?
    show_locked = true

    #---------------------------------------------------------------------------
    #  Handles the 'repository' trait being changed:
    #---------------------------------------------------------------------------

    def _repository_changed ( self, repository ):
        """ Handles the 'repository' trait being changed.
        """
        handler     = self.handler
        types       = self.handler.types
        roots       = []
        show_locked = self.show_locked
        for root in repository.roots:
            if ((show_locked or (not root.locked)) and
                (self.allows_type( root.path, types ) != False)):
                roots.append( RepositoryRootNode( root    = root,
                                                  handler = handler ) )

        self.roots = roots

    #---------------------------------------------------------------------------
    #  Handles the 'roots' trait being changed:
    #---------------------------------------------------------------------------

    def _roots_items_changed ( self, event ):
        """ Handles the 'roots' trait being changed.
        """
        roots = self.repository.roots

        for root_node in event.removed:
            roots.remove( root_node.root )

        for root_node in event.added:
            roots.append( root_node.root )
            root_node.handler = self.handler

        self.modified = True
        
#-------------------------------------------------------------------------------
#  'DirectoryNode' class:
#-------------------------------------------------------------------------------

class DirectoryNode ( RepositoryRootNode ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The user specified name of the directory:
    dir_name = Regex( 'New Folder', r'[A-Za-z.#@$%-_~]+' )

    # The handler for this tree:
    handler = Instance( 'enthought.envisage.repository.repository_handler.'
                        'RepositoryHandler' )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    view = View( 'dir_name{Name}',
                 title   = 'New Folder',
                 buttons = [ 'OK', 'Cancel' ],
                 width   = 300 )

    #---------------------------------------------------------------------------
    #  Gets the label to display for a specified object:
    #---------------------------------------------------------------------------

    def tno_get_label ( self, node ):
        """ Gets the label to display for a specified object.
        """
        return self.name

    #---------------------------------------------------------------------------
    #  Sets the label for a specified node:
    #---------------------------------------------------------------------------

    def tno_set_label ( self, node, label ):
        """ Sets the label for a specified object.
        """
        old_name = self.path
        dir_name = dirname( old_name )
        new_name = join( dir_name, label )
        try:
            rename( old_name, new_name )
            self.path     = new_name
            self.modified = True
        except:
            error( self.handler.parent, ("An error occurred while trying to "
                   "rename '%s' to '%s'") % ( basename( old_name ), label ) )

    #---------------------------------------------------------------------------
    #  Returns whether or not the object can be renamed:
    #---------------------------------------------------------------------------

    def tno_can_rename_me ( self, node ):
        """ Returns whether or not the object can be renamed.
        """
        return (not self.root.locked)

    #---------------------------------------------------------------------------
    #  Returns whether or not the object can be deleted:
    #---------------------------------------------------------------------------

    def tno_can_delete_me ( self, node = None ):
        """ Returns whether or not the object can be deleted.
        """
        return (not self.root.locked)

    #---------------------------------------------------------------------------
    #  Confirms that a specified object can be deleted or not:
    #  Result = True:  Delete object with no further prompting
    #         = False: Do not delete object
    #         = other: Take default action (may prompt user to confirm delete)
    #---------------------------------------------------------------------------

    def tno_confirm_delete ( self, node = None ):
        """ Confirms that a specified object can be deleted or not.
        """
        return (confirm( self.handler.parent,
                    "Delete '%s' and all of its contents?" % self.name,
                    'Delete Directory' ) == YES)

    #---------------------------------------------------------------------------
    #  Deletes the associated directory from the file system:
    #---------------------------------------------------------------------------

    def delete ( self, path = None ):
        """ Deletes the associated directory from the file system.
        """
        if path is None:
            path = self.path

        not_deleted = 0
        kept_fn     = ''
        try:
            for name in listdir( path ):
                fn = join( path, name )
                if isfile( fn ):
                    if self._resource_type_for( fn ) is not None:
                        remove( fn )
                        self.modified = True
                    else:
                        not_deleted += 1
                        kept_fn      = name
                elif isdir( fn ) and (not self.delete( fn )):
                    not_deleted += 1
            if not_deleted == 0:
                rmdir( path )
                self.modified = True
                return True
            if (not_deleted == 1) and (kept_fn == REPOSITORY_METADATA):
                remove( join( path, REPOSITORY_METADATA ) )
                rmdir( path )
                self.modified = True
                return True
        except:
            error( self.handler.parent, "Could not delete '%s'" % fn )
            return False

        # Remove the current types from the metadata for the repository:
        self.handler.repository.remove_metadata( path, self.handler.types )

        # Indicate that the directory was not deleted:
        return False

    #---------------------------------------------------------------------------
    #  Implementation of the (inherited) 'path' property:
    #---------------------------------------------------------------------------

    def _set_path ( self, path ):
        self._path = path

    def _get_path ( self ):
        return self._path


#-------------------------------------------------------------------------------
#  'FileNode' class:
#-------------------------------------------------------------------------------

class FileNode ( TreeNodeObject ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The RepositoryRoot this is a node for:
    root = Instance( RepositoryRoot )

    # The path to the associated file:
    path = Str

    # The resource type associated with this file:
    resource_type = Instance( ResourceType )

    # The name of the node:
    name = Property

    # The object associated with this node:
    object = Property

    # The handler for this tree:
    handler = Instance( 'enthought.envisage.repository.repository_handler.'
                        'RepositoryHandler' )

    # Event fired when a node is modified:
    modified = Property

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return splitext( basename( self.path ) )[0]

    #---------------------------------------------------------------------------
    #  Implementation of the 'object' property:
    #---------------------------------------------------------------------------

    def _get_object ( self ):
        """ Returns the object the node represents.
        """
        if not self._object_cached:
            self._object_cached = True
            self._object = self.resource_type.serializer.load( self.path )

        if self._object is not None:
            return self._object

        raise AttributeError( 'Could not load object definition' )

    #---------------------------------------------------------------------------
    #  Implementation of the 'modified' property:
    #---------------------------------------------------------------------------

    def _set_modified ( self, value ):
        self.handler.repository.modified = value

    #---------------------------------------------------------------------------
    #  Gets the label to display for a specified object:
    #---------------------------------------------------------------------------

    def tno_get_label ( self, node ):
        """ Gets the label to display for a specified object.
        """
        return self.name

    #---------------------------------------------------------------------------
    #  Sets the label for a specified node:
    #---------------------------------------------------------------------------

    def tno_set_label ( self, node, label ):
        """ Sets the label for a specified object.
        """
        old_name = self.path
        root_name, ext = splitext( old_name )
        dir_name = dirname( old_name )
        new_name = join( dir_name, label + ext )
        try:
            rename( old_name, new_name )
            self.path     = new_name
            self.modified = True
        except:
            error( self.handler.parent, ("An error occurred while trying to "
                   "rename '%s' to '%s'") % ( root_name, label ) )

    #---------------------------------------------------------------------------
    #  Returns the icon for a specified object:
    #---------------------------------------------------------------------------

    def get_icon ( self, object, is_expanded ):
        """ Returns the icon for a specified object.
        """
        return self.resource_type.image

    #---------------------------------------------------------------------------
    #  Confirms that a specified object can be deleted or not:
    #  Result = True:  Delete object with no further prompting
    #         = False: Do not delete object
    #         = other: Take default action (may prompt user to confirm delete)
    #---------------------------------------------------------------------------

    def tno_confirm_delete ( self, node = None ):
        """ Confirms that a specified object can be deleted or not.
        """
        return (confirm( self.handler.parent,
                         "Delete '%s' from the repository?" % self.name,
                         'Delete Repository Item' ) == YES)

    #---------------------------------------------------------------------------
    #  Deletes the associated file from the file system:
    #---------------------------------------------------------------------------

    def delete ( self ):
        """ Deletes the associated file from the file system.
        """
        try:
            remove( self.path )
            self.modified = True
        except:
            error( self.handler.parent, "Could not delete the file '%s'" %
                                        splitext( basename( self.path ) )[0] )


#-------------------------------------------------------------------------------
#  Repository tree editor:
#-------------------------------------------------------------------------------

repository_tree_editor = TreeEditor(
    #on_select  = 'handler.on_select',
    editable   = True,
    lines_mode = 'on',
    nodes      = [ ObjectTreeNode(
                       node_for  = [ RepositoryNode ],
                       label     = '=Repository',
                       children  = 'roots',
                       auto_open = True,
                       add       = [ ( RepositoryRootNode, True ) ] ),
                   ObjectTreeNode(
                       node_for = [ DirectoryNode ],
                       children = 'children',
                       name     = 'Folder' ),
                   ObjectTreeNode(
                       node_for  = [ RepositoryRootNode ],
                       children  = 'childrens',
                       name      = 'Repository Root',
                       label     = 'path',
                       auto_open = True ),
                   ObjectTreeNode(
                       node_for = [ FileNode ],
                       name='name') ]
)


