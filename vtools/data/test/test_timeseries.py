import unittest
import numpy
import datetime as _datetime
import vtools.data.timeseries
from vtools.data.timeseries import *
from vtools.data.vtime import *
from vtools.data.constants import *

class TestTimeSeries(unittest.TestCase):

    def setUp(self):
        self.size1=100000
        self.arr=numpy.arange(self.size1,dtype=float)
        self.stime1=_datetime.datetime(1992,3,7)
        self.stime2=_datetime.datetime(1992,3,7,1,0)
        self.dt=time_interval(minutes=15)
        props={TIMESTAMP:INST,AGGREGATION:MEAN,"UNIT":"CFS"}
        self.ts1=rts(self.arr,self.stime1,self.dt,props)
        self.ts2=rts(self.arr+2,self.stime2,self.dt,None)
        irreg_data=numpy.arange(5.,dtype=float)
        irreg_times=numpy.array([_datetime.datetime(1994,1,2),_datetime.datetime(1994,1,24),
                                 _datetime.datetime(1994,2,3),_datetime.datetime(1994,2,16),
                                 _datetime.datetime(1994,2,18)])
        self.its1=its(irreg_times,irreg_data,None)

    def testHasnan(self):
        
        self.assertEqual(self.ts1.has_gap(),False)
        
        dt=time_interval(months=1)
        st=parse_time("1/1/1991")
        data=numpy.array([1.0])
        numpy.put(data,[0],numpy.nan)        
        ts=rts(data,st,dt)
        self.assertEqual(ts.has_gap(),True)
        
    def testRTSInterval(self):
        self.assertEqual(self.ts1.interval, time_interval(minutes=15))
        self.assertEqual(self.ts1.start,self.stime1)
        self.assertEqual(self.ts1.end,self.stime1 + (self.size1 - 1)*self.dt)
        self.assertEqual(len(self.ts1),self.size1)

    def testSlice(self):
        #x=self.ts1[_datetime.datetime(1992,3,7,0,0):_datetime.datetime(1992,3,7,1,45)]
        x=self.ts1[_datetime.datetime(1992,3,7,1,0):_datetime.datetime(1992,3,7,1,45)]
        self.assertEqual(len(x),3)  # assure that the values is clipped noninclusively on right
        x=self.ts1[_datetime.datetime(1992,3,7,0,0):_datetime.datetime(1992,3,7,0,45,1)]
        self.assertEqual(len(x),4)
        x=self.ts1[self.ts1.end - minutes(15): self.ts1.end]
        self.assertEqual(x,self.ts1.data[-2:-1])
        x=self.ts1[-1: self.ts1.end + minutes(1)]
        self.assertEqual(x,self.ts1.data[-1:])

    def testAddTimeSeries(self):
        # todo: binary, unary, various intervals
        #       incompabible interval NA
        ts3=self.ts1+self.ts2
        self.assertEqual(ts3[4].value,6.0)
        self.assertEqual(ts3.start,self.stime1)
        self.assertEqual(len(ts3),self.size1+4)
        self.assertEqual(ts3.end, increment(self.stime2,self.dt,(self.size1 - 1)))
        dt1=_datetime.datetime(1992,3,7,1,30)
        dt2=_datetime.datetime(1992,3,7,2,30)
        self.assertEqual(ts3[5].value,8.0)
        
        ts3=rts(self.arr,self.stime1+self.dt+self.dt,self.dt,{})
        ts4=ts3+self.ts1
        self.assertEqual(len(ts4),len(ts3)+2)
        self.assertTrue(numpy.isnan(ts4.data[0]))
        self.assertTrue(numpy.isnan(ts4.data[1])) 
        self.assertEqual(ts4.data[2],ts3.data[0]+self.ts1.data[2])
        self.assertTrue(numpy.isnan(ts4.data[-1])) 
        self.assertTrue(numpy.isnan(ts4.data[-2])) 
        
    
    def testAverageTimeseries(self):
        # test average multiple ts together
        stime=_datetime.datetime(1992,2,10)
        stime2=_datetime.datetime(1992,2,11)
        arr=numpy.arange(20)
        #arr2=2*arr
        #arr3=1.5*arr
        dt=time_interval(days=1)
        props={TIMESTAMP:PERIOD_START,AGGREGATION:MEAN,"UNIT":"CFS"}
        ts1=rts(arr,stime,dt,props)
        ts2=rts(arr,stime,dt,props)
        ts3=rts(arr,stime2,dt,props)
        ts4=(ts1+ts2)/2.0
        self.assertEqual(len(ts4),len(ts1))
        self.assertEqual(ts4.data[-1],ts1.data[-1])
        ts5=(ts1+ts3)/2.0
        self.assertEqual(len(ts5),len(ts1)+1)
        self.assertTrue(numpy.isnan(ts5.data[0]))
        self.assertTrue(numpy.isnan(ts5.data[-1]))
        self.assertEqual(ts5.data[1],(ts1.data[1]+ts3.data[0])/2.0)
        self.assertEqual(ts5.data[-2],(ts1.data[19]+ts3.data[18])/2.0)
                         
    def testAddTimeAlignmentBad(self):
        data = numpy.arange(100.)
        ts4 = rts(data, self.stime1, time_interval(minutes=60), None)
        self.assertRaises(ValueError, self.ts1.__add__, ts4)
        # Monthly, yearly

    def testAddScalar(self):
        ts4 = self.ts1 + 5.
        self.assertEqual(ts4[0].value,5.)
        self.assertEqual(ts4.start,self.ts1.start)
        self.assertEqual(len(ts4),len(self.ts1))
        self.assertTrue(ts4.is_regular())
        self.assertEqual(ts4.interval,self.ts1.interval)
        self.assertEqual(ts4.end,self.ts1.end)
        ts5 = self.its1+4.
        self.assertEqual(ts5[0].value,4.)
        self.assertEqual(ts5[4].value,8.)
        self.assertEqual(ts5.start,self.its1.start)
        self.assertTrue(not ts5.is_regular())

    def testInPlaceAddScalar(self):
        ts4=self.ts1 
        ts4 +=5.
        self.assertEqual(ts4[0].value,5.)
        self.assertEqual(ts4.start,self.ts1.start)
        self.assertEqual(len(ts4),len(self.ts1))
        self.assertTrue(ts4.is_regular())
        self.assertEqual(ts4.interval,self.ts1.interval)
        self.assertEqual(ts4.end,self.ts1.end)
        self.assertEqual(ts4.props["UNIT"],"CFS")
        self.assertEqual(ts4.props[AGGREGATION],MEAN)
        
    def testSubtractTimeSeries(self):
        # todo: binary, unary, various intervals
        #       incompabible interval
        ts5=self.ts2-self.ts1
        self.assertEqual(ts5[4].value,-2.0)
        self.assertEqual(ts5.start,self.stime1)
        self.assertEqual(len(ts5),self.size1+4)
        self.assertEqual(ts5.end, increment(self.stime2,self.dt,(self.size1 - 1)))
        #self.assert_(isNA(ts5[0]))
        #self.assert_(!isNA(ts5[4])
        #self.assert_(isNA(ts5[len(ts5)-1])        

    def testSubtractScalar(self):
        ts4 = self.ts1 - 5.
        self.assertEqual(ts4[0].value,-5.)
        self.assertEqual(ts4.start,self.ts1.start)
        self.assertEqual(len(ts4),len(self.ts1))
        self.assertEqual(ts4.interval,self.ts1.interval)
        self.assertEqual(ts4.end,self.ts1.end)
        
        ts5=5.0-self.ts1
        self.assertEqual(ts5[0].value,5.)
        self.assertEqual(ts5.start,self.ts1.start)
        self.assertEqual(len(ts5),len(self.ts1))
        self.assertEqual(ts5.interval,self.ts1.interval)
        self.assertEqual(ts5.end,self.ts1.end)


    def testRightSubtractScalar(self):
        # todo: binary, unary, various intervals
        #       incompabible interval
        ts5=self.ts2-5.
        self.assertEqual(ts5[0].value,-3.0)
        self.assertEqual(ts5[4].value,1.0)        
        self.assertEqual(ts5.start,self.ts2.start)
        self.assertEqual(len(ts5),len(self.ts2))
        self.assertEqual(ts5.end, self.ts2.end)

    def testNegate(self):
        ts5=-self.ts2
        self.assertEqual(ts5[0].value,-2.0)
        self.assertEqual(ts5[4].value,-6.0)  
        self.assertEqual(ts5.start,self.ts2.start)
        self.assertEqual(len(ts5),len(self.ts2))
        self.assertEqual(ts5.end, self.ts2.end)

    def testAbsValue(self):
        ts5=abs(self.ts1 - 2)
        self.assertEqual(ts5[0].value,2.0)
        self.assertEqual(ts5[4].value,2.0)        
        self.assertEqual(ts5.start,self.ts1.start)
        self.assertEqual(len(ts5),len(self.ts1))
        self.assertEqual(ts5.end, self.ts1.end)

    def testMultiply(self):
        ts5=self.ts2*self.ts1
        self.assertEqual(ts5[4].value,8.)
        self.assertTrue(numpy.isnan(ts5.data[-1]))
        ts5=self.ts1*2.
        self.assertEqual(ts5[4].value,8.)
        ts5=3.*self.ts1
        self.assertEqual(ts5[4].value,12.)

    def testDivide(self):
        ts5=self.ts2/self.ts1
        self.assertEqual(ts5[4].value,0.5)
        ts5=self.ts1/2.
        self.assertEqual(ts5[4].value,2.)
        ts6=2./self.ts1
        self.assertEqual(ts6[4].value,0.5)


    def testIter(self):
        i=0
        for el in self.ts1:
            val = el.value
            tk = el.ticks

    def test_is_regular(self):

        data=list(range(1000))
        start=self.stime1
        interval=time_interval(months=1)

        ts=rts(data,start,interval,{})

        self.assertTrue(ts.is_regular())

        interval=time_interval(hours=1)
        ts=rts(data,start,interval,{})

        self.assertTrue(ts.is_regular())
        
    def test_index_after(self):
        data=list(range(1000))
        start=self.stime1
        interval=time_interval(months=1)

        ts=rts(data,start,interval,{})
        
        t1=ts.ticks[0]
        i=ts.index_after(t1)        
        self.assertEqual(i,0)
        
        t2=ts.ticks[-1]
        i=ts.index_after(t2)
        self.assertEqual(i,len(ts)-1)

        # Before the first one
        t1 = ts.ticks[0] - 1
        i = ts.index_after(t1)
        self.assertEqual(i, 0)

        # After the last one
        t1 = ts.ticks[-1] + 1
        i = ts.index_after(t1)
        self.assertEqual(i, len(ts))

    def test_indexes_after(self):
        n = 10
        data = list(range(n))
        start = self.stime1
        interval = time_interval(days=1)
        ts = rts(data, start, interval, {})

        tm = [ts.start - minutes(1), ts.start, ts.start + minutes(1),
              ts.end, ts.end + minutes(1)]
        indexes = list(ts.index_after(tm))
        self.assertEqual(indexes, [0, 0, 1, n - 1, n])

    def test_get_span(self):
        n = 10
        data = list(range(n))
        start = self.stime1
        interval = time_interval(days=1)
        ts = rts(data, start, interval, {})

        # Inside
        stime = ts.start
        etime = ts.start + time_interval(days=2)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (0, 2))

        stime = ts.start + minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (1, 2))

        stime = ts.start
        etime = ts.start + days(2) + minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (0, 2))

        # Left outside
        stime = ts.start - time_interval(days=1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (0, 2))

        # Right outside
        stime = ts.start + time_interval(days=1)
        etime = ts.end + time_interval(days=1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (1, n - 1))

        # Both outside
        stime = ts.start - time_interval(days=1)
        etime = ts.end + time_interval(days=1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, False)
        self.assertEqual(indexes, (0, n - 1))

        # Totally outside
        stime = ts.start - time_interval(days=2)
        etime = ts.start - time_interval(days=1)
        self.assertRaises(ValueError, vtools.data.timeseries._get_span, ts,
                                                   stime, etime, False, False)

        stime = ts.end + time_interval(days=1)
        etime = ts.end + time_interval(days=2)
        self.assertRaises(ValueError, vtools.data.timeseries._get_span, ts,
                                                   stime, etime, False, False)

        # Inside with Left
        stime = ts.start + minutes(1)
        etime = ts.start + time_interval(days=2)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, True, False)
        self.assertEqual(indexes, (0, 2))

        stime = ts.start
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, True, False)
        self.assertEqual(indexes, (0, 2))

        # Left on the boundary
        stime = ts.start - minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, True, False)
        self.assertEqual(indexes, (0, 2))

        # Inside with Right
        stime = ts.start
        etime = ts.start + days(2) + minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, True)
        self.assertEqual(indexes, (0, 3))

        stime = ts.start
        etime = ts.end
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, True)
        self.assertEqual(indexes, (0, n - 1))

        stime = ts.start
        etime = ts.end + minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, False, True)
        self.assertEqual(indexes, (0, n - 1))

        # Left and Right
        stime = ts.start + minutes(1)
        etime = ts.start + days(1) + minutes(1)
        indexes = vtools.data.timeseries._get_span(ts,
                                                   stime, etime, True, True)
        self.assertEqual(indexes, (0, 2))

    def test_index_before(self):
        data=list(range(1000))
        start=self.stime1
        interval=time_interval(months=1)

        ts=rts(data,start,interval,{})
        # First one
        t1=ts.times[0]
        i=ts.index_before(t1)
        self.assertEqual(i, 0)

        # Between the first and second one
        t1=ts.times[0] + minutes(10)
        i=ts.index_before(t1)
        self.assertEqual(i, 0)

        # Last one
        t1=ts.times[-1]
        i=ts.index_before(t1)
        self.assertEqual(i, len(ts)-1)

        # Before the first one
        t1=ts.times[0] - minutes(10)
        i=ts.index_before(t1)
        self.assertEqual(i, -1)

        # After the last one
        t1=ts.times[-1] + minutes(1)
        i=ts.index_before(t1)
        self.assertEqual(i, len(ts)-1)

    def test_ts_copy(self):
        ## test copy part of a ts      
        stime=self.ts1.times[0]
        etime=self.ts1.times[8]
        newts=self.ts1.copy(start=stime,end=etime)
        self.assertEqual(len(newts),9)
        self.assertEqual(newts.props["UNIT"],"CFS")
        self.assertEqual(newts.props[AGGREGATION],MEAN)
        self.assertTrue(newts.data[0]==self.ts1.data[0])
        self.ts1.data[0]+=2.0
        self.assertTrue(not(newts.data[0]==self.ts1.data[0]))
       
        
        stime=self.its1.times[0]
        etime=self.its1.times[4]
        newits=self.its1.copy(start=stime,end=etime)
        self.assertEqual(len(newits),5)      
        self.assertTrue(newits.data[0]==self.its1.data[0])
        self.its1.data[0]+=2.0
        self.assertTrue(not(newits.data[0]==self.its1.data[0]))
        
        
    def test_ts_window(self):
        ## test windowing part of a ts
        stime=self.ts1.times[0]
        etime=self.ts1.times[8]
        newts=self.ts1.window(start=stime,end=etime)
        self.assertEqual(len(newts),9)
        self.assertEqual(newts.props["UNIT"],"CFS")
        self.assertEqual(newts.props[AGGREGATION],MEAN) 
        self.assertTrue(newts.data[0]==self.ts1.data[0])
        self.ts1.data[0]+=2.0
        self.assertTrue(newts.data[0]==self.ts1.data[0])
        
        stime=self.ts1.start + minutes(5)
        etime=self.ts1.times[8] + minutes(5)
        
        newts1=self.ts1.window(start=stime,end=etime)
        self.assertEqual(len(newts1),8)

        self.assertEqual(newts1.data[0],self.ts1.data[1])
        self.assertEqual(newts1.data[7],self.ts1.data[8])

        # Start of window is exact start of series
        newts1=self.ts1.window(start=self.ts1.start,end=etime,left=True)        
        self.assertEqual(len(newts1),9)
        self.assertEqual(newts1.data[0],self.ts1.data[0])
        self.assertEqual(newts1.data[8],self.ts1.data[8])
        
        newts1=self.ts1.window(start=self.ts1.start,end=etime,left=False)        
        self.assertEqual(len(newts1),9)
        self.assertEqual(newts1.data[0],self.ts1.data[0])
        self.assertEqual(newts1.data[8],self.ts1.data[8])        

        # End of window is exact end of series
        newts1=self.ts1.window(start=self.ts1.end - minutes(50),end=self.ts1.end,left=True)           
        self.assertEqual(len(newts1),5)
        self.assertEqual(newts1.data[0],self.ts1.data[-5])
        self.assertEqual(newts1.data[4],self.ts1.data[-1])
                
        # End of window is exact end of series
        newts1=self.ts1.window(start=self.ts1.end - minutes(50),end=self.ts1.end,left=True,right=True)           
        self.assertEqual(len(newts1),5)
        self.assertEqual(newts1.data[0],self.ts1.data[-5])
        self.assertEqual(newts1.data[4],self.ts1.data[-1])


                
        newts1=self.ts1.window(start=stime,end=etime,left=True)        
        self.assertEqual(len(newts1),9)
        self.assertEqual(newts1.data[0],self.ts1.data[0])
        self.assertEqual(newts1.data[8],self.ts1.data[8])
        
        newts1=self.ts1.window(start=stime,end=etime,right=True)       
        self.assertEqual(len(newts1),9)
        self.assertEqual(newts1.data[0],self.ts1.data[1])
        self.assertEqual(newts1.data[8],self.ts1.data[9])
        
        newts1=self.ts1.window(start=stime,end=etime,right=True,left=True)
        self.assertEqual(len(newts1),10)
        self.assertEqual(newts1.data[0],self.ts1.data[0])
        self.assertEqual(newts1.data[9],self.ts1.data[9])

        stime=self.ts1.end - minutes(100)
        etime=self.ts1.end - minutes(25)
        newts1=self.ts1.window(start=stime,end=etime)
        
        
        stime=self.ts1.end - minutes(100)
        etime=self.ts1.end - minutes(5)
        newts1=self.ts1.window(start=stime,end=etime)        
                 
        stime=self.its1.times[0]
        etime=self.its1.times[4]
        newits=self.its1.window(start=stime,end=etime)
        self.assertEqual(len(newits),5)      
        self.assertTrue(newits.data[0]==self.its1.data[0])
        self.its1.data[0]+=2.0
        self.assertTrue(newits.data[0]==self.its1.data[0])
        
        stime=self.ts1.start - minutes(2)
        etime=self.ts1.start - minutes(1)
        self.assertRaises(ValueError, self.its1.window, start=stime, end=etime)

        stime=self.ts1.end + minutes(1)
        etime=self.ts1.end + minutes(2)
        self.assertRaises(ValueError, self.its1.window, start=stime, end=etime)


    def test_ts_copy_left_right(self):
        ## test copy ts using left and right option
        dt=time_interval(minutes=2)
        stime=self.ts1.times[2]-dt
        etime=self.ts1.times[10]+dt
        newts=self.ts1.copy(start=stime,end=etime,left=True,right=True)
        self.assertEqual(len(newts),11)
        self.assertTrue(newts.data[0]==self.ts1.data[1])
        self.assertTrue(newts.data[10]==self.ts1.data[11])

        self.assertRaises(ValueError,self.ts1.copy,etime,stime)    
    
    def test_ts_replace(self):
        
        dt=time_interval(hours=1)
        data=[1.0,1.0,1.0,1.0,1.0,1.0]
        st=parse_time("1/30/1991")
        ts=rts(data,st,dt)
        start=parse_time("1/30/1991 1:00")
        end=parse_time("1/30/1991 3:00")
        val=2.0
        new_ts=ts.replace(val,start,end)
        self.assertEqual(new_ts.data[1],val)
        self.assertEqual(new_ts.data[2],val)
        self.assertEqual(new_ts.data[3],val)
        self.assertEqual(new_ts.data[0],ts.data[0])
        self.assertEqual(new_ts.data[4],ts.data[4])
        self.assertEqual(new_ts.data[5],ts.data[5])
        ts2=rts([val,val,val],start,dt)
        new_ts=ts.replace(ts2,start,end)
        self.assertEqual(new_ts.data[1],val)
        self.assertEqual(new_ts.data[2],val)
        self.assertEqual(new_ts.data[3],val)
        
        self.assertRaises(TypeError, ts.replace,"invalid",start,end)
        ts2=rts([val,val,val],start,time_interval(days=1))
        self.assertRaises(ValueError, ts.replace,ts2,start,end)
        ts2=rts([],start,dt)
        self.assertRaises(ValueError, ts.replace,ts2,start,end)
        

    def test_ts_start_after_28_with_relativedelta(self):
        dt=time_interval(months=1)
        st=parse_time("1/30/1991")
        num=120
        d2=parse_time("2/28/1991")
        data=list(range(num))
        ts1=rts(data,st,dt)
        self.assertEqual(ts1.times[1],d2)
        
        dt=time_interval(years=1)
        st=parse_time("2/29/2000")
        num=20
        data=list(range(num))
        ts2=rts(data,st,dt)
        d2=parse_time("2/28/2001")
        self.assertEqual(ts2.times[1],d2)
    
    def test_ts_centered(self):
          
        ## test of regular ts with interval of 15min 
        ts1_centered=self.ts1.centered(copy_data=False)
        self.assertEqual(len(ts1_centered),len(self.ts1)-1)
        self.assertEqual(ts1_centered.data[0],self.ts1.data[0])
        self.assertEqual(ts1_centered.data[-1],self.ts1.data[-2])
        rts_dt_half  = ticks(self.ts1.interval)/2
        centered_rts_start = self.ts1.times[0]+ticks_to_interval(rts_dt_half)
        self.assertEqual(ts1_centered.times[0],centered_rts_start) 
        
        dt=time_interval(months=1)
        st=parse_time("1/1/1991")
        num=120
        data=list(range(num))
        ts1=rts(data,st,dt)
        ## test of month interval ts
        ts1_centered = ts1.centered(copy_data=False, neaten=True)
        self.assertEqual(len(ts1_centered),num-1)
        self.assertEqual(ts1_centered.data[0],data[0])
        self.assertEqual(ts1_centered.data[-1],data[-2])
        self.assertEqual(ts1_centered.times[0],parse_time("1/15/1991"))
        ## check if new data share data with old one
        ts1.data[0]=-9999
        self.assertEqual(ts1_centered.data[0],ts1.data[0])
        ## check not share data with old one
        ts1_centered_not_share_data = ts1.centered(copy_data=True, neaten=True)
        ts1.data[0]=-10000
        self.assertNotEqual(ts1_centered_not_share_data.data[0],ts1.data[0])
        
        ## test of irregular ts
        its1_centered = self.its1.centered(copy_data=False)
        self.assertEqual(len(its1_centered),len(self.its1)-1)
        self.assertEqual(its1_centered.data[0],self.its1.data[0])
        self.assertEqual(its1_centered.data[-1],self.its1.data[-2])
        its_dt1 = self.its1.times[1]-self.its1.times[0]
        its_dt1_half  = ticks(its_dt1)/2
        centered_its_start = self.its1.times[0]+ticks_to_interval(its_dt1_half)
        self.assertEqual(its1_centered.times[0],centered_its_start)
        
    def test_ts_shift_rts(self):  

       # Test operations on ts of varied values.
       # ts_start, ts_len, ts_interval, shift_interval_str, shift_interval
        test_input=[(_datetime.datetime(1990,2,3,11,15),
                     3005,minutes(5),"1hour",_datetime.datetime(1990,2,5,11,30),_datetime.datetime(1990,2,8,11,30)),
                    (_datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3407,hours(1),"1day",_datetime.datetime(1990,2,5,11,30),_datetime.datetime(1990,2,8,11,30)),
                    (_datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),
                     3005,time_interval(minutes=5),"-1hour",_datetime.datetime(1990,2,5,11,30),_datetime.datetime(1990,2,8,11,30))                 
                    ]

        for (ts_start,ts_len,ts_intvl,shift_interval,shift_start,shift_end) in test_input:
            data=numpy.repeat(10.,ts_len)
            diff=parse_interval(shift_interval)
            
            # This ts is the orignial one
            ts0=rts(data,ts_start,ts_intvl)
            
            # First move forward.
            ts=ts0.shift(shift_interval,shift_start,shift_end)
           
            
           
    def test_ts_shift_its(self):  
    
        ts_len=10
        data=numpy.repeat(10.0,ts_len)
        ts_start=_datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        times=[ts_start]*ts_len
        
        intervals=[minutes(x) for x in [0,18,34,18,15,34,23,17,19,20]]
       
        for i in range(1,ts_len):
            times[i]=times[i-1]+intervals[i]
            
        ts0=its(times,data,{})        
        shift_interval=minutes(15)
        
        re=ts0.shift(shift_interval,start=ts0.times[3],end=ts0.times[7])
            
        correct_times = times
        
        for i in range(3,8):
            correct_times[i]=correct_times[i]+shift_interval
            
        for a,b in zip(correct_times,ts0.times):
            self.assertEqual(a,b)
        
    def test_rts_const(self):
        
        val =1.0
        start=_datetime.datetime(1990,2,3)
        end  =_datetime.datetime(1990,3,1)
        interval =hours(1)
        ts=rts_constant(start,end,interval,val=val)
        self.assertEqual(start,ts.start)
        self.assertEqual(end,ts.end)
        self.assertEqual(interval,ts.interval)
        self.assertEqual(ts.data[-1],val)
        
    
        start=_datetime.datetime(1990,2,3)
        end  =_datetime.datetime(1990,3,1)
        interval =hours(1)
        ts=rts_constant(start,end,interval)
        self.assertEqual(start,ts.start)
        self.assertEqual(end,ts.end)
        self.assertEqual(interval,ts.interval)
       
        self.assertTrue(np.isnan(ts.data).all())
        
        
    def test_ts_extension(self):
        
        dt=time_interval(hours=1)
        st=parse_time("1/1/1991")
        num=120
        data=list(range(100,num+100))
        ts1=rts(data,st,dt)
        
        new_start=parse_time("12/23/1990")
        new_end=parse_time("1/11/1991")
        val=1.0
        ts_new=extrapolate_ts(ts1,new_start,end=new_end,method="constant",val=val)
        self.assertEqual(new_start,ts_new.start)
        self.assertEqual(new_end,ts_new.end)
        index=0
        touchBegin=False
        touchEnd=False
        for index in range(len(ts_new)):
            if ts_new.data[index]==ts1.data[0]:
                self.assertEqual(ts_new.times[index],ts1.times[0])
                touchBegin=True
            if ts_new.data[index]==ts1.data[-1]:
                self.assertEqual(ts_new.times[index],ts1.times[-1])
                touchEnd=True
        self.assertTrue(touchBegin)
        self.assertTrue(touchEnd)
        
        ## test taper methods
        ts_new=extrapolate_ts(ts1,new_start,end=new_end,method="taper",val=val)
        self.assertAlmostEqual(ts_new.data[0],val)
        self.assertAlmostEqual(ts_new.data[-1],val)
        
        ## test taper with nan in old ts
        data[0]=np.nan
        ts1=rts(data,st,dt)
        ts_new=extrapolate_ts(ts1,new_start,end=new_end,method="taper",val=val)
        self.assertAlmostEqual(ts_new.data[0],val)
        self.assertAlmostEqual(ts_new.data[-1],val)

if __name__ == '__main__':
    unittest.main()
