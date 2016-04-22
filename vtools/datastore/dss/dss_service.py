# stanadard library import
from sys import argv
import os.path
from shutil import rmtree
from os import mkdir,rmdir
from string import split,strip,rstrip
import re


#scipy import
from scipy import zeros,concatenate

#vtools import 
from vtools.datastore.service import Service
from vtools.data.timeseries import TimeSeries,its
from vtools.datastore.catalog_schema import CatalogSchemaItem
from vtools.data.vtime import parse_interval,number_intervals,\
     increment


#dateutil import
import dateutil.parser

#pydss import
from pydss.hecdss import open_dss,zfver
from pydss.hecdss import DssFile,zrdpat,open_dss,zset
from pydss.hecdss import zopnca,zrdcat
from pydss.hecdss import zustfh,zstfh
from pydss.fortranfile import fortran_file,FortranFile


#vtools import
from vtools.data.constants import *
from vtools.data.timeseries import rts
from vtools.data.vtime import parse_interval,\
     parse_time, round_time,align
from vtools.datastore.data_reference import *
#from vtools.debugtools.timeprofile import debug_timeprofiler

from vtools.datastore.dss.dss_catalog import DssCatalog
from vtools.datastore.dss.dss_constants import *
from vtime_dss_utility import dss_rts_to_ts
from vtime_dss_utility import dss_its_to_ts
from vtime_dss_utility import datetime_to_dss_julian_date
from vtime_dss_utility import validate_rts_for_dss
from vtime_dss_utility import validate_its_for_dss
from vtime_dss_utility import discover_valid_rts_start,\
     discover_valid_rts_end
from vtime_dss_utility import dss_julian2python,interval_to_D,valid_dss_interval_dic_in_delta


__all__=["DssAccessError","DssCatalogServiceError","DssService"]

class DssAccessError(Exception):

    def _init_(self,st="Error in dss data source"):

        self.description_str=st
        
    def _str_(self):

        return self.description_str

class DssCatalogServiceError(Exception):

    def _init_(self,st="Error in cataloging dss file"):

        self.description_str=st
        
    def _str_(self):

        return self.description_str

