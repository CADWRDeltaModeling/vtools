

import unittest,random,pdb

## Datetime import
import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import ticks,number_intervals
from vtools.data.vtime import ticks_to_time,ticks\
     ,number_intervals,time_sequence,time_interval,hours

from vtools.data.sample_series import *

## numpy testing suite import.
from numpy.testing import assert_array_equal, assert_equal
from numpy.testing import assert_almost_equal, assert_array_almost_equal,\
                          assert_array_equal
from numpy import arange
## numpy import.
import numpy
## Local import 
from filter import *
from pylab import *
from scipy.signal import lfilter,filtfilt
from scipy.signal.filter_design import butter
 
pi=numpy.pi

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
        """ Butterworth filter on a series of 1hour interval with four
            frequencies.
        """
        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),\
                  int(numpy.math.pow(2,10)),time_interval(hours=1)),]

        f1=0.76
        f2=0.44
        f3=0.95
        f4=1.23
        av1=f1*pi/12
        av2=f2*pi/12
        av3=f3*pi/12
        av4=f4*pi/12
        import pylab as plt        
        for (st,num,delta) in test_ts:
            ## this day contains components of with frequecies of 0.76/day,
            ## 0.44/day, 0.95/day, 1.23/day            
            data=[numpy.math.sin(av1*k)+0.7*numpy.math.cos(av2*k)+2.4*numpy.math.sin(av3*k) 
                  +0.1*numpy.math.sin(av4*k) for k in range(num)] 
                                
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

    def test_boxcar_nan(self):
        
        """ test boxcar performance with a nan in data"""
                
        data=[1.0]*200+[2.0]*100+[1.0]*100
        data=numpy.array(data)
        data[201]=numpy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        test_ts=rts(data,st,delta,{})
        nt=boxcar(test_ts,11,12)
        
        ## besides the leading and trailing nan, there will be
        ## 24 nan in the middle 
        self.assert_(numpy.alltrue(numpy.isnan(nt.data[190:213])))
        
        
    def test_boxcar(self):
        
        """ test boxcar performance in each steps of a godin filter"""
                
        data=[1.0]*200+[2.0]*100+[1.0]*100
        data=numpy.array(data)
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        test_ts=rts(data,st,delta,{})
        
        
        ## first round of boxcar in 24 (11,12).
        nt=boxcar(test_ts,11,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt.data[0:11])))
        assert_array_almost_equal(nt.data[11:188],[1]*177,12)
        self.assert_(numpy.alltrue(numpy.greater(nt.data[188:211],1)))
        self.assertAlmostEqual(nt.data[196],1.375)
        assert_array_almost_equal(nt.data[211:288],[2]*77,12)
        self.assert_(numpy.alltrue(numpy.greater(nt.data[288:311],1)))
        self.assertAlmostEqual(nt.data[301],1.4166666667)
        assert_array_almost_equal(nt.data[311:388],[1]*77,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt.data[388:400])))
    
        ## second round of boxcar in 24 (12,11)
        nt2=boxcar(nt,12,11)
        self.assert_(numpy.alltrue(numpy.isnan(nt2.data[0:23])))
        assert_array_almost_equal(nt2.data[23:177],[1]*154,12)
        self.assert_(numpy.alltrue(numpy.greater(nt2.data[177:223],1)))
        self.assertAlmostEqual(nt2.data[196],1.364583333)
        assert_array_almost_equal(nt2.data[223:277],[2]*54,12)
        self.assert_(numpy.alltrue(numpy.greater(nt2.data[277:323],1)))
        self.assertAlmostEqual(nt2.data[301],1.439236111)
        assert_array_almost_equal(nt2.data[323:377],[1]*54,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt2.data[377:400])))
        
        ## third round of boxcar.   
        nt3=boxcar(nt2,12,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt3.data[0:35])))
        assert_array_almost_equal(nt3.data[35:165],[1]*130,12)
        self.assert_(numpy.alltrue(numpy.greater(nt3.data[165:235],1)))
        self.assertAlmostEqual(nt3.data[196],1.393055556)
        assert_array_almost_equal(nt3.data[235:265],[2]*30,12)
        self.assert_(numpy.alltrue(numpy.greater(nt3.data[265:335],1)))
        self.assertAlmostEqual(nt3.data[301],1.453819444)
        assert_array_almost_equal(nt3.data[335:365],[1]*30,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt3.data[365:400])))

    def test_daily_average(self):
        
        """ Test godin filter on 2-dimensional data set."""
        
        d1=[1.0]*800+[2.0]*400+[1.0]*400
        d2=[1.0]*800+[2.0]*400+[1.0]*400
        data=numpy.array([d1,d2])
        data=numpy.transpose(data)
        data[336,:]=numpy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        nt3=daily_average(test_ts)
        
    def test_godin(self):
        """ test a godin filter on a series of 1hour interval with four
            frequencies.
        """
        # Test operations on ts of varied values.
        test_ts=[(datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15),\
                  int(numpy.math.pow(2,10)),time_interval(hours=1)),]

        f1=0.76
        f2=0.44
        f3=0.95
        f4=1.23
        av1=f1*numpy.pi/12
        av2=f2*numpy.pi/12
        av3=f3*numpy.pi/12
        av4=f4*numpy.pi/12
                 
        for (st,num,delta) in test_ts:
            ## this day contains components of with frequecies of 0.76/day,
            ## 0.44/day, 0.95/day, 1.23/day            
            data=[numpy.math.sin(av1*k)+0.7*numpy.math.cos(av2*k)+2.4*numpy.math.sin(av3*k) 
                  +0.1*numpy.math.sin(av4*k) for k in range(num)] 
                                
            # This ts is the orignial one.           
            ts0=rts(data,st,delta,{})   
            ts=godin(ts0)
            self.assert_(ts.is_regular())
            
    def test_godin_15min(self):        
        """ test godin filtering on a 15min constant values 
            data series with a nan.
        """        
        data=[1.0]*800+[2.0]*400+[1.0]*400
        data=numpy.array(data)
        data[336]=numpy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        nt3=godin(test_ts)
        self.assert_(numpy.alltrue(numpy.isnan(nt3.data[0:144])))
        assert_array_almost_equal(nt3.data[144:192],[1]*48,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt3.data[192:481])))
        assert_array_almost_equal(nt3.data[481:656],[1]*175,12)
        self.assert_(numpy.alltrue(numpy.greater(nt3.data[656:944],1)))
        self.assertAlmostEqual(nt3.data[868],1.916618441)
        assert_array_almost_equal(nt3.data[944:1056],[2]*112,12)
        self.assert_(numpy.alltrue(numpy.greater(nt3.data[1056:1344],1)))
        self.assertAlmostEqual(nt3.data[1284],1.041451845)
        assert_array_almost_equal(nt3.data[1344:1456],[1]*112,12)
        self.assert_(numpy.alltrue(numpy.isnan(nt3.data[1456:1600])))   
                                   
    def test_godin_2d(self):
        
        """ Test godin filter on 2-dimensional data set."""
        
        d1=[1.0]*800+[2.0]*400+[1.0]*400
        d2=[1.0]*800+[2.0]*400+[1.0]*400
        data=numpy.array([d1,d2])
        data=numpy.transpose(data)
        data[336,:]=numpy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(minutes=15)
        test_ts=rts(data,st,delta,{})
        
        nt3=godin(test_ts)
        d1=nt3.data[:,0]
        d2=nt3.data[:,1]
        self.assert_(numpy.alltrue(numpy.isnan(d1[0:144])))
        assert_array_almost_equal(d1[144:192],[1]*48,12)
        self.assert_(numpy.alltrue(numpy.isnan(d1[192:481])))
        assert_array_almost_equal(d1[481:656],[1]*175,12)
        self.assert_(numpy.alltrue(numpy.greater(d1[656:944],1)))
        self.assertAlmostEqual(d1[868],1.916618441)
        assert_array_almost_equal(d1[944:1056],[2]*112,12)
        self.assert_(numpy.alltrue(numpy.greater(d1[1056:1344],1)))
        self.assertAlmostEqual(d1[1284],1.041451845)
        assert_array_almost_equal(d1[1344:1456],[1]*112,12)
        self.assert_(numpy.alltrue(numpy.isnan(d1[1456:1600]))) 
        
        self.assert_(numpy.alltrue(numpy.isnan(d2[0:144])))
        assert_array_almost_equal(d2[144:192],[1]*48,12)
        self.assert_(numpy.alltrue(numpy.isnan(d2[192:481])))
        assert_array_almost_equal(d2[481:656],[1]*175,12)
        self.assert_(numpy.alltrue(numpy.greater(d2[656:944],1)))
        self.assertAlmostEqual(d2[868],1.916618441)
        assert_array_almost_equal(d2[944:1056],[2]*112,12)
        self.assert_(numpy.alltrue(numpy.greater(d2[1056:1344],1)))
        self.assertAlmostEqual(d2[1284],1.041451845)
        assert_array_almost_equal(d2[1344:1456],[1]*112,12)
        self.assert_(numpy.alltrue(numpy.isnan(d2[1456:1600]))) 
    
    def test_lanczos_cos_filter_coef(self):
        """ Test the sum of lanczos filter coefficients"""    
        cf=0.2
        m=10
        coef=lowpass_cosine_lanczos_filter_coef(cf,m,False)
        coef=numpy.array(coef)
        coefsum=numpy.sum(coef)
        self.assertAlmostEqual(numpy.abs(1.0-coefsum),0.0,places=1)
        
        m=40
        coef=lowpass_cosine_lanczos_filter_coef(cf,m,False)
        coef=numpy.array(coef)
        coefsum=numpy.sum(coef)
        self.assertAlmostEqual(numpy.abs(1.0-coefsum),0.0,places=3)
    
    def test_lanczos_cos_filter_phase_neutral(self):
        """ Test the phase neutriality of cosine lanczos filter"""
        
        ## a signal that is sum of two sine waves with frequency of
        ## 5 and 250HZ, sampled at 2000HZ
        t=numpy.linspace(0,1.0,2001)
        xlow=numpy.sin(2*numpy.pi*5*t)
        xhigh=numpy.sin(2*numpy.pi*250*t)
        x=xlow+xhigh
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        ts=rts(x,st,delta,{})
        
        ## cutoff period is 30 hours, filterd result should be xlow
        ## approximately
        nt1=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=20,padtype="odd")
        self.assertAlmostEqual(numpy.abs(nt1.data-xlow).max(),0,places=1)
        
    
    def test_lanczos_cos_filter_period_freq_api(self):
        """ Test the cutoff period and frequency of filter"""
        
        ## a signal that is sum of two sine waves with frequency of
        ## 5 and 250HZ, sampled at 2000HZ
        t=numpy.linspace(0,1.0,2001)
        xlow=numpy.sin(2*numpy.pi*5*t)
        xhigh=numpy.sin(2*numpy.pi*250*t)
        x=xlow+xhigh
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        ts=rts(x,st,delta,{})
        
    
        nt1=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=20,\
                          padtype="even")
        
        ## cutoff_frequency is expressed as ratio of nyquist frequency
        ## ,which is 1/0.5/hours
        cutoff_frequency=2.0/30
        nt2=cosine_lanczos(ts,cutoff_frequency=cutoff_frequency,filter_len=20,\
                           padtype="even")
        
        self.assertEqual(numpy.abs(nt1.data-nt2.data).max(),0)
        
    def test_lanczos_cos_filter_len_api(self):
        """ Test the filter len api of the cosine filter"""
        
        ## a signal that is sum of two sine waves with frequency of
        ## 5 and 250HZ, sampled at 2000HZ
        t=numpy.linspace(0,1.0,2001)
        xlow=numpy.sin(2*numpy.pi*5*t)
        xhigh=numpy.sin(2*numpy.pi*250*t)
        x=xlow+xhigh
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        ts=rts(x,st,delta,{})
        
        ## filter len is none
        nt1=cosine_lanczos(ts,cutoff_period=hours(40),padtype="even")
        self.assertTrue(nt1.is_regular())
        ## filter len by defaut lis 40*1.25=50, use it explicitly and
        ## see if the result is the same as the nt1
        nt2=cosine_lanczos(ts,cutoff_period=hours(40),filter_len=50,padtype="even")
        self.assertEqual(numpy.abs(nt1.data-nt2.data).max(),0)
   
    def test_lanczos_cos_filter_len(self):
        """ test cosine lanczos input filter length api"""
        
        data=[2.0*numpy.math.cos(2*pi*i/5+0.8)+3.0*numpy.math.cos(2*pi*i/45+0.1)\
             +7.0*numpy.math.cos(2*pi*i/55+0.3) for i in range(1000)]
        data=numpy.array(data)
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        ts=rts(data,st,delta,{})
        
        filter_len=24
        t1=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=filter_len)
        
        filter_len=days(1)
        t2=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=filter_len)
        
        assert_array_equal(t1.data,t2.data)
        
        
        filter_len="invalid"
        self.assertRaises(TypeError,cosine_lanczos,ts,cutoff_period=hours(30),\
                          filter_len=filter_len)
   

    def test_lanczos_cos_filter_nan(self):
        """ Test the data with a nan filtered by cosine lanczos filter"""
        data=[2.0*numpy.math.cos(2*pi*i/5+0.8)+3.0*numpy.math.cos(2*pi*i/45+0.1)\
             +7.0*numpy.math.cos(2*pi*i/55+0.3) for i in range(1000)]
        data=numpy.array(data)
        nanloc=336
        data[nanloc]=numpy.nan
        st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
        delta=time_interval(hours=1)
        ts=rts(data,st,delta,{})
        m=20
     
        nt1=cosine_lanczos(ts,cutoff_period=hours(30),filter_len=m,padtype="even")
        ## result should have nan from nanidx-2*m+2 to nanidx+2*m-1
        nanidx=numpy.where(numpy.isnan(nt1.data))[0]
        nanidx_should_be=numpy.arange(nanloc-2*m,nanloc+2*m+1)
        assert_array_equal(nanidx,nanidx_should_be)
        
