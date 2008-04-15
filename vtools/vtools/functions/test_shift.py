import sys,os,unittest,shutil,random,pdb
from numpy import repeat
from datetime import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *


# Shift function import
from shift import *

class TestShift(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):
        super(TestShift,self).__init__(methodName)
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        
    def test_shift_operation_rts(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval
        test_input=[(datetime(1990,2,3,11,15),
                     3005,minutes(5),"1hour",),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3301,days(1),"1month"),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3407,hours(1),"3days"),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=45),
                     6093,days(1),"1year"),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,time_interval(minutes=5),"-1hour")                 
                    ]

        for (ts_start,ts_len,ts_intvl,shift_interval) in test_input:
            
            data=repeat(10.,ts_len)
            diff=parse_interval(shift_interval)
            
            # This ts is the orignial one
            ts0=rts(data,ts_start,ts_intvl)
            
            # First move forward.
            ts=shift(ts0,shift_interval)
            
            # Now ts ticks should has a forward
            # difference from ts0.
            self.assertEqual(ts0.start+diff,ts.start)
            
            # This line maynot work for calendar 
            # dependent shift interval.
            self.assertEqual(ts0.end+diff,ts.end)
            
            # Then move backward
            #diff=parse_interval(shift_interval)
            #print diff
            #ts=shift(ts0,shift_interval)

            # Now ts ticks should has no
            # difference from ts0.
            #self.assertEqual(ts0.start+diff,ts.start)
            #self.assertEqual(ts0.end+diff,ts.end)

            #for s1,s2 in zip(ts0.ticks,ts.ticks):
            #    self.assertEqual(s1,s2)
                       

    def test_shift_operation_its(self):        
        ts_len=1000
        data=repeat(10.0,ts_len)
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        times=[ts_start]*ts_len
        
        for i in range(1,ts_len):
            times[i]=times[i-1]+time_interval(hours=i%5)
            
        ts0=its(times,data,{})        
        test_input=[hours(1),months(1),days(3),years(1)]
        
        for shift_interval in test_input:  
            ts=its(times,data)         
            ts=shift(ts,shift_interval)
            t=ts0.times+shift_interval
            for a1,b1 in zip(t,ts.times):
                self.assertEqual(a1,b1)
            
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
