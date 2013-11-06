

import unittest,random,pdb

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
from resample import *

class TestResamplefunctions(unittest.TestCase):

    """ test functionality of shift operations """

    def __init__(self,methodName="runTest"):

        super(TestResamplefunctions,self).__init__(methodName)
                         
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.test_interval=[time_interval(minutes=30),time_interval(hours=2),
                            time_interval(days=1)]
                
    def test_resample_rts(self):

        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     int(scipy.math.pow(2,10)),time_interval(minutes=5)),
                    ]
        
        for (st,num,delta) in test_ts:
            data=[scipy.math.sin(0.01*scipy.math.pi*k) for k in range(num)]
            # This ts is the orignial one
            ts0=rts(data,st,delta,{})              
            for interval in self.test_interval:
                sample_num=number_intervals(ts0.start,ts0.end,interval)
                ts=resample(ts0,interval)
                self.assert_(ts.is_regular())
                self.assert_(len(ts.data)==(sample_num+1))
                
    def test_resample_rts_in(self):
        # Test operations on ts of with incomplete end hour
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=45)
        delta=time_interval(minutes=15)
        resample_interval=time_interval(hours=1)
        data=range(-1,10)
        ts=rts(data,st,delta,{})
        nts=resample(ts,resample_interval)
        self.assert_(nts.data[2]==ts.data[9])
        self.assert_(len(nts)==3)
         
        nt2=resample(ts,resample_interval,aligned=False)
        self.assert_(nt2.data[2]==ts.data[8])
        self.assert_(len(nt2)==3)
        
    def test_resample_rts_aligned(self):
        # test resampling regular time series with aligned start
        data=range(100)
        st=datetime.datetime(year=2000,month=2,day=1,hour=2,minute=15)
        delta=time_interval(minutes=15)
        ts=rts(data,st,delta,{})
        resample_interval=time_interval(hours=1)
        nts=resample(ts,resample_interval,aligned=True)
        rstart=datetime.datetime(year=2000,month=2,day=1,hour=3)
        self.assertEqual(rstart,nts.start)
        
                
    def test_decimate_rts(self):
        
        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     int(scipy.math.pow(2,10)),time_interval(minutes=5)),]
        
        for (st,num,delta) in test_ts:
            data=[scipy.math.sin(0.01*scipy.math.pi*k) for k in range(num)]            
            # This ts is the orignial one
            ts0=rts(data,st,delta,{})              
            for interval in self.test_interval:
                sample_num=number_intervals(ts0.start,ts0.end,interval)+1
                ts=decimate(ts0,interval)
                self.assert_(ts.is_regular())
                self.assert_(len(ts.data)==sample_num)
                
    def test_decimate_rts_2d(self):
        
        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     int(scipy.math.pow(2,10)),time_interval(minutes=5)),]
        
        for (st,num,delta) in test_ts:
            data=[[scipy.math.sin(0.01*scipy.math.pi*k),scipy.math.cos(0.01*scipy.math.pi*k)] for k in range(num)]  
            data=scipy.array(data)          
            # This ts is the orignial one
            ts0=rts(data,st,delta,{})              
            for interval in self.test_interval:
                sample_num=number_intervals(ts0.start,ts0.end,interval)+1
                ts=decimate(ts0,interval)
                self.assert_(ts.is_regular())
                self.assert_(len(ts.data)==sample_num)

    
                        
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
