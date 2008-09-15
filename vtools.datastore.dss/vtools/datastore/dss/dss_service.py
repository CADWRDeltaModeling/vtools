# stanadard library import
from sys import argv
import os.path
from shutil import rmtree
from os import mkdir,rmdir
from string import split,strip,rstrip
import re
import pdb

#scipy import
from scipy import zeros,concatenate

#vtools import 
from vtools.datastore.service import Service
from vtools.data.timeseries import TimeSeries
from vtools.datastore.catalog_schema import CatalogSchemaItem
from vtools.data.vtime import parse_interval,number_intervals,\
     increment

#gadfly import
from gadfly import gadfly

#dateutil import
import dateutil.parser

#pydss import
from pydss.hecdss import open_dss,zfver
from pydss.hecdss import DssFile,zrdpat,open_dss,zset
from pydss.hecdss import zopnca,zrdcat
from pydss.hecdss import zustfh,zstfh
from pydss.fortranfile import fortran_file,FortranFile
from pydss.fortranfile import fortran_file,FortranFile

#vtools import
from vtools.data.constants import *
from vtools.data.vtime import parse_interval,\
     parse_time
from vtools.datastore.data_reference import *
#from vtools.debugtools.timeprofile import debug_timeprofiler

#local import
from dss_catalog import DssCatalog
from dss_constants import *
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
    entrydb=None
    db_file_use_number=0 ## how many source I have cataloged so far in this run

    has_dss_catalog_table=False
    # the last dssfile index used
    dss_file_index_last=0  
    dss_file_index_used=[]

    identification=DSS_DATA_SOURCE
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

        if idtype==REGULARTS:
            (time_window,header,unit,type)=\
            self._retrieve_rts_prop(dssf,path,dparts)
        elif idtype==IRREGULARTS:
            (time_window,header,unit,type)=\
            self._retrieve_its_prop(dssf,path,dparts)
        else:
            raise ValueError("Unimplemented record type.")
        
        return (time_window,header,unit,type)

    def remove_dssfile(self,dss_file_path):
        self._remove_dssfile_catalog(dss_file_path)

    def reload_dss_records(self,dss_file_path):
        """ Update db info about dss file and return new
            info necessary to update a catalog instance.
        """
        self._update_dss_file_catalog(dss_file_path)

        self.dbcursor.execute(selsql,(strip(dss_file_path),))
        findex=self.dbcursor.fetchone()[0]
        createviewsql="create view tv as select A,B,C,D,E,F \
                       from dsscatalog where F_ID="+str(findex)
        
        self.dbcursor.execute(createviewsql)        
        selsql="select * from tv"        
        self._reduce_catalog(selsql,None)

        records=self.dbcursor.fetchall()        
        dropviewsql="drop view tv"
        self.dbcursor.execute(dropviewsql)
        return records

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
            self._create_db()
            DssService.first_initialization=False
     
        self.entrydb=DssService.entrydb
        self.dbcursor=DssService.entrydb.cursor()
    
        #if no tables available yet,create them
        if not(DssService.has_dss_catalog_table):
            self._create_tables()
            DssService.has_dss_catalog_table=True
        ## following line must be excuted for the
        ## sake of making ts-header unstuff func
        ## to work correctly.
        zset('MLEVEL','',0)


    ########################################################################### 
    # Protected interface.
    ###########################################################################
    def _get_catalog(self,dss_file_path):
        """ Return a catalog of dss file."""
        selsql=" select F_ID,MODIFYTIME from dssfile where FPATH=?"
        self.dbcursor.execute(selsql,(dss_file_path,))
