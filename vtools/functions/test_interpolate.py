
## Python standard import
from copy import deepcopy
import sys,os,unittest,shutil,random,pdb
from random import sample
from datetime import datetime

## vtools import.
from vtools.data.timeseries import rts,its
from vtools.data.vtime import *


## Scipy import.
from scipy import array as sciarray
from scipy import add as sciadd
from scipy import minimum as sciminimum
from scipy import maximum as scimaximum
from scipy import nan,isnan,allclose,reshape,\
put,take,alltrue,sin,pi,greater,choose,\
concatenate,arange


## Interpolate func import.
from interpolate import *

def cross_loop(*sequences):

    if sequences:
        for x in sequences[0]:
            for y in cross_loop(sequences[1:]):
                print (x,)+y
                yield (x,)+y
                
    else:
        yield()
    
    
def cross(*sequences):
    wheels=map(iter,sequences)
    digits=[it.next() for it in wheels]
    while True:
        yield tuple(digits)
        for i in range(len(digits)-1,-1,-1):
            try:
                digits[i]=wheels[i].next()
                break
            except StopIteration:
                wheels[i]=iter(sequences[i])
                digits[i]=wheels[i].next()
            else:
                break
            
def cross_list(*sequences):
    
    result=[[]]
    for seq in sequences:
        result=[sublist+[item] for sublist in result for item in seq]
    return result
        
        

class TestInterpolate(unittest.TestCase):

    """ test functionality of period operations """

    def __init__(self,methodName="runTest"):

        super(TestInterpolate,self).__init__(methodName)
        
        self.max_val=1000
        self.min_val=0.01
        self.large_data_size=100000
        self.rts1_years=5
        interval="1day"
        self.rts1_delta=parse_interval(interval) 
        self.rts1=self.create_rts(self.rts1_delta,self.rts1_years*365)        
        self.rts2=self.create_rts(self.rts1_delta,self.rts1_years*365)
        
        self.rts_has_nan=self.create_rts(self.rts1_delta,self.rts1_years*365)
        ts_len=len(self.rts_has_nan)
        #self.nan_indexes=sample(range(5,ts_len-5,1),ts_len/5)
        ## bulit a array for position of nan will be put
        ## into rts_has_nan
        nan_indexes=sciarray([5,12,14,15,20,21,22,23,45,49,101,112,\
                          203,204,205])
        ii=arange(500,520)
        ii2=sciarray([600,607,700,709])
        nan_indexes=concatenate((nan_indexes,ii,ii2))
        ## remove possible large indexes that over the range.
        nan_indexes=choose(greater(nan_indexes,ts_len-5),\
                           (nan_indexes,ts_len-5))
        
        self.nan_indexes=nan_indexes       
       
        put(self.rts_has_nan.data,self.nan_indexes,nan) 
        
        self.its1=self.create_its()
        self.function_to_test=[linear,spline,monotonic_spline,rhistinterp]

                
