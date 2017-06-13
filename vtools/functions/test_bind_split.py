

import sys,os,unittest,shutil,random,pdb

## Datetime import

## vtools import
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals,\
     is_calendar_dependent,parse_interval,ticks_per_minute
#from vtools.debugtools.timeprofile import debug_timeprofiler
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval,parse_time,\
     ticks_per_day,parse_interval
from vtools.data.constants import *

from bind_split import *

## Scipy import.
from scipy import array as sciarray
from scipy import add as sciadd
from scipy import multiply as scimultiply
from scipy import minimum as sciminimum
from scipy import maximum as scimaximum
from scipy import nan,isnan,allclose

## Scipy testing suite import.
from numpy.testing import assert_array_equal, assert_equal
from numpy.testing import assert_almost_equal, assert_array_almost_equal
import datetime

class TestBindSplitOp(unittest.TestCase):

    """ test functionality of split/bind operations """
    def __init__(self,methodName="runTest"):
        super(TestBindSplitOp,self).__init__(methodName)

    def test_bind_op_irregular(self):
        """ Test behaviour of bind operation on irregular TS."""
        times=[12,15,32,38,43,52,84,138,161,172]
        #times=sciadd.accumulate(times)
        start_datetime = parse_time("1996-2-1")
        start_ticks = ticks(start_datetime)
        times=scimultiply(times,ticks_per_minute)
        times=sciadd(times,start_ticks)
        data=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        ts1=its(times,data,{})
        ts2=its(times,data,{})
 
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),len(ts1))
        self.assertEqual(new_ts.start,ts1.start)
       
        for (d1,d2),d  in zip(new_ts.data,data):
            self.assertEqual(d1,d)
            self.assertEqual(d2,d)
            
    def test_bind_op_regular(self):
        """ Test behaviour of bind operation on regular TS."""
    
        #times=sciadd.accumulate(times)
        start = parse_time("1996-2-1")
        interval = parse_interval("1hour")
        data=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        ts1=rts(data,start,interval,{})
        ts2=rts(data,start,interval,{})
 
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),len(ts1))
        self.assertEqual(new_ts.start,ts1.start)
        self.assertEqual(new_ts.interval,interval)
        for (d1,d2),d  in zip(new_ts.data,data):
            self.assertEqual(d1,d)
            self.assertEqual(d2,d)
        
        ## partial overlap
        start2 = parse_time("1996-2-1 4:00")
        ts2=rts(data,start2,interval,{})
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),14)
        self.assertEqual(new_ts.start,ts1.start)
        self.assertEqual(new_ts.times[-1],ts2.times[-1])
        self.assertEqual(new_ts.interval,interval)
        for i in range(4):
            self.assertTrue(isnan(new_ts.data[i,1]))
            self.assertTrue(isnan(new_ts.data[i+10,0]))
        for i in range(10):
            self.assertEqual(new_ts.data[i,0],data[i])
            self.assertEqual(new_ts.data[i+4,1],data[i])
          
         ##no overlap,immediately after
        start2 = parse_time("1996-2-1 10:00")
        ts2=rts(data,start2,interval,{})
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),20)
        self.assertEqual(new_ts.start,ts1.start)
        self.assertEqual(new_ts.times[-1],ts2.times[-1])
        self.assertEqual(new_ts.interval,interval)
        for i in range(10):
            self.assertTrue(isnan(new_ts.data[i,1]))
            self.assertTrue(isnan(new_ts.data[i+10,0]))
        for i in range(10):
            self.assertEqual(new_ts.data[i,0],data[i])
            self.assertEqual(new_ts.data[i+10,1],data[i])
        
        ## smaller interval
        start2 = parse_time("1996-2-1 8:00")
        interval2=parse_interval("15min")
        ts2=rts(data,start2,interval2,{})
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),42)
        self.assertEqual(new_ts.start,ts1.start)
        self.assertEqual(new_ts.times[-1],ts2.times[-1])
        self.assertEqual(new_ts.interval,interval2)
        ts1_id = [4*x for x in range(10)]
        nan_id =  range(len(new_ts))
        for i in ts1_id:
            nan_id.remove(i) ## those id supoose have nan
        ts1_val = new_ts.data[ts1_id,0]
        left_val = new_ts.data[nan_id,0]
        for d1,d2 in zip(ts1_val,data):
            self.assertEqual(d1,d2)
        for d in left_val:
            self.assertTrue(isnan(d))
        ts2_id = range(32,42)
        ts2_val = new_ts.data[ts2_id,1]
        for d1,d2 in zip(ts2_val,data):
            self.assertEqual(d1,d2)
            
    def test_bind_multivar(self):
        """ test behaviour of bind on multvariate ts"""
        start = parse_time("1996-2-1")
        interval = parse_interval("1hour")
        data1=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        data2t=sciarray([[1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0],
                        [2.0,2.1,2.8,9.1,3.2,0.5,0.1,8.1,1.2,1.1]])
        data2=data2t.transpose()
        
        data_temp= sciarray([data1[:],data2t[0,:],data2t[1,:]]).transpose()             
                        
        ts1=rts(data1,start,interval,{})
        ts2=rts(data2,start,interval,{})
       
        new_ts = ts_bind(ts1,ts2)
        self.assertEqual(len(new_ts),len(ts1))
        self.assertEqual(new_ts.start,ts1.start)
        self.assertEqual(new_ts.interval,interval)
        for (d1,d2,d3),(dt1,dt2,dt3) in zip(new_ts.data,data_temp):
            self.assertEqual(d1,dt1)
            self.assertEqual(d2,dt2)
            self.assertEqual(d3,dt3)
            
    def test_split_op_irregular(self):
        """ Test behaviour of split operation on irregular TS."""
        times=[12,15,32,38,43,52,84,138,161,172]
        #times=sciadd.accumulate(times)
        start_datetime = parse_time("1996-2-1")
        start_ticks = ticks(start_datetime)
        times=scimultiply(times,ticks_per_minute)
        times=sciadd(times,start_ticks)
        data1=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        data2=sciarray([7.0,1.2,10.5,3.0,1.0,1.0,9.0,3.0,0.0,0.2])
        
        ts = its(times,sciarray([data1,data2]).transpose())
        
        ts1,ts2 =ts_split(ts,False)
           
        
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0    
        self.assertNotEqual(ts1.data[5],ts.data[5,0])
        self.assertNotEqual(ts2.data[2],ts.data[2,1])
        
        for t1,t2 in zip(ts1.times,ts.times):
           self.assertEqual(t1,t2)
        for t1,t2 in zip(ts2.times,ts.times):
           self.assertEqual(t1,t2)
           
        ts1,ts2 =ts_split(ts,True)
        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0
    
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
       
        for t1,t2 in zip(ts1.times,ts.times):
           self.assertEqual(t1,t2)
        for t1,t2 in zip(ts2.times,ts.times):
           self.assertEqual(t1,t2)

    def test_split_op_regular(self):
        """ Test behaviour of split operation on regular TS."""
        
        #times=sciadd.accumulate(times)
        start = parse_time("1996-2-1")
        interval = parse_interval("1hour")
        data1=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        data2=sciarray([7.0,1.2,10.5,3.0,1.0,1.0,9.0,3.0,0.0,0.2])
        
        ts = rts(sciarray([data1,data2]).transpose(),start,interval)
        
        ts1,ts2 =ts_split(ts,False)
        
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
            
        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0    
        self.assertNotEqual(ts1.data[5],ts.data[5,0])
        self.assertNotEqual(ts2.data[2],ts.data[2,1])
         
        self.assertEqual(ts1.start,ts.start)
        self.assertEqual(ts1.interval,ts.interval)
        self.assertEqual(len(ts1),len(ts))
        self.assertEqual(ts2.start,ts.start)
        self.assertEqual(ts2.interval,ts.interval)
        self.assertEqual(len(ts2),len(ts))
        
        ts1,ts2 =ts_split(ts,True)

        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0
    
        
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
         
        self.assertEqual(ts1.start,ts.start)
        self.assertEqual(ts1.interval,ts.interval)
        self.assertEqual(len(ts1),len(ts))
        self.assertEqual(ts2.start,ts.start)
        self.assertEqual(ts2.interval,ts.interval)
        self.assertEqual(len(ts2),len(ts))
        
    def test_split_op_regular_3(self):
        """ Test behaviour of split operation on regular TS with more than 3 variable"""
        
        #times=sciadd.accumulate(times)
        start = parse_time("1996-2-1")
        interval = parse_interval("1hour")
        data1=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        data2=sciarray([7.0,1.2,10.5,3.0,1.0,1.0,9.0,3.0,0.0,0.2])
        data3=sciarray([0.03,1.02,70.5,0.0,1.0,1.0,9.6,13.0,0.0,2.2])
        
        ts = rts(sciarray([data1,data2,data3]).transpose(),start,interval)
        
        ts1,ts2,ts3 =ts_split(ts,False)
        
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,2],ts3.data):
            self.assertEqual(d1,d2)
            
        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0    
        self.assertNotEqual(ts1.data[5],ts.data[5,0])
        self.assertNotEqual(ts2.data[2],ts.data[2,1])
         
        self.assertEqual(ts1.start,ts.start)
        self.assertEqual(ts1.interval,ts.interval)
        self.assertEqual(len(ts1),len(ts))
        self.assertEqual(ts2.start,ts.start)
        self.assertEqual(ts2.interval,ts.interval)
        self.assertEqual(len(ts2),len(ts))
        
        ts1,ts2,ts3 =ts_split(ts,True)

        ts1.data[5] = -9999.0
        ts2.data[2] = -9999.0
    
        
        for d1,d2 in zip(ts.data[:,0],ts1.data):
            self.assertEqual(d1,d2)
        for d1,d2 in zip(ts.data[:,1],ts2.data):
            self.assertEqual(d1,d2)
         
        self.assertEqual(ts1.start,ts.start)
        self.assertEqual(ts1.interval,ts.interval)
        self.assertEqual(len(ts1),len(ts))
        self.assertEqual(ts2.start,ts.start)
        self.assertEqual(ts2.interval,ts.interval)
        self.assertEqual(len(ts2),len(ts))
        
        ts = rts(sciarray(data1),start,interval)
        [ts1] =ts_split(ts,True)

        ts1.data[5] = -9999.0
       
        
        for d1,d2 in zip(ts.data,ts1.data):
            self.assertEqual(d1,d2)
      
         
        self.assertEqual(ts1.start,ts.start)
        self.assertEqual(ts1.interval,ts.interval)
        self.assertEqual(len(ts1),len(ts))
      
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
