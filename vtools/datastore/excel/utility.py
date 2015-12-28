"""
    Utility function to store time series into or retrieve time
    series from excel file. 
"""

## python lib import
import re,pdb
from operator import isNumberType
from datetime import datetime
import os.path

## win32 lib import
import win32com.client
from win32com.client import constants

## numpy import
from numpy import array,where,nan,reshape

## vtools lib import
from vtools.data.vtime import *
from vtools.data.timeseries import rts,its

__all__=["excel_store_ts","excel_retrieve_ts"]



def excel_store_ts(ts,excel_file,selection,header=None,write_times="all"):
    """ store single series or list of series into excel"""
    
    if not ts:
        raise TypeError("Input time series can not be None")
    if not selection:
        raise TypeError("Selection is None")
    
    app=win32com.client.Dispatch(r'Excel.Application')
    newfile=False
    
    abspath=os.path.abspath(excel_file)
    
    if os.path.exists(abspath):
        try:
            book = app.Workbooks.Open(abspath)
            newFile = False
        except:
            raise ValueError("Could not open Excel file. Is it open? Previous failure may have left it open?")
    else:
        newfile=True
        book=app.Workbooks.Add()

    try:
        _excel_store_ts(ts,book,selection,header,write_times)        
    except Exception, e:
        book.Close()
        del app
        raise e
    
    if newfile:
        if os.path.exists(abspath):
            os.remove(abspath)
        book.SaveAs(abspath)
    else:
        book.Save()

    book.Close()
    del app

def excel_retrieve_ts(excel_file,selection,ts_type,time=None,**args):
    """" retrieve ts from excel file
         may return a single ts or list of ts.
    """
    app=win32com.client.Dispatch(r'Excel.Application')
    book = app.Workbooks.Open(excel_file)
##    if os.path.exists(excel_file):
##        try:
##            book = app.Workbooks.Open(abspath)
##        except:
##            pass
##    else:
##        raise ValueError("Excel file does not exist")
    
        
    unique=False
    if "unique" in args.keys():
        unique=args["unique"]
        del args["unique"]
    
    try:
        if ts_type=="rts":
            ts_lst=_retrieve_rts(book,selection,time,**args)
        else:
            ts_lst=_retrieve_ts(book,selection,time,**args)
    except Exception,e:
        #app.Workbooks(1).Close(SaveChanges=0)
        app.Application.Quit()
        del app
        raise e
        
    #app.Workbooks(1).Close(SaveChanges=0)
    app.Application.Quit()
    del app

    if unique and type(ts_lst)==list and len(ts_lst)>1:
        raise Warning("your selection criteria"
              "matches more than one timeseries,"
              "please check it.") 

    return ts_lst

 
### private helper funcs #####

def _excel_store_ts(ts,book,selection,header,write_times):
    """ helper function to store single/list of ts."""
    
    rvar=_parse_range(selection)
    
    try:
        sheet=book.Worksheets(rvar[0])
    except:
        book.Worksheets.Add()
        sheet=book.ActiveSheet
        sheet.Name=rvar[0]

    if not type(ts)==list:
        ts=[ts]
        
    col_offset=0
    i=0
    write_time=True
    
    for tts in ts:        
        header_dic=None
        num_header=0
        if write_times=="none":
            write_time=False
        elif write_times=="all":
            write_time=True
        elif write_times=="first":
            if i>0:
                write_time=False

        if header:
            if type(header)==dict: ## header is a dict itself
                header_dic=header
            else:    
                if type(header[0])==dict: ## decision is based on first item
                    header_dic=header[i] ## this means var header contain a dic of header
                                         ## for each ts, not recommended for regular
                                         ## usage,it is here for the purpose of
                                         ## batch transfer to work.
                    ## try to fill the values contain
                    ## ${*?} with ts attribute.
                    header_dic=_fill_dic(header_dic,tts)
                else:
                    header_dic=_check_in_header(tts,header)                    
            num_header=len(header_dic)
            
        _check_store_selection(tts,num_header,rvar,write_time)
        ## header here is passed to in to force header item stored in original order
        _write_to_sheet(tts,sheet,rvar,header_dic,header,write_time,col_offset)
        col_offset=col_offset+1
        if write_time:
            col_offset=col_offset+1
        i=i+1

