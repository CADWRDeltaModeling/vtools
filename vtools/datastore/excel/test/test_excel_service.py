import sys,os,unittest,shutil
from copy import deepcopy
from random import random
from itertools import islice

from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.excel.excel_service import EXCEL_DATA_SOURCE
from vtools.datastore.data_reference import DataReferenceFactory
from vtools.data.timeseries import TimeSeries,rts
from vtools.data.vtime import ticks_to_time,parse_interval,parse_time
from vtools.datastore.excel.excel_catalog import ExcelCatalog
from vtools.datastore.excel.utility import *

   
class TestExcelService(unittest.TestCase):
    
    def __init__(self,methodName="runTest"):

        super(TestExcelService,self).__init__(methodName)
        import vtools.datastore.excel
        pkgfile = vtools.datastore.excel.__file__
        self.test_file_path='test\\test.xls'
        self.test_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.test_file_path)
        self.backup_xls_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'test/backup_excelfile/test.xls') 
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        shutil.copy(self.backup_xls_file,self.test_file_path)  
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.excel_service=self.servic_emanager.get_service(EXCEL_DATA_SOURCE)
    
    def test_get_catalog(self):
        c=self.excel_service.get_catalog(self.test_file_path)
        self.assertTrue(type(c)==ExcelCatalog)
                       
    def test_get_data(self):

        c=self.excel_service.get_catalog(self.test_file_path)

        ## filter catalog to get some data reference of rts.
        selector="worksheet=hydro_flow;range=A6:E110;"
        dref=c.filter_catalog(selector)
      
        for d in dref:
            ts=self.excel_service.get_data(d)
            self.assertTrue(ts.is_regular())
            self.assertEqual(len(ts),104)

        ## filter catalog to get some data reference of its.
        selector="worksheet=its_data;range=B6:F110;"
        dref=c.filter_catalog(selector)
      
        for d in dref:
            ts=self.excel_service.get_data(d)
            self.assertTrue(not(ts.is_regular()))
            self.assertEqual(len(ts),104)

    def test_add_data(self):

        def rand_gen():
            while True:
                yield random()

        tss=[]
        
        ## create several ts
        # 1
        st=parse_time("1/2/1987 10:30")
        dt=parse_interval("1hour")
        prop={"agency":"dwr","interval":"1hour","station":"rsac045",\
              "datum":"NGVD88","var":"flow"}
        n=13470
        data=list(islice(rand_gen(),n))
        ts=rts(data,st,dt,prop)
        tss.append(ts)
        # 2
        st=parse_time("3/20/1997 10:30")
        dt=parse_interval("1day")
        prop={"bearu":"usgs","interval":"1day","lat":70.90,\
              "long":34.45,"datum":"NGVD88","var":"stage"}
        n=40960
        data=list(islice(rand_gen(),n))
        ts=rts(data,st,dt,prop)
        tss.append(ts)
        
        # 3
        st=parse_time("1/2/1967 4:30")
        dt=parse_interval("15min")
        prop={"place":"uml","interval":"15min","station":"rsac045",\
              "datum":"NGVD88","var":"bod"}
        n=20000
        data=list(islice(rand_gen(),n))
        ts=rts(data,st,dt,prop)
        tss.append(ts)

      
        #
        ref=DataReferenceFactory(EXCEL_DATA_SOURCE,"store.xls",\
                                 selector="dss2excel$B5")

        self.excel_service.batch_add(ref,tss)
       
                
        
        

        
if __name__=="__main__":
    
    unittest.main()      
        
 




        

                 

    
    
