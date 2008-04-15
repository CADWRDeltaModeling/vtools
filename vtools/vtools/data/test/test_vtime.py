import unittest
from vtools.data.vtime import *
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from datetime import datetime

class TestVTime(unittest.TestCase):

    def setUp(self):
        self.stime1=datetime(1992,3,7)
        self.stime2=datetime(1992,3,7,1,0)
        return

    def testTimeInterval(self):
        self.assertEquals(time_interval(seconds=15),seconds(15))
        self.assertEquals(time_interval(minutes=15),minutes(15))
        self.assertEquals(time_interval(hours=15),hours(15))
        self.assertEquals(time_interval(days=15),days(15))
        self.assertEquals(time_interval(months=2),months(2))
        self.assertEquals(time_interval(years=2),years(2))
        assert isinstance(months(15), relativedelta)
        return

    def testIncrement(self):
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    years(10),10
                                    ),
                          datetime(2092,3,7))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    months(10),12
                                    ),
                          datetime(2002,3,7))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    days(10),37
                                    ),
                          datetime(1993,3,12))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    hours(10),24
                                    ),
                          datetime(1992,3,17))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    minutes(10),240
                                    ),
                          datetime(1992,3,8,16,0))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    seconds(10),360
                                    ),
                          datetime(1992,3,7,1,0))        

    def testIncrementNegative(self):
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    years(10),-10
                                    ),
                          datetime(1892,3,7))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    years(-10),10
                                    ),
                          datetime(1892,3,7))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    months(-10),12
                                    ),
                          datetime(1982,3,7))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    months(10),-12
                                    ),
                          datetime(1982,3,7))
        
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    days(10),-37
                                    ),
                          datetime(1991,3,3))
        self.assertEquals(increment(datetime(1992,3,7,0,0,0),
                                    days(-10),37
                                    ),
                          datetime(1991,3,3))
        


    def testNumberIntervalsTime(self):
        self.assertEquals(number_intervals(datetime(1992,3,7,0,0,0),
                                           datetime(1992,3,8,1,0,0),
                                           time_interval(minutes=15)),
                          100)
        self.assertEquals(number_intervals(datetime(1992,3,7,0,0,0),
                                           datetime(1992,3,8,1,1,0),
                                           time_interval(minutes=15)),
                          100)

        self.assertEquals(number_intervals(datetime(1993,2,7,0,0,0),
                                           datetime(1993,3,8,0,0,0),
                                           time_interval(hours=1)),
                          (29*24))
 
        self.assertEquals(number_intervals(datetime(1993,2,7,0,0,0),
                                           datetime(1993,3,8,1,1,0),
                                           time_interval(hours=1)),
                          (29*24+1))


        self.assertEquals(number_intervals(datetime(1993,2,7,0,0,0),
                                           datetime(1994,2,8,1,1,0),
                                           time_interval(days=2)),
                          183)

        self.assertEquals(number_intervals(datetime(1993,2,7,0,0,0),
                                           datetime(1993,2,7,1,17,0),
                                           time_interval(hours=1)),
                          1)
        return

    def testNumberIntervalsCalendar(self):
        for i in range(1,12):
            for j in range(i,13):
                #if number_intervals(datetime(1992,i,7,0,0,0),
                #                                   datetime(1992,j,7,0,0,0),
                #                                   time_interval(months=2)) != \
                #    (j-i)//2:
                #    print "*****************i:%s j:%s" % (i,j)
                self.assertEquals(number_intervals(datetime(1992,i,7,0,0,0),
                                                   datetime(1992,j,7,0,0,0),
                                                   time_interval(months=2)),
                                  (j-i)//2)
                
                self.assertEquals(number_intervals(datetime(1992,i,7,0,0,0),
                                                   datetime(1992,j,8,0,0,0),
                                                   time_interval(months=1)),
                                  j-i)
        
            self.assertEquals(number_intervals(datetime(1992,i,7,0,0,0),
                                               datetime(1992,i+1,6,0,0,0),
                                               time_interval(months=1)),
                              0)

            self.assertEquals(number_intervals(datetime(1980,2,29,0,0,0),
                                               datetime(1990,3,1,0,0,0),
                                               time_interval(years=1)),
                              10)

            
        
        return
     
     
    def testTimeSequenceTime(self):
        from datetime import timedelta
        from enthought.util import numerix
        interval=timedelta(days=1)
        interval_ticks=ticks(interval)
        sticks=ticks(self.stime1)
        n=1000
        timeseq1=[sticks+i*interval_ticks for i in range(0,n)]
        timeseq2=time_sequence(self.stime1,interval,n)
        for t1,t2 in zip(timeseq1,timeseq2):
            self.assertEqual(t1,t2)
        
        # Incorrect start date
        wrongstime=datetime(1993,3,29)
        interval=months(1)
        self.assertRaises(ValueError,time_sequence,wrongstime,interval,n)

        # Test only one interval is desired.
        n=1
        interval=days(1)
        timeseq=time_sequence(self.stime1,interval,n)
        self.assertEqual(len(timeseq),1)

        
        
    
    def testTimeSequenceCalendar(self):
        from dateutil import rrule
        from enthought.util import numerix
        #import pdb

        interval=relativedelta(months=1,days=2,hours=3,minutes=13,seconds=27)
        n=100
        timeseq1=map(ticks,[increment(self.stime1,interval,i) \
                            for i in range(n)])
        timeseq2=time_sequence(self.stime1,interval,n)
        for t1,t2 in zip(timeseq1,timeseq2):
            self.assertEqual(t1,t2)



        test_cases=[("years",1,rrule.YEARLY),("months",1,rrule.MONTHLY), ("days",7,rrule.WEEKLY),
                   ("days",1,rrule.DAILY), ("hours",1,rrule.HOURLY),
                   ("minutes",1,rrule.MINUTELY), ("seconds",1,rrule.SECONDLY)]
        
        for (argname,argval,frequency) in test_cases:     
            interval=relativedelta()
            setattr(interval,argname,argval)
            n=100
            set=rrule.rruleset()
            set.rrule(rrule.rrule(frequency,dtstart=self.stime1,count=n))
            set.rdate(self.stime1)
            timeseq1=list(set)
            timeseq1=map(ticks,timeseq1)
            timeseq2=time_sequence(self.stime1,interval,n)
            for t1,t2 in zip(timeseq1,timeseq2):
                self.assertEqual(t1,t2)

    def testParseInterval(self):
        
        
        testcases=(('2s',seconds(2)),
                   ('5min',minutes(5)),
                   ('-12hours',hours(-12)),
                   ('1month',months(1)),
                   ('1mon',months(1)),
                   ('1year',years(1)),
                   ('1 year',years(1)),
                   ('1y1mon2h3min',time_interval(years=1,months=1,hours=2,minutes=3)),
                   ('1year 2month 2hours 10minutes',time_interval(years=1,months=2,hours=2,minutes=10)),
                   ('15minutes',timedelta(minutes=15)),('10h',timedelta(hours=10)),('60 min',timedelta(minutes=60)))
                   

        for (in1,out1) in testcases:

            out=parse_interval(in1)
            self.assertEqual(out,out1)

        invalidinput={}
        self.assertRaises(TypeError,parse_interval, invalidinput)

        invalidstring="not a time"
        self.assertRaises(ValueError,parse_interval, invalidstring)

    def testticks(self):




        invalid_dt=relativedelta(months=1)
        self.assertRaises(ValueError,ticks, invalid_dt)

#        valid_dt=relativedelta(days=1,hours=2,minutes=3,seconds=35)
#        dt_ticks=valid_dt.days*ticks_per_day + valid_dt.seconds*ticks_per_second+\
#                   valid_dt.hours*ticks_per_minute*60 + valid_dt.minutes*ticks_per_minute
#        self.assertEqual(ticks(valid_dt),dt_ticks)

        valid_dt=timedelta(days=1,hours=2,minutes=3,seconds=35)
        dt_ticks=valid_dt.days*ticks_per_day + valid_dt.seconds*ticks_per_second
        self.assertEqual(ticks(valid_dt),dt_ticks)

                

if __name__ == '__main__':
    unittest.main()
