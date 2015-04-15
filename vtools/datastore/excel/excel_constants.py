
MAX_TS_AT_A_TIME=20
MAX_TS_LEN=64000
EXCEL_DATA_SOURCE="vtools.datastore.excel.ExcelService"


VAR_NAME="var_name"
START_TIME="start_time"
TIME_INTERVAL="time_interval"
DATA_TYPE="data_type"
DATA_UNIT="data_unit"


ll=['A','B','C','D','E',\
                   'F','G','H','I','J',\
                   'K','L','M','N','O',\
                   'P','Q','R','S','T',\
                   'U','V','W','X','Y','Z'
                   ]

EXCEL_COLUMN_NAME=['A','B','C','D','E',\
                   'F','G','H','I','J',\
                   'K','L','M','N','O',\
                   'P','Q','R','S','T',\
                   'U','V','W','X','Y','Z'
                   ]

for a in ll:
    for b in ll:
        EXCEL_COLUMN_NAME.append(a+b)
        
EXCEL_COLUMN_NAME=EXCEL_COLUMN_NAME[0:256]