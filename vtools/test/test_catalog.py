"""  Test handy utility functions to read data from or save data to dss source.
"""
## python import
import sys,os,shutil,unittest,pdb

## vtools import
from vtools.datastore.dss.utility import dss_catalog
from vtools.datastore.catalog import catalog_string
from vtools.data.timeseries import TimeSeries
from vtools.datastore.service import get_data
from vtools.datastore.data_reference import DataReference

from vtools.datastore.dss.dss_service import *
from vtools.datastore.excel.excel_service import *

class TestCatalog(unittest.TestCase):

    """ test functionality of dss utility funcs """


    def __init__(self,methodName="runTest"):

        super(TestCatalog,self).__init__(methodName)
        import vtools.test
        pkgfile = vtools.test.__file__
        self.dss_file_path='testfile.dss'
        self.dss_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.dss_file_path)
        self.backup_dss_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'backup/testfile.dss')   
        
    def setUp(self):
           
        if os.path.exists(self.dss_file_path):
            os.remove(self.dss_file_path)
            
        shutil.copy(self.backup_dss_file,self.dss_file_path)

      

    def test_get_data(self):
        """ test retrieve ts from a source based on path and
            time window desired.
        """
        ## get dss data.
        dssfile_path=self.dss_file_path
        c1=dss_catalog(dssfile_path)
        
        for e in c1:
            ts=get_data(e)
            self.assertEqual(type(ts),TimeSeries)

    def test_data_references(self):
         
        """" test itertor of data references within catalog class"""

        ## dss data.
        dssfile_path=self.dss_file_path
        c1=dss_catalog(dssfile_path)
     
        for ref in c1.data_references():
            self.assertEqual(type(ref),DataReference)
              

if __name__=="__main__":
    
    unittest.main()        
        

        
        

        

        


    