#        delta=time_interval(minutes=15)
#        data[nanloc:nanloc+10]=numpy.nan
#        ts=rts(data,st,delta,{})
#        m=20
#        nt2=cosine_lanczos(ts,cutoff_period=hours(1),filter_len=m,padtype="even")
##        
#        subplot(111)
##        
#        plot(ts.times,ts.data,label="data",color='black')
#        plot(nt2.times,nt2.data,label="C-L",color="red")
#        legend()
#        show()
        
        
    
    def test_fill__godin_nan(self):
        
        ts=example_data("pt_reyes_tidal_1hour")
        ts_godin=godin(ts)
        nanloc=len(ts)/2
        ts.data[nanloc]=numpy.nan
        ts_nan_godin=godin(ts)
        ts.data[nanloc]=0.0
        ts_0_godin=godin(ts)
        ts.data[nanloc]=(ts.data[nanloc+1]+ts.data[nanloc-1])/2.0
        ts_m_godin=godin(ts)
#        subplot(111)
#        
#        plot(ts.times,ts.data,label="data",color='black')
#        plot(ts_godin.times,ts_godin.data,label="godin",color="black")
#        plot(ts_nan_godin.times,ts_nan_godin.data,label="godin_nan",color="blue")
#        plot(ts_0_godin.times,ts_0_godin.data,label="godin_0",color="brown")
#        plot(ts_m_godin.times,ts_m_godin.data,label="godin_m",color="red")

    def test_gaussian_filter(self):
       """ Test the nan data with gaussian filter"""
       data=[2.0*numpy.math.cos(2*pi*i/5+0.8)+3.0*numpy.math.cos(2*pi*i/45+0.1)\
             +7.0*numpy.math.cos(2*pi*i/55+0.3) for i in range(1000)]
       data=numpy.array(data)
       nanloc=336
       data[nanloc]=numpy.nan
       st=datetime.datetime(year=1990,month=2,day=3,hour=11, minute=15)
       delta=time_interval(hours=1)
       ts=rts(data,st,delta,{})
       sigma=2
     
       nts=[]
       for order in range(4):
           nts.append(ts_gaussian_filter(ts,sigma,order=order))
           
#       subplot(111)   
#       plot(ts.times,ts.data,label="data",color='black')
#       orders=range(4)
#       colors=["red","green","brown","grey"]
#       for nt,order,color in zip(nts,orders,colors):
#           plot(nt.times,nt.data,label="gaussian_order_"+str(order),\
#                color=color)
#       legend()
#       show()    
         
              
if __name__=="__main__":
    
    unittest.main()       

   

    

            

        
        

        
            


        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
