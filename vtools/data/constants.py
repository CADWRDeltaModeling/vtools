
""" This module contains string constants used in timeseries properties."""

## all the key names values given in lower case, all the other constants given in
## upper case.

__all__=["AGGREGATION","MAX","MIN","MEAN","SUM","INDIVIDUAL","INST","TIMESTAMP",\
         "PERIOD_START","PERIOD_END","START_SHIFTED",\
         "TS_PROPERTIES","UNIT","INTERVAL","UND"]

################################
AGGREGATION="aggregation"  #: Period op representing how samples are aggregated
## below are its possible values.
MAX="MAX"                  #: Period max
MIN="MIN"                  #: Period min
MEAN="MEAN"                #: Period mean
SUM="ACCUM"                #: Accumulation
INDIVIDUAL="INST-VAL"      #: Instantaneous values
################################
TIMESTAMP="timestamp"
## below are its possible values.
PERIOD_START="PERIOD_START"
PERIOD_END="PERIOD_END"
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
