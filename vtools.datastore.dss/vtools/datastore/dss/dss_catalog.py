#standard libary import
import os, sys,re
from copy import copy,deepcopy
from datetime import datetime
#import pdb 

#vtools import
from vtools.datastore.catalog import Catalog,CatalogEntry
from vtools.datastore.catalog_schema import CatalogSchemaItem
from vtools.datastore.data_reference import DataReference
from vtools.datastore.dimension import RangeDimension
from vtools.data.vtime import time_interval
from vtools.data.constants import *


#pydss import
from pydss.hecdss import DssFile,open_dss,zgpnp

#dateutil import
import dateutil.parser

#scipy import
from scipy import zeros

#traits import
from enthought.traits.api import Bool,Int

#local import 
from vtime_dss_utility import string_to_dss_julian_date,uncondensed_Dparts
from dss_constants import DSS_DATA_SOURCE

__all__=["DssCatalogError","DssCatalog"]

class DssCatalogError(Exception):
    """ Exception tracking error happend in dss catalog operations"""

    ########################################################################### 
    # Object interface.
    ###########################################################################  
    def __init__(self,st="Error in cataloging dss file"):

        self.description_str=st
        
    def __str__(self):

        return self.description_str
        

## Block size dictionary, used for adjust etime later.
one_day=time_interval(days=1)
one_month=time_interval(months=1)
one_year=time_interval(years=1)
one_decade=time_interval(years=10)
one_century=time_interval(years=100)

block_dic={"1MIN":one_day,"2MIN":one_day,"3MIN":one_day,\
           "4MIN":one_day,"5MIN":one_day,"10MIN":one_day,\
           "15MIN":one_month,"20MIN":one_month,"30MIN":one_month,\
           "1HOUR":one_month,"2HOUR":one_month,"3HOUR":one_month,\
           "4HOUR":one_month,"6HOUR":one_month,"8HOUR":one_month,\
           "12HOUR":one_month,"1DAY":one_year,"1WEEK":one_decade,\
           "1MON":one_decade,"1YEAR":one_century,"IR-DAY":one_day,\
           "IR-MONTH":one_month,"IR-YEAR":one_year,"IR-DECADE":one_decade}

NUM_OF_CHANGES_CAUSE_AUTO_UPDATE=10


