from vtools.datastore.data_access_service import DataAccessError

class HDF5AccessError(DataAccessError):

    def __init__(self,st="Error in HDF5 data source"):

        self.description_str=st
        
    def __str__(self):

        return self.description_str
