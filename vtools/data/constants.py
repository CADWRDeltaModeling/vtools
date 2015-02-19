
""" This module contains string constants used in timeseries properties."""

## all the key names values given in lower case, all the other constants given in
## upper case.

__all__=["AGGREGATION","MAX","MIN","MEAN","SUM","INDIVIDUAL","INST","TIMESTAMP",\
         "PERIOD_START","PERIOD_END","START_SHIFTED",\
         "TS_PROPERTIES","UNIT","INTERVAL","UND"]

################################
AGGREGATION="aggregation"  #: Attribute name for sample aggregation over steps
## below are its possible values.
MAX="MAX"                  #: AGGREGATION value: Period max
MIN="MIN"                  #: AGGREGATION value: Period min
MEAN="MEAN"                #: AGGREGATION value: Period mean
SUM="ACCUM"                #: AGGREGATION value: Accumulation
INDIVIDUAL="INST-VAL"      #: AGGREGATION value: Instantaneous values
################################
TIMESTAMP="timestamp"      #: TIMESTAMP value: Attribute name for time stamping convention 
## below are its possible values.
PERIOD_START="PERIOD_START" #: TIMESTAMP value: Stamped at beginning of period
PERIOD_END="PERIOD_END"     #: TIMESTAMP value: Stamped at end of period
INST="INST-VAL"
################################
START_SHIFTED="start_shifted"
################################
## LIST OF TS UNIFORM PROPERTIES

TS_PROPERTIES=[AGGREGATION,TIMESTAMP]
## optional standard properties name
UNIT="unit"
INTERVAL="interval"
UND="und"