##        except:
##            self.entrydb.close()
##            self._create_db()
##            DssService.first_initialization=False
##            self.entrydb=DssService.entrydb
##            self.dbcursor=DssService.entrydb.cursor()
##            self._create_tables()        
##            DssService.has_dss_catalog_table=True
##            self.dbcursor.execute(selsql,(strip(dss_file_path),))
        
        info=self.dbcursor.fetchall()
        
        if info: ## info is in form of [(1,2222344)],2222344 is time, 1 is f index
            last_modified_time=info[0][1]
            #print last_modified_time,os.stat(dss_file_path)[8]
            #####################################################################
            ##              comment and observation                            ##
            ## This decision is done by comparing the update time of a dss file##
            ## stored within db to its updatetime returned by windows query on ##
            ## file property, if they are different, catalog will redone to    ##
            ## refelect the change that might happen from last time. When they ##
            ## same, just used info stored in db to save time. But it may fail,##
            ## sometimes when last modification on dss file is very close to   ##
            ## current time, for instance doing a catalog modification right   ##
            ## after some saving ts into dss, like in test_all_module(when     ##
            ## test_modify right after test_save_data, sometimes two times are ##
            ## the same,even file is different already).No solution currrently ##
            #####################################################################
            if not(last_modified_time==\
                   os.stat(dss_file_path)[8]):
                self._remove_dssfile_catalog(dss_file_path)
                self._cataloging_dss_file(strip(dss_file_path))
        else:
            self._cataloging_dss_file(strip(dss_file_path))

        self.dbcursor.execute(selsql,(strip(dss_file_path),))
        findex=self.dbcursor.fetchone()[0]

        #createviewsql="create view tv as select A,B,C,D,E,F \
        #               from dsscatalog where F_ID="+str(findex)
        
        #self.dbcursor.execute(createviewsql)        
        #selsql="select * from tv"
        selsql="select A,B,C,D,E,F from dsscatalog where F_ID="+str(findex)
        
        self._reduce_catalog(selsql,None)

        table_column_index_map=self._create_column_index_map()
        schema=self._generate_schema(table_column_index_map)
        
        records=self.dbcursor.fetchall()        
        #dropviewsql="drop view tv"
        #self.dbcursor.execute(dropviewsql)

        ##### time profile ####
        #print 'time at done with create catalog record iter',\
        #      debug_timeprofiler.timegap()
        ######################
        
        return DssCatalog(dss_file_path,schema,self,records)

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
    
    def _get_data(self,data_ref):
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
                #pdb.set_trace()
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
            return self._retrieve_regularTS(data_ref)
        elif cdtype=="ITS":
            return self._retrieve_irregularTS(data_ref)
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
    
    def _create_db(self):      
        """ Create a new tempory gadfly db file to store dss catalogs
            and return db curosr.

        """        
        fname="tempdb"
        fs=__file__
        (fsp,fsn)=os.path.split(fs)
        fsp=fsp+"\\temp"

        if not os.path.exists(fsp):
            try:
                mkdir(fsp)
            except Exception,e:
                raise e

        DssService.database_file_dir=fsp
        
        try:
            DssService.entrydb=gadfly()
            DssService.entrydb.startup(fname,fsp)
        except Exception,e:
            raise e

                
##    def  __del__(self):
##        """ Clean up temp file used."""
##        
##        if DssService.db_file_use_number==0 :               
##            try:
##                self.entrydb.close()
##            except Exception, e:
##                raise e            


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
            
        self._retrieve_catalog_to_db(dss_file_path)

        #add the amount of class instance using dababase by one
        self._add_use()

        ##### time profile ####
        #print 'total time in loading catalog info to db',debug_timeprofiler.timegap()
        ######################    

    def _update_dss_file_catalog(self,dss_file_path):
        """ Update the catalog database for file at dss_file_path
            if its info found in db.
        """

        selsql=" select F_ID from dssfile where FPATH=?"
        self.dbcursor.execute(selsql,(strip(dss_file_path),))
        if self.dbcursor.fetchall():
            self._remove_dssfile_catalog(dss_file_path)
            self._cataloging_dss_file(dss_file_path)

    def _create_tables(self):
        """ Create the catalog table in temp db file."""
                
        sqlstatement="create table dsscatalog (F_ID integer,A varchar, \
                      B varchar,C varchar,D varchar,E varchar,F varchar)" 
        self.dbcursor.execute(sqlstatement)
        sqlstatement="create table dssfile (F_ID integer, FPATH varchar,MODIFYTIME integer)"        
        self.dbcursor.execute(sqlstatement)
        self.entrydb.commit()
            
    def _remove_use(self):

        if DssService.db_file_use_number>0:
            DssService.db_file_use_number=DssService.db_file_use_number-1

    def _add_use(self):

        DssService.db_file_use_number=DssService.db_file_use_number+1


    def _retrieve_catalog_to_db(self,dss_file_path):
        """ Retrieve all the catalog entries of a dssfile
            and save it in a temp gadfly db file.
        """
        
        insertstat = "insert into dsscatalog (F_ID,A,B,C,D,E,F) \
                      values (?,?,?,?,?,?,?)"
       
        #dssfile=open_dss(dss_file_path)
        #if dssfile and type(dssfile)==DssFile:

        if os.path.exists(dss_file_path):            
