

import sys,os,unittest,shutil,random,pdb

## Datetime import

## vtools import
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals,\
     is_calendar_dependent,parse_interval,ticks_per_minute
#from vtools.debugtools.timeprofile import debug_timeprofiler
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval,parse_time,\
     ticks_per_day
from vtools.data.constants import *

from period_op import *

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


class TestPeriodOp(unittest.TestCase):

    """ test functionality of period operations """
    def __init__(self,methodName="runTest"):
        super(TestPeriodOp,self).__init__(methodName)

        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000

    def test_period_op(self):

        ## Test operations on ts of varied values.
        test_input=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,time_interval(minutes=5),"1hour",time_interval(hours=1),
                     datetime.datetime(year=1990,month=2,day=3,hour=12, minute=0)),
                    (datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3301,time_interval(days=1),"1month",time_interval(months=1),
                     datetime.datetime(year=1990,month=3,day=1,hour=00, minute=00)),
                    (datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3407,time_interval(hours=1),"1day",time_interval(days=1),
                     datetime.datetime(year=1990,month=2,day=4,hour=00, minute=00)),
                    (datetime.datetime(year=1990,month=2,day=3,hour=11, minute=45),
                     6093,time_interval(days=1),"1year",time_interval(years=1),
                     datetime.datetime(year=1991,month=1,day=1,hour=00, minute=00)),
                    (datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,time_interval(days=1),"1year",time_interval(years=1),
                     datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00)),
                    (datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,time_interval(days=1),"7 day",time_interval(days=7),
                     datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00)),
                    ]

        for (st,num,delta,interval,op_delta,aligned_start) in test_input:

            data=[random.uniform(self.min_val,self.max_val) \
                  for k in range(num)]
            ts=rts(data,st,delta,{})
            ## The length of new generated time series.
            nt_len=number_intervals(aligned_start,ts.end,op_delta)
            for op in [MIN,MAX,SUM]:
                nt=period_op(ts,interval,op)
                self.assertEqual(nt.start,aligned_start)
                self.assertEqual(len(nt.data),nt_len)

            for op in [MEAN]:
                for method in [RECT,TRAPEZOID]:
                    nt=period_op(ts,interval,op,method=method)
                    self.assertEqual(nt.start,aligned_start)
                    self.assertEqual(nt.props[TIMESTAMP],PERIOD_START)
                    self.assertEqual(nt.props[AGGREGATION],op)
                    self.assertEqual(len(nt.data),nt_len)

            ## Test operations on ts of constant values.
            data=[1 for k in range(num)]
            ts=rts(data,st,delta,{})
            ## This is the data values that new ts should be
            nt_data=[1]*nt_len
            #pdb.set_trace()
            for op in [MEAN]:
                for method in [RECT,TRAPEZOID]:
                    nt=period_op(ts,interval,op,method=method)
                    l=min(len(nt.data),len(nt_data))
                    assert_array_equal(nt.data[0:l],nt_data[0:l],\
                                       err_msg="two array not equal in averaging" \
                                       " by %s"%(method))

    def test_period_op2(self):

        """ Run test with known result time series."""

        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        delta=time_interval(minutes=5)
        interval='1 hour'
        op_delta=time_interval(hours=1)
        aligned_start=datetime.datetime(year=1990,month=2,day=3,hour=12, minute=0)

        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]

        ## Reformalize raw data, insert known mini_val and max_val
        ## and calcuate hourly mean to use later.
        i0=9  # this is the first index with aligned calendar.
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
        nt_sum=sciadd.reduce(nt_data,1)
        nt_min=sciminimum.reduce(nt_data,1)
        nt_max=scimaximum.reduce(nt_data,1)
        ts=rts(data,st,delta,{})

        for (op,op_data) in [(MIN,nt_min),(MAX,nt_max),(SUM,nt_sum)]:
            nt=period_op(ts,interval,op)
            assert_array_equal(nt.data,op_data,\
            err_msg="two array not equal in average" \
            " by %s"%(op))

    def test_period_op3(self):

        """ Test period operation on time series with 2-dimensional data."""

        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        dimension2=3
        delta=time_interval(minutes=5)
        interval='1 hour'
        op_delta=time_interval(hours=1)
        aligned_start=datetime.datetime(year=1990,month=2,day=3,hour=12, minute=0)

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
        nt_sum=sciadd.reduce(nt_data,1,)
        nt_min=sciminimum.reduce(nt_data,1,)
        nt_max=scimaximum.reduce(nt_data,1,)

        ts=rts(data,st,delta,{})

        for (op,op_data) in [(MIN,nt_min),(MAX,nt_max),(MEAN,nt_mean),(SUM,nt_sum)]:
            nt=period_op(ts,interval,op)
            assert_array_equal(nt.data,op_data,\
            err_msg="two array not equal in average" \
            " by %s"%(op))

    def test_period_op_large(self):

        """ Test performance of period operation on very large size of TS.
            Print out time used also.
        """
        st=datetime.datetime(year=10,month=2,day=3,hour=11, minute=15)
        num=self.large_data_size
        delta=time_interval(hours=1)
        dimension2=3
        interval='1 day'

        data=[[random.uniform(self.min_val,self.max_val) for i in range(dimension2)] \
              for k in range(num)]
        data=sciarray(data)
        ts=rts(data,st,delta,{TIMESTAMP:INST})

        for op in [MIN,MAX,MEAN,SUM]:

            ##### time profile ####
            #debug_timeprofiler.mark()
            ######################
            nt=period_op(ts,interval,op)
            ##### time profile ####
            #print "time used in %s operation \
            #on a large timeseries of size %s:"%
            #(op,num),debug_timeprofiler.timegap()
            ######################

    def test_period_op_irregular(self):
        """ Test behaviour of period operation on irregular TS."""
        times=[12,15,32,38,43,52,84,138,161,172]
        #times=sciadd.accumulate(times)
        start_datetime = parse_time("1996-2-1")
        start_ticks = ticks(start_datetime)
        times=scimultiply(times,ticks_per_minute)
        times=sciadd(times,start_ticks)
        data=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0])
        ts=its(times,data,{})
        op=MEAN
        ts_op=period_op(ts,"1 hour",op)
        self.assertEqual(len(ts_op),3)
        self.assertEqual(ts_op.data[0],1.0)
        self.assertEqual(ts_op.data[1],2.0)
        self.assertEqual(ts_op.data[2],3.0)

        times=[0,15,32,38,43,52,60,120,138,161,180]
        data=sciarray([1.0,1.0,1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0,4.0])
        times=scimultiply(times,ticks_per_minute)
        times=sciadd(times,start_ticks)
        ts=its(times,data,{})
        op=MEAN
        ts_op=period_op(ts,"1 hour",op)
        self.assertEqual(len(ts_op),4)
        self.assertEqual(ts_op.data[0],1.0)
        self.assertEqual(ts_op.data[1],2.0)
        self.assertEqual(ts_op.data[2],3.0)
        self.assertEqual(ts_op.data[3],4.0)

        data=sciarray([1.0,2.0,3.0,4.0,5.0,6.0,2.0,3.0,4.0,5.0,4.0])
        ts=its(times,data,{})
        op=MIN
        ts_op=period_op(ts,"1 hour",op)
        self.assertEqual(len(ts_op),4)
        self.assertEqual(ts_op.data[0],1.0)
        self.assertEqual(ts_op.data[1],2.0)
        self.assertEqual(ts_op.data[2],3.0)
        self.assertEqual(ts_op.data[3],4.0)


        op=MAX
        ts_op=period_op(ts,"1 hour",op)
        self.assertEqual(len(ts_op),4)
        self.assertEqual(ts_op.data[0],6.0)
        self.assertEqual(ts_op.data[1],2.0)
        self.assertEqual(ts_op.data[2],5.0)
        self.assertEqual(ts_op.data[3],4.0)

        times=[0,15,28,30,58,64,80,90,91]
        start_datetime = parse_time("1996-1-1")
        start_ticks = ticks(start_datetime)
        times=scimultiply(times,ticks_per_day)
        times=sciadd(times,start_ticks)
        data=sciarray([1.0,1.0,1.0,1.0,2.0,3.0,3.0,3.0,4.0])
        ts=its(times,data,{})
        op=MEAN
        ts_op=period_op(ts,"1 month",op)
        self.assertEqual(len(ts_op),4)
        self.assertEqual(ts_op.data[0],1.0)
        self.assertEqual(ts_op.data[1],2.0)
        self.assertEqual(ts_op.data[2],3.0)
        self.assertEqual(ts_op.data[3],4.0)


    def test_period_op_uncompatible_interval(self):
        """ Test behaviour of period operation on TS with interval uncompatible
            with operation time interval
        """
        test_input=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,time_interval(minutes=45),"1hour",time_interval(hours=1)),
                    (datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3301,time_interval(days=1),"1hour",time_interval(hours=1)),
                    (datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,time_interval(days=2),"1 month",time_interval(months=1)),
                    (datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     10957,time_interval(minutes=35),"3 days",time_interval(days=3)),
                    (datetime.datetime(year=1990,month=1,day=1,hour=00, minute=00),
                     59,time_interval(months=5),"3 years",time_interval(years=3)),
                   ]

        for (st,num,delta,interval,op_delta) in test_input:
            data=[random.uniform(self.min_val,self.max_val) \
                  for k in range(num)]
            ts=rts(data,st,delta,{})
            for op in [MIN,MAX,MEAN,SUM]:
                self.assertRaises(ValueError,period_op,ts,interval,op)

    def test_period_op_nan(self):

        """ Test the behaviour of period operation on data with NaN."""

        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        num=3005
        delta=time_interval(minutes=5)
        interval='1 hour'
        op_delta=time_interval(hours=1)
        aligned_start=datetime.datetime(year=1990,month=2,day=3,hour=12, minute=0)

        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]



        # Reformalize raw data, insert known mini_val and max_val
        # and calcuate hourly mean to use later.
        i0=9 # this is the first index with aligned calendar
        num_interval=(num-i0+1)//12

        # Here a nan is insert into ts.
        data[9+12*2]=nan

        times=time_sequence(st,delta,num)
        ts=rts(data,st,delta,{})

        nt=period_op(ts,interval,MEAN)
        self.assertTrue(isnan(nt.data[2]))

        nt=period_op(ts,interval,SUM)
        self.assertTrue(isnan(nt.data[2]))

        nt=period_op(ts,interval,MIN)
        if not isnan(nt.data[2]):
            print("period_op omits nan during period_min")

        nt=period_op(ts,interval,MAX)
        if not isnan(nt.data[2]):
            print("period_op omits nan during period_min")


    def test_period_time_stamp(self):

        st=datetime.datetime(year=1990,month=1,day=1)
        num=31
        delta=time_interval(days=1)
        op_delta=time_interval(months=1)
        aligned_start=datetime.datetime(year=1990,month=1,day=1)

        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(31)]

        ts_sum = sum(data)

        ts=rts(data,st,delta,{TIMESTAMP:PERIOD_START,AGGREGATION:MEAN})

        ts_op = period_op(ts,op_delta,SUM)

        self.assertEqual(ts_op.start,aligned_start)
        self.assertEqual(len(ts_op),1)
        self.assertEqual(ts_op.data[0],ts_sum)

if __name__=="__main__":

    unittest.main()
