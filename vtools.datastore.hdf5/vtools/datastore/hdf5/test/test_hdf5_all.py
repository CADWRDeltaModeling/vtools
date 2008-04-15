import sys,os,unittest

from test_hdf5_service import TestHDF5Service
from test_hdf5_catalog import TestHDF5Catalog


def suite():    
    suite = unittest.TestSuite()
    
    suite.addTest(TestHDF5Service("test_get_catalog"))
    suite.addTest(TestHDF5Service("test_get_data"))
    suite.addTest(TestHDF5Catalog("test_get_data_reference"))    
    return suite


if __name__=="__main__":

    hdfsuit=suite()
    runner=unittest.TextTestRunner()
    result=runner.run(hdfsuit)
    print result
