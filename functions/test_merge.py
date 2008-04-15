

import sys,os,unittest,shutil,random,pdb

## Datetime import
import datetime

##scipy import
import scipy as spy

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.timeseries import prep_binary
from vtools.data.vtime import ticks,number_intervals
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval


## Local import 
from merge import *


class TestMerge(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):

        super(TestMerge,self).__init__(methodName)
                         
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.test_interval=[time_interval(minutes=30),time_interval(hours=2),
                            time_interval(days=1)]
                
    def test_merge_rts_no_intersect(self):
        """ Test merging two rts without intersection."""
        
        d1=[1]*int(spy.math.pow(2,10))
        d2=[2]*int(spy.math.pow(2,11))
        
        st1=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        st2=datetime.datetime(year=1990,month=5,day=3,hour=11, minute=15)
        
        ts1=rts(d1,st1,time_interval(hours=1))
        ts2=rts(d2,st2,time_interval(hours=1))
        nt=merge(ts1,ts2)
        
        self.assertEqual(nt.start,ts1.start)
        self.assertEqual(nt.end,ts2.end)
        
        total_n=number_intervals(ts1.start,ts2.end,ts1.interval)+1
        
        self.assertEqual(len(nt.data),total_n)
        s1=nt.index_after(ts1.end)
        s2=nt.index_after(ts2.start)
        
        self.assert_(spy.alltrue(spy.isnan(nt.data[s1+1:s2])))
        self.assert_(spy.allclose(nt.data[0:s1+1],ts1.data))
        self.assert_(spy.allclose(nt.data[s2:len(nt.data)],ts2.data))
        

    def test_merge_rts_intersect(self):
        """ Test merging two rts with intersection."""
        
        d1=[1.0]*int(spy.math.pow(2,10))
        d2=[2.0]*int(spy.math.pow(2,11))
        
        st1=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        st2=datetime.datetime(year=1990,month=3,day=3,hour=11, minute=15)
        
        ts1=rts(d1,st1,time_interval(hours=1))
        ts2=rts(d2,st2,time_interval(hours=1))
        
        ## Intentionally put some nan into ts1 to see effect.
        ii=ts1.index_after(st2)
        num_nan=10
        ts1.data[ii+1:ii+num_nan+2]=spy.nan               
        
        
        nt=merge(ts1,ts2)
        
        self.assertEqual(nt.start,ts1.start)
        self.assertEqual(nt.end,ts2.end)
        
        total_n=number_intervals(ts1.start,ts2.end,ts1.interval)+1
        
        self.assertEqual(len(nt.data),total_n)
        
        s1=nt.index_after(ts1.end)
        s2=nt.index_after(ts2.start)
        s3=ts2.index_after(ts1.end)
        self.assert_(spy.allclose(nt.data[0:ii+1],ts1.data[0:ii+1]))
        self.assert_(spy.allclose(nt.data[ii+1:ii+num_nan+2],ts2.data[0:num_nan+1]))
        self.assert_(spy.allclose(nt.data[ii+num_nan+2:s1+1],ts1.data[ii+num_nan+2:s1+1]))
        self.assert_(spy.allclose(nt.data[s1+1:len(nt.data)],ts2.data[s3+1:len(ts2.data)]))
    
    def test_merge_rts_2d_intersect(self): 
        
        """ Test merging of two rts of 2-d data and has intersection."""
        
        d1=[[1.0,2.0]]*int(spy.math.pow(2,10))
        d2=[[3.0,4.0]]*int(spy.math.pow(2,11))
        
        st1=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        st2=datetime.datetime(year=1990,month=3,day=3,hour=11, minute=15)
        
        ts1=rts(d1,st1,time_interval(hours=1))
        ts2=rts(d2,st2,time_interval(hours=1))
        
        ## Intentionally put some nan into ts1 to see effect.
        ii=ts1.index_after(st2)
        num_nan=10
        ts1.data[ii+1:ii+num_nan+2,]=spy.nan  
        
        nt=merge(ts1,ts2)
        
        self.assertEqual(nt.start,ts1.start)
        self.assertEqual(nt.end,ts2.end)
        
        total_n=number_intervals(ts1.start,ts2.end,ts1.interval)+1
        
        self.assertEqual(len(nt.data),total_n)
        s1=nt.index_after(ts1.end)
        s2=nt.index_after(ts2.start)
        s3=ts2.index_after(ts1.end)
        self.assert_(spy.allclose(nt.data[0:ii+1,],ts1.data[0:ii+1,]))
        self.assert_(spy.allclose(nt.data[ii+1:ii+num_nan+2,],ts2.data[0:num_nan+1,]))
        self.assert_(spy.allclose(nt.data[ii+num_nan+2:s1+1,],ts1.data[ii+num_nan+2:s1+1,]))
        self.assert_(spy.allclose(nt.data[s1+1:len(nt.data),],ts2.data[s3+1:len(ts2.data),]))

    def test_merge_large_rts(self):

        largenum=250000        

        st1=datetime.datetime(1920,1,2)
        data1=range(0,largenum)
        dt=datetime.timedelta(minutes=15)
        rt1=rts(data1,st1,dt,{})

        st2=rt1.end+dt
        data2=range(largenum,2*largenum)
        rt2=rts(data2,st2,dt,{})

        st3=rt2.end+dt
        data3=range(2*largenum,3*largenum)
        rt3=rts(data3,st3,dt,{})

        st4=rt3.end+dt
        data4=range(3*largenum,4*largenum)
        rt4=rts(data4,st4,dt,{})        
        
        ts=merge(rt1,rt2,rt3,rt4)

        self.assertEqual(len(ts),largenum*4)
        self.assertEqual(ts.data[largenum],data2[0])
        self.assertEqual(ts.data[2*largenum],data3[0])
        self.assertEqual(ts.data[3*largenum],data4[0])
                            
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
