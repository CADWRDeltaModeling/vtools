import unittest
import numpy
import datetime
from vtools.data.timeseries import *
from vtools.data.vtime import *
from vtools.data.constants import *
class TestTimeSeries(unittest.TestCase):

    def setUp(self):
        self.size1=100000
        self.arr=numpy.arange(self.size1,dtype=float)
        self.stime1=datetime(1992,3,7)
        self.stime2=datetime(1992,3,7,1,0)
        self.dt=time_interval(minutes=15)
        props={TIMESTAMP:INST,AGGREGATION:MEAN,"UNIT":"CFS"}
        self.ts1=rts(self.arr,self.stime1,self.dt,props)
        self.ts2=rts(self.arr+2,self.stime2,self.dt,None)
        irreg_data=numpy.arange(5.,dtype=float)
        irreg_times=numpy.array([datetime(1994,1,2),datetime(1994,1,24),
                                 datetime(1994,2,3),datetime(1994,2,16),
                                 datetime(1994,2,18)])
        self.its1=its(irreg_times,irreg_data,None)


    def testRTSInterval(self):
        self.assertEquals(self.ts1.interval, time_interval(minutes=15))
        self.assertEqual(self.ts1.start,self.stime1)
        self.assertEqual(self.ts1.end,self.stime1 + (self.size1 - 1)*self.dt)
        self.assertEqual(len(self.ts1),self.size1)

    def testSlice(self):
        #x=self.ts1[datetime(1992,3,7,0,0):datetime(1992,3,7,1,45)]
        x=self.ts1[datetime(1992,3,7,1,0):datetime(1992,3,7,1,45)]
        self.assertEqual(len(x),3)  # assure that the values is clipped noninclusively on right
        x=self.ts1[datetime(1992,3,7,0,0):datetime(1992,3,7,0,45,1)]
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
        dt1=datetime(1992,3,7,1,30)
        dt2=datetime(1992,3,7,2,30)
        self.assertEqual(ts3[5].value,8.0)

    def testAverageTimeseries(self):
        # test average multiple ts together
        stime=datetime(1992,2,10)
        stime2=datetime(1992,2,11)
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
        self.assert_(numpy.isnan(ts5.data[0]))
        self.assert_(numpy.isnan(ts5.data[-1]))
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
        self.assert_(ts4.is_regular())
        self.assertEqual(ts4.interval,self.ts1.interval)
        self.assertEqual(ts4.end,self.ts1.end)
        ts5 = self.its1+4.
        self.assertEqual(ts5[0].value,4.)
        self.assertEqual(ts5[4].value,8.)
        self.assertEqual(ts5.start,self.its1.start)
        self.assert_(not ts5.is_regular())

    def testInPlaceAddScalar(self):
        ts4=self.ts1 
        ts4 +=5.
        self.assertEqual(ts4[0].value,5.)
        self.assertEqual(ts4.start,self.ts1.start)
        self.assertEqual(len(ts4),len(self.ts1))
        self.assert_(ts4.is_regular())
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
        #self.assertEqual(ts4.interval,self.ts1.interval)
        self.assertEqual(ts4.end,self.ts1.end)


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
        self.assert_(numpy.isnan(ts5.data[-1]))
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

        data=range(1000)
        start=self.stime1
        interval=time_interval(months=1)

        ts=rts(data,start,interval,{})

        self.assert_(ts.is_regular())

        interval=time_interval(hours=1)
        ts=rts(data,start,interval,{})

        self.assert_(ts.is_regular())
        
    def test_index_after(self):
        
        data=range(1000)
        start=self.stime1
        interval=time_interval(months=1)

        ts=rts(data,start,interval,{})
        
        t1=ts.ticks[0]
        i=ts.index_after(t1)
        
        self.assertEqual(i,0)

    def test_ts_copy(self):
        ## test copy part of a ts      
        stime=self.ts1.times[0]
        etime=self.ts1.times[8]
        newts=self.ts1.copy(start=stime,end=etime)
        self.assertEqual(len(newts),9)
        self.assertEqual(newts.props["UNIT"],"CFS")
        self.assertEqual(newts.props[AGGREGATION],MEAN)
        self.assert_(newts.data[0]==self.ts1.data[0])
        self.ts1.data[0]+=2.0
        self.assert_(not(newts.data[0]==self.ts1.data[0]))
       
          
        stime=self.its1.times[0]
        etime=self.its1.times[4]
        newits=self.its1.copy(start=stime,end=etime)
        self.assertEqual(len(newits),5)      
        self.assert_(newits.data[0]==self.its1.data[0])
        self.its1.data[0]+=2.0
        self.assert_(not(newits.data[0]==self.its1.data[0]))

    def test_ts_window(self):
        ## test windowing part of a ts
        stime=self.ts1.times[0]
        etime=self.ts1.times[8]
        newts=self.ts1.window(start=stime,end=etime)
        self.assertEqual(len(newts),9)
        self.assertEqual(newts.props["UNIT"],"CFS")
        self.assertEqual(newts.props[AGGREGATION],MEAN) 
        self.assert_(newts.data[0]==self.ts1.data[0])
        self.ts1.data[0]+=2.0
        self.assert_(newts.data[0]==self.ts1.data[0])
                 
        stime=self.its1.times[0]
        etime=self.its1.times[4]
        newits=self.its1.window(start=stime,end=etime)
        self.assertEqual(len(newits),5)      
        self.assert_(newits.data[0]==self.its1.data[0])
        self.its1.data[0]+=2.0
        self.assert_(newits.data[0]==self.its1.data[0])
                

    def test_ts_copy_left_right(self):
        ## test copy ts using left and right option
        dt=time_interval(minutes=2)
        stime=self.ts1.times[2]-dt
        etime=self.ts1.times[10]+dt
        newts=self.ts1.copy(start=stime,end=etime,left=True,right=True)
        self.assertEqual(len(newts),11)
        self.assert_(newts.data[0]==self.ts1.data[1])
        self.assert_(newts.data[10]==self.ts1.data[11])

        self.assertRaises(ValueError,self.ts1.copy,etime,stime)    

    def test_ts_start_after_28_with_relativedelta(self):
        dt=time_interval(months=1)
        st=parse_time("1/30/1991")
        num=120
        d2=parse_time("2/28/1991")
        data=range(num)
        ts1=rts(data,st,dt,num)
        self.assertEqual(ts1.times[1],d2)
        
        dt=time_interval(years=1)
        st=parse_time("2/29/2000")
        num=20
        data=range(num)
        ts2=rts(data,st,dt,num)
        d2=parse_time("2/28/2001")
        self.assertEqual(ts2.times[1],d2)
        
                
  

if __name__ == '__main__':
    unittest.main()