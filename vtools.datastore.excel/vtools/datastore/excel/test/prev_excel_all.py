import sys,os,unittest

##from test_excel_service import TestExcelService
##from test_excel_catalog import TestExcelCatalog
from test_excel_utility import TestExcelUtility

def suite():    
    suite = unittest.TestSuite()
    suite.addTest(TestExcelUtility("test_retrieve_rts_notimes"))
    suite.addTest(TestExcelUtility("test_retrieve_rts_all_time"))
    suite.addTest(TestExcelUtility("test_retrieve_ts"))                            
    suite.addTest(TestExcelUtility("test_retrieve_rts_col_time"))
    suite.addTest(TestExcelUtility("test_store_ts"))
    return suite

if __name__=="__main__":

    excelsuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(excelsuit)
    print result