def _write_to_sheet(ts,sheet,rvar,header_dic,header,write_times,col_off_set):
    """ actual func to write a ts into spreadsheet """

    st_col=rvar[1]
    st_row=rvar[2]
    #pdb.set_trace()     
    st_col=sheet.Range(st_col+str(st_row)).Columns[0].Column
    st_col=st_col+col_off_set
    
    num_header=0   
    if header_dic:
        num_header=len(header_dic)    

    ## if there are limitation of how many rows
    ## can be written.
    len_ts=0
    if len(rvar)==5:
        len_ts=rvar[4]-st_row+1-num_header
        if len_ts>len(ts):
            len_ts=len(ts)
    else:
        len_ts=len(ts)
        
    ## moving postion indication
    r=st_row
    c=st_col
    
    if write_times:        
        base=ticks(datetime(1899,12,31))
        LEAP_CORRECT = 1. # Need to improve on this!!
        tlst = (ts.ticks-base)/float(ticks_per_day) + LEAP_CORRECT
        tarr = reshape(tlst, (len(tlst),1))
        
        if num_header: #need to write header labels
            #write header labels
            st_cell=sheet.Cells(r,c)
            end_cell=sheet.Cells(r+num_header-1,c)
            if type(header)==type([]):
                val=array(header)
            else:
                val=array(header_dic.keys())
            val=reshape(val,(len(val),1))
            sheet.Range(st_cell,end_cell).Value=val
            r=r+num_header
            
        time_start=sheet.Cells(r,c)    
        time_end=sheet.Cells(r+len_ts-1,c)
        sheet.Range(time_start,time_end).Value=tarr
        sheet.Range(time_start,time_end).Columns(1).NumberFormat="m/d/yyyy h:mm"
        c=c+1
        r=st_row

    if num_header: ##need to write header vals
        st_cell=sheet.Cells(r,c)
        end_cell=sheet.Cells(r+num_header-1,c)
        val=[]
        if type(header)==type([]):
              for i in range(len(header)):
                  val.append(header_dic[header[i]])
              val=array(val)
        else:
            val=array(header_dic.values())
        val=reshape(val,(len(val),1))
        sheet.Range(st_cell,end_cell).Value=val
        r=r+num_header
        
    data_start=sheet.Cells(r,c)           
    data_end=sheet.Cells(r+len_ts-1,c)
    varr = reshape(ts.data, (len(ts),1))
    sheet.Range(data_start,data_end).Value=varr
    sheet.Range(data_start,data_end).NumberFormat="#0.###"
                
def _check_in_header(ts,header):
    """ check header input, if correct return a dict"""
    
    hdic={}    
    if not ((type(header)==list) or (type(header)==tuple)):
        raise Value("invalid header input")
    
    for h in header:
        if type(h)==tuple:
            hdic[h[0]]=h[1]
        elif type(h)==type(" "):
            try:
                hdic[h]=ts.props[h]
            except:
                raise  StandardError("header items %s can't" 
                 "be found within input timeseris"%h)
    return hdic


def _fill_dic(hdic,ts):
    """ try to fill the unfinshed item h
    with attribute from ts if existing.
    it is here for the purpose of
    batch transfer still.
    """
    val_re=re.compile("\$\{(.+)\}")

    for (key,val) in hdic.items():
        vg=val_re.match(val)
        if vg:
            attr_name=vg.group(1)
            if hasattr(ts,attr_name):
                hdic[key]=getattr(ts,attr_name)
            elif attr_name in ts.props.keys():
                hdic[key]=ts.props[attr_name]
    return hdic
        
       
        
