
#standard libary import
import pdb
from string import strip
import re
from copy import copy

#vootls import 
from vtools.datastore.catalog import Catalog
from vtools.datastore.catalog_schema import CatalogSchemaItem
from vtools.datastore.data_reference import DataReference
from vtools.datastore.dimension import ChannelDimension
from vtools.datastore.dimension import RangeDimension

#local import
from hdf5_constants import *

__all__=["HDF5CatalogError","HDF5Catalog"]

class HDF5CatalogError(Exception):
    """ Exception store error informaiton during HDF5 operations"""
    ########################################################################### 
    # Object interface.
    ###########################################################################
    def __init__(self,st="Error in cataloging hdf5 file"):
        self.description_str=st
        
    def __str__(self):
        return self.description_str


class HDF5Catalog(Catalog):
    """ Class store a number of HDF5 data catalog entries"""
    
    ########################################################################### 
    # Object interface.
    ###########################################################################
    
    def __init__(self,file_path,schema,service,entries=None):

        super(HDF5Catalog,self).__init__()
        self.hdf5file_path=file_path
        self._orginial_service=service
        if entries:
            self._entries=entries
            for e in self._entries:
                e.catalog=self
            self._schemalst=schema
            self.entry_dimension_map=self._built_entry_dimension_map()
        
    ########################################################################### 
    # Protected interface.
    ########################################################################### 

    def _schema(self):
        return self._schemalst
        
    def _get_data_reference(self,entry,extent):
        
        """ Create a data reference based on the entry given,

            It is assumed, dimension_selection contain a list of
            dimension selection in entry dimension order,such as
            ('channel 1','01/23/1990-03/21/2002','flow').

            To do: add code to consider cases when parameter is
            given.            
        """

        source=self.hdf5file_path
        id=HDF5_DATA_SOURCE
        view=entry.item('view')
        selector=entry.item('path')
        
        # Built extent string.
        index=entry.index
        dimension_selection=self.entry_dimension_map[index]
                
        if not extent:
            extent=""
        else:
            extent=extent.rstrip(";")
            extent=extent+";"
            
        for (dimension,selection) in \
            zip(entry.dimension_scales(),dimension_selection):            
            name=dimension.name
            if  not name in extent:
                ## special handling for time window
                if HDF_TIME_SCALE  in name:
                    selection="("+str(selection[0])+","+\
                               str(selection[1])+")"
                    extent=extent+name+"="+selection+";"
                else:
                    extent=extent+name+"="+str(selection)+";"
        extent=strip(extent,';')
        
        data_ref=DataReference(id,source,view,selector,extent)        
        return data_ref

    def _filter_catalog(self,selector):
        """ hdf implementaion of catalog filtering.

            selector is assumed given as string like
            'path=/hydro/data/channel_flow;channel_number=1;
            channl_location=upstream;time_window=(1991-11-1
            24:00,1993-2-3 12:00)'. Just return a dataref for
            the moment.
        """

        select_pattern=self._parse_pattern(selector)        
        qualified_entries=[ copy(e) for e in self._entries \
                          if self._selected(e,select_pattern)]
        for i in range(0,len(qualified_entries)):
            qualified_entries[i].index=i
                                
        filtered_catalog=HDF5Catalog(self.hdf5file_path,self._schemalst,\
                                    self._orginial_service,qualified_entries)
        
        for i in range(0,len(qualified_entries)):
            qualified_entries[i].catalog=filtered_catalog
            
        return filtered_catalog        

    ########################################################################### 
    # Private interface.
    ###########################################################################
    def _parse_pattern(self,selector):
        """ built path regular expression matcher from selector string."""

        #selector=selector.upper()
        
        ## replace *
        selector=selector.replace("*",".*?")
        
        ## replace possible +, -
        selector=selector.replace("+","\\+")
        selector=selector.replace("-","\\-")
        
        return re.compile(selector)

    def _selected(self,entry,selector_pattern):
        """ Decide if a catalog entry conforms to criteria set by
            selector.
        """
        
        path=entry.item("path")
        
        if selector_pattern.match(path):
            return True
        else:
            return False    


    def _built_entry_dimension_map(self):

        """ Search dimensions of every catalog entry and built
            a map list of selection of every dimension on dataset.

            objective of builting such a map is to seperate the
            specified selection from catalog entry dimensions,
            which contains all selection choices. This
            map will be used in building data reference,
            and may be updated through GUI interaction.
        """
        map=[]

        # dimension selection map is in the order of entries
        for entry in self._entries:
            map_entry=[]
            for dimension in entry.dimension_scales():
                if type(dimension)==ChannelDimension:
                    map_entry.append(dimension.get_channel(0))                
                elif type(dimension)==RangeDimension:
                    map_entry.append(dimension.get_range())
            map.append(map_entry)
        return map


                
                

        

   
    

        
        

                

    

        
        
        
        
            

        
      
                

            

        

            

        

        

        



    




        

        
         

         
        
            
        
        
        
            
                
                

                

        

        
   
