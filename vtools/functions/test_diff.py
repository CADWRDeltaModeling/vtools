import sys,os,unittest,shutil,random,pdb
from numpy import repeat
from datetime import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *


# diff function import
from diff import *

## scipy import
from scipy import randn

class TestDiff(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):
        super(TestDiff,self).__init__(methodName)
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000

    def test_shift_operation_rts(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval

        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=6093
        ts_intvl=days(1)
        data=randn(ts_len)


        # This ts is the orignial one
        ts0=rts(data,ts_start,ts_intvl)

        ts1=time_diff(ts0,1)
        ts2=time_diff(ts0,2)
        ts3=time_diff(ts0,3)

        self.assertTrue(len(ts2),ts_len-2)




if __name__=="__main__":

    unittest.main()
