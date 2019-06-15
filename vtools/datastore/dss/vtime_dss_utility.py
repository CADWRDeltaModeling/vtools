
# Standard library import
#import pdb
import datetime
from string import upper
import copy
# scipy import
from scipy import nan,isnan,where,array,\
     arange,compress,zeros

# pydss import
from pydss.hecdss import zofset

# vtools import 
from vtools.data.timeseries import TimeSeries
from vtools.data.vtime import * 
from vtools.data.timeseries import rts,its
from vtools.data.constants import *

# local import
from .dss_constants import *

########################################################################### 
# Public interface.
###########################################################################

__all__=["valid_dss_interval_seconds","valid_dss_interval_dic_in_mins",\
         "valid_dss_interval_dic_in_delta","validate_rts_for_dss",\
         "string_to_dss_julian_date","dss_julian_date_to_string",\
         "datetime_to_dss_julian_date","dss_rts_to_ts",\
         "dss_its_to_ts","validate_its_for_dss",\
         "discover_valid_rts_start","discover_valid_rts_end","dss_julian2python",
         "uncondensed_Dparts","interval_to_D"]

valid_dss_interval_seconds=[60,120,180,240,300,360,600,900,1200,1800,3600,7200,10800,14400,21600,\
                            28800,43200,86400,604800,2592000,31536000]

valid_dss_interval_dic_in_mins={"1MIN":1,"2MIN":2,"3MIN":3,"4MIN":4,"5MIN":5,"6MIN":6,"10MIN":10,\
                                "15MIN":15,"20MIN":20,"30MIN":30,"1HOUR":60,"2HOUR":120,\
                                "3HOUR":180,"4HOUR":240,"6HOUR":360,"8HOUR":480,"12HOUR":720,\
                                "1DAY":1440,"1WEEK":10080,"1MON":43200,"1YEAR":518400}

valid_dss_interval_dic_in_delta=[time_interval(minutes=1),time_interval(minutes=2),time_interval(minutes=3),
                                 time_interval(minutes=4),time_interval(minutes=5),time_interval(minutes=6),time_interval(minutes=10),
                                 time_interval(minutes=15),time_interval(minutes=20),time_interval(minutes=30),
                                 time_interval(hours=1),time_interval(hours=2),time_interval(hours=3),
                                 time_interval(hours=4),time_interval(hours=6),time_interval(hours=8),time_interval(hours=12),
                                 time_interval(days=1),time_interval(days=7),time_interval(months=1),time_interval(years=1)]

## convert a interval object into string repr for D part
interval_to_D=["1MIN","2MIN","3MIN","4MIN","5MIN","6MIN","10MIN","15MIN","20MIN","30MIN",\
             "1HOUR","2HOUR","3HOUR","4HOUR","6HOUR","8HOUR","12HOUR",\
             "1DAY","1WEEK","1MON","1YEAR"]


_one_day=time_interval(days=1)
_one_month=time_interval(months=1)
_one_year=time_interval(years=1)
_one_decade=time_interval(years=10)
_one_century=time_interval(years=100)

_dss_block_size={"1MIN":_one_day,"2MIN":_one_day,"3MIN":_one_day,"4MIN":_one_day,"5MIN":_one_day,"6MIN":_one_day,"10MIN":_one_day,\
                "15MIN":_one_month,"20MIN":_one_month,"30MIN":_one_month,"1HOUR":_one_month,"2HOUR":_one_month,\
                "3HOUR":_one_month,"4HOUR":_one_month,"6HOUR":_one_month,"8HOUR":_one_month,"12HOUR":_one_month,\
                "1DAY":_one_year,"1WEEK":_one_decade,"1MON":_one_decade,"1YEAR":_one_century,"IR-DAY":_one_day,\
                 "IR-MONTH":_one_month,"IR-YEAR":_one_year,"IR-DECADE":_one_decade}

        