def _check_store_selection(ts,num_header,rvar,write_times):
    """check the validity of range selection. """
    if len(rvar)==5:
        st=rvar[2]
        et=rvar[4]
        if et-st+1<(len(ts)+num_header):
            print """"     Warning: your range selection
                   contain less cells than input time 
                   series length, part of data will not
                   be stored."""
        if write_times:
            sc=rvar[1]
            ec=rvar[3]
            if sc==ec:
                raise ValueError("You choose to store times, but your"
                " range selection contain only one column")
         
    
def _retrieve_rts(book,selection,time,**args):
    """ private helper funcs to retrieve rts from excel """

    #(sheet_name,range)=_parse_sheet_range(selection)
    if time==None: ## time is deferred from input args or headers
        return _retrieve_rts_no_time(book,selection,**args)
    elif time=="all": ## time is given for every pecice of ts
        return _retrieve_rts_all_time(book,selection,**args)
    else:
        return _retrieve_rts_col_time(book,selection,time,**args)


def _retrieve_rts_no_time(book,selection,**args):
    """ return ts when no time col is given,
        in such case, time start and interval
        are deferred from input arguments or from
        header, for instance:

        _retrieve_rts_no_time(file,selection,start=datetime(1991,1,1),interval=hours(1))
        ## comment, so in this case ts must have same start and interval,but may have
        ## different length
            name	martinez	rsac
            unit	feet	    cfs
                    1           50
                    2           101
                    .            .
                    .            .

        or:
        
        _retrieve_rts_no_time(file,selection,headerlabels=["name","start","interval"])
        ## comment, so in this case ts can have diffrent time stamps and varied length
            name	martinez	rsac
            interval	15min	1hour
            start	1-Jan-90	1-Feb-91
            unit	feet	    cfs
                    1           50
                    2           101
                    .           .
                    .           .

        comment on headerlabels: headerlabels can be a valid range contain labels, or
              list/tuple of labels. If not given in input, all the data within selection
              is treated as time series data only, so don't include any invalid data rows in
              your input selection in such a case. If header labels is given as 
    """
    
    rvar=_parse_range(selection)
    sheet=book.Worksheets(rvar[0])
    mix_re=_retrieve_start_intl(sheet,rvar,**args)

    if type(mix_re)==tuple:
       start_data_row=rvar[2]                 
    elif type(mix_re)==list:
       start_data_row=rvar[2]+len(mix_re[0][2])

    test_data_col1=rvar[1]
    test_data_col2=rvar[3]

    test_val=sheet.Range(test_data_col1+str(start_data_row)+":"\
                      +test_data_col2+str(start_data_row)).Value
    
    if type(test_val)==tuple:
        for val in test_val:
            for v in val: ##for excel return re like ((1,2,3),)
                if not isNumberType(v):
                    raise ValueError("invalid selection for ts data")
    else:
        if not isNumberType(test_val):
            raise ValueError("invalid selection for ts data")

    data_range=rvar[1]+str(start_data_row)+":"+rvar[3]+str(rvar[4])    
    ts_data=sheet.Range(data_range).Value
    ts_data=array(ts_data,float)    
    num_ts=ts_data.shape[1]
    tss=[]

    for i in range(num_ts):
        header_dic={}
        if type(mix_re)==tuple:
           start,intl=mix_re
        else:
            header_dic=mix_re[i][2]
            if "start" in header_dic.keys():
                del header_dic["start"]
            if "interval" in header_dic.keys():
                del header_dic["interval"]
            start=mix_re[i][0]
            intl=mix_re[i][1]
        ts=rts(ts_data[:,i],start,intl,header_dic)
        tss.append(ts)
    if len(tss)==1:
        return tss[0]
    else:
        return tss
            
