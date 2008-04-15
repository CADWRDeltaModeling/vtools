

class HDF5CatalogServiceError(Exception):

    def __init__(self,st="Error in cataloging HDF5 file"):

        self.description_str=st
        
    def __str__(self):

        return self.description_str
