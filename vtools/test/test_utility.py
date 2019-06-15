"""  Test handy utility functions to read data from or save data to dss source.
"""
## python import
import sys,os,shutil,unittest,pdb

## vtools import
from vtools.data.vtime import *
from vtools.data.timeseries import rts,its
from vtools.datastore import *
from vtools.datastore.dss import *
from vtools.datastore.dss.utility import *

from vtools.datastore.dss.dss_service import *



class TestUtility(unittest.TestCase):

    """ test functionality of dss utility funcs """


    def __init__(self,methodName="runTest"):

        super(TestUtility,self).__init__(methodName)
        import vtools.test
        pkgfile = vtools.test.__file__
        self.dss_file_path='testfile.dss'
        self.dss_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.dss_file_path)
        self.backup_dss_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'backup/testfile.dss') 
        
        
        
    def setUp(self):
        if os.path.exists(self.dss_file_path):
            os.remove(self.dss_file_path)
        shutil.copy(self.backup_dss_file,self.dss_file_path)
        
    def tearDown(self):
        
        if os.path.exists(self.dss_file_path):
            os.remove(self.dss_file_path)

    def test_retrieve_rts_data(self):
        """ test retrieve ts from a source based on path and
            time window desired.
        """
        ## retrieve all data.
        dssfile_path=self.dss_file_path
        selector="/RLTM+CHAN/RSAN112/FLOW//1DAY/DWR-OM-JOC-DSM2/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(len(ts),938)

        ## retrieve some data within a time window.
        ## this should contain 11 data
        time_window="(10/01/1997 02:00,10/12/1997 03:00)"
        ts=dss_retrieve_ts(dssfile_path,selector,time_window)
        self.assertEqual(len(ts),11)
        
    def test_save_rts_data(self):
        """ test adding a rts to source."""

        ## save some data.
        dssfile_path=self.dss_file_path
        path="/RLTM+CHAN/RSAN112/FLOW//15MIN/DWR-OM-JOC-DSM2/"
        data=[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0, \
              10.0,11.0,12.0,13.0,14.5,15.1,16.8,\
              17.2,14.2,19.2,20.0]
        start="01/15/1997"
        props={}
        ts = rts(data,start,minutes(15))
        dss_store_ts(ts,dssfile_path,path)

    def test_save_its_data(self):
        """ test adding a its to source."""

        ## save some data.
        dssfile_path=self.dss_file_path
        path="/HERE/IS/ITS//IR-YEAR/TEST/"
        data=[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0, \
              10.0,11.0,12.0,13.0,14.5,15.1,16.8,\
              17.2,14.2,19.2,20.0]
       
        times=["01/15/1997","02/17/1997","03/5/1997",\
               "04/25/1997","05/1/1997","06/15/1997",\
               "07/25/1997","08/14/1997","09/17/1997",\
               "10/15/1997","11/21/1997","12/3/1997",\
               "01/9/1998","02/15/1998","03/19/1998",\
               "04/15/1998","05/19/1998","06/30/1998",\
               "07/15/1998","08/24/1998"]
        times =list(map(parse,times))
        props={}
        ts = its(times,data,props=props)
        dss_store_ts(ts,dssfile_path,path)

    def test_cataloging_data(self):
        ##
        dssfile_path=self.dss_file_path
        c=dss_catalog(dssfile_path)
        print(c)
      
        
        
   


if __name__=="__main__":
    
    unittest.main()        
        

        
        

        

        


    


