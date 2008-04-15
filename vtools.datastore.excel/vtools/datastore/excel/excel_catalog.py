""" Catalog class for a excel file data, for the moment, it is virtually
    an empty class.
"""
## Standard Library imports
import re,os.path
from string import strip

## vtools import
from vtools.datastore.catalog import Catalog
from vtools.datastore.data_reference import DataReference

## local import
from excel_constants import *

class ExcelCatalog(Catalog):

    """ A simple catalog class for excel data source,no fancy capacity
        for the time being.
    """
 
    ########################################################################### 
    # Private traits.
    ###########################################################################
    def __init__(self,excel_file_path):

        if os.path.isfile(excel_file_path):
            self._excel_file_path=os.path.abspath(excel_file_path)
        else:
            raise ValueError("input excel path is invalid.")

 
    ########################################################################### 
    # Public interface.
    ###########################################################################
    

    ########################################################################### 
    # Protected interface.
    ###########################################################################
    
    def _remove(self,entry):
        raise NotImplementedError("This function has not be implemented yet.")
    def _modify(self,old_entry,new_entry):
        raise NotImplementedError("This function has not be implemented yet.")
    def _copy(self, entry):
        raise NotImplementedError("This function has not be implemented yet.")
    
    def _get_data_reference(self,entry):
        """ Based on given a column range of excel worksheet,
        generate a data ref.
        """

        raise  NotImplementedError("This function has not be implemented yet.")
        
    def data_references(self,selector,excelformatentry):
        """ Excel implementaiton of create data ref based on
            selector and format setting, different from other
            type of data sources.
        """
        raise NotImplementedError("This function has not be implemented yet.")
    
##        id=EXCEL_DATA_SOURCE
##        source=self._excel_file_path
##        view=""
##        selector=selector 
##        extent=""
##        dref=DataReference(id,source=source,view=view,\
##        selector=selector,extent=extent)
##        dref.props["ts_type"]=excelformatentry.ts_type
##        dref.props["time"]=excelformatentry.time
##        dref.props["header"]=excelformatentry.header
##        dref.props["write_times"]=excelformatentry.write_times
##        dref.props["interval"]=excelformatentry.interval
##        dref.props["start"]=excelformatentry.start
##                
##        return [dref]

    def _filter_catalog(self,selector):
        """ For the time being only generate a reference
        based on selector untouched.  
        """       

        return self  

    ########################################################################### 
    # Private interface.
    ###########################################################################     

    def _parse_worksheet(self,s):
        """ parse out name of excel worksheet in selector s such as
            s="worksheet=hydro_flow;range=A1:E277;"
        """
        selector=s.upper()
        ## To match patter like worksheet=***;
        r1=re.compile("(WORKSHEET=)(.*?);")
        s1=r1.search(selector)
        if s1:
            worksheet=s1.group(2)
            return worksheet
        else:
            raise ValueError("No worksheet name given in "
                             "excel data selector.")
        

    def _parse_column_range(self,s):
        """ parse out range within excel worksheet in selector s
            such as s="worksheet=hydro_flow;range=A1:E277;"
        """
        selector=s.upper()
        ## To match patter like range=***;
        r1=re.compile("(RANGE=)(.*?);")
        s1=r1.search(selector)
        if s1:
            rg=s1.group(2)
            return self._analyze_range(rg)
        else:
            raise ValueError("No range given in"
                             " excel data selector.")

    def _analyze_range(self,rg):
        
        """ analyze info within range string return list of
             selected columan with its interval range as string.
             such as [(A7:A109),(B7:B109)].
        """

        rg=strip(rg)
        rr=re.compile(r"([A-Z]*?)([0-9]*?)(:)([A-Z]*)([0-9]*)")
        sg=rr.match(rg)

        if sg:
            start_col=sg.group(1)
            start_index=sg.group(2)
            end_col=sg.group(4)
            end_index=sg.group(5)

            if not (start_col in EXCEL_COLUMN_NAME) or\
               not (end_col) in EXCEL_COLUMN_NAME:
                raise ValueError("Invalid given worksheet column name.")
                
            i1=EXCEL_COLUMN_NAME.index(start_col)
            i2=EXCEL_COLUMN_NAME.index(end_col)
            ranges=[]

            for a in EXCEL_COLUMN_NAME[i1:i2+1]:
                ranges.append(a+str(start_index)+":"+a+str(end_index))
            return ranges                
        else:
            raise ValueError("no range info is given in excel selector.")
        
         
         

               
    
    





    
        



  
        
