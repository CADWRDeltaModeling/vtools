import sys,os,unittest

from test_period_op import TestPeriodOp
from test_interpolate import TestInterpolate
from test_decimate import TestDecimate
from test_filter import TestFilter
from test_godin import TestGodin
from test_merge import TestMerge
from test_shift import TestShift
from test_resample import TestResamplefunctions
from test_diffnorm import TestDiffNorm

def suite():    
    suite = unittest.TestSuite()

    ## Period op tests
    suite.addTest(TestPeriodOp("test_period_op"))
    suite.addTest(TestPeriodOp("test_period_op2"))
    suite.addTest(TestPeriodOp("test_period_op3"))
    suite.addTest(TestPeriodOp("test_period_op_large"))
    suite.addTest(TestPeriodOp("test_period_op_irregular"))
    suite.addTest(TestPeriodOp("test_period_op_uncompatible_interval"))
    suite.addTest(TestPeriodOp("test_period_op_nan"))

    ## Interpolation test.
    suite.addTest(TestInterpolate("test_rts_at_regular_points"))
    suite.addTest(TestInterpolate("test_rts_at_bounded_regular_points"))
    suite.addTest(TestInterpolate("test_rts_at_irregular_points"))
    suite.addTest(TestInterpolate("test_its_at_regular_points"))
    suite.addTest(TestInterpolate("test_its_at_irregular_points"))
    suite.addTest(TestInterpolate("test_rts_near_nan_point"))
    suite.addTest(TestInterpolate("test_multidimension_tsdata"))
    suite.addTest(TestInterpolate("test_flat"))
    
    ##  Decimate 
    suite.addTest(TestDecimate("test_decimate_rts"))
    suite.addTest(TestResamplefunctions("test_resample_rts_aligned"))
    suite.addTest(TestResamplefunctions("test_resample_rts"))
    suite.addTest(TestResamplefunctions("test_decimate_rts"))
    suite.addTest(TestResamplefunctions("test_decimate_rts_2d"))

    ## filtering
    suite.addTest(TestFilter("test_butterworth"))
    suite.addTest(TestFilter("test_boxcar"))
    suite.addTest(TestFilter("test_daily_average"))
    suite.addTest(TestFilter("test_butterworth_noevenorder")) 

    ## godin
    suite.addTest(TestGodin("test_godin"))
    suite.addTest(TestGodin("test_godin_15min"))
    suite.addTest(TestGodin("test_godin_2d"))

    ## merge
    suite.addTest(TestMerge("test_merge_rts_no_intersect"))
    suite.addTest(TestMerge("test_merge_rts_intersect"))
    suite.addTest(TestMerge("test_merge_rts_intersect2"))
    suite.addTest(TestMerge("test_merge_rts_2d_intersect"))
    suite.addTest(TestMerge("test_merge_large_rts"))

    ## shift                  
    suite.addTest(TestShift("test_shift_operation_rts"))
    suite.addTest(TestShift("test_shift_operation_its"))             

    
    ## diffnorm                  
    suite.addTest(TestDiffNorm("test_norm_L1"))
    suite.addTest(TestDiffNorm("test_norm_L2"))
    suite.addTest(TestDiffNorm("test_norm_Linf"))
    suite.addTest(TestDiffNorm("test_ts_equal"))
    return suite


if __name__=="__main__":

    funcsuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(funcsuit)
    print result