def validate_rts_for_dss(rt):
    """ Validate the time and property of
        regualr time series for storage in dss.
    """

    if type(rt)==TimeSeries:
        (flags,lflags,cunits,cdate,ctime)=\
        _validate_properties_of_regular_timeseries(rt)
        
        aggregation_before_translate=INDIVIDUAL
        aggregation=INDIVIDUAL
        ## this is the props going to be reurned
        corrected_props=copy.deepcopy(rt.props) 
        if rt.props and (AGGREGATION in list(rt.props.keys())):
            aggregation=rt.props[AGGREGATION]
            aggregation_before_translate=aggregation
            #remove this aggregation item,for it is not needed in dss storage
            del corrected_props[AGGREGATION] 
        else:
            aggregation=INDIVIDUAL
        ## if aggregation need to be translate into dss term 
        if aggregation in list(RTS_VT_PROPTY_TO_DSS.keys()):
            aggregation=RTS_VT_PROPTY_TO_DSS[aggregation]        
        
        ctype=aggregation
        
        if rt.props and (TIMESTAMP in list(rt.props.keys())):
            timestamp=rt.props[TIMESTAMP]
            #remove this timestamp for it is not needed in dss storage
            del corrected_props[TIMESTAMP]
        else:
            timestamp=INST    
                   
        if aggregation_before_translate in [MEAN,MAX,MIN] and timestamp==PERIOD_START:
            (cdate,ctime)=_move_start_forward_a_interval(rt)
                   
    else:
        raise TypeError("input is not type of TimeSeries in validating rts for dss storage")

    return (flags,lflags,cunits,ctype,cdate,ctime,corrected_props)


def string_to_dss_julian_date(sdate):

    return _string_to_dss_julian_date(sdate)

def dss_julian_date_to_string(jdate,time_unit):
    """ Jdate must be in minutes."""

    dss_juilan_base=parse_time("31-DEC-1899")

    if time_unit=="hour":
        jdate=jdate*60
    elif time_unit=="second":
        jdate=jdate/60
    elif time_unit=="day":
        jdate=jdate*24*60

    d=dss_juilan_base+minutes(jdate)

    return d.isoformat(' ')



def datetime_to_dss_julian_date(dtime):
    """ Convert a  datetime to dss julian dates (start from 12/31/1899).
    """
    dss_juilan_base=parse_time("31-DEC-1899")
    dss_julian_day=(dtime-dss_juilan_base).days 
    return dss_julian_day

##def retrieve_value_at_bits_n(val,n):
##    """ return the bit vlaue at specified location n in val """
##    v=val>>(n-1)
##    return v&1

def dss_rts_to_ts(data,startdate,starttime,time_interval,iofset,prop=None,flags=None):
    """ Convert dss file time seris into TimeSeries class.
    data: array of values
    startdate: start date of time windows desired as string conformed to dss style
    starttime: start time of time windows desired as string conformed to dss style
    time_interval: time interval of time windows desired as mintues conformed to dss style
    prop: dict save info get from dss func
    flags:list of data quality flag returned by zrrtx or zrrtsx
        
    adjustment of  startdatetime of regular time series with
    averaging aggreation setting:
    read from dss: starttime need to be move backward a interval
    store into dss: startime need to be move forward a interval
    """
            
    #string stardate need to converted to julian date in days.
    jul=_string_to_dss_julian_date(startdate)

    #string startime need to be converted to minutes passed midnight.
    itime=_string_time_to_minutes(starttime)
    #string time_interval need to be converted to mintues.
    intl=_string_interval_to_minutes(time_interval)
    
    #this part to get the startdate and time of first value returned.
    [jul,itime,iofset]=zofset(jul,itime,intl,2,iofset)


    start_datetime=_dss_julian_datetime_to_python_datetime(jul,itime)
    interval_timedelta=parse_interval(time_interval)

    if not prop:
        prop={}
        
    #some operation on property dic
    relative_interval=None
    ## is it PER-AVE,PER-MIN, PER-MAX...
    isAggregated=False
    if CTYPE in list(prop.keys()):
        tsstype=prop[CTYPE]
        #translate vtools time aggreation term into dss term
        # Todo: make the automatic conversion a user controlled
        # those handlinges for the type of mean,min,max over a period only     
        if tsstype in list(RTS_DSS_PROPTY_TO_VT.keys()):
           #start_datetime=start_datetime-interval_timedelta
           isAggregated=True
           prop[TIMESTAMP]=PERIOD_START
           prop[AGGREGATION]=RTS_DSS_PROPTY_TO_VT[tsstype]
        elif tsstype in list(RTS_DSS_PROPTY_TO_VT.values()):
           #start_datetime=start_datetime-interval_timedelta
           isAggregated=Ture
           prop[TIMESTAMP]=PERIOD_START
           prop[AGGREGATION]=tsstype
        else:
           prop[TIMESTAMP]=INST
           prop[AGGREGATION]=INDIVIDUAL
                
        # del ctype for vtools ts don't need it    
        del prop[CTYPE]
    else: 
        prop[TIMESTAMP]=INST
        prop[AGGREGATION]=INDIVIDUAL

    (data,starti)=_validate_dss_data_series(data,flags)
    if not(isAggregated):
        start_datetime=increment(start_datetime,interval_timedelta,starti)
        ts= rts(data,start_datetime,interval_timedelta,prop)
        return ts
    else:
        ## if begining of continueous valid data start at the begining of
        ## data read back, then the first data is out of reading time window
        ## should be get rid of
        if starti==0:
            dataOneLess= data[1:len(data)]
            ts= rts(dataOneLess,start_datetime,interval_timedelta,prop)
            return ts
        ## then first valid data is at least located at the early side of reading
        ## time window, it should be kept
        else:
            ## use starti-1 here for vtools aggregated data is stamped on the
            ## begining of interval, we need to more time read back from dss file
            ## one interval back
            start_datetime=increment(start_datetime,interval_timedelta,starti-1)
            ts= rts(data,start_datetime,interval_timedelta,prop)
            return ts
            