##            try:
            dsdfile=self._open_catalog(dss_file_path)
            #dtt=self._read_catalog_file(cf0)
            dtt=self._read_dsd_file(dsdfile)
            if not dtt:
                raise DssCatalogServiceError\
                      ("%s isn't a valid dss file"%(dss_file_path))
            self.dbcursor.execute(insertstat,dtt)
            self.entrydb.commit()
            
        #cf0.close()  
        #del dssfile


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
                
        dtt.append((self.dss_file_index,pre_parts[0],pre_parts[1],pre_parts[2],\
                pre_parts[5],pre_parts[4],pre_parts[3]))
        return dtt

##    def _read_catalog_file(self,cf0):
##        """retrieve abbreivated path entries from catalog file cf0,
##           if success, a list of pathes will be returned.
##        """
##
##        ##### time profile ####
##        #debug_timeprofiler.mark("reading catalog for dss file")
##        ######################
##        
##        ipos=0
##        inumb=0
##        lend=False
##        cf0.rewind()
##        dtt=[]
##        #part_re=re.compile(\
##        #    r'/(?P<A>.*?)/(?P<B>.*?)/(?P<C>.*?)/(?P<D>.*?)/(?P<E>.*?)/(?P<F>.*?)/')
##        
##        i=0
##        pre_dt=[]
##        pre_A=None
##        pre_B=None
##        pre_C=None
##        pre_D=None
##        pre_E=None
##        pre_F=None
##
##
##
####        nfound=1
####        ctags="     "
####        ntags=1
####        npath=1
####        cd0=fortran_file(FortranFile.DUMMY_FILE_UNIT)
##        while not(lend):
##        #while  nfound:
##            [ipos,inumb,ctag,cpath,npath,lend]=zrdpat(cf0,ipos,inumb)
##            #[ctags,cpath,npath,nfound]= zrdcat(cf0,True,cd0,ctags,ntags)
##            #pdb.set_trace()
##            if cpath:
##                clst=cpath.split("/")
##                A=clst[1]
##                B=clst[2]
##                C=clst[3]
##                D=clst[4]
##                E=clst[5]
##                F=clst[6]
##                
##                
##                if i==0: ## first one will always be appended
##                    #dtt.append((self.dss_file_index,A,B,C,D,E,F))
##                    pre_A=A
##                    pre_B=B
##                    pre_C=C
##                    pre_D=D
##                    pre_E=E
##                    pre_F=F
##                else: ## try to merge records of the same abbreviated path
##                    if A==pre_A and B==pre_B \
##                       and C==pre_C and E==pre_E \
##                       and F==pre_F:
##                        pre_D=pre_D+","+D
##                    else:
##                        dt=(self.dss_file_index,pre_A,pre_B,pre_C,pre_D,pre_E,pre_F)
##                        dtt.append(dt)
##                        pre_A=A
##                        pre_B=B
##                        pre_C=C
##                        pre_D=D
##                        pre_E=E
##                        pre_F=F
##                i=i+1
##
##        dtt.append((self.dss_file_index,pre_A,pre_B,pre_C,pre_D,pre_E,pre_F))
##        ##### time profile ####
##        #print 'time used in reading catalog info ',debug_timeprofiler.timegap()
##        ######################
##
##        return dtt
    
    def _open_catalog(self,fpath):
        """" Open or create standard catalog file of the dssfile for retrieving."""
                       
        fpath=fpath.lower()
        fnames=os.path.split(fpath)
        
        dsdpath=os.path.join(fnames[0],fnames[1].replace(".dss",".dsd"))
        dscpath=os.path.join(fnames[0],fnames[1].replace(".dss",".dsc"))
        
        if os.path.exists(dsdpath):
            os.remove(dsdpath)
        if os.path.exists(dscpath):
            os.remove(dscpath)            
            
        cf0=fortran_file()
        cd0=fortran_file()
        cn0=fortran_file(FortranFile.DUMMY_FILE_UNIT)

        ##### time profile ####
        #debug_timeprofiler.mark("opening catalog for dss file")
        ######################
  
        [lopnca,lcatlg,lopncd,lcatcd,nrecs]=zopnca(fpath,cf0,True,cd0,True)
        
        if not(lopnca):
            raise DssCatalogServiceError\
                  ("unable to open/create catalog file for dss file %s"%fname)

        if not(lcatlg):
            dssfile=open_dss(fpath)
            [lcdcat,nrecs]=dssfile.zcat(cf0,cd0,cn0,' ',True,True)
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

        if DssService._num_db_clean>200:
            self.entrydb.close()
            self._create_db()
            DssService.first_initialization=False
            self.entrydb=DssService.entrydb
            self.dbcursor=DssService.entrydb.cursor()
        else:            
            del_sql="drop table dssfile"        
            self.dbcursor.execute(del_sql)
            del_sql="drop table dsscatalog"
            self.dbcursor.execute(del_sql)
            self.entrydb.commit()
        DssService._num_db_clean=DssService._num_db_clean+1
        self._create_tables()        
        DssService.has_dss_catalog_table=True
        
    def _add_dss_file_record(self,fpath,index):
        """" Insert dssfile path into table DssFile."""
        
        insertstat = "insert into dssfile (F_ID, FPATH,MODIFYTIME) values (?,?,?)"
        self.dbcursor.execute(insertstat,tuple([index,fpath,os.stat(fpath)[8]]))
        self.entrydb.commit()

    def _remove_dss_file_record(self,index):
        """ Remove dssfile path from table DssFile."""
        
        delstat="DELETE FROM dssfile WHERE F_ID= ?"
        self.dbcursor.execute(delstat,(index,))
        self.entrydb.commit()


    def _remove_paths_record(self,index):
        """ Remove all the paths record of a specified dssfile by index."""
        
        delstat="DELETE FROM dsscatalog WHERE F_ID= ?"
        self.dbcursor.execute(delstat,(index,))
        self.entrydb.commit()
    
    def _remove_dss_file(self,index):
        """ Remove all the db record related to a dss file 
            indexed by input index.
        """
        self._remove_dss_file_record(index)
        self._remove_paths_record(index)

    def _remove_dssfile_catalog(self,dss_file_path):
        """ Delete all catalog record about dss_file_path in db"""

        selsql=" select F_ID from dssfile where FPATH=?"
        self.dbcursor.execute(selsql,(strip(dss_file_path),))
       
        if not(self.dbcursor.fetchall()):
            raise DssCatalogServiceError\
                  ("dss file %s is not founded in database"%dss_file_path)
        
        self.dbcursor.execute(selsql,(strip(dss_file_path),))
        for findex in self.dbcursor.fetchall():
            ## for findex is returned as tuple of size 1. 
            self._remove_dss_file(findex[0])
            ## also release the used findex from used list
            DssService.dss_file_index_used.remove(findex[0])
            
    def _create_column_index_map(self):

        """ Return a correspondance between table column index 
            and  catalog entry item name.
        """

        des=self.dbcursor.description

        l=len(des)
        map={}
        for i in range(0,l):
            colname=des[i][0]
            map[colname]=i
        return map

   
    def _reduce_catalog(self,selsql,parameter=None):
        """ Return some catalog entries from catalog database based 
            criteria parameter given, if no paramter given all catalog
            in a dss file will be return.
        """
        
        [selsql,parameter]=self._modify_select_sql(selsql,parameter)

        if parameter:
            self.dbcursor.execute(selsql,parameter)
        else:
            self.dbcursor.execute(selsql)

    def _modify_select_sql(self,selsql,parameter):
        """ Rebuilt string of selection sql query to add query parameters.
           If no parameter given, just return query intact.
        """   
         
        if type(parameter)==str:  #must be in format of A=WWW,B=WWW,C=WWW
            parameter=strip(parameter)
            itemlist=split(parameter,",")
            
            if len(itemlist)>0:
                selsql=selsql+" where "
                val=[]
                for aitem in itemlist:
                    elelist=split(strip(aitem),"=")
                    selsql=selsql+"("+strip(elelist[0])+"=?) and"
                    val.append(strip(elelist[1]))
                selsql=rstrip(selsql,"and") #remove the last and
                parameter=tuple(val)
                
        return (selsql,parameter)
          

    def _retrieve_data_type(self,dssfile,cpath):
        """ Get info about data series type,also return its block size."""
        
        [nsize,lexist,cdtype,idtype]=dssfile.zdtype(cpath)
        [nhead,ndata,lfound]=dssfile.zcheck(cpath)

        return [idtype,cdtype,ndata]


    def _retrieve_rts_prop(self,dssf,cpath,dparts):
        """ Retrieve all the prop about a rts record."""
        #pdb.set_trace()
        firstD=dparts[0]
        firstpath=cpath.replace('//','/'+firstD+'/')
        #pdb.set_trace()
        (header_dic,data,cunits,ctype)=\
        self._retrieve_regular_header(dssf,firstpath)
                
        ## find out start datetime
        ce=firstpath.split('/')[5]
        interval=parse_interval(ce)
        cd=firstD
        start=parse_time(cd) 
        ## move forward for aver,min, and min,max data
        if ctype.upper()=="PER-AVER" or ctype.upper()=="PER-MIN" \
           or ctype.upper()=="PER-CUM" or ctype.upper()=="PER-MAX":
            start=start+interval       ## in dss storage,this is
                                      ## the actual start time 
                                      ## of the data block.

                   

        valid_start=discover_valid_rts_start(data,start,interval)

        ## find out start datetime of ending data block.
        lastD=dparts[-1]
        lastpath=cpath.replace('//','/'+lastD+'/')
        (header_dic,data,cunits,ctype)=\
        self._retrieve_regular_header(dssf,lastpath)       
        end=parse_time(lastD)
        valid_end=discover_valid_rts_end(data,end,interval)

        ## time window is up to but not include right side of
        ## extent
        time_window=(valid_start,valid_end+interval)

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

        #pdb.set_trace()        
        try:            
            [itimes,vals,nvals,jbdate,flags,lfread,cunits,\
             ctype,headu,nheadu,istat]= \
            dssf.zritsx(cpath,juls,istime,jule,ietime,nvals,False,500,0)
        except Exception,e:
            dssf.close()
            raise e

        header_dic=self._unstuff_header(headu,nheadu)
        start=dss_julian2python(jbdate,itimes[0])
        end=dss_julian2python(jbdate,itimes[nvals-1])

        return (header_dic,(start,end),cunits,ctype)
    