class DssService(Service):
    """" Service to cataloging dss file, access and edit dss data"""


    ## static method to decide whether a source can be served.

    def serve(source):
        return source.lower().endswith('.dss')

        
    serve=staticmethod(serve)

    ########################################################################### 
    # Public interface.
    ###########################################################################

    first_initialization=True
    database_file_dir=""
    db_file_use_number=0 ## how many source I have cataloged so far in this run

    has_dss_catalog_table=False
    # the last dssfile index used
    dss_file_index_last=0  
    dss_file_index_used=[]

    identification=DSS_DATA_SOURCE

    ############################################################################
    # Private member
    ############################################################################
    # map dss file pathes to fileid and modify time
    _dss_file_opened = {}
    # map dss files id to their catalog
    _dss_catalogs    = {}
    _num_db_clean=0
    
    def load_record_property(self,path,dparts,source):
        """ This public sub should be only be called by
            dss catalog only, to load complete properties
            of a record.

            path is in condenseded form and dparts is
            a tuple contain all the d parts of the record.
        """        

        dssf=open_dss(source)       
        
        firstD=dparts[0]
        firstpath=path.replace('//','/'+firstD+'/')
        ## find out type of record.

        (idtype,d1,d2)=self._retrieve_data_type(dssf,firstpath)

        if (idtype==REGULARTS) or (idtype==REGULARTS_DOUBLE):
            (time_window,header,unit,type)=\
            self._retrieve_rts_prop(dssf,path,dparts)
        elif idtype==IRREGULARTS:
            (time_window,header,unit,type)=\
            self._retrieve_its_prop(dssf,path,dparts)
        else:
            raise ValueError("Unimplemented record type: %i path: %s"%(idtype,path))
        dssf.close()
        del dssf
        return (time_window,header,unit,type)

    def remove_dssfile_catalog(self,dss_file_path):
        """
           remove all the catalog information about a dss file,
           this function can be used to reload catalog when it 
           placed before a get_catalog function
        """
        self._remove_dssfile_catalog(dss_file_path)

    def update_db(self,dss_file_path):
        """ update db record about dss file."""
        self._update_dss_file_catalog(dss_file_path)
        
    
        
        
       
    ########################################################################### 
    # Object interface.
    ###########################################################################

    def __init__(self):
        """ Major task is to create a temp db file to store
        catalog entries.
        """
        
        if DssService.first_initialization:
            DssService.first_initialization=False
            
        ## following line must be excuted for the
        ## sake of making ts-header unstuff func
        ## to work correctly.
        zset('MLEVEL','',0)


    ########################################################################### 
    # Protected interface.
    ###########################################################################
    def _get_catalog(self,dss_file_path):
        """ Return a catalog of dss file."""
        try:
            info=self._dss_file_opened[dss_file_path]
        except:
            info = ()    
        
    
        if len(info) != 0: ## info is in form of (1,2222344),2222344 is time, 1 is f index
            last_modified_time=info[1]
            #print last_modified_time,os.stat(dss_file_path)[8]
            ##########################################
            ##              comment and observation                                       ##
            ## This decision is done by comparing the update time of a dss file           ##
            ## stored within db to its updatetime returned by windows query on            ##
            ## file property, if they are different, catalog will redone to               ##
            ## refelect the change that might happen from last time. When they            ##
            ## same, just used info stored in db to save time. But it may fail,           ##
            ## sometimes when last modification on dss file is very close to              ##
            ## current time, for instance doing a catalog modification right              ##
            ## after some saving ts into dss, like in test_all_module(when                ##
            ## test_modify right after test_save_data, sometimes two times are            ##
            ## the same,even file is different already).No solution currrently            ##
            #########################################
            #if not(last_modified_time==os.stat(dss_file_path)[8]):
            self._remove_dssfile_catalog(dss_file_path)
            return self._cataloging_dss_file(strip(dss_file_path))
            #else:
            #    return self._dss_catalogs[info[0]]
        else:
            return self._cataloging_dss_file(strip(dss_file_path))


    def _generate_schema(self,table_column_index_map):

        """ Create the schema dictionary  catalog rows,thus 
            column can be accessed by name through schema dic.
        """
        schema=[]
        
        adic={"name":"A","column":table_column_index_map["A"],"editable":True,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))
        adic={"name":"B","column":table_column_index_map["B"],"editable":True,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))
        adic={"name":"C","column":table_column_index_map["C"],"editable":True,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))
        adic={"name":"D","column":table_column_index_map["D"],"editable":False,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))
        adic={"name":"E","column":table_column_index_map["E"],"editable":False,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))
        adic={"name":"F","column":table_column_index_map["F"],"editable":True,\
              "role":"identification","element_type":""}
        schema.append(CatalogSchemaItem(adic))       
        adic={"name":"TIME_WINDOW","value":"Input a valid time","editable":True,\
              "role":"extent","element_type":"dimension_scale"}
        schema.append(CatalogSchemaItem(adic))

        return schema
    
    def _get_data(self,data_ref,overlap):
        """ Return time series referenced by data_reference.

            note: different to standard dss lib retrieving
            function, which retrieve the values without
            the end of time window of regular ts, this function
            will return it.
        """

        # Source file.
        fname=getattr(data_ref,"source")
        # Dss path with the source.
        path=getattr(data_ref,"selector")
        ## a quick fix for null of a part 
        if "(null)" in path:
            path=path.replace("(null)","")
            data_ref.selector=path
        # Create dss file object.
        dssf=open_dss(fname)

        # Try to use check if path exists in source
        # if full data path is given as style of "/A/B/C/D/E/F/ ".
        plist=split(path,"/")

        # If it is a full path, check if it exist, if not throw exception
        # to save time.
        if plist[4]:
            (nsize,lexist,cdtype,idtype)=dssf.zdtype(path)
            if not(lexist):
                del dssf
                raise DssAccessError("record %s doesn't exist "%path)
        # Maybe it is a path with D omitted, continue to find out
        # is it a irregular or regular time series based on part E.
        else:
            e=plist[5]
            if "IR-" in e:
                cdtype="ITS"
            else:
                cdtype="RTS"
                
        del dssf
        
        if cdtype=="RTS":
            ## overlap option is not available for rts
            if (overlap!=None):
                raise ValueError("overlap option is not available for regular time series") 
            return self._retrieve_regularTS(data_ref)
        elif cdtype=="ITS":
            if (overlap==(0,0))or (overlap==(1,1)) \
               or(overlap==(1,0)) or (overlap==(0,1))or(overlap is None):
                return self._retrieve_irregularTS(data_ref,overlap)
            else:
                raise ValueError("incorrect overlap format") 
        else:
            raise DssAccessError\
                  ("Not recorgizable time series in dss data reference.")

    
    def _add_data(self,data_reference,ts):
        """ Save a timesereis to the place referenced by data_reference.
        """
        
        if type(ts)==TimeSeries:            
            ## stuff header here.
            clabels=[]
            citems=[]
            
            if ts.is_regular():
                (flags,lflags,cunits,ctype,cdate,ctime,cprops)=\
                validate_rts_for_dss(ts)
                
                if cprops:                   
                    for key in cprops.keys():
                        val=cprops[key]
                        clabels.append(key)
                        citems.append(val)
                
                headu,nheadu=self._stuff_header(clabels,citems)
                ## here we use cdate and ctime to parse new start time and end time
                ##for we may move start time point a interval to comform dss storage
                ##format
                stime=parse_time(cdate+" "+ctime[0:2]+":"+ctime[2:4])
                etime=stime+(ts.end-ts.start)
                self._check_path_ts(data_reference,ts)
                nvals=len(ts)
                values=ts.data
                self._save_regularTS_extend(data_reference,stime,etime,\
                                            nvals,values,ts.interval,flags,\
                                            lflags,cunits,ctype,headu,\
                                            nheadu)                
            else:
                itimes,flags,lflags,jbdate,cunits,ctype,cprops=\
                validate_its_for_dss(ts)
                if cprops:                   
                    for key in cprops.keys():
                        val=cprops[key]
                        clabels.append(key)
                        citems.append(val)
                
                headu,nheadu=self._stuff_header(clabels,citems)                
                
                nvals=len(ts)
                values=ts.data
                self._save_irregularTS_extend(data_reference,itimes,\
                                              values,nvals,jbdate,flags,\
                                              lflags,cunits,ctype,headu,\
                                              nheadu)

            ## update catalog if applicable.
            dss_file_path=data_reference.source
            self._update_dss_file_catalog(dss_file_path)   


    ########################################################################### 
    # Private interface.
    ###########################################################################
                

    def _cataloging_dss_file(self,dss_file_path):

        """ Catalog a dss file sepcified by dss_file_path,
            save records into db.
        """

        # Generate a uniqe index for the dssfile used,
        # class DssFile will prevent a dssfile opened more
        # than once concurrently.       

        index=self._dss_file_index()
        self.dss_file_index=index
        
        self._add_dss_file_record(dss_file_path,index)

        ##### time profile ####
        #debug_timeprofiler.mark("loading catalog for dss file")
        ######################
            
        dtt=self._retrieve_catalog_records(dss_file_path)

        table_column_index_map=self._create_column_index_map()
        schema=self._generate_schema(table_column_index_map)
        ##### time profile ####
        #print 'time at done with create catalog record iter',\
        #      debug_timeprofiler.timegap()
        ######################
        catalog = DssCatalog(dss_file_path,schema,self,dtt)

        self._dss_catalogs[dss_file_path] = catalog
    
        #add the amount of class instance using dababase by one
        self._add_use()

        ##### time profile ####
        #print 'total time in loading catalog info to db',debug_timeprofiler.timegap()
        ######################    
        return catalog
    def _update_dss_file_catalog(self,dss_file_path):
        """ Update the catalog database for file at dss_file_path
            if its info found in db.
        """
        try:
            info=self._dss_file_opened[dss_file_path]
        except:
            info = ""       
        
        if info: 
            self._remove_dssfile_catalog(dss_file_path)
            self._cataloging_dss_file(dss_file_path)

            
    def _remove_use(self):

        if DssService.db_file_use_number>0:
            DssService.db_file_use_number=DssService.db_file_use_number-1

    def _add_use(self):

        DssService.db_file_use_number=DssService.db_file_use_number+1


    def _retrieve_catalog_records(self,dss_file_path):
        """ Retrieve all the catalog entries of a dssfile
            and return them.
        """
        dtt =[]  
        if os.path.exists(dss_file_path):            
            dsdfile=self._open_catalog(dss_file_path)
            dtt=self._read_dsd_file(dsdfile)
            if not dtt:
                raise DssCatalogServiceError\
                      ("%s isn't a valid dss file"%(dss_file_path))
        return dtt
        
    def _read_dsd_file(self,dsd_file_path):        
        dsd=open(dsd_file_path)
        ready_status="ready"
        begin_status="begin"
        read_status="read"
        no_act_status="no act"

        status=no_act_status

        rtag=re.compile(r"( Tag\s*)(?=A Part)")
        rapart=re.compile(r"(A Part\s*)(?=B Part)")
        rbpart=re.compile(r"(B Part\s*)(?=C Part)")
        rcpart=re.compile(r"(C Part\s*)(?=F Part)")
        rfpart=re.compile(r"(F Part\s*)(?=E Part)")
        repart=re.compile(r"(E Part\s*)(?=D Part)")
    
