""" Service to access excel data source."""

## stanadard library import.
#import pdb
import os.path,itertools
import re

## dateutil import.
import dateutil.parser

## scipy import.
from scipy import array

## standard python lib import.
from operator import isNumberType

## vtools import. 
from vtools.datastore.service import Service
from vtools.data.vtime import parse_time,parse_interval
from vtools.data.timeseries import rts,its
from vtools.data.constants import *
from vtools.datastore.data_reference import *
## local import.
from excel_catalog import ExcelCatalog
from excel_constants import *
from utility import *

__all__=["ExcelService"]

class ExcelService(Service):
    """ Service to access excel data source."""

    ## static method to decide whether a source can be served.

    def serve(source):
        return source.lower().endswith('.xls')
        
    serve=staticmethod(serve)    
    ########################################################################### 
    # Public interface.
    ###########################################################################
    identification=EXCEL_DATA_SOURCE
    
    def batch_add(self,ref,ts_list):
        """ Add a number of ts into a excel worksheet pointed by ref.

            input:
                ts_list: might be single ts or list of ts.
                ref: data refernce instance.
            For the limitation of excel, a number of ts has to be
            added into excel worksheet in one time.
        """

        self._batch_add(ref,ts_list)       
    ########################################################################### 
    # Object interface.
    ###########################################################################
    def __init__(self):
        pass

        ## range of ts data is specified by user in data reference
        ## or selector, note: odbc always treat the first line
        ## of a selected range as data label, so to maintain orginal
        ## data untouched in retrieving ts by odbc, always put a label
        ## row at the first line of selected range or leave it empty.
        ## limitation of worksheet size row<=65536,column<=256
        

    ########################################################################### 
    # Protected interface.
    ###########################################################################
    def _get_data(self,dataref):
        excel_file=ref.source
        selection=ref.selector

        ts_type="rts"
        if "ts_type" in dataref.decoration.keys():
            ts_type=dataref["ts_type"]

        time=None
        if "time" in dataref.decoration.keys():
            time=dataref["time"]

        start=None
        if "start" in dataref.decoration.keys():
            start=dataref["start"]

        interval=None
        if "interval" in dataref.decoration.keys():
            time=dataref["interval"]

        header_labels=None
        if "header_labels" in dataref.decoration.keys():
            time=dataref["header_labels"]

        excel_retrieve_ts(excel_file,selection,ts_type,time=time,\
        start=start,interval=interval,header_labels=header_labels)
                            
            
    def _get_catalog(self,excel_file):
        return ExcelCatalog(excel_file)

    def _add_data(self,dataref,ts):
        self._batch_add(dataref,ts)
                
    def _modify_data(self,dataref,data):
        raise NotImplementedError("Function _modify_data has not be implemented yet \
        for class ExcelService.")

    def _remove_data(self,dataref):

        raise NotImplementedError("Function _remove_data has not be implemented yet \
        for class ExcelService.")

    def _check_data_reference(self,dataref):

        pass
    
    ########################################################################### 
    ## Private interface.
    ###########################################################################    
    def _batch_add(self,ref,ts):
        
        excel_file=ref.source
        selection=ref.selector

        header=None
        if ref.decoration and "header" in ref.decoration.keys():
            header=ref.decoration["header"]        
        write_times=None
        if ref.decoration and "write_times" in ref.decoration.keys():
            write_times=ref.decoration["write_times"]
    
        excel_store_ts(ts,excel_file,selection,\
        header=header,write_times=write_times)

    def _dissect(self,dataref):
        return None

    def _assemble(self,translation,**kargs):
        
        (selection,header_template,write_times)=\
         _analyze_excel_mapping(translation)

        pre_sel=kargs["pre_sel"]

        if write_times=="none" or write_times=="all":
            write_time=write_times
        elif write_times=="first":
            if not pre_sel: ## it is first ts in a number of ts
                write_time="all"
            else:
                write_time="none"
        else:
            raise ValueError("%s is inappropriate time writing method"%write_times)
        
        if not pre_sel:
            sel=selection ## like "sheet1$a12"
        else:
            sel=_generate_col_label(pre_sel,write_time)
            
        if not "dest" in kargs.keys():
            raise ValueError("Destination source must be provided"
                             "in assembling excel references")
        dest=kargs["dest"]

        excel_ref= DataReferenceFactory(EXCEL_DATA_SOURCE,source=dest,\
        selector=sel)

        ref_dic={}
        if "ref_dic" in kargs.keys():
            ref_dic=kargs["ref_dic"]
            
        if ref_dic:
            header=_fill_excel_header(ref_dic,header_template)
        
        excel_ref.decoration={}
        excel_ref.decoration["header"]=header
        excel_ref.decoration["write_times"]=write_time        
        
        return excel_ref
    