###############################################
##
##    test of low level usage of interpolation
##    functions. 
##            
###############################################      

    def test_rts_extrapolation_error(self):
      """ Test doing extrapolation using interpolating function.
      """

      msgtr="at  test_rts_extrapolation_error"        
      ts=self.rts1
      movetime=minutes(5)
      intpolate_points=time_sequence(ts.start-movetime, minutes(15), 10)
      methods=[NEAREST,PREVIOUS,NEXT,LINEAR,SPLINE,MSPLINE,RHIST]
      
      for method in methods:
          self.assertRaises(ValueError, interpolate_ts,ts,intpolate_points,method=method)
       
    def test_rts_at_regular_points(self):
        
        """ Test interpolation of regular timeseries at
            regular time ponts.
        """
        msgstr="at test_rts_at_regular_points"
        ts=self.rts1
        interval=parse_interval("15min")
        start=ts.start+interval
                       
        num=number_intervals(start,ts.end-interval,interval)
        times=time_sequence(start,interval,num)  

        for funcs in self.function_to_test:
            nts=funcs(ts,times)
            self.assertEqual(len(nts),len(times),"test of %s fail %s."\
                             %(funcs.__name__,msgstr))

    def test_rts_at_bounded_regular_points(self):
        
        """ Test interpolation by limited points from regular timeseries.
        """
        msgstr="at test_rts_at_regular_points"
        ts=self.rts1
        interval=parse_interval("15min")
        start=ts.start+interval
                       
        num=number_intervals(start,ts.end-interval,interval)
        times=time_sequence(start,interval,num)  

        for funcs in self.function_to_test:
            nts=funcs(ts,times)
            self.assertEqual(len(nts),len(times),"test of %s fail %s."%(funcs.__name__,msgstr))
            
    def test_rts_at_irregular_points(self):
        
        """ Test interpolation of  regular timeseries at
            irregular points.
        """
        msgstr="at test_rts_at_irregular_points"
        ts=self.rts1
        years=self.rts1_years
        start_year=ts.start.year
        times=self.create_irregular_timesequence(start_year,years)    
        for funcs in self.function_to_test:
            nts=funcs(ts,times)
            self.assertEqual(len(nts),len(times),"test of %s fail %s."%(funcs.__name__,msgstr))
        
        
    def test_its_at_irregular_points(self):
        
        """ Test interpolation from irregular timeseries at
            irregular time ponts.
        """
        msgstr="at test_its_at_irregular_points"
        ts=self.its1
        times=self.create_irregular_timesequence2(ts.start.year,self.its1_years-1)
        function_to_test=[linear,spline,monotonic_spline]
        for funcs in function_to_test:
            nts=funcs(ts,times)
            self.assertEqual(len(nts),len(times),"test of %s fail %s."%(funcs.__name__,msgstr))
        
    def test_its_at_regular_points(self):
        
        """ Test interpolation of irregular timeseries at
            regular time ponts.
        """
        msgstr="at test_its_at_regular_points"
        ts=self.its1
        interval=parse_interval("15min")
        start=ts.start+interval
        
        ## this about 35000 ponits
        num=number_intervals(start,ts.end-interval,interval)        
        times=time_sequence(start,interval,num)
        
        ## times2 is times in datetime format.
        times2=map(ticks_to_time,times)

        nt1=[]
        i=0
        function_to_test=[linear,spline,monotonic_spline]
        for funcs in function_to_test:
            nt1.append(funcs(ts,times))
            self.assertEqual(len(nt1[i]),len(times),"test of %s fail %s."%(funcs.__name__,msgstr))
            i=i+1
            
        ## Repeat same task by datetime list instead of ticks array above.
        nt2=[]
        i=0
        for funcs in function_to_test:
            nt2.append(funcs(ts,times2))
            self.assertEqual(len(nt2[i]),len(times2),"test of %s fail %s."%(funcs.__name__,msgstr))
            self.assert_(allclose(nt1[i].data,nt2[i].data),"test of %s fail %s."%(funcs.__name__,msgstr))
            i=i+1
        
        ## Repeat same task again by datetime array.
        times3=sciarray(map(ticks_to_time,times))
        nt3=[]
        i=0
        for funcs in function_to_test:
            nt3.append(funcs(ts,times3))
            self.assertEqual(len(nt3[i]),len(times3),"test of %s fail %s."%(funcs.__name__,msgstr))
            self.assert_(allclose(nt1[i].data,nt3[i].data),"test of %s fail %s."%(funcs.__name__,msgstr))
            i=i+1
        
    def test_rts_near_nan_point(self):
        
        """ Test function behavoir at nan points when nan is filtered, in such
            a case if a interpoltion is made before or after or on a nan point,
            the next non-nan point should be used as interpolating basis.
        """
        
        msgstr="at test_rts_at_nan_points"
        ts=self.rts2
        
        #data=map(float,range(35))
        #ts=rts(data,datetime.datetime(year=1990,month=1,day=2),parse_interval("1hour"),{})
        
        ## Test interpolating on a ts data point should 
        ## return same value.    
        pos=30
        time=[ts.ticks[pos]]
        for funcs in self.function_to_test:
            nt=funcs(ts,time)
            self.assertAlmostEqual(nt.data[0],ts.data[pos],2,\
                                   msg="test of %s fail %s."%(funcs.__name__,msgstr))
        
        ## It is observed nan can only given to float array
        ## no effect on int array.       
        ts.data[pos]=nan
        time=[ts.ticks[pos]]
        
        for funcs in self.function_to_test:
            nt=funcs(ts,time,filter_nan=True)
            if funcs==linear:
                self.assertAlmostEqual(nt.data[0],(ts.data[pos-1]+ts.data[pos+1])/2,\
                                   msg="test of %s fail %s."%(funcs.__name__,msgstr))
            else:
                self.assert_(not(isnan(nt.data[0])),\
                             "test of %s fail %s."%(funcs.__name__,msgstr))
        
    def test_multidimension_tsdata(self):
        
        """ Test interploation methods on multi-dimensional data set."""
        
        msgstr="on test_multidimension_tsdata"
        num=1000
        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]
        data=sciarray(data).reshape(num/4,4)
        ts=rts(data,datetime(year=1990,month=1,day=2),parse_interval("1hour"),{})
        times=time_sequence(datetime(year=1990,month=1,day=3),\
                            parse_interval("1hour"),50)
        ##rhsit won't pass this test
        for funcs in self.function_to_test:
             nts=funcs(ts,times,filter_nan=False)
             self.assertEqual(len(nts),len(times),\
                              msg="test of %s fail %s."%(funcs.__name__,msgstr))
             self.assertEqual(nts.data.shape[1],ts.data.shape[1],\
                              msg="test of %s fail %s."%(funcs.__name__,msgstr))
             
    def test_flat(self):
        
        """ Test the behavior of flat interpolation. """
        
        data=[sin(i*3.14/3) for i in range(20)]       
        times=[1,3,7,14,19,29,35,41,42,44,60,61,67,69,72,76,77,79,89,90]
        data[4]=nan
        data[5]=nan
        ts=its(times,data)        

        ## Interpolation time locations.
        st=[2,9,19,20,29,34,50,72.4]
        
        for func in [nearest_neighbor,previous_neighbor,next_neighbor]:            
            irt=func(ts,st)
            for vv in irt.data:
                self.assert_(vv in ts.data)