class DssCatalog(Catalog):
    """ Contains a number of DSS metadata entries"""

    ########################################################################### 
    # Public interface.
    ###########################################################################
    need_update=Bool(False) ## if or not need to udpate database
    changes=Int(0)
    ########################################################################### 
    # Object interface.
    ###########################################################################
    
    def __init__(self,dss_file_path,schema,service,records_iterator=None,editable=True):
              
        
        super(DssCatalog,self).__init__()
        self._dss_file_path=dss_file_path
        self._schemalst=schema
        self._condensed_catalog=True
        self._orginial_service=service
        self.need_update=False
        self.changes=0
        self._editable=editable
        
        # List of tuples storing D parts before condensing
        # if no condense, just a empty list.
        self._uncondensed_D_parts=[]

        if records_iterator: 
            self._populate_entries(records_iterator)
            self.entry_dimension_map=self._built_entry_dimension_map()

    ##def __del__(self):
        ## Clean up its records in db.       
        ## self._orginial_service.remove_dssfile(self._dss_file_path)
    ###########################################################################
    ## public methods
    ###########################################################################
    def set_editable(self):
        self._editable=True
    def set_uneditable(self):
        self._editable=False
    ########################################################################### 
    # Protected interface.
    ###########################################################################

    def _reload(self):

        if not self._editable:
            raise DssCatalogError("This catalog is not editable!")

        service=self._orginial_service
        records=service.reload_dss_records(self._dss_file_path)
        self._entries=[]
        self._populate_entries(records)
        self.entry_dimension_map=self._built_entry_dimension_map()
        self.need_update=False
        self.changes=0
        
    def _remove(self,entry):
        """ Remove catalog entry from catalog, this will also remove data
            associate with the entry.
        """
        if not self._editable:
            raise DssCatalogError("This catalog is not editable!")
        
        del self._entries[entry.index]
        
        #rangedimension=self.entry_dimension_map[entry.index]
        #self.entry_dimension_map.remove(rangedimension)
        del self.entry_dimension_map[entry.index]
        
        # If condensed,remove its d parts list also.
        dparts=[]
        if self._condensed_catalog:
            d_parts=self._uncondensed_D_parts[entry.index]
            self._uncondensed_D_parts.remove(d_parts)
            d0=d_parts[0]
            dt=d_parts[-1]
            dparts=uncondensed_Dparts(entry.item("E"),d0,dt)
        
        # Reformarize index of existing entries
        # behind this one.
        # index of entry is its location 
        # in catalog entries list.
        index=entry.index
        for i in range(index,len(self._entries)):
            self._entries[i].index=i
            
        path=self._path_from_entry(entry)
        dss_file_path=self._dss_file_path
        dssfile=open_dss(dss_file_path)

        if self._condensed_catalog:            
            con_path=path
            entry_index=entry.index

            for d in dparts:
                path=con_path.replace('//','/'+d+'/')
                lfound=dssfile.zdelet(path)                
        else:
            lfound=dssfile.zdelet(path)

        del dssfile
        
        if not(lfound):
            raise DssCatalogError('fail to delete'
            ' data in deleting catalog entry')
        
        self.changes=self.changes+1
        
        
    def _modify(self,old_entry,new_entry):
        """ Modify a entry from catalog with a new one.

            This function changes the metadata of
            catalog entry.
        """

        if not self._editable:
            raise DssCatalogError("This catalog is not editable!")
        
        # Force new entry to use old entry index value.
        index=old_entry.index
        new_entry.index=index      
        self._entries[index]=new_entry
                
        old_path=self._path_from_entry(old_entry)
        new_path=self._path_from_entry(new_entry)
        dss_file_path=self._dss_file_path
        dssfile=open_dss(dss_file_path)

        if self._condensed_catalog:            
            con_oldpath=old_path
            con_newpath=new_path
            d0=self._uncondensed_D_parts[index][0]
            dt=self._uncondensed_D_parts[index][-1]
            dparts=uncondensed_Dparts(old_entry.item("E"),d0,dt)

            for dd in dparts:                
                old_path=con_oldpath.replace('//','/'+dd+'/')
                new_path=con_newpath.replace('//','/'+dd+'/')
##                (nhead,ndata,lfound)=dssfile.zcheck(old_path)
##                if lfound:
                lfound=dssfile.zrenam(old_path,new_path)