def dss_its_to_ts(data,jbdate,itimes,prop,flags):
    """ Convert dss irregular time series into TimeSeries class.
    data:   list of raw data returned by zrits or zritsx
    jbadte: integer dss base date returned by zrits or zritsx
    itimes: offset list in minutes from base date for each time point
            it is also generated by zritx or zritsx
    prop:   dict save info get from dss func
    flags:  list of data quality flag returned by zritx or zritsx
    """

    if len(itimes)<len(data):
        raise ValueError("lenght of input itimes must not be less than data")

    (data,start_i)=_validate_dss_data_series(data,flags)
    itimes=itimes[start_i:start_i+len(data)]
    
    ts=None
    new_times=[]
    
    for itime in itimes:
        a_time=_dss_julian_datetime_to_python_datetime(jbdate,itime)
        new_times.append(a_time)
        
    new_times.sort()
    
    prop[TIMESTAMP]=INST
    prop[AGGREGATION]=INDIVIDUAL   
    ts= its(new_times[start_i:start_i+len(data)],data,prop)    
    return ts

def dss_julian2python(jbdate,itime):
    
    return _dss_julian_datetime_to_python_datetime(jbdate,itime)

def validate_its_for_dss(irrts):
    """ Validate parameters and create input
        necessary for a its to store in dss.
    """    
    itimes=_itimes_from_ts_ticks(irrts.ticks,irrts.start)
    flags=zeros(1)
    lflags=False
    jbdate=_datetime_to_dss_julian_days(irrts.start)

    if irrts.props and UNIT in list(irrts.props.keys()):
        cunit=irrts.props[UNIT]
    else:
        cunit=UND

    ctype=INST
    
    return (itimes,flags,lflags,jbdate,cunit,ctype,irrts.props)

def discover_valid_rts_start(data,start,interval):
    """ given the rts data seq., which may contain empty data markers (e.g. -902)
        at begin or end, find out the datetime of first valid number
        and return.
        start, and interval must be datetime and timedelta respectively.
    """

    starti,l=_validate_dss_data_series(data,OnlyStartLen=1)
    return increment(start,interval,starti)

def discover_valid_rts_end(data,start,interval):
    """ given the rts data seq., which may contain continous invalid dss number
        at begin or end of sequence, find out the datetime of last valid number
        and return.
        start, and interval must be datetime and timedelta respectively.
    """

    l,endi=_validate_dss_data_series(data,OnlyStartLen=1)
    return increment(start,interval,endi)



def uncondensed_Dparts(interval_str,start_str,end_str):
    """" Generates list of uncondensed D parts according to star,
    end of block and interval

         interval_str is Epart,start_str is a Dpart         
    """

    st=parse_time(start_str)
    et=parse_time(end_str)
    intl=_dss_block_size[interval_str.upper()]
    ni=number_intervals(st,et,intl)
    tlst=time_sequence(st,intl,ni+1)
    tlst=list(map(ticks_to_time,tlst))
    nt=[d.strftime("%d%b%Y") for d in tlst]
    return nt
    
        

