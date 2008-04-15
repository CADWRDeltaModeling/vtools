import unittest
import numpy
import datetime
from vtools.data.timeseries import *
from vtools.data.vtime import *

class TestTimeSeries(unittest.TestCase):

    def setUp(self):
        self.size1=100000
        self.arr=numpy.arange(self.size1,dtype=float)
        self.stime1=datetime(1992,3,7)
        self.stime2=datetime(1992,3,7,1,0)
        self.dt=time_interval(minutes=15)
        self.ts1=rts(self.arr,self.stime1,self.dt,None)
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
        x=self.ts1[datetime(1992,3,7,0,0):datetime(1992,3,7,0,45)]
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
        self.assert_(not(numpy.isnan(ts5.data[-1])))
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
        
        

        

        
        

    #@todo: add test funcs for index_after of timeseries also.


if __name__ == '__main__':
    unittest.main()
