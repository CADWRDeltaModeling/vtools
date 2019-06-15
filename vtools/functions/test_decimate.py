import unittest,pdb

## Datetime import
import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval

import scipy
## local import
from resample import decimate




class TestDecimate(unittest.TestCase):

    """ test functionality of decimate operations """

    def __init__(self,methodName="runTest"):

        super(TestDecimate,self).__init__(methodName)

        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.test_interval=[time_interval(hours=1)]
        t=scipy.pi/3+scipy.arange(self.num_ts)*scipy.pi/12
        data=scipy.sin(t)
        start_time="1/1/1991"
        interval="15min"
        props={}
        self.ts=rts(data,start_time,interval,props)


    def test_decimate_rts(self):

        for resample_interval in self.test_interval:
            ts_resampled=decimate(self.ts,resample_interval)
            self.assertEqual(ts_resampled.interval,resample_interval)







if __name__=="__main__":

    unittest.main()