########################################################################### 
# Private interface.
###########################################################################

def _validate_properties_of_regular_timeseries(rt):
    """ For the use of storing regular timeseries into dss file, make sure the time series has
        property value sets for dss storage, if not default values will be set
        but for time_interval property it must have a string representation of
        time interval in dss tradition, or error will happen.
    """
    
    #props=rt.props

    if not(rt.is_regular()):
        raise ValueError("input timeseries is not regular")
    else:
        interval=rt.interval #interval saved as timedelta or relativedelta       
        _validate_interval_of_regualr_timeseries(interval)
        
    #validate flags
##    if not(FLAGS in rt.props.keys()):
##        rt.props[FLAGS]=0
##        rt.props[LFLAGS]=False
##
##    if not(LFLAGS in rt.props.keys()):
##        rt.props[LFLAGS]=False
    flags=False
    lflags=None
    
    if rt.props and (UNIT in list(rt.props.keys())):
        cunits=rt.props[UNIT]
    else:
        cunits=UND

        
##    ## An observation: how about when writing
##    ## to a existing path, which has ctype
##    ## defined but unkown to the user?
##    ## A good practice is to often define ctype
##    ## explicitly in rt.props, which should
##    ## be consistent with aggregation property
##    ## and ctype of the existing path.
##    if not(CTYPE in rt.props.keys()):
##        if AGGREGATION in rt.props.keys() and \
##           rt.props[AGGREGATION]==MEAN:
##            rt.props[CTYPE]="PER-AVER"
##        else:
##            rt.props[CTYPE]="INST-VAL"

    ## add cdate and ctime info also, it might
    ## be modified later if data is aggreated
    start=rt.start  
    date_format="%d%b%Y"
    hourmin_format="%H%M"
    cdate=start.strftime(date_format)
    ctime=start.strftime(hourmin_format)
    #rt.props[CDATE]=cdate
    #rt.props[CTIME]=ctime        
        
    return (flags,lflags,cunits,cdate,ctime)

def _validate_interval_of_regualr_timeseries(interval):
    """ for the use of storing regular timeseries into dss file, 
        make sure the time interval used by time series is legal
        for dss system.
    """

    if type(interval)==int:        
        interval_seconds=interval/ticks_per_second
        if not (interval_seconds in valid_dss_interval_seconds):
            raise ValueError("%d is incorrect time interval for dss storage"%interval_second)
    elif type(interval)==type("st"):
        if not (upper(interval) in list(valid_dss_interval_dic_in_mins.keys())):
            raise ValueError("%s is incorrect time interval for dss storage"%interval)
    elif type(interval)==type(time_interval(hours=1)) or type(interval)==type(time_interval(years=1)):
        if not interval in valid_dss_interval_dic_in_delta:
            raise ValueError("%s is incorrect time interval for dss storage"%interval)  
    else:
        raise TypeError("input into function _validate_interval_of_regular_timeseries"
                        " must be \ or ticks or timedelta or relativedelta")

def _move_start_forward_a_interval(rt):
    """ Move the start point of regular ts to store in dss file."""
       
    if not rt.is_regular():
        raise ValueError("Only regular timeseries accepted to move start time.")
    
    interval=rt.interval ## it is timedelta.
    start=rt.start
    dss_start=start+interval   
    date_format="%d%b%Y"
    hourmin_format="%H%M"
    cdate=dss_start.strftime(date_format)
    ctime=dss_start.strftime(hourmin_format)
    return (cdate,ctime)
    #rt.props["cdate"]=cdate
    #rt.props["ctime"]=ctime


def _string_to_dss_julian_date(sdate):
    """ Convert a string date to dss julian dates (start from 12/31/1899)
        sdate must in in format as '12JAN1987'.
    """
    dss_julian_day=1
    if not(len(sdate)==9):
        err_str= "%s is not the format acceptable to function \
        utility_string_to_dss_julian_date,use example '12JAN1987'"%sdate
        raise ValueError(err_str)

    sdate=sdate[0:2]+"-"+sdate[2:5]+"-"+sdate[5:9]
    d1=parse_time(sdate)
    dss_juilan_base=parse_time("31-DEC-1899")
    dss_julian_day=(d1-dss_juilan_base).days    
    return dss_julian_day