##                    if not(lfound):
##                        raise DssCatalogError\
##                     ('fail to rename data path %s with %s during'
##                      ' catalog entry modification'%(old_path,new_path))
                
        else:
            lfound=dssfile.zrenam(old_path,new_path)
            if not(lfound):
                raise DssCatalogError('fail to rename data'
                'path during catalog entry modification')

        del dssfile    
        self.changes=self.changes+1
        
    def _copy(self,entry):
        """ Copy data pointed by and metatdata of entry,
            return a new entry.

            This function will copy the data associated with
            entry to the path pointed by new entry.
        """
        
        if not self._editable:
            raise DssCatalogError("This catalog is not editable!")
        
        path1=self._path_from_entry(entry)

        # Create a empty entry first
        entry2=CatalogEntry(self.schema())

        # Copy metadata of entry to entry2 according to
        # items defined by schema
        for schemaitem in self.schema():
            item_name=schemaitem.get_element('name')
            meta_value=entry.item(item_name)
            #pdb.set_trace()
            if item_name=='A': # Suffixed A part value by a '_copy'
                meta_value=meta_value+'_COPY'
            entry2.add_item(item_name,meta_value)

        # Copy dimension info into new entry also
        for dimension in entry.dimension_scales():
            entry2.add_dimension_scale(deepcopy(dimension))
        
        self._entries.append(entry2)
        entry2.index=len(self._entries)-1
        
        # Append dimension selection map.
        if entry2.dimension_scales():
            time_exent=RangeDimension(entry2.dimensions_scales()[0].get_range())
            self.entry_dimension_map.append(time_exent)
        else:
            self.entry_dimension_map.append(None)

        # Append uncondensed D parts to inner list if condensed
        if self._condensed_catalog:
            dparts=self._uncondensed_D_parts[entry.index]
            self._uncondensed_D_parts.append(deepcopy(dparts))
    
        path2=self._path_from_entry(entry2)
        dss_file_path=self._dss_file_path
        dssfile=open_dss(dss_file_path)        
        buff1=range(750)
        buff2=range(100)
        
        if self._condensed_catalog:            
            con_path1=path1
            con_path2=path2
            entry_index=entry.index
            d0=self._uncondensed_D_parts[entry_index][0]
            dt=self._uncondensed_D_parts[entry_index][-1]
            dparts=uncondensed_Dparts(entry.item("E"),d0,dt)
            for d in dparts:
                path1=con_path1.replace('//','/'+d+'/')
                path2=con_path2.replace('//','/'+d+'/')
                istat=dssfile.zcorec(dssfile,path1,path2,buff1,750,buff2,100)
                
        else:
            istat=dssfile.zcorec(dssfile,path1,path2,buff1,750,buff2,100)

        del dssfile
        
        if istat>0:
            raise DssCatalogError('fail to copy data during catalog entry copying')

        
        self.changes=self.changes+1
        
        return entry2
    
    def _add(self,new_entry,data):
        """ Add a new record of data based on new_entry path.        
            Todo, it is not decided yet if this func should be here.
        """

        if not self._editable:
            raise DssCatalogError("This catalog is not editable!")
        
        new_path=self._path_from_entry(new_entry)
        self._entries.append(new_entry)
        #self._add(new_path,data)

    def _get_data_reference(self,entry,parameter):
        """ Create a data reference of plain text style based on a catalog entry.
            here parameter has only one option as a tiven time window string within
            the data path, etc. "time_window=(01/23/1990 1200,02/24/1997 1100)"  
        """              
        selector=self._path_from_entry(entry)

        if not entry.fully_loaded:
            self._load_entry_full(entry.index)
                
        id=DSS_DATA_SOURCE
        source= self._dss_file_path        
        extent=""
              
        ## Use rangedimension stored in map to built extent string
        ## all the data will be returned.
        if parameter==None:
            time_extent_selection=self.entry_dimension_map[entry.index]
            (stime,etime)=time_extent_selection.get_range()
            ## Adjust etime according to data block size(depends on time
            ## interval for regular ts or from E for irregular ts).This
            ## processing will make sure all data can be returned, although
            ## some extra space is provided when using this reference in
            ## retrieving data. dssregularTS_to_TimeSeries and dssirregularTS_to_TimeSeries
            ## will remove those extra space (in module vtools.datastore.
            ## .dss.vtime_dss_utility.py).
            # etime=self._adjust_etime(etime,selector)
            ## So time string is in format of month/day/year hours mintues
            #stime=stime.strftime('%m/%d/%Y %H%M')
            #etime=etime.strftime('%m/%d/%Y %H%M')
            stime=str(stime)
            etime=str(etime)
            extent="time_window=("+stime+","+etime+")"
        ## else time extent is given, use it.
        elif type(parameter)==type(" "):
            if not "time_window" in parameter:
                parameter="time_window="+parameter
            extent=parameter
        elif type(parameter)==tuple:
            start=parameter[0]
            end=parameter[1]
            if type(start)==str and type(end)==str:
                extent="time_window=("+start+","+end+")"
            elif type(start)==datetime and type(end)==datetime:
                extent="time_window=("+start.strftime('%m/%d/%Y %H:%M')\
                        +","+end.strftime('%m/%d/%Y %H:%M')+")"
            else:
                raise ValueError("invalid time window input")
        else:
            raise ValueError("invalid time window input")
        
        return DataReference(id,source,'',selector,extent)

    def _schema(self):
       
        return self._schemalst

    def _filter_catalog(self,selector):
        """ dss implementaion of catalog filtering.
            selector only contains path info.
        """
                
        if os.path.isfile(selector):
            f=file(selector)
            select_pattern=map(self._parse_pattern,\
            [p.strip() for p in f if p.strip()])
        else:
            select_pattern=self._parse_pattern(selector)        
        
        qualified_entry_indexes=[ e.index for e in self._entries \
                                if self._selected(e,select_pattern)]

        entries=[copy(self._entries[index]) for index \
                 in qualified_entry_indexes ]
        
        for i in range(0,len(entries)):
            entries[i].index=i
        
        uncondensed_dparts=[copy(self._uncondensed_D_parts[index]) \
                            for index in qualified_entry_indexes ]
                            
        filtered_catalog=DssCatalog(self._dss_file_path,self._schemalst,\
                                    self._orginial_service,editable=False)
        for i in range(0,len(entries)):
            entries[i].catalog=filtered_catalog
            
        filtered_catalog._entries=entries
        filtered_catalog._uncondensed_D_parts=uncondensed_dparts
        filtered_catalog.entry_dimension_map=filtered_catalog.\
        _built_entry_dimension_map()
        return filtered_catalog

    def _load_entry_full(self,index):
        """ dss implementation of loading entry in full."""
    
        entry=self._entries[index]
        
        if self._entries[index].fully_loaded:
            return
        
        path=self._path_from_entry(entry)
        source= self._dss_file_path
        dparts=self._uncondensed_D_parts[index]
        (time_window,header_dic,unit,dtype)= \
        self._orginial_service.load_record_property(path,dparts,source)
        time_extent=RangeDimension(time_window)
        self._entries[index].add_dimension_scale(time_extent)
        
        ## insert item within header_dic into entry
        for header_label,header_value in header_dic.items():
            self._entries[index].add_item(header_label,header_value)

        ## insert unit and type also.
        self._entries[index].add_item(UNIT,unit)                      
        self._entries[index].fully_loaded=True
        self.entry_dimension_map[index]=time_extent
                    
    ########################################################################### 
    # Private interface.
    ###########################################################################
    
    def _populate_entries(self,records_iterator):

        index=0
        for record in records_iterator:
            dic=self._entry_dictionary(record)
            catalogentry=CatalogEntry(self.schema(),self)
            Dpart=dic["D"] ## Dpart contains all D part seperated by ","
            Dlist=Dpart.split(",")
            for key in dic.keys():
                if key=="D": 
                    dd=Dlist[0]+"-"+Dlist[-1]
                    catalogentry.add_item(key,dd)
                    catalogentry.add_trait(key,dd) 
                else:
                    catalogentry.add_item(key,dic[key])
                    catalogentry.add_trait(key,dic[key]) 
            catalogentry.index=index
            index=index+1
            self._entries.append(catalogentry)
            self._uncondensed_D_parts.append(Dlist)
            

    def _built_entry_dimension_map(self):
        """ Built a map of time extent selction
            for each entry in catalog.
        """
        map=[]
        for entry in self._entries:
            if entry.fully_loaded:
                time_exent=RangeDimension(\
                entry.dimensions_scales()[0].get_range())
                map.append(time_extent)
            else:
                map.append(None)           
        return map  
                            
    def _entry_dictionary(self,record):
        """ Generate a entry element dictionary
            and a rangedimension for time window
            from a record withdrawn from database
            accroding to schema.
        """

        adic={}
        
        for schema_entry in self.schema():
            name=schema_entry.get_element('name')
            if schema_entry.has_element('column'):
                adic[name]=record[schema_entry.get_element('column')]
        
        if not("IR-" in adic["E"]):
            adic[INTERVAL]=adic["E"]
        else:
            adic[INTERVAL]="N/A"
            
        return adic   

    def _path_from_entry(self,entry):
        """ Compose dss record path from a entry. """
        
        partlist=["A","B","C","D","E","F"]
        path="/"
        for i in range(0,len(partlist)):

            partname=partlist[i]

            if entry.has_item(partname):
                if (partname=="D"): #and ("-" in entry.item("D")) :
                    # Always condensed entry, omit time part D 
                    path=path+"/"
                else:
                    path=path+entry.item(partname)+"/"
            else:
                path=path+"/"
        
        return path

    def _parse_time_window(self,selector):
        """ Search and return the time window info stored in
            selector string if no time window is given, None
            will be return, latter means all data returned.
        """
        selector=selector.upper()
        if "TIMEWINDOW" in selector:
            window_pattern=re.compile(r"TIMEWINDOW=.*?\)")
        elif "TIME_WINDOW" in selector:
            window_pattern=re.compile(r"TIME_WINDOW=.*?\)")
        else:
            return None
        
        mw=window_pattern.search(selector)
        if mw:
            return mw.group(0)
        else:
            return None

    def _parse_pattern(self,selector):
        """ Given selector string, return a regular
            expression to match data path. Assuming
            selector has a path sepcification
            in wildcard, such as path=/HIST/RSAC*/EC*//15MIN//;.
            If no path sepcification given, a mach pattern of
            /.*?/.*?/.*?/.*?/.*?/.*?/ will be return, which
            matchs all records.

            A support of selection pattern like "A=HIST,B=RSAC*,C=EC*,
            TIMEWINDOW=(10/2/1997 1200, 7/4/1998 1315)" was added.
        """
        if not selector:
            return re.compile("/.*?/.*?/.*?/.*?/.*?/.*?/")
        selector=selector.upper()
        ## To match pattern like /*/*/*/*/*/*/;
        r1=re.compile(r"(/)(.*/)?(;|$)")
        s1=r1.match(selector)
        if s1:
            pat=s1.group(2)
            pat="/"+pat
        else: ## try to use zgpnp to find out A,B,...
            nparts=zeros(6)
            selector=selector.replace(';',',')
            ca,cb,cc,cd,ce,cf,nparts=\
            zgpnp(selector,nparts)
            if not ca:
                ca=r"*"
            if not cb:
                cb=r"*"
            if not cc:
                cc=r"*"
            if not cd:
                cd=r"*"
            if not ce:
                ce=r"*"
            if not cf:
                cf=r"*"
            
            pat="/"+ca+"/"+cb+"/"+cc+"/"\
                 +cd+"/"+ce+"/"+cf+"/"
            
        ## Generate regular expression.
        pat=self._adjust_pattern(pat)            
        return re.compile(pat)
    
    def _adjust_pattern(self,pat):
        """ Adjust pattern match string, make it in format
            of regular expression.
        """
        ## replace *
        new_pat=pat.replace("*",".*?")
        new_pat=new_pat.replace("//","/.*?/")
        
        ## replace possible +, -
        new_pat=new_pat.replace("+","\\+")
        new_pat=new_pat.replace("-","\\-")
        return new_pat
        
    def _selected(self,entry,selector_pattern):
        """ Decide if a catalog entry conforms to criteria set by
            selector.
        """
        
        path=self._path_from_entry(entry)

        if type(selector_pattern)==list:
            matched=False
            for s in selector_pattern:
                if s.match(path):
                    matched=True
                    break
            return matched
        else:
            if selector_pattern.match(path):
                return True
            else:
                return False

    def _adjust_etime(self,etime,path):

        """ move etime from start of data block to the end of
            data block according to the path given.
        """        
        
        pathlist=path.split("/")
        epart=pathlist[5]
        block_size=block_dic[epart]
        return etime+block_size


    def _update_db(self):
        """ cause service update db records about source file."""
        self._orginial_service.update_db(self._dss_file_path)



             
        
        
        

    



        





    
    
        

    
            
      
          
      
        
        


            


        
            

            

        
        

    
