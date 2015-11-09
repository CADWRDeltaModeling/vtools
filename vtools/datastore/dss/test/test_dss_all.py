import sys,os,unittest

from test_dss_service import TestDssService
from test_dss_catalog import TestDssCatalog
from test_dss_utility import TestDssUtility

def suite():    
    suite = unittest.TestSuite()
    

    suite.addTest(TestDssService("test_get_catalog"))
    suite.addTest(TestDssService("test_get_data"))
    suite.addTest(TestDssService("test_get_data_all"))
    suite.addTest(TestDssService("test_save_data"))
    
    
    suite.addTest(TestDssCatalog("test_modify")) 
    
    suite.addTest(TestDssService("test_support_unaligned_ts"))
    suite.addTest(TestDssService("test_get_its_data_overlap"))
    suite.addTest(TestDssService("test_get_aggregated_data"))
    suite.addTest(TestDssService("test_save_ts_props"))
    suite.addTest(TestDssService("test_get_save_ts"))
    suite.addTest(TestDssService("test_read_aggregated_rts_timewindow"))
    suite.addTest(TestDssService("test_read_instant_rts_timewindow"))
    suite.addTest(TestDssService("test_retrievesave_longits"))
    suite.addTest(TestDssService("test_save2newf"))
    suite.addTest(TestDssService("test_get_two_catalog_same_time"))
    suite.addTest(TestDssService("test_get_save_ts_manytimes"))
    suite.addTest(TestDssUtility("test_save_ts_manytimes"))
    
    
    suite.addTest(TestDssUtility("test_retrieve_ts"))
    suite.addTest(TestDssUtility("test_retrieve_aver_ts"))
    suite.addTest(TestDssUtility("test_retrieve_save__inst_rts"))
    suite.addTest(TestDssUtility("test_retrieve_save_aver_rts"))
    suite.addTest(TestDssUtility("test_save_ts_invalid_path"))
    
    suite.addTest(TestDssCatalog("test_modify")) ## it may cause error
                                                 ## when it is move after
                                                ## test_save_data.
    suite.addTest(TestDssCatalog("test_get_data_reference"))
    suite.addTest(TestDssCatalog("test_copy_remove"))
    suite.addTest(TestDssCatalog("test_filter_catalog"))
    suite.addTest(TestDssCatalog("test_filter_catalog2"))
    suite.addTest(TestDssCatalog("test_data_references"))
    
    return suite


if __name__=="__main__":

    dsssuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(dsssuit)
    print result
