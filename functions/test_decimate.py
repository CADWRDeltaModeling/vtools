import unittest,pdb

## Datetime import
import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval


## Scipy import.
import scipy
## Local import 
from _decimate import *

class TestDecimate(unittest.TestCase):

    """ test functionality of decimate operations """

    def __init__(self,methodName="runTest"):

        super(TestDecimate,self).__init__(methodName)
                         
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.test_interval=[time_interval(minutes=30),time_interval(hours=2),
                            time_interval(days=1)]
                
    def test_decimate_rts(self):
                
        t=scipy.pi/3+scipy.arange(self.num_ts)*scipy.pi/12
        x=scipy.sin(t)
        
        q=4        
        tt=decimate(x,q)
        
        

       

    
                        
if __name__=="__main__":
    
    unittest.main()       
