
## some constants used by pydss lib
UNDEFINED=0
REGULARTS=100
IRREGULARTS=110
PAIRTS=200
TEXT=300


DSS_MAX_FILE_NUM=200
DSS_PATH_LENGTH=6

########################################

DSS_DATA_SOURCE="vtools.datastore.dss.DssService"

##DSS_REGULAR_TIME_SERIES="vtools.datastore.dss.regulartimeseries"
##DSS_IRREGULAR_TIME_SERIES="vtools.datastore.dss.irregulartimeseries"

# The maximum number of points allowable to retrieve
# from a irregualr time sereis path in one time
DSS_MAX_ITS_POINTS=1000
# The maximum number of points allowable to retrieve
# from a regualr time sereis path in one time
DSS_MAX_RTS_POINTS=35000

## The maximum number of array size used in
## retrieving data from a path, usually dss
## max block size is around 3000, so 4000
## is enough
DSS_MAX_DATA_SIZE=4000

## The maximum number of header item allowed within one
## record.
DSS_MAX_HEADER_ITEMS=100

## maximum length of header label and items
DSS_MAX_HEADER_LEN=20

## The list properties of rts and its
## that is not part of header
CDATE="cdate"
CTIME="ctime"
FLAGS="flags"
LFLAGS="lflags"
CUNITS="cunits"
CTYPE="ctype"
IPLAN="iplan"
ICOMP="icomp"
BASEV="basev"
LHIGH="lhigh"
IPREC="iprec"
ITIMES="itimes"
JBDATE="jbdate"

NOT_DSS_HEADER_PROP=[CDATE,CTIME,FLAGS,LFLAGS,\
                 CUNITS,CTYPE,IPLAN,ICOMP,\
                 BASEV,LHIGH,IPREC,ITIMES,\
                 JBDATE]

