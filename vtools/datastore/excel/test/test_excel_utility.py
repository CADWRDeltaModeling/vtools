import sys,os,unittest,shutil,pdb


from vtools.data.vtime import *           
from datetime import datetime         
from vtools.datastore.excel.utility import *
from vtools.data.timeseries import *


## numpy import
from numpy import arange,sin,pi,cos

class TestExcelUtility(unittest.TestCase):
    """ test utility functions of excel  """

    def __init__(self,methodName="runTest"):
        super(TestExcelUtility,self).__init__(methodName)
        self.test_file_path='test.xls'
        self.test_file_path=os.path.join(os.path.split(os.path.abspath(__file__))[0],self.test_file_path)
        self.data_file_path='data.xls'
        self.data_file_path=os.path.join(os.path.split(os.path.abspath(__file__))[0],self.data_file_path)
        self.backup_excel_file=os.path.join(os.path.split(os.path.abspath(__file__))[0],'backup_excelfile/test.xls')
         
    def setUp(self):
    
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)            
        shutil.copy(self.backup_excel_file,self.test_file_path)                

        if os.path.exists(self.data_file_path):
            os.remove(self.data_file_path)         
                   

    def test_retrieve_rts_notimes(self):
        excel_file=self.test_file_path

        ## test uniform start,intl given by func input        
        selection="hydro_flow$B5:F110"
        ts_type="rts"
        start=datetime(2003,10,15,12)
        intl=minutes(15)
        tss=excel_retrieve_ts(excel_file,selection,ts_type,start=start,\
                              interval=intl,header_labels=["unit","name"])

        self.assertEqual(len(tss),5)
        for ts in tss:
            self.assertEqual(len(ts),104)
        ## same as previous with excpet of retrieving only one ts
        selection="hydro_flow$B5:B110"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,start=start,\
                              interval=intl,header_labels=["unit","name"])
        self.assertEqual(type(tss),TimeSeries)
        self.assertEqual(len(tss),104)
            

        ## test varied start,intl given by header within sheet.       
        selection="hydro_flow$O8:S114"
        ts_type="rts"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,\
                              header_labels=["interval","start","name"])
        self.assertEqual(len(tss),5)
        self.assertEqual(tss[2].start,datetime(2001,3,12,15,15))
        self.assertEqual(tss[2].interval,days(1))
        self.assertEqual(len(tss[2]),104)
        ## same as previous with excpet of retrieving only one ts
        selection="hydro_flow$O8:O114"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,\
                        header_labels=["interval","start","name"])
        self.assertEqual(type(tss),TimeSeries)
        self.assertEqual(len(tss),104)
        

        ## same as previous with except of range used as header labels
        selection="hydro_flow$O8:S114"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,\
                              header_labels="N8:N10")
        self.assertEqual(len(tss),5)
        self.assertEqual(tss[2].start,datetime(2001,3,12,15,15))
        self.assertEqual(tss[2].interval,days(1))
        self.assertEqual(len(tss[2]),104)
        ## same as previous with excpet of retrieving only one ts
        selection="hydro_flow$O8:O114"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,\
                        header_labels="N8:N10")
        self.assertEqual(type(tss),TimeSeries)
        self.assertEqual(len(tss),104)
  

    def test_retrieve_rts_all_time(self):
        """ test of retrieving rts as time is given next to each data col"""
        excel_file=self.test_file_path
      
        selection="hydro_flow$w14:AF118"
        ts_type="rts"
    
        tss=excel_retrieve_ts(excel_file,selection,ts_type,time="all",\
                              header_labels=["name"])

        self.assertEqual(len(tss),5)
        for ts in tss:
            self.assertEqual(len(ts),104)

        selection="hydro_flow$w14:X118"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,time="all",\
                              header_labels=["name"])        
        self.assertEqual(type(tss),TimeSeries)
        self.assertEqual(len(tss),104)            
        ## left to do  header_labels not given use
        ## default single label "name"
        
    def test_retrieve_ts(self):
        """ test of retrieving rts as time is given next to each data col"""
        
        excel_file=self.test_file_path
        selection="hydro_flow$w14:AF118"
        ts_type="its"
        
        tss=excel_retrieve_ts(excel_file,selection,ts_type,time="all",\
                              header_labels=["name"])

        self.assertEqual(len(tss),5)
        for ts in tss:
            self.assert_(not (ts.is_regular()))

    def test_retrieve_rts_col_time(self):
        """ test of retrieving rts as all share one time col"""
        
        excel_file=self.test_file_path
      
        selection="hydro_flow$A125:F229"
        ts_type="rts"

        tss=excel_retrieve_ts(excel_file,selection,ts_type,time="auto",\
                              header_labels=["name"])

        self.assertEqual(len(tss),5)
        for ts in tss:
            self.assertEqual(len(ts),104)

        selection="hydro_flow$A125:B229"
        tss=excel_retrieve_ts(excel_file,selection,ts_type,time="auto",\
                              header_labels=["name"])        
        self.assertEqual(type(tss),TimeSeries)
        self.assertEqual(len(tss),104)

        
        ## left to do ,  header_labels not given use
        ## default single label "name"

    def test_store_ts(self):
        """ test store ts into excel file."""

        st=datetime(2001,3,12,15,15)
        intl=hours(1)
        data=arange(10020)
        data=sin(data*pi/12+0.23)
        prop={"name":"rsac101","datum":"ngvd88"}
        ts1=rts(data,st,intl,prop)

        st=datetime(1997,4,12,12,00)
        intl=minutes(30)
        data=arange(10080)
        data=cos(data*pi/12+0.01)
        prop={"name":"rsac102","datum":"ngvd88"}
        ts2=rts(data,st,intl,prop)

        st=datetime(1971,3,12,15,15)
        intl=days(1)
        data=arange(10200)
        data=sin(data*pi/12+0.03)
        prop={"name":"rsac103","datum":"ngvd88"}
        ts3=rts(data,st,intl,prop)        
       
        ts=[ts1,ts2,ts3]
        excel_file="store.xls" #self.data_file_path
        sheetname="ts2excel"
        ## test write complete data with time and header
        excel_store_ts(ts,excel_file,sheetname+"$B23",header=["name","datum"])

        ## test write 1000 data with time and header
        excel_store_ts(ts,excel_file,sheetname+"$I23:J1022",header=["name"])

        ## test write 1000 data without time
        excel_store_ts(ts,excel_file,sheetname+"$P23:P1022",header=["name"],\
                       write_times="none")

        ## test write 1000 data with only first ts time
        excel_store_ts(ts,excel_file,sheetname+"$s23:t1022",header=["name"],\
                       write_times="first")

                
              
        
        
if __name__=="__main__":
    
    unittest.main()  
        
        

        

        


    



        

        
        

    
                    




        

                 

    
    