def _retrieve_start_intl(sheet,rvar,**args):
    """ get start and intl from input or from sheet."""

    start_same=False ## if all ts share same start
    intl_same=False  ## if all ts share same intl

    start=None
    interval=None
    if "start" in args.keys():
        start=args["start"]
        del args["start"]
        if type(start)==type(" "):
            try:
                start=parse_time(start)
            except:
                raise ValueError("%s is not a valid time reprentation"%start) 
        start_same=True
        
    if "interval" in args.keys():
        interval=args["interval"]
        del args["interval"]
        if type(interval)==type(" "):
            try:
                interval=parse_interval(" ")
            except:
                raise ValueError("%s is not a valid interval reprentation"%interval) 
        intl_same=True

    header_dic_lst=None
    
    if "header_labels" in args.keys():
        header_labels=args["header_labels"]
        if header_labels:
            header_dic_lst=_retrieve_headers\
            (sheet,rvar,header_labels)    
    
    error_str="""  If you don't specify time range for
                 rts within spreadsheet, input arguments 
                 must contain start and interval, or list
                 of header_labels in case start and interval
                 info are presented within spreadsheet for
                 each rts."""    
    result=[]
    
    if header_dic_lst:
        for header_dic in header_dic_lst:
            if not start_same: ## if not give a uniform start, find
                               ## it in header dic
                try:
                    start=header_dic["start"]
                    if hasattr(start,"year"):
                        start=datetime(start.year,start.month,\
                                       start.day,start.hour,\
                                       start.minute)
                    else:
                        start=parse_time(str(start))
                    #del header_dic["start"]
                except:
                    raise ValueError("invalid or no start \
                    time specified for a rts")
            if not intl_same:
                try:
                    interval=header_dic["interval"]
                    interval=parse_interval(str(interval))
                    #del header_dic["interval"]
                except:
                    raise ValueError("invalid or no interval \
                    specified for a rts")
            result.append((start,interval,header_dic))
        return result        
    else:
        if (not start_same) or (not intl_same):
            raise ValueError(error_str)
        else:
            return (start,interval)
    
def _retrieve_headers(sheet,selection,header_labels):
    """ retrieve header values from range selection,
       return a dic use key defined in header_labels.
       selection is tuple of parsed range elements.
    """

    if type(header_labels)==type(" "): ##if header labels is given as range
                                       ##within same spreadsheet.
        try:
            ts=sheet.Range(header_labels).value
            header_labels=[]
            for t in ts:
                header_labels.append(str(t[0]))
                
        except:
            header_labels=None
                
    if not (type(header_labels)==type([])) and \
       not (type(header_labels)==type((2,3))):
        raise ValueError("header_labels must be given as list or tuple"
        " of labels or valid range within excel spreadsheet.")
    
    num_header_rows=len(header_labels)
    header_start_col=selection[1]
    header_start_row=selection[2]
    end_col=selection[3]
    header_end_col=end_col
    start_row=selection[2]
    header_end_row=start_row+num_header_rows -1   
    hr=header_start_col+str(header_start_row)+":"\
        +header_end_col+str(header_end_row)
    header_range=sheet.Range(hr)    

    val_lst=header_range.Value            
    val_lst=array(val_lst).transpose()
    hdiclst=[]        
    for hval in val_lst:
        header_dic=dict(zip(header_labels,map(str,hval)))
        hdiclst.append(header_dic)
    return hdiclst

_try_error_rows=10 ## find header labels by guess maximum number
                   ## of header elements.

def _retrieve_headers_by_tryerror(sheet,rvar,header_labels=None):
    """ retrieving header block within selection by try and error
        header_labels may contain range of label or list of labels,
        by defualt is none, search first col of time try to find
        labels.  rvar is parsed whole data selection.
    """

    test_start_row=rvar[2]                 
    test_data_col=rvar[1]

    if header_labels:
        if type(header_labels)==type(" "):
            try:
                header_labels=sheet.Range(hr).value
            except:
                header_labels=None
                
    find_header=False
    
    if (not(type(header_labels)==type([]))) and \
       (not(type(header_labels)==type((2,3)))):
        find_header=True
         
    if find_header: ## need to find header labels automatically
        end_row=test_start_row+_try_error_rows    
        guessed_header_range=sheet.Range(test_data_col+str(test_start_row)\
                            +":"+test_data_col+str(end_row))
        vals=guessed_header_range.Value
        header_labels=[]
        for val in vals:
            if type(val)==tuple:
                val=val[0]
            if not hasattr(val,"hour"): ##decide if this val is a pytime
                header_labels.append(str(val))
            else:
                break
            
        if header_labels==[None]:
            header_labels=["name"]
            
    if header_labels==[]:
        return(None,test_start_row)
            
    r1=sheet.Range(test_data_col+str(test_start_row))
    header1=r1
    #header1=r1.Offset(-1,0)
    header_end_col=rvar[3]
    header_end_row=test_start_row+len(header_labels)-1
    header2=sheet.Range(header_end_col+str(header_end_row))
    header_vals_lst=sheet.Range(header1,header2).Value    
    temp=[]
    for header_vals in header_vals_lst:
        header_vals=list(header_vals)
        header_vals.pop(0)
        header_vals=map(str,header_vals)
        header_vals=filter(lambda x: not(x=="None"),header_vals)
        temp.append(header_vals)
        
    tdic=[]
    temp=array(temp).transpose()
    for header_vals in temp:
        tdic.append(dict(zip(header_labels,header_vals)))
        
    return (tdic,test_start_row+len(header_labels)) ##first output is list of header dic, second
                                                   ##is start row of ts data block.

