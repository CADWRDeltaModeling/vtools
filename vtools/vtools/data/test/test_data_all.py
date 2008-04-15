import sys,os,unittest

from test_timeseries import TestTimeSeries
from test_vtime import TestVTime


def suite():    
    suite = unittest.TestSuite()
    suite.addTest(TestTimeSeries("testRTSInterval"))
    suite.addTest(TestTimeSeries("testSlice"))
    suite.addTest(TestTimeSeries("testAddTimeSeries"))
    suite.addTest(TestTimeSeries("testAddTimeAlignmentBad"))
    suite.addTest(TestTimeSeries("testAddScalar"))
    suite.addTest(TestTimeSeries("testSubtractTimeSeries"))
    suite.addTest(TestTimeSeries("testSubtractScalar"))
    suite.addTest(TestTimeSeries("testRightSubtractScalar")) 
    suite.addTest(TestTimeSeries("testNegate"))
    suite.addTest(TestTimeSeries("testAbsValue")) 
    suite.addTest(TestTimeSeries("testMultiply"))
    suite.addTest(TestTimeSeries("testDivide")) 
    suite.addTest(TestTimeSeries("testIter"))
    suite.addTest(TestTimeSeries("test_is_regular")) 
    suite.addTest(TestTimeSeries("test_index_after"))

    
    suite.addTest(TestVTime("testTimeInterval"))
    suite.addTest(TestVTime("testIncrement"))
    suite.addTest(TestVTime("testIncrementNegative"))
    suite.addTest(TestVTime("testNumberIntervalsTime"))
    suite.addTest(TestVTime("testNumberIntervalsCalendar"))
    suite.addTest(TestVTime("testTimeSequenceTime")) 
    suite.addTest(TestVTime("testTimeSequenceCalendar"))
    suite.addTest(TestVTime("testParseInterval")) 
    suite.addTest(TestVTime("testticks"))
    
    return suite


if __name__=="__main__":

    datasuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(datasuit)
    print result
