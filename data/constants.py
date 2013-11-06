
""" This module contains some string constants uesed in timeseries property."""

## all the key names values given in lower case, all the other constants given in
## upper case.

__all__=["MAX","MIN","MEAN","SUM","INDIVIDUAL","INST","PERIOD_START",\
         "PERIOD_END","AGGREGATION","TIMESTAMP","START_SHIFTED",\
         "TS_PROPERTIES","UNIT","INTERVAL","UND"]



################################
AGGREGATION="aggregation"
## below are its possible values.
MAX="MAX"
MIN="MIN"
MEAN="MEAN"
SUM="ACCUM"
INDIVIDUAL="INST-VAL"
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
