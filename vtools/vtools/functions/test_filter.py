

import unittest,random,pdb

## Datetime import
import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval

## Scipy testing suite import.
from numpy.testing import assert_array_equal, assert_equal
from numpy.testing import assert_almost_equal, assert_array_almost_equal
from numpy import arange
## Scipy import.
import scipy
## Local import 
from filter import *

pi=scipy.pi

class TestFilter(unittest.TestCase):

    """ test functionality of shift operations """

    def __init__(self,methodName="runTest"):

        super(TestFilter,self).__init__(methodName)
                         
        # Number of data in a time series.
        self.num_ts=1000
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.test_interval=[time_interval(minutes=30),time_interval(hours=2),
                            time_interval(days=1)]
   
    def setUp(self):
        pass        
        #self.out_file=open("result.txt","a")
                 
    def tearDown(self):
        pass
        #self.out_file.close()    
                
            
    def test_butterworth(self):
        """ test a godin filter on a series of 1hour interval with four
            frequencies.
        """
        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),\
                  int(scipy.math.pow(2,10)),time_interval(hours=1)),]

        f1=0.76
        f2=0.44
        f3=0.95
        f4=1.23
        av1=f1*pi/12
        av2=f2*pi/12
        av3=f3*pi/12
        av4=f4*pi/12
                 
        for (st,num,delta) in test_ts:
            ## this day contains components of with frequecies of 0.76/day,
            ## 0.44/day, 0.95/day, 1.23/day            
            data=[scipy.math.sin(av1*k)+0.7*scipy.math.cos(av2*k)+2.4*scipy.math.sin(av3*k) 
                  +0.1*scipy.math.sin(av4*k) for k in range(num)] 
                                
            # This ts is the orignial one.           
            ts0=rts(data,st,delta,{})   
            ts=butterworth(ts0)
            self.assert_(ts.is_regular())
            
    def test_butterworth_noevenorder(self):
        """ test a butterworth with non even order input
        """
        st=datetime.datetime(year=2000,month=2,day=3)
        delta=time_interval(hours=1)
        data=arange(100)
        order=7
        ts0=rts(data,st,delta,{})
        self.assertRaises(ValueError,butterworth,ts0,order)
        
    
    def test_boxcar(self):
        
        """ test boxcar performance in each steps of a godin filter"""
                
        data=[1.0]*200+[2.0]*100+[1.0]*100
        data=scipy.array(data)
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        test_ts=rts(data,st,delta,{})
        
        
        ## first round of boxcar in 24 (11,12).
        nt=boxcar(test_ts,11,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt.data[0:11])))
        assert_array_almost_equal(nt.data[11:188],[1]*177,12)
        self.assert_(scipy.alltrue(scipy.greater(nt.data[188:211],1)))
        self.assertAlmostEqual(nt.data[196],1.375)
        assert_array_almost_equal(nt.data[211:288],[2]*77,12)
        self.assert_(scipy.alltrue(scipy.greater(nt.data[288:311],1)))
        self.assertAlmostEqual(nt.data[301],1.4166666667)
        assert_array_almost_equal(nt.data[311:388],[1]*77,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt.data[388:400])))
    
        ## second round of boxcar in 24 (12,11)
        nt2=boxcar(nt,12,11)
        self.assert_(scipy.alltrue(scipy.isnan(nt2.data[0:23])))
        assert_array_almost_equal(nt2.data[23:177],[1]*154,12)
        self.assert_(scipy.alltrue(scipy.greater(nt2.data[177:223],1)))
        self.assertAlmostEqual(nt2.data[196],1.364583333)
        assert_array_almost_equal(nt2.data[223:277],[2]*54,12)
        self.assert_(scipy.alltrue(scipy.greater(nt2.data[277:323],1)))
        self.assertAlmostEqual(nt2.data[301],1.439236111)
        assert_array_almost_equal(nt2.data[323:377],[1]*54,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt2.data[377:400])))
        
        ## third round of boxcar.   
        nt3=boxcar(nt2,12,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt3.data[0:35])))
        assert_array_almost_equal(nt3.data[35:165],[1]*130,12)
        self.assert_(scipy.alltrue(scipy.greater(nt3.data[165:235],1)))
        self.assertAlmostEqual(nt3.data[196],1.393055556)
        assert_array_almost_equal(nt3.data[235:265],[2]*30,12)
        self.assert_(scipy.alltrue(scipy.greater(nt3.data[265:335],1)))
        self.assertAlmostEqual(nt3.data[301],1.453819444)
        assert_array_almost_equal(nt3.data[335:365],[1]*30,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt3.data[365:400])))

    def test_daily_average(self):
        
        """ Test godin filter on 2-dimensional data set."""
        
        d1=[1.0]*800+[2.0]*400+[1.0]*400
        d2=[1.0]*800+[2.0]*400+[1.0]*400
        data=scipy.array([d1,d2])
        data=scipy.transpose(data)
        data[336,:]=scipy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        nt3=daily_average(test_ts)
        
              
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
