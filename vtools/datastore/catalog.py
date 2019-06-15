
# Standard Library imports
# Application specific imports
from copy import deepcopy

# Local import
from .dimension import Dimension


class CatalogEntry(object):

    """ Single entry of a catalog of a datasource
    """ 
    ########################################################################### 
    # 'object' interface.
    ########################################################################### 

    def __init__(self,schema,catalog=None):
        
        self.fully_loaded=False
        self._index=0
        self._schema=schema
        self._item_name_to_index={}
        self._description=""
        self._metadata_items=[]
        self._dimensions=[]
        self.catalog=catalog
         
    def __str__(self):
        result=""

        for schema_entry in self._schema:
            if schema_entry.get_element("role")=="identification":
                item_name=schema_entry.get_element("name")
                item=self.item(item_name)
                result=result+"|"+item

        result=result+"|"        
        for scale in self._dimensions:
            result=result+" "+str(scale)

        result=result+"\n"
        return result

    def __copy__(self):
        result=self.__class__(self._schema)
        result.fully_loaded=self.fully_loaded
        result._index=self._index
        result._schema=self._schema
        result._item_name_to_index=deepcopy(self._item_name_to_index)
        result._description=self._description
        result._metadata_items=deepcopy(self._metadata_items)
        result._dimensions=self._dimensions
        result.catalog=self.catalog
        return result
        

    ########################################################################### 
    # Public interface.
    ###########################################################################

    def item(self,name):
        """ Function to return the value of metadata item within a CatalogEntry
            instance with the name specified
            
            If the item specified actually doesn't exist, error will be raised 
        """
        if name in list(self._item_name_to_index.keys()):
            index=self._item_name_to_index[name]
        else:
            return KeyError(" %s doesn't exist in this instance of CatalogEntry \
            "%name)
        return self._metadata_items[index]

    def has_item(self,name):
        """ Check if a item exist within a catalog entry."""
        if name in list(self._item_name_to_index.keys()):
            return True
        else:
            return False
        
    def add_item(self,name,value):
        """ Function to set the value of metadata within a CatalogEntry instance
            with the name specified.
            
        """        
        if(name in list(self._item_name_to_index.keys())):
            index=self._item_name_to_index[name]
            self._metadata_items[index]=value
        else:
            index=len(self._item_name_to_index)
            self._item_name_to_index[name]=index
            self._metadata_items.append(value)
            #return KeyError(" %s doesn't exist in this instance of CatalogEntry \
            #"%name)

       
    def set_item(self,name,value):
        """ Function set a item value.
            It actually call add_item.
        """

        self.add_item(name,value)

    def add_dimension_scale(self,dimension):

        """ Function to add a dimension instance
            to dimension list.
        """
        self._dimensions.append(dimension)
    
    def dimension_scales(self):
        """ Function to retrieve all the dimension
        defined within this CatalogEntry."""
        return self._dimensions

    def item_names(self):
        """
             Return names of all meta data item
             stored in this entry.
        """
        names=[None]*(len(self._metadata_items)+len(self._dimensions))
        for name in list(self._item_name_to_index.keys()):
            index=self._item_name_to_index[name]
            names[index]=name

        index=index+1        
        for scale in self._dimensions:
            label=scale.label
            names[index]=label
            index=index+1
            
        return names
        
    def get_index(self):
        
        return self._index
    
    def set_index(self,value):
        """ Set inner index value. """
        
        self._index=int(value)

    def load_full(self):
        """ Load full record about a entry if applicable."""
        if not self.fully_loaded:
            self.catalog.load_entry_full(self._index)
            self.fully_loaded=True
               
    index=property(get_index,set_index,doc="index of entry within a catalog")
    
class Catalog(object):

    """ Class contain a list of CatalogEntry, also provide a number of operations
        on those entries.
    """
    
    ########################################################################### 
    # Private traits,
    ###########################################################################
    #_entries=List([])
    #_schemalst=List([])
    #_orginial_service=Any(None)
    
    
    ########################################################################### 
    # Public interface.
    ###########################################################################
    
    def __init__(self):
        self._entries=[]
        self._schemalst=[]
        self._orginial_service=None
    
    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __str__(self):

        ret=""        
        for e in self._entries:
            ret=ret+str(e)
            ret=ret+"-"*60+"\n"
        return ret


    ###########################################################################        
    
    def remove(self,entry):
        """ Remove a entry from Catalog. """
        return self._remove(entry)

    def modify(self,old_entry,new_entry):
        """ Modify a entry within Catalog. """
        return self._modify(old_entry,new_entry)

    def copy(self, entry):
        """ Copy data associated with entry1 into entry2.
        """        
        return self._copy(entry)
    
    def entries(self):
        """ return a iterator over the inside list of CatalogEntries."""
        return self._entries
    
    def get_data_reference(self,entry,extent=None):
        """ return data record reference on a given catalog entry."""
        return self._get_data_reference(entry,extent)

    def data_references(self,selector=None,extent=None):
        """ return a itertor of the datareferences \
        to paths based on selector. """
        
        if selector:
            c=self.filter_catalog(selector)
        else:
            c=self
        entry_iter=iter(c._entries)
        while True:
            entry=next(entry_iter)
            ref=c.get_data_reference(entry,extent)
            yield ref
            

    def schema(self):
        """ return the schema which defined this catalog"""
        return self._schema()

    def filter_catalog(self,selector):
        """ Filter the current catalog based on given selector, return
            a list of data references conforms to selector. Usually selector
            is a line of regular expression string, such as for a xxx data
            source, it may be "A=RLTM;B=RSAC*;".
        """
        return self._filter_catalog(selector)
    
    def load_entry_full(self,index):

        """ Load the catalog entry by index in full, this sub used in
            lazy loading mode.
        """        
        self._load_entry_full(index)
            
    def reload(self):
        """ Lazily reload catalog info when entry has changed."""
        self._reload(self)

    ########################################################################### 
    # Protected interface.
    ###########################################################################    
    def _remove(self,entry):
        pass
    def _modify(self,old_entry,new_entry):
        pass
    def _copy(self, entry):
        pass    
    def _get_data_reference(self,entry,extent=None):
        pass
    def _schema(self):
        pass

    def _filter_catalog(self,selector):
        """ User may overload this function to define their own method of
            filtering catalog for different data source.  
        """       
        pass

    def _load_entry_full(self,index):
        
        pass

    def _reload(self):
        pass


def catalog_string(c,header=True):
    """Return a string representation of a catalog """
    headerline=""
    if header:
        for schema_entry in c._schemalst:
            if schema_entry.get_element("role")=="identification":
                item_name=schema_entry.get_element("name")
                headerline=headerline+"    |    "+item_name
                
        headerline=headerline+"   |    data_extents"
        headerline=headerline.strip()
        headerline=headerline+"\n"
        headerline=headerline+"="*80+"\n"
        result=headerline+str(c)
    else:
        result=str(c)

    return result        
         
       
