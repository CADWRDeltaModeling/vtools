import unittest,random,pdb

## Datetime import

## vtools import.
from vtools.data.timeseries import *
from vtools.data.vtime import *

## Scipy testing suite import.
from numpy.testing import assert_array_equal, assert_equal
from numpy.testing import assert_almost_equal, assert_array_almost_equal

## Scipy import.
import scipy
## Local import 
from godin import *

class TestGodin(unittest.TestCase):

    """ test functionality of shift operations """

    def __init__(self,methodName="runTest"):

        super(TestGodin,self).__init__(methodName)
                         
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
                
    def test_godin(self):
        """ test a godin filter on a series of 1hour interval with four
            frequencies.
        """
        # Test operations on ts of varied values.
        test_ts=[(datetime(year=1990,month=2,day=3,hour=11, minute=15),\
                  int(scipy.math.pow(2,10)),time_interval(hours=1)),]

        f1=0.76
        f2=0.44
        f3=0.95
        f4=1.23
        av1=f1*scipy.pi/12
        av2=f2*scipy.pi/12
        av3=f3*scipy.pi/12
        av4=f4*scipy.pi/12
                 
        for (st,num,delta) in test_ts:
            ## this day contains components of with frequecies of 0.76/day,
            ## 0.44/day, 0.95/day, 1.23/day            
            data=[scipy.math.sin(av1*k)+0.7*scipy.math.cos(av2*k)+2.4*scipy.math.sin(av3*k) 
                  +0.1*scipy.math.sin(av4*k) for k in range(num)] 
                                
            # This ts is the orignial one.           
            ts0=rts(data,st,delta,{})   
            ts=godin(ts0)
            self.assert_(ts.is_regular())
            
    def test_godin_15min(self):        
        """ test godin filtering on a 15min constant values 
            data series with a nan.
        """        
        data=[1.0]*800+[2.0]*400+[1.0]*400
        data=scipy.array(data)
        data[336]=scipy.nan
        st=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        nt3=godin(test_ts)
        self.assert_(scipy.alltrue(scipy.isnan(nt3.data[0:144])))
        assert_array_almost_equal(nt3.data[144:192],[1]*48,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt3.data[192:481])))
        assert_array_almost_equal(nt3.data[481:656],[1]*175,12)
        self.assert_(scipy.alltrue(scipy.greater(nt3.data[656:944],1)))
        self.assertAlmostEqual(nt3.data[868],1.916618441)
        assert_array_almost_equal(nt3.data[944:1056],[2]*112,12)
        self.assert_(scipy.alltrue(scipy.greater(nt3.data[1056:1344],1)))
        self.assertAlmostEqual(nt3.data[1284],1.041451845)
        assert_array_almost_equal(nt3.data[1344:1456],[1]*112,12)
        self.assert_(scipy.alltrue(scipy.isnan(nt3.data[1456:1600])))   
                                   
    def test_godin_2d(self):
        
        """ Test godin filter on 2-dimensional data set."""
        
        d1=[1.0]*800+[2.0]*400+[1.0]*400
        d2=[1.0]*800+[2.0]*400+[1.0]*400
        data=scipy.array([d1,d2])
        data=scipy.transpose(data)
        data[336,:]=scipy.nan
        st=datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        
        nt3=godin(test_ts)
        d1=nt3.data[:,0]
        d2=nt3.data[:,1]
        self.assert_(scipy.alltrue(scipy.isnan(d1[0:144])))
        assert_array_almost_equal(d1[144:192],[1]*48,12)
        self.assert_(scipy.alltrue(scipy.isnan(d1[192:481])))
        assert_array_almost_equal(d1[481:656],[1]*175,12)
        self.assert_(scipy.alltrue(scipy.greater(d1[656:944],1)))
        self.assertAlmostEqual(d1[868],1.916618441)
        assert_array_almost_equal(d1[944:1056],[2]*112,12)
        self.assert_(scipy.alltrue(scipy.greater(d1[1056:1344],1)))
        self.assertAlmostEqual(d1[1284],1.041451845)
        assert_array_almost_equal(d1[1344:1456],[1]*112,12)
        self.assert_(scipy.alltrue(scipy.isnan(d1[1456:1600]))) 
        
        self.assert_(scipy.alltrue(scipy.isnan(d2[0:144])))
        assert_array_almost_equal(d2[144:192],[1]*48,12)
        self.assert_(scipy.alltrue(scipy.isnan(d2[192:481])))
        assert_array_almost_equal(d2[481:656],[1]*175,12)
        self.assert_(scipy.alltrue(scipy.greater(d2[656:944],1)))
        self.assertAlmostEqual(d2[868],1.916618441)
        assert_array_almost_equal(d2[944:1056],[2]*112,12)
        self.assert_(scipy.alltrue(scipy.greater(d2[1056:1344],1)))
        self.assertAlmostEqual(d2[1284],1.041451845)
        assert_array_almost_equal(d2[1344:1456],[1]*112,12)
        self.assert_(scipy.alltrue(scipy.isnan(d2[1456:1600]))) 
              
if __name__=="__main__":
    
    unittest.main()       



    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
