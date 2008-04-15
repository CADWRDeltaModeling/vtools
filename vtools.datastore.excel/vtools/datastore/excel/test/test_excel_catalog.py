import sys,os,unittest,shutil
from copy import deepcopy

from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.catalog import CatalogEntry
from vtools.datastore.excel.excel_service import EXCEL_DATA_SOURCE
from vtools.datastore.data_reference import DataReference
from vtools.datastore.excel.excel_service import ExcelService
   
class TestExcelCatalog(unittest.TestCase):
    """ test functionality of dss service """

    def __init__(self,methodName="runTest"):

        super(TestExcelCatalog,self).__init__(methodName)
        self.test_file_path='test.xls'
        self.test_file_path=os.abspath(self.test_file_path)
        self.backup_xls_file=os.abspath('./backup_excelfile/test.xls')
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.excel_service=self.servic_emanager.get_service(EXCEL_DATA_SOURCE)

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
         
        shutil.copy(self.backup_xls_file,self.test_file_path) 

        self.excel_catalog=self.excel_service.get_catalog(self.test_file_path)

       
        
    def test_filter_catalog(self):

        selector="worksheet=hydro_flow;range=A1:E277;"
        dref=self.excel_catalog.filter_catalog(selector)
        self.assertEqual(len(dref),5)

                
    

if __name__=="__main__":
    
    unittest.main()      
        
 




        

                 

    
    