############################# some private helper funcs ###########################
        
l=['A','B','C','E','F','G','H'\
   ,'I','J','K','L','M','N','O',\
   'P','Q','R','S','T','U','V','W',\
   'X','Y','Z']

## this is give a enumerating list of excel
## col names, but this list sets a limit of
## maximal 650 excel col to save ts into excel
## sheet simutanouesly

_excel_cols=['A','B','C','E','F','G','H'\
   ,'I','J','K','L','M','N','O',\
   'P','Q','R','S','T','U','V','W',\
   'X','Y','Z']

for a1 in l:
    for a2 in l:
        _excel_cols.append(a1+a2)
        
def _generate_col_label(pre_sel,write_time):
    
    sel_pat=re.compile('[\w]+?\$([a-zA-Z]+?)(?=[0-9])')
    x=sel_pat.match(pre_sel)

    col_label=x.group(1)
    col_label=col_label.upper()
    try:
        col_i=_excel_cols.index(col_label)
    except:
        raise ValueError("%s is not a excel col label supported by vtools"%col_label)
    
    if write_time=="all":
        new_col_label=_excel_cols[col_i+2]
    else:
        new_col_label=_excel_cols[col_i+1]

    sel=pre_sel.replace("$"+col_label,"$"+new_col_label)    
    return sel

def _analyze_excel_mapping(translation):
    ## assume translation is a string like 'selection=sheet1$a1,name=
    ## ${B}_${C},unit=${unit},write_times=first'

    ele_lst=translation.split(",")
    header_template={}
    selection=""
    write_times="all"

    if not translation:
        raise ValueError("You must specify store setting when"
        "transfer time series into excel destination")
    else:
        for ele in ele_lst:
            els=ele.split("=")
            if els:
                if len(els)==1: ## this is selection
                    selection=els[0].strip()
                elif els[0].strip()=="selection": ## selection also
                    selection=els[1].strip()
                elif els[0].strip()=="write_times":
                    write_times=els[1].strip()
                else:
                    header_template[els[0].strip()]=els[1].strip()
                    
        sel_pat=re.compile('[\w]+?\$([a-zA-Z]+?)(?=[0-9])')
        x=sel_pat.match(selection)
        if not x:
            sheet_name=re.compile('[\w]+?')
            x2=sheet_name.match(selection)
            if x2: ## so only sheet name is given, move start to cell a5 by default
                selection=selection+'$a5'
            else:
                raise ValueError("%s is not a proper range input"%selection)
            
    return (selection,header_template,write_times)

def _fill_excel_header(ref_dic,header_template):
    """ Partially fill the headers for excel ts storage
        Partially means it only fills the keywords of
        like "$A", other will be handled by excel storing
        utilities.
    """
   
    header={}
    
    for (header_label,header_val) in header_template.items():
        for parts_key in ref_dic.keys():
            if "${"+parts_key+"}" in header_val:
                header_val=header_val.replace\
                ("${"+parts_key+"}",ref_dic[parts_key])
        header[header_label]=header_val

    return header      
    
    
        
