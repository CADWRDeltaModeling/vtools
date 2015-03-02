import unittest,os,shutil,sys

## pydss import
from pydss.hecdss import open_dss

## vtools import
from vtools.datastore.translate import *
from vtools.datastore.data_service_manager import DataServiceManager 

from vtools.datastore.dss.dss_service import *


class TestTranslate(unittest.TestCase):

    """ test functionality of translate data references """


    def __init__(self,methodName="runTest"):

        super(TestTranslate,self).__init__(methodName)
        self.test_file_path='testfile.dss'
        self.test_file_path=os.path.abspath(self.test_file_path)
        self.backup_dss_file=os.path.abspath('./backup/testfile.dss')
        self.test_file2="dest.dss"
        self.test_file2=os.path.abspath(self.test_file2)
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.dss_service=self.servic_emanager.get_service("vtools.datastore.dss.DssService")

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        shutil.copy(self.backup_dss_file,self.test_file_path)
        self.dest_dss=open_dss(self.test_file2)        
                                
    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        self.dest_dss.close()
        if os.path.exists(self.test_file2):
            os.remove(self.test_file2)
            
    def test_translate_dss(self):
        
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        selector="/HIST*/*/*/*/*/*/"
        dl=dssc.data_references(selector)
    
        ## given translation here
        translation="/${A}_AVER/${B}/${C}//1HOUR/${F}/"
        dest="this/is/only/test/location.dss"
        dt=translate_references(self.dss_service,dl,self.dss_service,dest,translation)
        self.assertEqual(len(dt),5)
        
        
if __name__=="__main__":
    
    unittest.main()          


        

        
        

    
                    




        

                 

    
    
