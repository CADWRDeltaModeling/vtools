
#vtools import 
from vtools.datastore.plugin.resource.default_resource_type import DefaultResourceType

# Enthought library imports.
from enthought.naming.api import ObjectSerializer
from enthought.traits.api import Str

__all__=["DssResourceType"]


class DssSerializer(ObjectSerializer):
    """ Serizlier for dss sources """

    ext = Str('.dss')
    
    def load(self, path):
        """ Loads an object from a file. 
        """
        
        try:
            obj = path
        except Exception, ex:
            print_exc()
            raise ex
        return obj
    

class DssResourceType(DefaultResourceType):
    """ The resource type for dss files. """
    #### 'FileResourceType' interface #########################################
    # The file extension recognized by this type.
    ext = Str('dss')
    serializer = DssSerializer( ext = '.dss' )
    
    
    
    
