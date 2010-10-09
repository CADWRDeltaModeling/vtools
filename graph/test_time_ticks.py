import unittest
from vtools.data.vtime import *
from dateutil.relativedelta import relativedelta
from datetime import datetime
from vtools.graph.time_ticks import auto_time_ticks,auto_interval,_calc_time_unit,align

class TestTimeTicks(unittest.TestCase):

    def testCalcTickUnit(self):
        t1 = ticks(datetime(1992,3,7,0,0,0))
        t2 = ticks(datetime(1992,3,10,0,0,0))
        t3 = ticks(datetime(1992,3,10,1,0,0))
        t4 = ticks(datetime(1992,2,1,0,0,0))
        t5 = ticks(datetime(1992,4,1,0,0,0))
        intvl1 = days(1)
        intvl2 = hours(2)
        intvl3 = minutes(15)
        calc = _calc_time_unit(t2-t1,t1)
        self.assertEqual(calc[0],days(1))
        self.assertEqual(calc[1],3.0)
        calc = _calc_time_unit(t3-t1,t1)        
        self.assertEqual(calc[0],days(1))
        self.assertEqual(calc[1],3.+1./24.)
        calc = _calc_time_unit(t5-t4,t4)        
        self.assertEqual(calc[0],months(1))
        self.assertEqual(calc[1],2.0)
        calc = _calc_time_unit(ticks(intvl3),t2)   
        self.assertEqual(calc[0],minutes(1))
        self.assertEqual(calc[1],15.0)
        
    def testAlign(self):
        self.assertEqual(align(datetime(1992,3,7,0,1,0),
                               minutes(15),-1), \
                         datetime(1992,3,7,0,0,0))
        self.assertEqual(align(datetime(1992,3,7,0,1,0),
                               minutes(15),1), \
                         datetime(1992,3,7,0,15,0))
        self.assertEqual(align(datetime(1992,3,7,0,0,0),
                               minutes(15),-1), \
                         datetime(1992,3,7,0,0,0))
        self.assertEqual(align(datetime(1992,3,7,0,0,0),
                               minutes(15),+1), \
                         datetime(1992,3,7,0,0,0))
        self.assertEqual(align(datetime(1992,1,1,0,0,0),
                               months(2),-1), \
                         datetime(1992,1,1,0,0,0))
        self.assertEqual(align(datetime(1992,1,1,0,0,0),
                               months(2),1), \
                         datetime(1992,1,1,0,0,0))
        self.assertEqual(align(datetime(1992,3,7,0,0,0),
                               months(2),-1), \
                         datetime(1992,3,1,0,0,0))
        self.assertEqual(align(datetime(1992,3,7,0,0,0),
                               months(2),+1), \
                         datetime(1992,5,1,0,0,0))
        
        
    def display(self,start,end,auto):
        print "start %s end %s auto: %s nintvl %s" % (start,end,auto, \
                                    number_intervals(start,end,auto))
        
        

    def testTimeTicks(self):
        for i in [4,7,10,12] :
            for j in [1,7,12,15,30]:
                for d in [1,7,29]:
                    start = datetime(1992,3,d)
                    end = datetime(1992,i,j)
                    tickpoints = auto_time_ticks(ticks(start),ticks(end),
                                     "auto","auto","auto",False)
                    ticktimes = map(ticks_to_time,tickpoints)
                    y= [ datetime.strftime(t,"%d%b%Y %H:%M") 
                           for t in ticktimes ]
                    #auto = auto_interval(ticks(start), ticks(end))
                    #self.display(start,end,auto)
        return

     


if __name__ == '__main__':
    unittest.main()

