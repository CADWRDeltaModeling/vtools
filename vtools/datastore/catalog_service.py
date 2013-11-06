
class CatalogService(object):
    """ abstract class defined interface of retrieveing catalog
        from data source.
    """

    #ID of this service
    identification=""

    ########################################################################### 
    # Public interface.
    ########################################################################### 
    
    def get_catalog(self,source):
        """ Retrieve Catalog from data source specified by argument source.  
            Single catalog object or list of catalog will be returned.
        """       
        return self._get_catalog(source)

     
        

    ########################################################################### 
    # Protected interface.
    ###########################################################################

    def _get_catalog(self,source):
        """ User may overload this function to define their own method of
            loading catalog.  
        """       
        pass


        

    
        
     

