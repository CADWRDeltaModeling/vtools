"""Examples of retrieve and strore time series from or into
   a excel file.
"""

## import necessary vtools lib.
from vtools.datastore.excel.api import *

###########################################################
### examples to retrieve time series from a excel source ####
###########################################################

## giving a existing datasource.
source="mustbeexist.xls"

## to retrieve all regular time series stored at
## a specific range (data only) within excel sheet,
## user supply indentical start time and interval
## for all time series, for instance:
##      1.2	0.3	-0.6	-1.5	-2.4
##      1.3	0.9	-0.6	-1.5	-2.4
##      1.4	1.5	-0.6	-1.5	-2.4
##      1.5	2.1	-0.6	-1.5	-2.4


selector="sheet1$B10:F200" ##this selection must contain data only
ts_type="rts"
start=datetime(2001,10,15,12)
intl=minutes(15)
tss=excel_retrieve_ts(source,selector,ts_type,\
                    start=start,interval=intl)

## Similar to previous example, with except user' selector contain
## time sereis header items in addition to data, then user must
## supply header labels list, for instance:
##         cfs	     cfs	feet	cfs	     feet
##         RSAC054	RSAC009	RSAC102	RSAC106	RSAC087
##         1.2	      0.3	-0.6	-1.5	-2.4
##         1.3	      0.9	-0.6	-1.5	-2.4
##         1.4	      1.5	-0.6	-1.5	-2.4


selector="sheet1$B8:F200" ## header items must be located at every begining
                          ## rows of range selection,selection should contain
                          ## header vals and data vals only.
ts_type="rts"
start=datetime(2001,10,15,12)
intl=minutes(15)
tss=excel_retrieve_ts(source,selector,ts_type,\
                    start=start,interval=intl,header_labels=["name","unit"])

## to retrieve all regular time series stored at
## a specific range (data and headers) within excel sheet,
## the start time and interval for each ts is found at
## headers above data, user should provide a header label
## list contains the "interval" and "start" in the order of
## header appearing in spreadsheet. For instance:
##      15min	         1hour	         1day	        30min	        1mon
##      3/12/2001 15:15	3/12/2001 15:15	3/12/2001 15:15	3/12/2001 15:15	3/12/2001 15:15
##      RSAC054	        RSAC009	        RSAC102	        RSAC106	         RSAC087
##       1.2	         0.3	        -0.6	        -1.5	         -2.4
##       1.3	         0.9	        -0.6	        -1.5	         -2.4
##       1.4	         1.5	         -0.6	        -1.5	         -2.4

selector="sheet1$B10:F200" ##this selection must contain data val and header vals only
ts_type="rts"
tss=excel_retrieve_ts(source,selector,ts_type,header_labels=["interval","start","name"])
 ## this example almost same as previous one,with except user specify a strings store
 ## within a range as header labels. 
tss=excel_retrieve_ts(source,selector,ts_type,header_labels="N8:N10")


## to retrieve all regular time series stored at
## a specific range (data and headers) within excel sheet,
## data times is given to the right of each data col 
## name	    RSAC054		               RSAC009		       RSAC102		          RSAC106		         RSAC087
## 3/12/2001 8:00	1.2	3/12/2001 8:30	0.3	3/12/2001 0:00	-0.6	3/12/2001 8:30	-1.5	3/12/2001 8:30	-2.4
## 3/12/2001 8:15	1.3	3/12/2001 9:30	0.9	3/13/2001 8:30	-0.6	3/12/2001 8:45	-1.5	3/12/2001 9:15	-2.4
## 3/12/2001 8:30	1.4	3/12/2001 10:30	1.5	3/14/2001 17:00	-0.6	3/12/2001 9:00	-1.5	3/12/2001 10:00	-2.4
selection="sheet1$w14:AF118"
ts_type="rts"
tss=excel_retrieve_ts(source,selection,ts_type,time="all",\
                      header_labels=["name"])

## to retrieve all regular time series stored at
## a specific range (data and headers) within excel sheet,
## data times is given to the left of the first data col, that
## means all ts share the same time.for instance
##   name	       RSAC054	 RSAC009	RSAC102	 RSAC106	RSAC087
## 3/12/2001 8:00	 1.2	     0.3	-0.6	 -1.5	    -2.4
##3/12/2001 8:15	 1.3	     0.9	-0.6	 -1.5	    -2.4
##3/12/2001 8:30	 1.4	     1.5	-0.6	 -1.5	    -2.4
##3/12/2001 8:45	1.5	         2.1	-0.6	 -1.5	    -2.4

selection="sheet1$A125:F229"
ts_type="rts"
tss=excel_retrieve_ts(excel_file,selection,ts_type,time="auto",\
                              header_labels=["name"])
 

## to retrieve all  irregular time series stored at
## a specific range (data and headers) within excel sheet,
## data times is given to the left of the each data col, all
## the ts will be treated as irregular ts
selection="sheet1$w14:AF118"
ts_type="its"
tss=excel_retrieve_ts(excel_file,selection,ts_type,time="all",\
                      header_labels=["name"])



###########################################################
### examples to store time series into a excel source     ####
###########################################################

## assume there is a list of ts or single ts.
tss=[ts1,ts2,ts3] ## tss=ts1 is also fine
excel_file="not_necessary_exist.xls" ## source can be a existing or not existing file

## save data and time to sheet with name of sheet1, with starting cell is B23
selection="sheet1$B23"
## also user want to save name and daturm header of ts into file also
header=["name","datum"] ## This input is optional,if don't want to save headers,
                        ## just leave it or set it none.
excel_store_ts(tss,excel_file,selection,header=["name","datum"])

## if user want to limited maximum number of length of time series to be stored,
## they can specify a range.
selection="sheet1$B23:C1023" ## range for the first ts is enough (should be two
                             ## neighboring cols,for time is also asked to be stored by
                             ## default)
excel_store_ts(tss,excel_file,selection,header=["name"])


## user can choose not storing times
selection="sheet1$B23" ## starting cells
excel_store_ts(tss,excel_file,selection,header=["name"],write_times="none")
## also without headers
excel_store_ts(tss,excel_file,selection,write_times="none")

## user can choose storing the times for the first time series
## in the input list only.
selection="sheet1$B23" ## starting cells
excel_store_ts(tss,excel_file,selection,header=["name"],write_times="first")

