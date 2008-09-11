import sys,os,unittest,shutil,random,pdb
from numpy import repeat
from datetime import datetime
from scipy import randn
from numpy import maximum as numpymaximum, add as numpyadd
## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *
# diff function import
from stats import *

class TestStat(unittest.TestCase):

    """ test functionality of shift operations """


    def __init__(self,methodName="runTest"):
        super(TestStat,self).__init__(methodName)
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        
    def test_ts_max(self):
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=100
        ts_intvl=days(1)            
        data=range(ts_len)
        ts0=rts(data,ts_start,ts_intvl)
        tsmax=ts_max(ts0)
        self.assertEqual(tsmax,data[-1])

        time_window=(ts0.times[5],ts0.times[30])
        truemax=data[30]
        tsmax=ts_max(ts0,window=time_window)
        self.assertEqual(tsmax,truemax)          
        
    def test_ts_sum(self):
        
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=100
        ts_intvl=days(1)            
        data=range(ts_len)
        ts0=rts(data,ts_start,ts_intvl)
        tssum=ts_sum(ts0)
        self.assertEqual(tssum,sum(data))

        time_window=(ts0.times[5],ts0.times[30])
        truesum=sum(data[5:31])
        tssum=ts_sum(ts0,window=time_window)
        self.assertEqual(tssum,truesum)        

    def test_ts_mean(self):
        
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=100
        ts_intvl=days(1)            
        data=range(ts_len)
        ts0=rts(data,ts_start,ts_intvl)
        tsmean=ts_mean(ts0)
        self.assertEqual(tsmean,sum(data)/ts_len)
        
        time_window=(ts0.times[5],ts0.times[30])
        truemean=sum(data[5:31])/26
        tsmean=ts_mean(ts0,window=time_window)
        self.assertEqual(tsmean,truemean)


    def test_ts_apply(self):
          
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=100
        ts_intvl=days(1)            
        data=range(ts_len)
        ts0=rts(data,ts_start,ts_intvl)

        larger=1000
        larger_ts=ts_apply(ts0,numpymaximum,other=larger)
        self.assertEqual(len(larger_ts),ts_len)
        self.assertEqual(larger,larger_ts.data[23])

        chop=50
        chop_ts=ts_apply(ts0,numpymaximum,other=chop)
        self.assertEqual(len(larger_ts),ts_len)
        self.assertEqual(larger,larger_ts.data[23])         

    def test_ts_accumulate(self):
        
        ts_start=datetime(year=1990,month=2,day=3,hour=11, minute=45)
        ts_len=100
        ts_intvl=days(1)            
        data=range(ts_len)
        ts0=rts(data,ts_start,ts_intvl)

        accadd_ts=ts_apply(ts0,numpyadd)
        self.assertEqual(len(larger_ts),ts_len)
        self.assertEqual(accad_ts.data[-1],sum(data))
            
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
