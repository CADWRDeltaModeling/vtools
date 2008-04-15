

import sys,os,unittest,shutil,random,pdb

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *

## Scipy import.
from scipy import array as sciarray
from scipy import add as sciadd
from scipy import minimum as sciminimum
from scipy import maximum as scimaximum
from scipy import nan,isnan,allclose

# Peroid func import
from period_op import *

class Testfunctions(unittest.TestCase):

    """ test functionality of dss catalog. """


    def __init__(self,methodName="runTest"):

        super(Testfunctions,self).__init__(methodName)
                         
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        
    def test_period_op(self):

        # Test operations on ts of varied values.
        test_input=[(datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,minutes(5),"1hour",hours(1),
                     datetime(year=1990,month=2,day=3,hour=12, minute=0)),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3301,days(1),"1month",months(1),
                     datetime(year=1990,month=3,day=1,hour=00, minute=00)),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3407,hours(1),"1day",days(1),
                     datetime(year=1990,month=2,day=4,hour=00, minute=00)),
                    (datetime(year=1990,month=2,day=3,hour=11, minute=45),
                     6093,days(1),"1year",years(1),
                     datetime(year=1991,month=1,day=1,hour=00, minute=00)),
                    (datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,days(1),"1year",years(1),
                     datetime(year=1990,month=1,day=1,hour=00, minute=00)),
                    (datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,days(1),"7 day",days(7)),
                     datetime(year=1990,month=1,day=1,hour=00, minute=00),
                    ]

        for (st,num,delta,interval,op_delta,aligned_start) in test_input:
            
            data=[random.uniform(self.min_val,self.max_val) \
                  for k in range(num)]
            times=time_sequence(st,delta,num)
            ts=its(times,data,{})

            # The length of new generated time series.
            nt_len=number_intervals(aligned_start,ts.end,op_delta)

            for op in [MIN,MAX,MEAN]:
                nt=period_op(ts,interval,op)
                self.assertEqual(nt.start,aligned_start)
                self.assertEqual(len(nt.data),nt_len)


            # Test operations on ts of constant values.
            data=[1 for k in range(num)]
            times=time_sequence(st,delta,num)
            ts=its(times,data,{})
            # This is the data values that new ts should be
            nt_data=[1]*nt_len

            for op in [MIN,MAX,MEAN]:                
                nt=period_op(ts,interval,op)                
                for (a,b) in zip(nt.data,nt_data):
                    self.assertEqual(a,b)

    def test_period_op2(self):

        """ Run test with known result time series."""

        st=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        delta=minutes(5)
        interval='1 hour'
        op_delta=hours(1)
        aligned_start=datetime(year=1990,month=2,day=3,hour=12, minute=0)
            
        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]

        # Reformalize raw data, insert known mini_val and max_val
        # and calcuate hourly mean to use later.
        i0=9 # this is the first index with aligned calendar
        num_interval=(num-i0+1)//12

        for k in range(num_interval):

            index=i0+k*12+1
            data[index]=self.min_val
            index=index+1
            data[index]=self.max_val

        nt_data=data[i0:12*num_interval+i0]
        nt_data=sciarray(nt_data)
        nt_data.shape=(num_interval,12)

        nt_mean=sciadd.reduce(nt_data,1)/12
        nt_min=sciminimum.reduce(nt_data,1)
        nt_max=scimaximum.reduce(nt_data,1)

        times=time_sequence(st,delta,num)
        ts=its(times,data,{})
        
        for (op,op_data) in [(MIN,nt_min),(MAX,nt_max),(MEAN,nt_mean)]:                
            nt=period_op(ts,interval,op)
            for (a,b) in zip(nt.data,op_data):
                self.assertEqual(a,b)

    def test_period_op3(self):
        
        """Test period operation on time series with 2-dimensional data."""

        st=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        dimension2=3
        delta=minutes(5)
        interval='1 hour'
        op_delta=hours(1)
        aligned_start=datetime(year=1990,month=2,day=3,hour=12, minute=0)
            
        data=[[random.uniform(self.min_val,self.max_val) for i in range(dimension2)] \
              for k in range(num)]

        data=sciarray(data)
        
        # Reformalize raw data, insert known mini_val and max_val
        # and calcuate hourly mean to use later.
        i0=9 # this is the first index with aligned calendar
        num_interval=(num-i0+1)//12

        for k in range(num_interval):
            index=i0+k*12+1
            data[index,]=self.min_val
            index=index+1
            data[index,]=self.max_val

        nt_data=data[i0:12*num_interval+i0,]
        nt_data=sciarray(nt_data)
        nt_data.shape=(num_interval,12,-1)

        nt_mean=sciadd.reduce(nt_data,1,)/12
        nt_min=sciminimum.reduce(nt_data,1,)
        nt_max=scimaximum.reduce(nt_data,1,)

        times=time_sequence(st,delta,num)
        ts=its(times,data,{})
        
        for (op,op_data) in [(MIN,nt_min),(MAX,nt_max),(MEAN,nt_mean)]:                
            nt=period_operation(ts,interval,op)
            for (a,b) in zip(nt.data,op_data):
                for (va,vb) in zip(a,b):
                    self.assertEqual(va,vb)

    def test_period_op_large(self):

        """ Test performance of period operation on very large size of TS.
            Print out time used also.
        """
        st=datetime(year=10,month=2,day=3,hour=11, minute=15)
        num=self.large_data_size
        delta=hours(1)
        dimension2=3
        interval='1 day'

        data=[[random.uniform(self.min_val,self.max_val) for i in range(dimension2)] \
              for k in range(num)]
        data=sciarray(data)
        ts=rts(data,st,delta,{})

        for op in [MIN,MAX,MEAN]:


            nt=period_operation(ts,interval,op)
        

    def test_period_op_irregular(self):

        """ Test behaviour of period operation on irregular TS."""


        times=[random.randint(1,100) for i in range(self.num_ts)]
        times=sciadd.accumulate(times)

        data=sciarray([random.random() for i in range(self.num_ts)])

        ts=its(times,data,{})

        for op in [MIN,MAX,MEAN]:
            self.assertRaises( ValueError,period_operation,ts,"1 day",op)

    def test_period_op_uncompatible_interval(self):

        """ Test behaviour of period operation on TS with interval uncompatible
            with operation time interval
        """
        test_input=[(datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,minutes(45),"1hour",hours(1)),                    
                    (datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3301,days(1),"1hour",hours(1)),                    
                    (datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,days(2),"1 month",months(1)),
                    (datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,minutes(35),"3 days",days(3))
                   ]

        for (st,num,delta,interval,op_delta) in test_input:            
            data=[random.uniform(self.min_val,self.max_val) \
                  for k in range(num)]
            times=time_sequence(st,delta,num)
            ts=its(times,data,{})
            for op in [MIN,MAX,MEAN]:
                self.assertRaises(ValueError,period_operation,ts,interval,op)

    def test_period_op_nan(self):

        """ Test the behaviour of period operation on data with NaN."""

        st=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        delta=minutes(5)
        interval='1 hour'
        op_delta=hours(1)
        aligned_start=datetime(year=1990,month=2,day=3,hour=12, minute=0)
            
        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]

        # Reformalize raw data, insert known mini_val and max_val
        # and calcuate hourly mean to use later.
        i0=9 # this is the first index with aligned calendar
        num_interval=(num-i0+1)//12

        nt_mean=[]
        for k in range(num_interval):
            index=i0+k*12+1
            data[index]=self.min_val
            index=index+1
            data[index]=self.max_val
            ## A nan is insert into data
            index=index+3
            data[index]=nan
            # Here calcualte mean over 12 numbers, nan is omitted
            # but 12 is still used in averaging.
            average_val=(sum(data[index-5:index])+sum(data[index+1:index+7]))/12
            nt_mean.append(average_val)

        nt_data=data[i0:12*num_interval+i0]
        nt_data=sciarray(nt_data)
        nt_data.shape=(num_interval,12)

        nt_min=[self.min_val]*num_interval
        nt_max=[self.max_val]*num_interval

        times=time_sequence(st,delta,num)
        ts=its(times,data,{})
        
        for (op,op_data) in [(MIN,nt_min),(MAX,nt_max),(MEAN,nt_mean)]:                
            nt=period_operation(ts,interval,op)
            self.assert_(allclose(nt.data,op_data))

        



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
