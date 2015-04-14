
# Standard Library imports
from string import split,strip
import re

class DataReference(object):

    """ Class maintain a reference a time series in plain language.

    """
    
    ########################################################################### 
    # Object interface.
    ###########################################################################
    
    def __init__(self,id,source=None,view=None,selector=None,extent=None):
        """
           All input of initailizing function of DataReference are strings

           For instance: a HDF reference: id="vtools.datastore.hdf5.HDF5Service",\
           source='D\data\test.h5,view='tidalfile',selector='\data\flow\channel',\
           extent='location=channel 1;time_window=(01/01/1991,02/02/2000);variable\
           =flow'
        """

        self.source=source  # File path /connection
        self.selector=selector  # Record path within source
        self.source_type_id=id 
        self.extent=extent
        self.view=view
        self.decoration=None ## reserved locations for future extending purposes.
        
    def __repr__(self):
        
        return 'DataReference(id=%s,source=%s,view=%s,selector=%s,extent=%s)'\
                %(self.source_type_id,self.source,self.view,self.selector,self.extent)
                
    def __str__(self):
        
        return 'source_type:%s,data_source:%s,data_view:%s,data_selector:%s,extent:%s'\
                %(self.source_type_id,self.source,self.view,self.selector,self.extent)
        
    ########################################################################### 
    # Public interface.
    ###########################################################################

    def extents(self):

        """ Parse extent string and return a list of tuples contain each exent
            element's name and value in strings
        """
        
        extent=self.extent

        if not extent:
            raise ValueError("Warning: this data reference doesn't \
            contain extent information.")
        
        extlist=split(extent,';')
        element_list=[]
        for elestr in extlist:
            elestr=strip(elestr)
            if elestr=="":
                continue
            sublist=split(elestr,'=')
            
            if ('time_window'  in elestr.lower() )\
               or ('timewindow' in elestr.lower()):
                range_re=re.compile(r'\((.*?)[,](.*?)\)')
                range_match=range_re.match(strip(sublist[1]))
                stime=range_match.group(1)
                etime=range_match.group(2)
                element_list.append((strip(sublist[0]),(stime,etime)))                    
            else:
                val=strip(sublist[1])
                ## if val represent number,try to parse it
                try:
                    if '.' in val:
                        val=float(val)
                    else:
                        val=int(val)
                except:
                    pass
                      
                element_list.append((strip(sublist[0]),val))
        return element_list

##############################################           
## Public Factory function.
##############################################
def DataReferenceFactory(id,source=None,view=None,\
                         selector=None,extent=None):

    return DataReference(id,source,view,\
                         selector,extent)
            
            

        

        
    



    
