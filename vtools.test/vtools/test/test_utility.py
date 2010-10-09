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

class TestUtility(unittest.TestCase):

    """ test functionality of dss utility funcs """


    def __init__(self,methodName="runTest"):

        super(TestUtility,self).__init__(methodName)
        self.dss_file_path='.\\testfile.dss'
        fs=__import__("vtools").__file__
        (fsp,fsn)=os.path.split(fs)
        self.dss_file_path=fsp+self.dss_file_path
        self.backup_dss_file=fsp+'\\test\\backup\\testfile.dss'
        
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
        selector="PATH=/RLTM+CHAN/RSAN112/FLOW//1DAY/DWR-OM-JOC-DSM2/;"
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(len(ts),938)

        ## retrieve some data within a time window.
        ## this should contain 11 data
        time_window="time_window=(10/01/1997 02:00,10/12/1997 03:00);"
        selector=time_window+selector
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(len(ts),11)
        
    def test_save_rts_data(self):
        """ test adding a rts to source."""

        ## save some data.
        dssfile_path=self.dss_file_path
        path="/RLTM+CHAN/RSAN112/FLOW//1DAY/DWR-OM-JOC-DSM2/"
        data=range(20)
        start="01/15/1997"
        props={}
        ts = rts(data,start,minutes(15))
        dss_store_ts(dssfile_path,path,ts)

    def test_save_its_data(self):
        """ test adding a its to source."""

        ## save some data.
        dssfile_path=self.dss_file_path
        path="/HERE/IS/ITS//IR-YEAR/TEST/"
        data=range(20)
       
        times=["01/15/1997","02/17/1997","03/5/1997",\
               "04/25/1997","05/1/1997","06/15/1997",\
               "07/25/1997","08/14/1997","09/17/1997",\
               "10/15/1997","11/21/1997","12/3/1997",\
               "01/9/1998","02/15/1998","03/19/1998",\
               "04/15/1998","05/19/1998","06/30/1998",\
               "07/15/1998","08/24/1998"]
        props={}
        ts = its(data,times,props=props)
        dss_store_ts(dssfile_path,path,ts)

    def test_cataloging_data(self):


        ##
        dssfile_path=self.dss_file_path
        c=dss_catalog(dssfile_path)

        for e in c.entries():
            print e.item("A"),e.item("DATATYPE"),e.item("UNIT")
        
        
   


if __name__=="__main__":
    
    unittest.main()        
        

        
        

        

        


    