##    def _retrieve_pair_header(self,dssfile,cpath):
##        """ Retrieve info about pair data. """       
##        kheadi=100
##        kheadc=100
##        kheadu=100
##        kdata=1
##        iplan=0
##        # First retrieve number of curve and ordinates by zreadx
##        [headi,nheadi,headc,nheadc,headu,nheadu,data,ndata,lfound]= \
##        dssfile.zreadx(cpath,kheadi,kheadc,kheadu,kdata,iplan)
##
##        # From headi get number of curve and ordinates
##        nord = headi[0]
##        ncurve = headi[1]
##        ihoriz = headi[2]
##        
##        
##        # This is really waste of system time to read whole time
##        # series value to get only header info and label, no
##        # better solution for the time being.
##        kvals=(ncurve+1)*nord
##        klabel=50 #50 labels at most
##        try:           
##            [nord1,ncurve1,ihoriz1,c1unit,c1type,c2unit,c2type,\
##             values,nvals,clabel,label,headu,nheadu,istat]\
##            =dssfile.zrpd(cpath,kvals,klabel,kheadu)
##        except Exception,e:
##            raise e
##        
##        dt=[]
##        dt.append(c1unit+","+c2unit)
##        dt.append(c1type+","+c2type)
##
##        if label:            
##            header_label="label"        
##            header_item="(" # usually there more than one labels
##            for i in range(0,ncurve):
##                header_item=header_item+clabel[i]+","
##            header_item=strip(header_item,",") #remove last ','
##            header_item=header_item+")"
##            
##        #pdb.set_trace()
##         
##        if nheadu:
##            [label,item]=self._unstuff_header(headu,nheadu)
##            header_label=header_label+","+label
##            header_item=header_item+","+item
##
##        dt.append(header_label)
##        dt.append(header_item)
##        return dt
        
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
        
    def _gen_rts_datetime_nval(self,data_ref):
        """ given a rts data_ref returns the character cdate,ctime
            and number of data contained within time extents.
        """
        ## here we requie data_ref must contain time extent for such a info are needed by
        ##fortran lib dss function to retirieve ts, it is best to generate data_ref from 
        ##a dss catalog,not directly to save th work of finding ts time extent
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

        # Next get string representation of start date and time
        # in dss function foramt ,like "01JAN2000","1030"
        # also find out how many data points within timewindow.
        step=parse_interval(time_interval)

        ## here is a fix to the standard dss retrieving util
        ## increasing etime by a interval to get the vale at
        ## the end of time window input by user
        etime=increment(etime,step)
        
        tnval=number_intervals(stime,etime,step)
        
        if tnval<DSS_MAX_RTS_POINTS:
            cdate=stime.date()
            cdate=cdate.strftime('%d%b%Y') 
            ctime=stime.time()
            ctime=ctime.strftime('%H%M')           
            return iter([(cdate,ctime,tnval)])
        else:
            return self._multiple_window(stime,etime,step)
        
    def _multiple_window(self,stime,etime,step):
        
        """ Create iterator of multiple time window for
            data set more than DSS_MAX_RTS_POINTS.
        """
    
        lt=[]
        stimet=stime
        
        while stimet<etime:
            
            etimet=increment(
                stimet,step,DSS_MAX_RTS_POINTS)
            nval=DSS_MAX_RTS_POINTS
            
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
                

    def _retrieve_regularTS(self,data_ref):
        """ Retrieve regular time sereis referenced by data_re.
            An instance of class TimeSereis is returned. 
        """        
        path=data_ref.selector
        dss_file_path=data_ref.source
        dssf=open_dss(dss_file_path)
        time_interval=strip(split(path,"/")[5])

        #cdate,ctime,nval=self._gen_rts_datetime_nval(data_ref)
        lt=self._gen_rts_datetime_nval(data_ref)
        
        lflags=True
        kheadu=DSS_MAX_HEADER_ITEMS
        index=0

        datat=None
        flagst=None
        
        while True:            
            try:
                cdate,ctime,nval=lt.next()
            except:
                break
            
            (nval,data,flags,lfread,cunits,ctype,headu,nheadu,iofset,icomp,istat)\
            =dssf.zrrtsx(path,cdate,ctime,nval,lflags,kheadu)

            if istat==5:
                #pdb.set_trace()
                del dssf
                raise DssAccessError("data of %s within your selection is invalid,change your timewindow"%path)
            if istat>5:
                del dssf 
                raise DssAccessError("error in access data of %s"%path)

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
        prop[UNIT]=cunits
        prop[CTYPE]=ctype

        if nnheadu>0:
            hdic=self._unstuff_header(hheadu,nnheadu,2)
            for key in hdic.keys():
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
            

    def _retrieve_irregularTS(self,data_ref):
        """ Retrieve irregular time sereis referenced by data_re.
            An instance of class TimeSereis is returned. 
        """
        
        path=data_ref.selector
        dss_file_path=data_ref.source
        dssf=open_dss(dss_file_path)

        juls,jule,istime,ietime=self._gen_its_jultime(data_ref)        
        # Max number of vals,integer defined in dss_constants.py
        kval=DSS_MAX_ITS_POINTS
        lflags=True
        kheadu=DSS_MAX_HEADER_ITEMS
        inflag=0
        
        #(itimes,data,nval,jbdate,cunits,ctype,istat)=dssf.zrits(path,juls,istime,jule,ietime,kval)
        (itimes,data,nval,jbdate,flags,lfread,cunits,ctype,headu,nheadu,istat)= \
        dssf.zritsx(path,juls,istime,jule,ietime,kval,lflags,kheadu,inflag)
        del dssf
        if istat==5:
            raise DssAccessError("no record of %s is found"%path)
        if istat>5:
            raise DssAccessError("error in access data of %s"%path)

        ## add those props.
        prop={}
        #prop[CTYPE]=ctype
        prop[UNIT]=cunits

        if nheadu>0:
            hdic=self._unstuff_header(headu,nheadu,2)
            for key in hdic.keys():
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
            if d=="${interval}" or  d=="${INTERVAL}" :
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


        




