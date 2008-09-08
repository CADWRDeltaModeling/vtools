import sys,os,unittest,shutil,pdb
from vtools.data.vtime import *        
from vtools.data.timeseries import *   
from datetime import datetime         
from scipy import arange,sin,pi,cos

from vtools.datastore.dss.utility import *

   
class TestDssUtility(unittest.TestCase):

    """ test utility functions of dss  """


    def __init__(self,methodName="runTest"):

        super(TestDssUtility,self).__init__(methodName)
        #self.test_file_path='\\datastore\\dss\\test\\sin.dss'
        #fs=__import__("vtools").__file__
        #(fsp,fsn)=os.path.split(fs)
        #self.test_file_path=fsp+self.test_file_path
        self.test_file_path=os.path.abspath('sin.dss')

        self.data_file_path='testfile.dss'
        self.data_file_path=os.path.abspath(self.data_file_path)
        self.backup_data_file=os.path.abspath('./backup_dssfile/testfile.dss')        
        
    def setUp(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        if os.path.exists(self.data_file_path):
            os.remove(self.data_file_path)
            
        shutil.copy(self.backup_data_file,self.data_file_path)            
                   
    def tearDown(self):   
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        if os.path.exists(self.data_file_path):
            os.remove(self.data_file_path)

    def test_save_ts_manytimes(self):
        
        start=datetime(1990,1,1,0,0)
        dt = hours(1)
        n=1000
        x=arange(n)
        data=sin(2*pi*x/24.)
        ts=rts(data,start,dt,{})
        destination=self.test_file_path

        num_ts=100
        for i in range(num_ts):
            path="/I_%s/CREATE/THIS//1HOUR/TS/"%i 
            dss_store_ts(ts,destination,path)

        self.assert_(os.path.exists(destination))

    def test_retrieve_ts(self):
   
        
        dssfile_path=self.data_file_path
        selector="/HIST*/SLTR*/*//15MIN/*/"
        tss=dss_retrieve_ts(dssfile_path,selector)
        numd=len(tss)
        
        range="(10/2/1997 1200, 7/4/1998 1315)"
        tss=dss_retrieve_ts(dssfile_path,selector,range)
        numd=len(tss)
        self.assertEqual(numd,3)

        range=("10/2/1997 12:00", "7/4/1998 13:15")
        tss=dss_retrieve_ts(dssfile_path,selector,range)
        numd=len(tss)
        self.assertEqual(numd,3)

        start=datetime(1997,10,2,12)
        end=datetime(1998,7,4, 13,15)
        range=(start, end)
        tss=dss_retrieve_ts(dssfile_path,selector,range)
        numd=len(tss)
        self.assertEqual(numd,3)

        start=datetime(1997,10,1)
        end=datetime(1998,9,30, 23,45)        
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(type(ts),TimeSeries)
        self.assertEqual(ts.start,start)
        self.assertEqual(ts.end,end)

        start=datetime(1997,10,2)
        end=datetime(1998,9,15, 23,45)        
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/"
        ts=dss_retrieve_ts(dssfile_path,selector,(start,end))

        self.assertEqual(type(ts),TimeSeries)
        self.assertEqual(ts.start,start)
        self.assertEqual(ts.end,end)

    def test_dss_delete_ts(self):
    
        dssfile_path=self.data_file_path
        selector="/HIST*/SLTR*/*//15MIN/*/"
        dss_delete_ts(dssfile_path,selector)
        self.assertRaises(Warning,dss_retrieve_ts,dssfile_path,selector)


    def test_dss_catalog(self):
        dssfile_path=self.data_file_path
        selector="/HIST*/SLTR*/*//15MIN/*/"
        cat=dss_catalog(dssfile_path)
        self.assertEqual(len(cat),25)
        cat=dss_catalog(dssfile_path,selector)
        self.assertEqual(len(cat),3)
        
if __name__=="__main__":
    
    unittest.main()  
        
        

        

        


    



        

        
        

    
                    




        

                 

    
    