###############################################
##
##    test of high level usage of interpolation
##    functions. 
##            
###############################################          
        
    def test_interpolate_ts_nan(self):
     
        """ Test filling nan within a regular time series
        
        """  
        
        #ts=self.rts_has_nan
        #if ts_len<50:
        #    raise VlaueError("Test data is not long enough, skip test_interpolate_ts")

        for method in [SPLINE,MONOTONIC_SPLINE,LINEAR,PREVIOUS,NEXT,NEAREST]:
            ts=deepcopy(self.rts_has_nan)
            ts=interpolate_ts_nan(ts,method=method)
            self.assert_(alltrue(isnan(ts.data))==False)
        
        ## test max_gap option
      
        data=sciarray([0.3*sin(k*pi/1200+pi/15)+0.4*sin(k*pi/1100+pi/6)+1.1*sin(k*pi/990+pi/18) \
              for k in range(50)])
        
        put(data,[12,13,14],nan)
        put(data,[34,35,36,37,38,39,40,41,42,43],nan)
        
        max_gap=4
        start_time="1/2/1990"
        interval="15min"
        
       
        ts_with_nans=rts(data,start_time,interval,{})
        
        for method in [SPLINE,MONOTONIC_SPLINE,LINEAR,PREVIOUS,NEXT,NEAREST]:
            ts_new=interpolate_ts_nan(ts_with_nans,max_gap=max_gap, method=method)
            self.assert_(not(isnan(ts_new.data[12])))
            self.assert_(not(isnan(ts_new.data[13])))
            self.assert_(not(isnan(ts_new.data[14])))
            self.assert_((isnan(ts_new.data[34])))
            self.assert_((isnan(ts_new.data[35])))
            self.assert_((isnan(ts_new.data[36])))
            self.assert_((isnan(ts_new.data[37])))
            self.assert_((isnan(ts_new.data[38])))
            self.assert_((isnan(ts_new.data[39])))
            self.assert_((isnan(ts_new.data[40])))
            self.assert_((isnan(ts_new.data[41])))
            self.assert_((isnan(ts_new.data[42])))
            self.assert_((isnan(ts_new.data[43])))
            
        
            
        ## test no nan exits
        data=sciarray([0.3*sin(k*pi/1200+pi/15)+0.4*sin(k*pi/1100+pi/6)+1.1*sin(k*pi/990+pi/18) \
              for k in range(50)])
        
        ts_without_nans=rts(data,start_time,interval,{})
        for method in [SPLINE,MONOTONIC_SPLINE,LINEAR,PREVIOUS,NEXT,NEAREST]:
            ts_new=interpolate_ts_nan(ts_without_nans,max_gap=max_gap,method=method)
            for old_value, new_value in zip(ts_without_nans.data,ts_new.data):
                self.assert_(old_value==new_value)
                
        
        data=sciarray([0.3*sin(k*pi/1200+pi/15)+0.4*sin(k*pi/1100+pi/6)+1.1*sin(k*pi/990+pi/18) \
              for k in range(50)])
        
        put(data,[12,13,14],nan)
        
        max_gap=2
        ## should do nothing for its gap wider than max_gap
        ts_less_nans=rts(data,start_time,interval,{})

        for method in [SPLINE,MONOTONIC_SPLINE,LINEAR,PREVIOUS,NEXT,NEAREST]:
            ts_new=interpolate_ts_nan(ts_less_nans,max_gap=max_gap,method=method)
            self.assert_((isnan(ts_new.data[12])))
            self.assert_((isnan(ts_new.data[13])))
            self.assert_((isnan(ts_new.data[14])))
        
        
            
        
            
        

    def test_interpolate_rts_its(self):
        """ Test create a regular ts by interpolating its
        
        """
        
        its1=self.its1
        interval="1day"

        for method in [SPLINE,MONOTONIC_SPLINE,\
                       LINEAR,PREVIOUS,NEXT,NEAREST]:
            #pdb.set_trace()
            rt=interpolate_ts(its1,interval,method=method)
            self.assert_(rt.is_regular())
            self.assertEqual(rt.interval,parse_interval(interval))

        # change interval to 1hour
        interval="1hour"
        for method in [SPLINE,MONOTONIC_SPLINE,\
                       LINEAR,PREVIOUS,NEXT,NEAREST]:

            rt=interpolate_ts(its1,interval,method=method)
            self.assert_(rt.is_regular())
            self.assertEqual(rt.interval,parse_interval(interval))

    def test_interpolate_rts_rts(self):
        """ Test create a finer regular ts by interpolating rts
        
        """
       
        rts1=self.rts1
        interval="1hour"
        for method in [SPLINE,MONOTONIC_SPLINE,\
                       LINEAR,PREVIOUS,NEXT,NEAREST]:
           
            rt=interpolate_ts(rts1,interval,method=method)
            self.assert_(rt.is_regular())
            self.assertEqual(rt.interval,parse_interval(interval))
            
    
         
    def test_interpolate_rts_rts_month2day(self):
        """ Test create a finer regular ts by interpolating rts"""

        delta=months(1)
        num=103
        rts1=self.create_rts(delta,num)
        interval="1day"

        for method in [SPLINE,MONOTONIC_SPLINE,\
                       LINEAR,PREVIOUS,NEXT,NEAREST]:
            rt=interpolate_ts(rts1,interval,method=method)
            self.assert_(rt.is_regular())
            self.assertEqual(rt.interval,parse_interval(interval))

    def test_interpolate_flat_extroplate_end(self):
        """ Test interoplation using flat method with extrapolation
            at the end of ts. 
        """

        delta=months(1)
        num=103
        rts1=self.create_rts(delta,num)
        interval="1day"
        for method in [PREVIOUS,NEXT,NEAREST]:
            rt=interpolate_ts(rts1,interval,method=method,extrapolate=3)
            self.assert_(rt.is_regular())
            self.assertEqual(rt.interval,parse_interval(interval))            
            self.assertEqual(rt.data[-1],rt.data[-4])

    def test_rhistinterp(self):
        """ test interpolating by  histospline"""

        delta=days(1)
        num=201
        rts1=self.create_rts(delta,num)
        interval=hours(1)
        num=number_intervals(rts1.start,rts1.end+interval,interval)
        
        ts2=rhistinterp(rts1,interval,lowbound=-1)        
        self.assertEqual(num,len(ts2))
            
