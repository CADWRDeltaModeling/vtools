import unittest
import datetime as _datetime
from vtools.data.vtime import *
from dateutil.relativedelta import relativedelta


class TestVTime(unittest.TestCase):

    def setUp(self):
        self.stime1=_datetime.datetime(1992,3,7)
        self.stime2=_datetime.datetime(1992,3,7,1,0)
        return

    def testTimeInterval(self):
        self.assertEqual(time_interval(seconds=15),seconds(15))
        self.assertEqual(time_interval(minutes=15),minutes(15))
        self.assertEqual(time_interval(hours=15),hours(15))
        self.assertEqual(time_interval(days=15),days(15))
        self.assertEqual(time_interval(months=2),months(2))
        self.assertEqual(time_interval(years=2),years(2))
        assert isinstance(months(15), relativedelta)
        return

    def testIncrement(self):
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    years(10),10
                                    ),
                          _datetime.datetime(2092,3,7))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    months(10),12
                                    ),
                          _datetime.datetime(2002,3,7))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    days(10),37
                                    ),
                          _datetime.datetime(1993,3,12))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    hours(10),24
                                    ),
                          _datetime.datetime(1992,3,17))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    minutes(10),240
                                    ),
                          _datetime.datetime(1992,3,8,16,0))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    seconds(10),360
                                    ),
                          _datetime.datetime(1992,3,7,1,0))        

    def testIncrementNegative(self):
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    years(10),-10
                                    ),
                          _datetime.datetime(1892,3,7))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    years(-10),10
                                    ),
                          _datetime.datetime(1892,3,7))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    months(-10),12
                                    ),
                          _datetime.datetime(1982,3,7))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    months(10),-12
                                    ),
                          _datetime.datetime(1982,3,7))
        
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    days(10),-37
                                    ),
                          _datetime.datetime(1991,3,3))
        self.assertEqual(increment(_datetime.datetime(1992,3,7,0,0,0),
                                    days(-10),37
                                    ),
                          _datetime.datetime(1991,3,3))
        


    def testNumberIntervalsTime(self):
        self.assertEqual(number_intervals(_datetime.datetime(1992,3,7,0,0,0),
                                           _datetime.datetime(1992,3,8,1,0,0),
                                           time_interval(minutes=15)),
                          100)
        self.assertEqual(number_intervals(_datetime.datetime(1992,3,7,0,0,0),
                                           _datetime.datetime(1992,3,8,1,1,0),
                                           time_interval(minutes=15)),
                          100)

        self.assertEqual(number_intervals(_datetime.datetime(1993,2,7,0,0,0),
                                           _datetime.datetime(1993,3,8,0,0,0),
                                           time_interval(hours=1)),
                          (29*24))
 
        self.assertEqual(number_intervals(_datetime.datetime(1993,2,7,0,0,0),
                                           _datetime.datetime(1993,3,8,1,1,0),
                                           time_interval(hours=1)),
                          (29*24+1))


        self.assertEqual(number_intervals(_datetime.datetime(1993,2,7,0,0,0),
                                           _datetime.datetime(1994,2,8,1,1,0),
                                           time_interval(days=2)),
                          183)

        self.assertEqual(number_intervals(_datetime.datetime(1993,2,7,0,0,0),
                                           _datetime.datetime(1993,2,7,1,17,0),
                                           time_interval(hours=1)),
                          1)
        return

    def testNumberIntervalsCalendar(self):
        for i in range(1,12):
            for j in range(i,13):
                #if number_intervals(_datetime.datetime(1992,i,7,0,0,0),
                #                                   _datetime.datetime(1992,j,7,0,0,0),
                #                                   time_interval(months=2)) != \
                #    (j-i)//2:
                #    print "*****************i:%s j:%s" % (i,j)
                self.assertEqual(number_intervals(_datetime.datetime(1992,i,7,0,0,0),
                                                   _datetime.datetime(1992,j,7,0,0,0),
                                                   time_interval(months=2)),
                                  (j-i)//2)
                
                self.assertEqual(number_intervals(_datetime.datetime(1992,i,7,0,0,0),
                                                   _datetime.datetime(1992,j,8,0,0,0),
                                                   time_interval(months=1)),
                                  j-i)
        
            self.assertEqual(number_intervals(_datetime.datetime(1992,i,7,0,0,0),
                                               _datetime.datetime(1992,i+1,6,0,0,0),
                                               time_interval(months=1)),
                              0)

            self.assertEqual(number_intervals(_datetime.datetime(1980,2,29,0,0,0),
                                               _datetime.datetime(1990,3,1,0,0,0),
                                               time_interval(years=1)),
                              10)

            
        
        return
     
     
    def testTimeSequenceTime(self):
        
        interval=_datetime.timedelta(days=1)
        interval_ticks=ticks(interval)
        sticks=ticks(self.stime1)
        n=1000
        timeseq1=[sticks+i*interval_ticks for i in range(0,n)]
        timeseq2=time_sequence(self.stime1,interval,n)
        for t1,t2 in zip(timeseq1,timeseq2):
            self.assertEqual(t1,t2)

        # Test only one interval is desired.
        n=1
        interval=days(1)
        timeseq=time_sequence(self.stime1,interval,n)
        self.assertEqual(len(timeseq),1)

    def testTimeSequenceZeroLen(self):
        
        interval=_datetime.timedelta(days=1)
        n=0
        timeseq=time_sequence(self.stime1,interval,n)
        self.assertEqual(len(timeseq),0)
    
    def testTimeSequenceCalendar(self):
        from dateutil import rrule
        #import pdb

        interval=relativedelta(months=1,days=2,hours=3,minutes=13,seconds=27)
        n=100
        timeseq1=list(map(ticks,[increment(self.stime1,interval,i) \
                            for i in range(n)]))
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
            timeseq1=list(map(ticks,timeseq1))
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
                   ('15minutes',_datetime.timedelta(minutes=15)),('10h',_datetime.timedelta(hours=10)),('60 min',_datetime.timedelta(minutes=60)))

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

        valid_dt=_datetime.timedelta(days=1,hours=2,minutes=3,seconds=35)
        dt_ticks=valid_dt.days*ticks_per_day + valid_dt.seconds*ticks_per_second
        self.assertEqual(ticks(valid_dt),dt_ticks)

    def testRoundTime(self):

        stime=_datetime.datetime(1992,3,7,10,24)
        correct_result= _datetime.datetime(1992,3,7,10)
        stime_rounded = round_time(stime,interval=hours(1))[0]
        self.assertEqual(stime_rounded,correct_result)

        stime=_datetime.datetime(1992,3,7,10,35)
        correct_result= _datetime.datetime(1992,3,7,11)
        stime_rounded = round_time(stime,interval=hours(1))[0]
        self.assertEqual(stime_rounded,correct_result)
        
        correct_result= _datetime.datetime(1992,3,7,10,30)
        stime_rounded = round_time(stime,interval=minutes(15))[0]
        self.assertEqual(stime_rounded,correct_result)

    def testAlignTime(self):
        stime=_datetime.datetime(1992,3,7,10)
        correct_result= _datetime.datetime(1992,3,7,10)
        left  = -1
        right = 1
        stime_aligned = align(stime,hours(1),left)
        self.assertEqual(stime_aligned,correct_result)
        stime_aligned = align(stime,hours(1),right)
        self.assertEqual(stime_aligned,correct_result)


        stime=_datetime.datetime(1992,3,7,10,24)
        correct_result_left_aligned = _datetime.datetime(1992,3,7,10)
        correct_result_right_aligned= _datetime.datetime(1992,3,7,11)
        left  = -1
        right = 1
        stime_aligned_left = align(stime,hours(1),left)
        self.assertEqual(stime_aligned_left,correct_result_left_aligned)
        stime_aligned_right = align(stime,hours(1),right)
        self.assertEqual(stime_aligned_right,correct_result_right_aligned)


    def testInferInterval(self):
        time_seq = [_datetime.datetime(1990,3,2,0,1,27),_datetime.datetime(1990,3,2,0,15,28),
                    _datetime.datetime(1990,3,2,0,30,28),_datetime.datetime(1990,3,2,0,45,28),
                    _datetime.datetime(1990,3,2,1,1,27),_datetime.datetime(1990,3,2,1,15,28),
                    _datetime.datetime(1990,3,2,1,30,28),_datetime.datetime(1990,3,2,1,45,28),
                    _datetime.datetime(1990,3,2,2,1,27),_datetime.datetime(1990,3,2,2,16,31)]
        self.assertEqual(minutes(15),infer_interval(time_seq,4./9.-0.001))
        self.assertFalse(infer_interval(time_seq,4./9.+0.001))
        self.assertFalse(infer_interval(time_seq,0.6,standard = [minutes(6),hours(1)]))
        self.assertEqual(infer_interval(time_seq,0.7,standard = [minutes(6),minutes(15),hours(1)]),minutes(15))
        time_seq = [_datetime.datetime(1990,3,2,0,1,27),_datetime.datetime(1990,3,2,0,15,0),
                    _datetime.datetime(1990,3,2,0,31,28),_datetime.datetime(1990,3,2,0,45,18),
                    _datetime.datetime(1990,3,2,1,1,27),_datetime.datetime(1990,3,2,1,15,28),
                    _datetime.datetime(1990,3,2,1,30,28),_datetime.datetime(1990,3,2,1,45,28),
                    _datetime.datetime(1990,3,2,2,1,27),_datetime.datetime(1990,3,2,2,16,31)]  
        ntvl = infer_interval(time_seq,0.7,standard = [minutes(6),minutes(15),hours(1)])
        print(ntvl)        
        self.assertEqual(ntvl,minutes(15))       
        print("Done")        

if __name__ == '__main__':
    unittest.main()