def _format_single_col_vals(val_lst):
    """ flatten structure of returned string values list from excel
        
    """
    t=[]
    for val in val_lst:
        if type(val)==tuple:
           tt=val[0]
        else:
           tt=val
        t.append(str(tt))
    return t
    
def _parse_range(selection):
    """based on selection string,return sheet name,start col,start row
       end col and end row as a tuple.
    """
    if ":" in selection: #range pattern
        range_pattern=re.compile("(.+?)\$(\D+?)(\d+?)\:(\D+?)(\d+?)$")
        gg=range_pattern.match(selection)
        if not gg:
            raise ValueError("%s is not a valid excel range"%selection)
        return (gg.group(1),gg.group(2),int(gg.group(3)),\
                gg.group(4),int(gg.group(5)))
    else: ## try cell pattern
        cell_pattern=re.compile("(.+?)\$(\D+?)(\d+?)$")
        gg=cell_pattern.match(selection)
        if not gg: ## thus treate it is as a sheet name only, default
                   ## set writing start at B5
            return (selection,"B",5)
            #raise ValueError("%s is not a valid excel range"%selection)
        return (gg.group(1),gg.group(2),int(gg.group(3)))

    
def _retrieve_rts_all_time(book,selection,**args):
    """ return ts when all times are given to the left of each data col"""
    
    rvar=_parse_range(selection)
    sheet=book.Worksheets(rvar[0])

    if "header_labels" in args.keys():
        header_labels=args["header_labels"]
    else:
        header_labels=None

    (header_lst,data_start_row)=_retrieve_headers_by_tryerror\
                                 (sheet,rvar,header_labels)
    
    data_range=sheet.Range(rvar[1]+str(data_start_row)+":"+rvar[3]+str(data_start_row))
    ts_time_data=data_range.Value   
    num_ts=len(ts_time_data[0])/2

    tsl=[]

    t1=sheet.Range(rvar[1]+str(data_start_row))
    col=t1.Columns[0].Column
    t2=sheet.Cells(data_start_row+3,col)
    d1=sheet.Cells(data_start_row,col+1)
    d2=sheet.Cells(rvar[4],col+1)
    
    for i in range(0,num_ts):  
        ts_time=sheet.Range(t1,t2).Value
        tt0=ts_time[0][0]
        tt1=ts_time[1][0]
        tt0=datetime(tt0.year,tt0.month,tt0.day,tt0.hour,tt0.minute)
        tt1=datetime(tt1.year,tt1.month,tt1.day,tt1.hour,tt1.minute)
        data=sheet.Range(d1,d2).Value
        data=array(data)
        
        if data.shape[1]==1:
            data=data.flatten()
            
        if header_lst:
            ts=rts(data,tt0,tt1-tt0,header_lst[i])
        else:
            ts=rts(data,tt0,tt1-tt0)
            
        tsl.append(ts)
        col=col+2
        t1=sheet.Cells(data_start_row,col)
        t2=sheet.Cells(data_start_row+3,col)
        d1=sheet.Cells(data_start_row,col+1)
        d2=sheet.Cells(rvar[4],col+1)        
        
    if len(tsl)==1:
        return tsl[0]
    else:
        return tsl
    
