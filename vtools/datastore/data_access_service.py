
class DataAccessService(object):
    """ abstract class defined interface of retrieveing data 
        from data source.
    """

    ########################################################################### 
    # Public interface.
    ###########################################################################
    def get_data(self,dataref,overlap=None):
        """ Retrieve the time series specified by argument dataref.
        """
        self._check_data_reference(dataref)
        return self._get_data(dataref,overlap)

    def add_data(self,dataref,data):
        """ Add the time series data to place specified by dataref.
        """  
        self._check_data_reference(dataref)
        self._add_data(dataref,data)

    def modify_data(self,dataref,data):
        """ Modify the time series specified by argument dataref.
        """    
        self._check_data_reference(dataref)
        self._modify_data(dataref,data)

    def remove_data(self,dataref):
        """ Remove the time series specified by argument dataref.
        """    
        self._check_data_reference(dataref)
        self._remove_data(dataref,data)

    def dissect(self,dataref):
        """ Analyze the elements contained within a dataref and return
            result as dict, acutall result depends on data service.
        """
        return self._dissect(dataref)

    def assemble(self,translation,**kargs):
        """ Make a data ref based on the mapper and input
            used in transfer majorly.
        """
        return self._assemble(translation,**kargs)

    ########################################################################### 
    # Protected interface.
    ###########################################################################
    def _get_data(self,dataref):

        pass

    def _add_data(self,dataref,data):

        pass

    def _modify_data(self,dataref,data):

        pass

    def _remove_data(self,dataref):

        pass

    def _check_data_reference(self,dataref):

        pass

    def _dissect(self,dataref):
        pass

    def _assemble(self,translation,**kargs):
        pass
    
class DataAccessError(Exception):
    pass

       

    
