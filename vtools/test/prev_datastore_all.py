import sys,os,unittest

from test_catalog import TestCatalog
from test_transfer import TestTransfer
from test_translate import TestTranslate

def suite():    
    suite = unittest.TestSuite()
    suite.addTest(TestCatalog("test_get_data"))
    suite.addTest(TestCatalog("test_data_references"))

    suite.addTest(TestTransfer("test_batch_transfer_rts1"))
    suite.addTest(TestTransfer("test_batch_transfer_all"))
    suite.addTest(TestTransfer("test_batch_transfer_rts"))
    suite.addTest(TestTransfer("test_batch_transfer_dss2excel"))
    suite.addTest(TestTransfer("test_batch_transfer_dss2excel_file_selector"))
    suite.addTest(TestTransfer("test_batch_transfer_hdf2dss")) 

    suite.addTest(TestTranslate("test_translate_dss"))    
    return suite


if __name__=="__main__":

    storesuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(storesuit)
    print result