def _retrieve_rts_col_time(book,selection,time_range,**args):
    """ return ts when all ts share a common time col """

    rvar=_parse_range(selection)
    sheet=book.Worksheets(rvar[0])

    if "header_labels" in args.keys():
        header_labels=args["header_labels"]
    else:
        header_labels=None

    (header_lst,data_start_row)=_retrieve_headers_by_tryerror\
                                 (sheet,rvar,header_labels)
    

    time_range=sheet.Range(rvar[1]+str(data_start_row)+":"+rvar[1]+str(rvar[4]))
    col=time_range.Columns[0].Column+1
    data_range_start=sheet.Cells(data_start_row,col)
    data_range_end=sheet.Range(rvar[3]+str(rvar[4]))
    data_range=sheet.Range(data_range_start,data_range_end)
    
    ts_time=time_range.Value  ## block contain all time and data  
    ts_data=data_range.Value
    ts_data=array(ts_data,float)
        
    num_ts=ts_data.shape[1]

    tsl=[]
    t0=ts_time[0][0]
    t1=ts_time[1][0]
    t0=datetime(t0.year,t0.month,t0.day,t0.hour,t0.minute)
    t1=datetime(t1.year,t1.month,t1.day,t1.hour,t1.minute)
    intl=t1-t0
    
    for i in range(1,num_ts+1):
        data=ts_data[:,i-1]
        #data=array(data)
        ts=rts(data,t0,intl,header_lst[i-1])
        tsl.append(ts)
        
    if len(tsl)==1:
        return tsl[0]
    else:
        return tsl
    
    
def _pytime2datetime(p):
    return datetime(p.year,p.month,p.day,p.hour,p.minute)


def _strip_ending_none(data):
    """ remove contiouse trailing none from one dimensional array
        or list.
    """
    i=len(data)-1
    while not data[i]:
        i=i-1
        
    return data[0:i+1]

def _retrieve_ts(book,selection,time_column,**args):
    """ private helper funcs to retrieve mixed its 
    from excel.
    """
    rvar=_parse_range(selection)
    sheet=book.Worksheets(rvar[0])

    if "header_labels" in args.keys():
        header_labels=args["header_labels"]
    else:
        header_labels=None

    (header_lst,data_start_row)=_retrieve_headers_by_tryerror\
                                 (sheet,rvar,header_labels)
    
    data_range=sheet.Range(rvar[1]+str(data_start_row)+":"+rvar[3]+str(data_start_row))
    ts_time_data=data_range.Value   
    num_ts=len(ts_time_data[0])/2
    tsl=[]

    t1=sheet.Range(rvar[1]+str(data_start_row))
    col=t1.Columns[0].Column
    t2=sheet.Cells(rvar[4],col)
    d1=sheet.Cells(data_start_row,col+1)
    d2=sheet.Cells(rvar[4],col+1)    
    
    for i in range(0,num_ts):
        ts_time=sheet.Range(t1,t2).Value
        ts_data=sheet.Range(d1,d2).Value
        ts_time=array(ts_time).flatten()
        ts_data=array(ts_data).flatten()
        
        ## removing possilbe trailing none
        ts_time=_strip_ending_none(ts_time)
        ts_data=ts_data[0:len(ts_time)]
        
        ts_time=map(_pytime2datetime,ts_time)
        
        if header_lst:
            ts=its(ts_time,ts_data,header_lst[i])
        else:
            ts=its(ts_time,ts_data)
        tsl.append(ts)
        col=col+2
        t1=sheet.Cells(data_start_row,col)
        t2=sheet.Cells(rvar[4],col)
        d1=sheet.Cells(data_start_row,col+1)
        d2=sheet.Cells(rvar[4],col+1)         
        
    if len(tsl)==1:
        return tsl[0]
    else:
        return tsl


    



     
    
    
