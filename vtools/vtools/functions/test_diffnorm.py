import sys,os,unittest,shutil,random,pdb
from numpy import repeat
from datetime import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *


# diff function import
from diffnorm import *

## scipy import
from scipy import randn

class TestDiffNorm(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):
        super(TestDiffNorm,self).__init__(methodName)
        # Number of data in a time series.
        self.num_ts=100
        self.max_val=100
        self.min_val=0.01
        
    def test_norm_L1(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval

        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=00)
        ts_len=10
        ts_intvl=hours(1)            
        data=range(ts_len)
        
        # This ts is the orignial one
        ts0=rts(data,ts_start,ts_intvl)
        ts1=rts(data,ts_start,ts_intvl)
        l1norm=norm_diff_l1(ts0,ts1)        
        self.assertEqual(l1norm,0.0)
        
        d2=[1.,2.,0.]
        d3=[0.,0.,1.]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)    
        l1norm2=norm_diff_l1(ts0,ts1)        
        self.assertEqual(l1norm2,4.0)
        
    def test_norm_L2(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval

        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=00)
        ts_len=10
        ts_intvl=hours(1)            
        data=range(ts_len)
        
        # This ts is the orignial one
        ts0=rts(data,ts_start,ts_intvl)
        ts1=rts(data,ts_start,ts_intvl)
        l1norm=norm_diff_l2(ts0,ts1)        
        self.assertEqual(l1norm,0.0)
        
        d2=[1.,2.,0.]
        d3=[0.,0.,1.]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)    
        l1norm2=norm_diff_l2(ts0,ts1)        
        self.assertEqual(l1norm2,numpy.sqrt(6.0))
        
        
    def test_norm_Linf(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval

        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=00)
        ts_len=10
        ts_intvl=hours(1)            
        data=range(ts_len)
        
        # This ts is the orignial one
        ts0=rts(data,ts_start,ts_intvl)
        ts1=rts(data,ts_start,ts_intvl)
        l1norm=norm_diff_linf(ts0,ts1)        
        self.assertEqual(l1norm,0.0)
        
        d2=[1.,2.,0.]
        d3=[0.,0.,1.]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)    
        l1norm2=norm_diff_linf(ts0,ts1)        
        self.assertEqual(l1norm2,2.0)
        
    def test_ts_equal(self):
        # Test operations on ts of varied values.
        # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval

        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=00)
        ts_len=10
        ts_intvl=hours(1)            
        data=range(ts_len)
        
        # This ts is the orignial one
        ts0=rts(data,ts_start,ts_intvl)
        ts1=rts(data,ts_start,ts_intvl)
        re=ts_equal(ts0,ts1)        
        self.assertEqual(re,True)
        
        d2=[1.,2.,0.]
        d3=[0.,0.,1.]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)    
        re=ts_equal(ts0,ts1)        
        self.assertEqual(re,False)
        
        tol=1.0e-8
        d2=[1.0,2.0,0.0]
        d3=[1.0+tol*2.0,2.0,0.0]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)    
        re=ts_equal(ts0,ts1,tol=tol)        
        self.assertEqual(re,False)  

        tol=1.0e-8
        d2=[1.0,2.0,0.0]
        d3=[1.0+tol/2.0,2.0,0.0]
        ts0=rts(d2,ts_start,ts_intvl)
        ts1=rts(d3,ts_start,ts_intvl)      
        re=ts_equal(ts0,ts1,tol=tol)        
        self.assertEqual(re,True)         
                               
            
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