##########################################
##
##    utility functions.
##            
##########################################            
                               
    def create_irregular_timesequence(self,start_year,years): 
        
        times=[]
        months=[1,4,7,9,11]
        days=[3,7,9,14,19,23]
        hours=[1,5,9,11,14,17,18,23]
        minutes=[0,12,25,34,44,55]
        crossloop=cross_list(months,days,hours,minutes)
        
        for i in range(years):
            year=start_year+i
            sub_times=[datetime(year=year,month=month,day=day,hour=hour,minute=minute)
                       for (month,day,hour,minute)in crossloop]
            times=times+sub_times
        return times
    
    def create_irregular_timesequence2(self,start_year,years): 
        
        times=[]
        months=[2,3,5,8,10]
        days=[2,6,13,17,20,25]
        hours=[0,3,6,10,15,19,20,22]
        minutes=[11,27,39,47,56]
        crossloop=cross_list(months,days,hours,minutes)
        
        for i in range(years):
            year=start_year+i
            sub_times=[datetime(year=year,month=month,day=day,hour=hour,minute=minute)
                       for (month,day,hour,minute)in crossloop]
            times=times+sub_times
        return times

    def create_rts(self,delta,num):

        """ Only create a regular time series for usage of testing.
        """
        ## This is a ten years long time series aproximately.
        st=datetime(year=1990,month=1,day=1,hour=00, minute=00)
        data=[0.3*sin(k*pi/1200+pi/15)+0.4*sin(k*pi/1100+pi/6)+1.1*sin(k*pi/990+pi/18) \
              for k in range(num)]
        
        ts=rts(data,st,delta,{})
        return ts
    
    def create_its(self):
        
        """ Only create a irregular time series for usage of testing.
        """
           
        times=self.create_irregular_timesequence(2000,1)
        self.its1_years=2
        num=len(times)       
        data=[random.uniform(self.min_val,self.max_val) \
              for k in range(num)]
        ts=its(times,data,{})
        return ts
        
            
if __name__=="__main__":
    
    unittest.main()
    
   

        
        
        

        
        

        

        


        

             



            
        
    
        
        

 

        

        
        

    
                    




        

                 

    
    