##        rdic={"tag":rtag,"A":rapart,"B":rbpart,"C":rcpart,"F":rfpart,"E":repart}
##        starti={"tag":0,"A":0,"B":0,"C":0,"F":0,"E":0,"D":0}
##        endi={"tag":0,"A":0,"B":0,"C":0,"F":0,"E":0,"D":0}
##        parts={"A":"","B":"","C":"","F":"","E":"","D":""}
##        pre_parts={"A":"","B":"","C":"","F":"","E":"","D":""}

        rdic=[rtag,rapart,rbpart,rcpart,rfpart,repart]
        starti=[0,0,0,0,0,0,0]
        endi=[0,0,0,0,0,0,0]
        parts=["","","","","",""]
        pre_parts=["","","","","",""]
        i0=0
        it=0
        dtt=[]
        nrec=0

        for line in dsd:
            if "A Part" in line and "B Part" in line and "C Part" in line and \
               "D Part" in line and "E Part" in line and "F Part" in line:
                status=ready_status
                for pn in range(6):
                    lpn=len(rdic[pn].search(line).group(1))
                    starti[pn]=lpn
                    endi[pn]=lpn

                starti[0]=0                                    
                for pn in range(1,6):
                    starti[pn]=endi[pn-1]
                    endi[pn]=starti[pn]+endi[pn]
                    
                starti[6]=endi[5]
                
            if line.strip()=="" and status==ready_status:
                status=read_status
            if status==read_status and line.strip() and \
               not line.strip().startswith("*"):
                endi[6]=len(line)
                
                for pn in range(1,7):
                    i0=starti[pn]
                    it=endi[pn]
                    part=line[i0:it].strip()
                    if "- - -" in part:
                        part=pre_parts[pn-1]
                    if pn==6:
                        ## for case if dsd file contain records with missing period
                        ## vista will compile dsd file and add * into after the record
                        part=part.replace("*","") 
                        part=part.replace(" - ",",")
                    
                    parts[pn-1]=part.strip()

                if nrec==0:
                    for pn in range(6):
                        pre_parts[pn]=parts[pn]
                else:
                    if parts[0]==pre_parts[0] and  parts[1]==pre_parts[1] and parts[2]==pre_parts[2]  \
                       and parts[3]==pre_parts[3] and  parts[4]==pre_parts[4]:
                        pre_parts[5]=pre_parts[5]+","+parts[5]
                    else:
                        dtt.append((self.dss_file_index,pre_parts[0],pre_parts[1],pre_parts[2],\
                                pre_parts[5],pre_parts[4],pre_parts[3]))
                        for pn in range(6):
                            pre_parts[pn]=parts[pn]
                nrec=nrec+1
        
        if nrec>0:
            dtt.append((self.dss_file_index,pre_parts[0],pre_parts[1],pre_parts[2],\
                pre_parts[5],pre_parts[4],pre_parts[3]))
        return dtt

    def _open_catalog(self,fpath):
        """" Open or create standard catalog file of the dssfile for retrieving."""
                       
        fpath=fpath.lower()
        fnames=os.path.split(fpath)
        
        dsdpath=os.path.join(fnames[0],fnames[1].replace(".dss",".dsd"))
        dscpath=os.path.join(fnames[0],fnames[1].replace(".dss",".dsc"))
        
            
        cf0=fortran_file()
        cd0=fortran_file()
        cn0=fortran_file(FortranFile.DUMMY_FILE_UNIT)

        ##### time profile ####
        #debug_timeprofiler.mark("opening catalog for dss file")
        ######################
  
        [lopnca,lcatlg,lopncd,lcatcd,nrecs]=zopnca(fpath,cf0,True,cd0,False)
        
        ## lopnca is ture if the catalog file is successfully opened. If 
        ## the file could not be opened, lopnca will be set to false
        if not(lopnca):
            raise DssCatalogServiceError\
                  ("unable to open/create catalog file for dss file %s"%fname)

        ## lcatlg logical variable returned as ture if file contains
        ## valid catalog, if lcatlg is false , zcat should be called to
        ## generated a new catalog of the dss file
        #if not(lcatlg):
      
        dssfile=open_dss(fpath)
        [lcdcat,nrecs]=dssfile.zcat(cf0,cd0,cn0,' ',True,True) 
        ## if lcadcat is true, a condensed catalog is
        ## produced.
        if not(lcdcat):
            print "Warning:condensed catalog is not created for %s"%fpath
  
        dssfile.close()
        del dssfile

        ##### time profile ####
        #print 'time used in opening catalog',debug_timeprofiler.timegap()
        ######################  
        cd0.close()
        cf0.close()
        return dsdpath
    
    def _dss_file_index(self):
        """ Return a unique index for a dss file opened."""

        index=DssService.dss_file_index_last

        while index<DSS_MAX_FILE_NUM:
             if not(index in DssService.dss_file_index_used):
                 break
             index=index+1
             
        if index>=DSS_MAX_FILE_NUM:## if catalogs saved in db is too much,
                                   ## try to empty db, restart a new one.
            index=0
            self._clean_db()
            DssService.dss_file_index_used=[]
            #raise DssCatalogServiceError("not enough index for dss file")
            
        DssService.dss_file_index_used.append(index)
        DssService.dss_file_index_last=index+1
        return index

    def _clean_db(self):
        """ clearn all the entry within db tables."""

        DssService._num_db_clean=DssService._num_db_clean+1
        self._dss_catalogs ={}     
        
        
    def _add_dss_file_record(self,fpath,index):
        """" Insert dssfile path into  DssFile dic."""
        self._dss_file_opened[fpath] = (index,os.stat(fpath)[8])

    def _remove_dss_file_record(self,index):
        """ Remove dssfile path from table DssFile."""
        
        temp_dic = dict((k,v) for k, v in self._dss_file.iteritems() if v[0]==index)
        self._dss_file = temp_dic


    def _remove_paths_record(self,index):
        """ Remove all the paths record of a dssfile specified  by index."""
        temp_dic = dict((k,v) for k, v in self._dss_catalogs.iteritems() if k ==index)
        self._dss_catalogs = temp_dic   
        
    
    def _remove_dss_file(self,index):
        """ Remove all the db record related to a dss file 
            indexed by input index.
        """
        self._remove_dss_file_record(index)
        self._remove_paths_record(index)


    def _remove_dssfile_catalog(self,dss_file_path):
        """ Delete all catalog record about dss_file_path in db"""

        try:
            findex = self._dss_file[dss_file_path][0]
        except Exception,e:
            return
        self._remove_paths_record(findex)
        
    def _create_column_index_map(self):

        """ Return a correspondance between table column index 
            and  catalog entry item name.
        """

        des=(("A"),("B"),("C"),("D"),("E"),("F"))
    
        l=len(des)
        map={}
        for i in range(0,l):
            colname=des[i][0]
            # record entry is like (fileindex,Apart,Bpart, Cpart,...)
            map[colname]=i+1
        return map


    def _retrieve_data_type(self,dssfile,cpath):
        """ Get info about data series type,also return block size."""
        
        [nsize,lexist,cdtype,idtype]=dssfile.zdtype(cpath)
        [nhead,ndata,lfound]=dssfile.zcheck(cpath)

        return [idtype,cdtype,ndata]


    def _retrieve_rts_prop(self,dssf,cpath,dparts):
        """ Retrieve all the prop about a rts record.
            returned extent is stamped at the begining of
            period for aggregated data to observe vtools
            tradition, that is different from what user
            will see use HecdssVue
        """
      
        firstD=dparts[0]
        firstpath=cpath.replace('//','/'+firstD+'/')
        (header_dic,data,cunits,ctype)=\
        self._retrieve_regular_header(dssf,firstpath)
                
        ## find out start datetime
        ce=firstpath.split('/')[5]
        interval=parse_interval(ce)
        cd=firstD
        start=parse_time(cd) 
       
        valid_start=discover_valid_rts_start(data,start,interval)

        ## find out start datetime of ending data block.
        lastD=dparts[-1]
        lastpath=cpath.replace('//','/'+lastD+'/')
        (header_dic,data,cunits,ctype)=\
        self._retrieve_regular_header(dssf,lastpath)       
        end=parse_time(lastD)
        valid_end=discover_valid_rts_end(data,end,interval)
        
        ## dss file stamping time at the the end of 
        ## aggregating period, so valid data period
        ## begins one interval, no such operation
        ## for the end for it is already stamped at the
        ## end of aggregating period
        if ctype in RTS_DSS_PROPTY_TO_VT.keys():
            valid_start=valid_start-interval
        
        
        time_window=(valid_start,valid_end)

        return (time_window,header_dic,cunits,ctype)
       
    
    def _retrieve_blank_header(self):

        return {}
        
    def _retrieve_regular_header(self,dssf,cpath):
        """ Retrieve header information for regular time series."""

        nvals=DSS_MAX_DATA_SIZE
        kheadu=DSS_MAX_HEADER_ITEMS
        #
        try:
            [nvals,vals,flags,lfread,cunits,ctype,headu,nheadu,\
             iofset,icomp,istat]=dssf.zrrtsx(cpath," "," ",nvals,True,kheadu)
        except Exception,e:
            dssf.close()
            raise e

        hdic=self._unstuff_header(headu,nheadu,0)
        return (hdic,vals[0:nvals],cunits,ctype)
