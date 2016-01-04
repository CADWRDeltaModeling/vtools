import unittest,sys,os,shutil,pdb

## Datetime import
import datetime

## vtools import.
from vtools.datastore.transfer import *
from vtools.datastore.data_service_manager import \
     DataServiceManager

## vtools time series function import
from vtools.functions.resample import *
from vtools.functions.period_op import *
from vtools.functions.filter import *
from vtools.functions.shift import *


## vtools data service import
from vtools.datastore.dss.dss_service import *
from vtools.datastore.excel.excel_service import *


class TestTransfer(unittest.TestCase):
    """ test functionality of data transfer """
    
    def __init__(self,methodName="runTest"):

        super(TestTransfer,self).__init__(methodName)
        import vtools.test
        pkgfile = vtools.test.__file__
        self.test_file_path='testfile.dss'
        self.test_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.test_file_path)
        self.backup_dss_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'backup/testfile.dss') 
        
        self.test_file2="dest.dss"
        self.test_file2=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.test_file2)
        
        self.xls_file="test.xls"
        self.xls_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.xls_file)

        if os.path.exists(self.xls_file):
            os.remove(self.xls_file)
            
        self.path_file='paths.txt'
        self.path_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.path_file)
        self.backup_path_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'backup/paths.txt')
            
    def setUp(self):
        
        self.service_manager=DataServiceManager()
        self.dss_service=self.service_manager.get_service\
        ("vtools.datastore.dss.DssService")
        self.excel_service=self.service_manager.get_service\
        ("vtools.datastore.excel.ExcelService")
        
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
            
        shutil.copy(self.backup_dss_file,self.test_file_path)
        
        if os.path.exists(self.path_file):
            os.remove(self.path_file)
            
        shutil.copy(self.backup_path_file,self.path_file)
              
            
    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        
        if os.path.exists(self.test_file2):
            os.remove(self.test_file2)
        
    def test_batch_transfer_rts1(self):
        """ test transfer several time series to a new source without
            any transform.
        """
        dssfile_path=self.test_file_path
        selector="/HIST+CHAN/*/*/*/*/*/"
        time_window="(10/2/1997 1200, 7/4/1998 1315)"
        ## given selector2 here, translation in fact.
        translation="/${A}_AVER/${B}/${C}//${E}/${F}/"
        dest=self.test_file2
        ## transfer to different source
        batch_transfer(dssfile_path,dest,selector,time_window,translation)
        ## tranfer to same soure
        dest=dssfile_path
        batch_transfer(dssfile_path,dest,selector,time_window,translation)

        ## try to copy only one record
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/"
        batch_transfer(dssfile_path,dest,selector,None,translation)
        
        ## try a different path selection method.        
        selector="A=HIST+CHAN,B=SLTMP*"
        time_window="(10/2/1997 1200, 7/4/1998 1315)"
        translation="/${A}/${B}/${C}//${E}/${F}/"
        batch_transfer(dssfile_path,dest,selector,time_window,translation)

    def test_batch_transfer_all(self):
        """ test transfer all data within a dss to another"""
        dssfile_path=self.test_file_path
        selector=None
        time_window=None
        ## given selector2 here, translation in fact.
        translation="/${A}/${B}/${C}//${E}/${F}/"
        dest=self.test_file2
        batch_transfer(dssfile_path,dest)

    def test_batch_transfer_rts(self):
        """ test transfer several time sereies to a new source with some
            transformation.
        """

        ## selecting time series 
        dssfile_path=self.test_file_path
        selector="/HIST+CHAN/*/*/*/*/*/" 
        time_window="(10/2/1997 1200, 7/4/1998 1315)"
        
        ## period operations
        funcs=[period_min,period_max,period_ave]

        for func in funcs:
            interval="1HOUR"
            translation="/${A}_"+func.__name__\
                         +"/${B}/${C}//"+interval+"/${F}/"
            dest=self.test_file2
            ## transfer to dss file
            batch_transfer(dssfile_path,dest,selector,time_window,translation,func,\
                           interval=interval)
            ## transfer to excel file
            dest=self.xls_file
            translation="selection=dss2excel_%s$B10,name=${B}_${C},unit=\
            ${unit},write_times=first"%func.__name__
            batch_transfer(dssfile_path,dest,selector,time_window,translation\
                           ,func,interval=interval)            

        ## filtering operations
        funcs=[godin,butterworth]

        for func in funcs:
            translation="/${A}_"+func.__name__\
                         +"/${B}/${C}//${E}/${F}/"
            dest=self.test_file2
            batch_transfer(dssfile_path,dest,selector,time_window,translation,func)
            ## transfer to excel file
            dest=self.xls_file
            translation="selection=dss2excel_%s$B10,name=${B}_${C},unit=\
            ${unit},write_times=first"%func.__name__
            batch_transfer(dssfile_path,dest,selector,time_window,translation\
                           ,func) 

        ## resample operations.
        funcs=[decimate,resample]

        
        for func in funcs:
            interval="1HOUR"
            translation="/${A}_"+func.__name__\
                         +"/${B}/${C}//"+interval+"/${F}/"
            dest=self.test_file2
            batch_transfer(dssfile_path,dest,selector,time_window,translation,func,\
                           interval=interval)
            ## transfer to excel file
            dest=self.xls_file
            translation="selection=dss2excel_%s$B10,name=${B}_${C},unit=\
            ${unit},write_times=first"%func.__name__
            batch_transfer(dssfile_path,dest,selector,time_window,translation,\
                           func,interval=interval) 


    def test_batch_transfer_dss2excel(self):
        """ test transfer several time series to a excel file without
            any transformation.
        """
        dssfile_path=self.test_file_path
        selector="/HIST+CHAN/*/*/*/*/*/"
        time_window="(10/2/1997 1200, 7/4/1998 1315)"
        
        ## given translation in visual dss style.
        translation="dsstoexcel_dsstyle$B10,name=${B}_${C},unit=\
        ${unit},write_times=first"
        dest=self.xls_file
        batch_transfer(dssfile_path,dest,selector,time_window,translation)

        ## given tranlation in plain style.
        translation="dsstoexcel_plainstyle"
        batch_transfer(dssfile_path,dest,selector,time_window,translation)

    
                                            
if __name__=="__main__":
    
    unittest.main()       
