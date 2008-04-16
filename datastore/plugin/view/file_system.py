""" Classes that model a local file system. """


# Standard library imports.
from os import listdir
from os.path import basename, dirname, isdir, join

# Enthought library imports.
from enthought.traits.api import HasStrictTraits, Instance, List, Str, Property


class FileSystemObject(HasStrictTraits):
    """ Abstract base class for all files/folders in a file system. """

    # The absolute pathname of the file/folder.
    path = Str

    # The basename of the file/folder.
    name = Str

    def _path_changed(self, new):
        """ Called when the path is changed. """

        self.name = basename(self.path)

        return

    
class File(FileSystemObject):
    """ A file in a local file system. """
    
    pass


class Folder(FileSystemObject):
    """ A folder in a local file system. """

    # The folder's children.
    children = Property(List(FileSystemObject))

    # children
    def _get_children(self):
        """ Returns the contents of a folder. """
        
        if isdir(self.path):
            children = []
            for filename in listdir(self.path):
                path = join(self.path, filename)
                if isdir(path):
                    child = Folder(path=path)

                else:
                    child = File(path=path)

                children.append(child)

        else:
            children = []

        return children


class FileSystem(HasStrictTraits):
    """ A local file system. """

    # The root for the file system.
    root = Instance(Folder)

##### EOF #####################################################################