##

    def _retrieve_its_prop(self,dssf,cpath,dparts):
        """ Retrieve all the prop about a rts record."""
        
        ## first find out how many data stored in this path
        #total_num=self._find_data_num(cpath,dparts,dssf)
        
        firstD=dparts[0]
        firstpath=cpath.replace('//','/'+firstD+'/')
        (header_dic,time_extent1,cunits,ctype)=\
        self._retrieve_irregular_header(dssf,firstpath)
        start=time_extent1[0]
        
        lastD=dparts[-1]
        lastpath=cpath.replace('//','/'+lastD+'/')
        (header_dic,time_extent2,cunits,ctype)=\
        self._retrieve_irregular_header(dssf,lastpath)
        end=time_extent2[1]
                                        
        time_window=(start,end)
        
        return (time_window,header_dic,cunits,ctype)
    
    def _retrieve_irregular_header(self,dssf,cpath):
        """ Retrieve header information for its, cpath
            must be a complete path (has Dpart).
        """

        nvals=DSS_MAX_DATA_SIZE
        juls=-2
        istime=-2
        jule=-2
        ietime=-2

           
        try:            
            [itimes,vals,nvals,jbdate,flags,lfread,cunits,\
             ctype,headu,nheadu,istat]= \
            dssf.zritsx(cpath,juls,istime,jule,ietime,nvals,False,500,0)
        except Exception,e:
            dssf.close()
            raise e

        header_dic=self._unstuff_header(headu,nheadu,0)
        start=dss_julian2python(jbdate,itimes[0])
        end=dss_julian2python(jbdate,itimes[nvals-1])

        return (header_dic,(start,end),cunits,ctype)
    
        
    def _unstuff_header(self,headu,nheadu,output_form=1):
        """ Return unstuffed labels and item as two string list
            or dic.

            optional output_form decide what kind of format used
            in output header and label, default is as list of two
            string, if set to other, it will be output as dic.
        """        
        ipos=0
        
        clabel=" "*DSS_MAX_HEADER_LEN
        clabels=""
        citems=""
        dic={}

        if nheadu==0:
            return dic
        
        while (ipos>=0):
            try:
                [clabelout,citem,ipos,istat]=zustfh(clabel,0,ipos,headu)
            except Exception, e:
                raise e
            ## for output from zustfh is one-string list  
            clabels=clabels+","+clabelout[0]
            citems=citems+","+citem[0]
            dic[clabelout[0]]=citem[0]

        if output_form==1:
            return [strip(clabels,","),strip(citems,",")]
        else:
            return dic

    def _stuff_header(self,clabels,citems):
        """ Return stuffed headu and nuhead.

            clabels and citems may be list
            of string or array of strings,
            they must be of same length.
        """

        ihead=zeros(500)
        nhead=0
        ihead,nhead,ierr=zstfh(clabels,citems,ihead,0)
        return (ihead,nhead)

    def _multiple_window(self,stime,etime,step):
        
        """ Create iterator of multiple time window for
            data set more than DSS_MAX_RTS_POINTS.
        """
    
        lt=[]
        stimet=stime
        
        while stimet<etime:

            nval=DSS_MAX_RTS_POINTS
            try:
                etimet=increment(
                stimet,step,DSS_MAX_RTS_POINTS)
            except: ## in case when step is big like month, DSS_MAX_RTS_POINTS will
                    ## cause over reasonable year range. Such case should  use
                    ## one windows 
                etimet=etime
                nval=number_intervals(stimet,etimet,step)
            
            
            if etimet>etime:
                etimet=etime
                nval=number_intervals(stimet,etimet,step)
                
            cdate=stimet.date()
            cdate=cdate.strftime('%d%b%Y') 
            ctime=stimet.time()
            ctime=ctime.strftime('%H%M')
            stimet=etimet
            lt.append((cdate,ctime,nval))
            
        return iter(lt)
       
    def _save_regularTS_extend(self,dataref,stime,etime,nvals,values,step,flags=0,\
                                lflags=False,cunits="UND",ctype="UND",headu=0,\
                                nheadu=0,iplan=0,icomp=0,basev=0,lbasev=False,\
                                lhigh=False,iprec=0):
        """ Save values of regular time sereis into dss by calling zsrtsx of pydss."""
        
        path=dataref.selector      
        dss_file_path=dataref.source
        dssf=open_dss(dss_file_path)
        
        windows=None 
        if nvals<DSS_MAX_RTS_POINTS:
            cdate=stime.date()
            cdate=cdate.strftime('%d%b%Y') 
            ctime=stime.time()
            ctime=ctime.strftime('%H%M')           
            windows=[(cdate,ctime,nvals)]
        else:
            windows=self._multiple_window(stime,etime,step)

        if not windows:
            raise DssAccessError("Failure in creating time series storage windows.")

        i=0         
        for (cdate,ctime,nval) in windows:
            valt=values[i:i+nval]
            try:
                istat=dssf.zsrtsx(path,cdate,ctime,nval,valt,flags,lflags,cunits,ctype,\
                                  headu,nheadu,iplan,icomp,basev,lbasev,lhigh,iprec)
                i=i+nval
            except Exception, e:
                dssf.close()
                del dssf
                raise e
            
        dssf.close()
        del dssf
        
    def _save_irregularTS_extend(self,dataref,itimes,values,nvals,jbdate,flags=0,\
                                  lflags=False,cunits="UND",ctype="UND",headu=0,\
                                  nheadu=0,inflag=0):
        """ Save values of irregular time sereis into dss by calling zsitsx of pydss."""        

        
        path=dataref.selector
        dss_file_path=dataref.source
        dssf=open_dss(dss_file_path)
        
        try:            
            istat=dssf.zsitsx(path,itimes,values,nvals,jbdate,flags,lflags,cunits,ctype,\
                              headu,nheadu,inflag)
        except Exception, e:
            del dssf
            raise e

        del dssf

    def _gen_rts_datetime_nval(self,data_ref,dssf):
        """ given a rts data_ref returns the character cdate,ctime
            and number of data contained within time extents.
        """
        ## here we requie data_ref must contain time extent for such a info are needed by
        ##fortran lib dss function to retirieve ts, it is best to generate data_ref from 
        ##a dss catalog,not directly ,to save th work of finding ts time extent
        if not data_ref.extent:
            raise ValueError("data reference doesn't contain time extent.")        
        
        # It is expected dss data_re has only one extent setting
        # extent has value like ('time_window',("'01/11/1991 10:30:00'",\
        # "'02/11/1995 10:30:00'")).
        (dummy,extent)=data_ref.extents()[0]
        
      
        # Start time and end time in string.
        stime=extent[0]
        etime=extent[1]
        # Parse string datetime into datetime instance.
        stime=dateutil.parser.parse(stime)
        etime=dateutil.parser.parse(etime)
        path=data_ref.selector
        time_interval=strip(split(path,"/")[5])        
        step=parse_interval(time_interval)

        if (stime>etime) :
            raise ValueError("input time window start time is behind end time.")
       
        
        ## find out the valid time extent of the ts 
        (juls,istime,jule,ietime,cunits,ctype,lqual,ldouble,lfound)= dssf.ztsinfox(data_ref.selector)
    
        firstfound = False
        lastfound  = False
        
        if juls:
            firstfound = True
            lfound     = True
        
        if jule:
            lastfound  = True
            lfound     = True
            
       
        if(not lfound):
            dssf.close()
            raise DssAccessError("input path is invalid %s"%data_ref.selector)
         
        ts_start = dss_julian2python(juls,istime)
        ts_end   = dss_julian2python(jule,ietime)
        
        if (not firstfound) or (not lastfound):
           
            dssf_catalog = self._dss_catalogs[data_ref.source]
            ## filter out other paths
            filtered_catalog = dssf_catalog.filter_catalog(data_ref.selector)
            firstDpart=filtered_catalog.uncondensed_D_parts(0)[0]
            lastDpart =filtered_catalog.uncondensed_D_parts(0)[-1]
            if (not firstfound):
                ts_start = parse_time(firstDpart)
            if (not lastfound):
                ts_end   = parse_time(lastDpart)
        
            
            

        ## for aggregated ts move time stamp to begining of interval
        if (ctype in RTS_DSS_PROPTY_TO_VT.keys()):
            ts_start =ts_start - step
            ts_end   =ts_end - step

        if (etime<ts_start) or (stime>ts_end):
            raise ValueError("input time window is out of valid data extent %s."%data_ref.selector)

    
        if (stime<ts_start):
            stime = ts_start

        ##  for aggregated ts move a interval forward to make sure including the last data
        if (etime>(ts_end+step)) and (ctype in RTS_DSS_PROPTY_TO_VT.keys()):
            etime = ts_end+step
        elif (etime>(ts_end)) and (not(ctype in RTS_DSS_PROPTY_TO_VT.keys())):
            etime = ts_end
        
            
        cdate=stime.date()
        cdate=cdate.strftime('%d%b%Y') 
        ctime=stime.time()
        ctime=ctime.strftime('%H%M')
       
        right = 1
        left  =-1
        if ((align(stime,step,right)!= stime) and (align(ts_start,step,right) == ts_start)):
            stime = align(stime,step,right)
        if ((align(etime,step,left)!=etime) and (align(ts_end,step,left) == ts_end)):
            etime = align(etime,step,left)

        if (etime<stime): ## no data should be return in such a case
            return (cdate,ctime,0)

        ## here is a fix
        ## giving a example in reading aggregated ts, timewindow (3/14/2000,3/15/2000)
        ## time interval 1 day. number_interval will only return one interval for this
        ## timewindow, that means dss reading function will only retreieve one value
        ## stamped on 3/14/2000 (3/13/2000 24:00, dss file stamp time on the end of period)
        ##, which is actully the data of 3/13/2000 for daily aggregated data.
        ## So we need read one more value to get data stampped at
        ## 3/15/2000 (3/14/2000 24:00) which is the exact the aggreaged data on period (3/14/2000 - 3/15/2000)
        ## the extra one data will be abandoned when converting data into vtools ts object.
        ## In case of instaneous data, this fix works ok for we want data stamped on the late side of
        ## time window also. For instance time window (3/14/2000,3/15/2000) with interval of 1 day. We want
        ## data on 3/14 and 3/15, but number_interval(3/14/2000,3/15/2000) will only return 1 interval, so
        ## we can use number_interval(3/14/2000,3/16/2000)=2 as the number of data we want.
        etime=increment(etime,step)

        return self._multiple_window(stime,etime,step)
        #tnval=number_intervals(stime,etime,step) 
        #return (cdate,ctime,tnval)
       
    def _retrieve_regularTS(self,data_ref):
        """ Retrieve regular time sereis referenced by data_re.
            An instance of class TimeSereis is returned. 
        """        
       
        path=data_ref.selector
        dss_file_path=data_ref.source
        dssf=open_dss(dss_file_path)
        time_interval=strip(split(path,"/")[5])
        window_iter = self._gen_rts_datetime_nval(data_ref,dssf)
        
        lflags=True
        kheadu=DSS_MAX_HEADER_ITEMS
        index=0

        datat =[]
        flagst=[]
        iofset=0
        ccdate=""
        cunits=""
        ctype =""
        nnheadu=0
        hheadu=None
        cdate =""
        ctime =""
        nvalt =0
        while True:            
            try:
                cdate,ctime,nval=window_iter.next()
            except:
                break
            
            if nval==0:
                break
            nvalt = nval
            (nval,data,flags,lfread,cunits,ctype,headu,nheadu,iofset,icomp,istat)\
            =dssf.zrrtsx(path,cdate,ctime,nval,lflags,kheadu)

            if istat==5:
                del dssf
                raise DssAccessError("Your selection in record %s is invalid, change your timewindow?"%path)
            if istat>5:
                del dssf 
                raise DssAccessError("Error access data: %s erro code:"%path)

            if index==0: ## keep first set of dic and date.
                ccdate=cdate
                cctime=ctime
                nnheadu=nheadu
                hheadu=headu
                datat=data
                flagst=flags
            else:
                datat=concatenate((datat,data))
                flagst=concatenate((flagst,flags))
                
            index=index+1
            
        if strip(ccdate)=="":
            ccdate=strip(split(path,"/")[4])
            cctime="0000"

        del dssf

         ## add those props.
        prop={}
        
        if (nvalt==0):
            return rts([],cdate,time_interval,prop)
       
        prop[UNIT]=cunits
        prop[CTYPE]=ctype
        
        if nnheadu>0:
            hdic=self._unstuff_header(hheadu,nnheadu,2)
            for key in hdic.keys():
                if not((key==UNIT)or(key==CTYPE)):
                    prop[key]=hdic[key]

             
        ts=dss_rts_to_ts\
        (datat,ccdate,cctime,time_interval,iofset,prop,flagst)
        
        return ts
                    
    
    def _gen_its_jultime(self,data_ref):
        """ given a its data_ref returns the
            start and end time in format of dss.
        """

        # It is expected dss data_re has only one extent setting
        # extent has value like ('time_window',("'01/11/1991
        # 10:30:00'","'02/11/1995 10:30:00'")).
        (dummy,extent)=data_ref.extents()[0]

        # Start time and end time in string.
        stime=extent[0]
        etime=extent[1]
        # Parse string datetime into datetime instance.
        stime=dateutil.parser.parse(stime)
        etime=dateutil.parser.parse(etime)
        # Interger for dss julian day.
        juls=datetime_to_dss_julian_date(stime) 
        jule=datetime_to_dss_julian_date(etime)

        # Calculate mintues passed midnight
        istime=stime.hour*60+stime.minute  
        ietime=etime.hour*60+etime.minute 

        return (juls,jule,istime,ietime)               
            

    def _retrieve_irregularTS(self,data_ref,overlap=None):
        """ Retrieve irregular time sereis referenced by data_re.
            An instance of class TimeSereis is returned. 
        """
        
        path=data_ref.selector
        dss_file_path=data_ref.source
        dssf=open_dss(dss_file_path)

        juls,jule,istime,ietime=self._gen_its_jultime(data_ref)        
        # Max number of vals can be retrived one time, this consant is defined in dss_constants.py
        kval=DSS_MAX_ITS_POINTS
        lflags=True
        kheadu=DSS_MAX_HEADER_ITEMS
        if (overlap==(0,0))or (overlap is None):
            inflag= int(0)
        elif (overlap==(1,1)):
            inflag= int(3)
        elif (overlap==(1,0)):
            inflag= int(1)
        else :
            inflag= int(2)
        
        (itimes,data,nval,jbdate,flags,lfread,cunits,ctype,headu,nheadu,istat)= \
        dssf.zritsx(path,juls,istime,jule,ietime,kval,lflags,kheadu,inflag)
        del dssf
         ## add those props.
        prop={}
        #prop[CTYPE]=ctype
        prop[UNIT]=cunits
        
        if istat==5:
            raise DssAccessError("no record of %s is found"%path)
        if istat>5:
            raise DssAccessError("error in access data of %s"%path)
        if istat==4: ##no data found,return a 0 len its
            return its([],[],prop)
       

        if nheadu>0:
            hdic=self._unstuff_header(headu,nheadu,2)
            for key in hdic.keys():
                if not((key==UNIT)or(key==CTYPE)):
                    prop[key]=hdic[key]
                
        data=dss_its_to_ts(data,jbdate,itimes,prop,flags)
        return data

    def _check_path_ts(self,data_reference,ts):
        """ check E part of path used by data_reference to be
            compatible with ts (for rts only).
        """
      
        if ts.is_regular():
            interval=ts.interval
            path=data_reference.selector
            pp=path.split("/")
            d=pp[5].strip()         
            if d=="${interval}" or  d=="${INTERVAL}":
                ii=valid_dss_interval_dic_in_delta.index(ts.interval)
                dt=interval_to_D[ii]
                data_reference.selector=path.replace(d,dt)
            else:
                dint=parse_interval(d)
                if not interval==dint:
                    raise ValueError("D part of referenced path %s is not same as"
                                     "the interval used by timeseries to be saved,"
                                     "which is %s"%(path,interval))

    def _dissect(self,dataref):
        parts=dataref.selector.split("/")
        le=[('A',1),('B',2),('C',3),('D',4),('E',5),('F',6)]
        part_dic={}
        for (part,index) in le:
            part_dic[part]=parts[index]
        part_dic["extent"]=dataref.extent
        return part_dic

    def _assemble(self,translation,**kargs):

        path=translation
        if not path:
            path="/${A}/${B}/${C}/${D}/${INTERVAL}/${F}/"
        parts=['A','B','C','D','E','F']
        ref_dic={}
        if "ref_dic" in kargs.keys():
            ref_dic=kargs["ref_dic"]
            
        if ref_dic:
            for part in parts:
                if part in ref_dic.keys():
                    if part=='E':
                        if not ref_dic[part] in interval_to_D:
                            path=path.replace("${INTERVAL}",ref_dic[part])
                        else:
                            path=path.replace("${"+part+"}",ref_dic[part])
                    else:
                        path=path.replace("${"+part+"}",ref_dic[part])
            if "extent" in ref_dic.keys():
                extent=ref_dic['extent']
        if "(null)" in path:
            path=path.replace("(null)","")        
        id=DSS_DATA_SOURCE
        extent=None

        dest=""
        if not "dest" in kargs.keys():
            raise ValueError("Destination source must be provided"
                             "in assembling dss references")
        dest=kargs["dest"]
        dataref=DataReferenceFactory(id,source=dest,view=None,\
                             selector=path,extent=extent)

        return dataref
    
if __name__=="__main__":
    st=DssService()
    print st.identification


        