def _string_time_to_minutes(stime):
    """ to convert a string time into num of minutes pass midnight
        must be in form of '0430', hours 0-23
    """
    num_time=1

    if not(len(stime)==4):
        err_str= "%s is not the format acceptable to function \
        utility_string_time_to_minutes,use example '1430'"%stime
        raise ValueError(err_str)
    
    hours=int(stime[0:2])
    mins=int(stime[2:4])
    num_time=hours*60+mins
    return num_time

def _string_interval_to_minutes(time_interval):
    """
        Convert string time_interval to mintues (nominaly in dss tradition,
        it is important to use function zoffset from dss lib).
    """
    num_min=1

    if not(time_interval in list(valid_dss_interval_dic_in_mins.keys())):
        err_str= "%s is not a valid dss regular time interval"%time_interval
        raise ValueError(err_str)
    
    num_min=valid_dss_interval_dic_in_mins[time_interval]       
    return num_min

def _dss_julian_datetime_to_python_datetime(jul,itime):
    """ Convert dss julian date and time to datetime
        jul is int in days,itime is int in minutes.
    """
    dss_juilan_base=parse_time("31-DEC-1899")
    jul=int(jul)
    itime=int(itime)
    d=dss_juilan_base+days(jul)+minutes(itime) 
    return d

## two binary int for testing flag bits values  
_d1=int('00011',2)
_d2=int('11100',2)    

def _validate_dss_data_series(data,flags=None,OnlyStartLen=0):
    """ Validate the values of data, replace invalid data with NaN. """
    if not(flags is None):
        if len(flags)<len(data):
            err_str= "not enough data flags for data series"
            raise ValueError(err_str)
        if not type(flags)==type(array([2,3])):
            flags=array(flags)

    if not type(data)==type(array([2,3])):
        data=array(data)
    data=where((data==float(-901)) | (data==float(-902)),nan,data)
    ## set nan according to if 3,4,5 bits of flag set or not.
    ## operation is implemented by bit_wise or/and.
    if not(flags is None):
        ## filter out those invalid flags.
        flags=where((flags==int(-901)) | (flags==int(-902)),0,flags)
        data=where(((flags|_d1)&_d2),nan,data)
    
    ## Here is a handling findout those possible continoues
    ## nan at the begin and end of data array, for those
    ## nan are generated by wider time window used than
    ## actual data time span.
    ii=arange(len(data))
    indexes=where(isnan(data),-1,ii)
    ii=compress(indexes!=-1,indexes)

    ## it maybe possible all the data are nan.then
    ## ii is a empty array.
    if not len(ii):
        first_nonnan_i=-1
        last_nonnan_i=-1
        if OnlyStartLen:
            return (first_nonnan_i,last_nonnan_i)
        else:
            return (numpy.array([]),first_nonnan_i)
    else:
        first_nonnan_i=ii[0]
        last_nonnan_i=ii[-1]+1
    
    if OnlyStartLen:
        return (first_nonnan_i,last_nonnan_i)
    else:
        return (data[first_nonnan_i:last_nonnan_i],first_nonnan_i)
        #return (data[first_nonnan_i:(ii[-1]+1)],first_nonnan_i)
                               
##def _adjust_times_by_a_relative_interval(ls_times,dt):
##    """ Add relative time delta to every member of times."""
##    
##    if hasattr(ls_times,"_iter_"):
##        if type(dt)==relativedelta.relativedelta:
##            new_ls=[]
##            for a_time in ls_times:
##                a_time=a_time+dt
##                new_ls.append(a_time)
##            new_ls.sort()
##            return new_ls

def _ticks_to_dss_julian_days(ticks):

    dss_juilan_base=parse_time("31-DEC-1899")
    a_time=ticks_to_time(ticks)

    delta=a_time-dss_juilan_base
    return delta.days

def _datetime_to_dss_julian_days(time):

    dss_juilan_base=parse_time("31-DEC-1899")

    delta=time-dss_juilan_base
    return delta.days

def _itimes_from_ts_ticks(tticks,start_datetime):
    
    """ Create a times squence (in mins) suitable for dss file
        storage based on a ticks series.
    """
    
    year=start_datetime.year
    month=start_datetime.month
    day=start_datetime.day
    basedate=datetime.datetime(year=year,month=month,day=day)
    start_ticks=ticks(basedate)
    itimes=[(ttick-start_ticks)/ticks_per_minute for ttick in tticks]

    return itimes
