import sys,os,unittest,shutil,pdb
from vtools.data.vtime import *        
from vtools.data.timeseries import *   
from vtools.data.constants import *
from vtools.datastore.dss.dss_constants import *
from datetime import datetime         
from scipy import arange,sin,pi,cos

from vtools.datastore.dss.utility import *
from vtools.datastore.dss.dss_service import DssService,DssAccessError
from vtools.datastore.dss.dss_catalog import DssCatalogError

class TestDssUtility(unittest.TestCase):

    """ test utility functions of dss  """


    def __init__(self,methodName="runTest"):

        super(TestDssUtility,self).__init__(methodName)
        #self.test_file_path='\\datastore\\dss\\test\\sin.dss'
        #fs=__import__("vtools").__file__
        #(fsp,fsn)=os.path.split(fs)
        #self.test_file_path=fsp+self.test_file_path


        import vtools.datastore.dss
        pkgfile = vtools.datastore.dss.__file__
        self.test_file_path='sin.dss'
        self.test_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.test_file_path)
        self.data_file_path='testfile.dss'
        self.data_file_path=os.path.abspath(self.data_file_path)
        self.backup_data_file=os.path.abspath('./backup_dssfile/testfile.dss')        
        
        self.data_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.data_file_path)
        ##self.backup_data_file=os.path.abspath('./backup_dssfile/testfile.dss')        
        self.backup_data_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'test/backup_dssfile/testfile.dss')
         
    def setUp(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        if os.path.exists(self.data_file_path):
            os.remove(self.data_file_path)
            
        shutil.copy(self.backup_data_file,self.data_file_path)            
                   
    def tearDown(self):   
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        ##if os.path.exists(self.data_file_path):
        ##    os.remove(self.data_file_path)

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
        
    def test_save_ts_invalid_path(self):
        start=datetime(1990,1,1,0,0)
        dt = hours(1)
        n=1000
        x=arange(n)
        data=sin(2*pi*x/24.)
        ts=rts(data,start,dt,{})
        destination=self.test_file_path       
        path="invalid path"
        self.assertRaises(ValueError,dss_store_ts,ts,destination,path)
        
        
    def test_save_retrieve_6min_rts(self):
        start=datetime(1990,1,1,0,0)
        dt = minutes(6)
        n=1000
        x=arange(n)
        data=sin(2*pi*x/24.)
        ts=rts(data,start,dt,{})
        destination=self.test_file_path
        path="/A/B/C//6MIN/F/"
        dss_store_ts(ts,destination,path)
        c=dss_catalog(destination)
        del c
        ts_back=dss_retrieve_ts(destination,path)
        self.assertEqual(len(ts),len(ts_back))
        self.assertEqual(ts.interval,ts_back.interval)
        for d1,d2 in zip(ts.data,ts_back.data):
            self.assertAlmostEqual(d1,d2)

    def test_retrieve_ts(self):
        
        ## READ A SHORT INST REGUALR TS
        dssfile_path=self.data_file_path
        selector="/HIST*/RSAC054/STAGE//15MIN/UCB-ELI/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(len(ts),673)
        self.assertEqual(ts.times[0],datetime(1999,7,12))
        self.assertEqual(ts.props[TIMESTAMP],INST)
        self.assertEqual(ts.props[AGGREGATION],INDIVIDUAL)
        self.assertAlmostEqual(ts.data[0],4.49960184)
        self.assertAlmostEqual(ts.data[-1],-0.41016656)
        
         ## READ A VERY LONG AVER REGUALR TS
        dssfile_path=self.data_file_path
        selector="/RSAC054/MTZ/EC//15MIN/DWR-DMS-200905_PER_AVE/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        self.assertEqual(len(ts),686768)
        self.assertEqual(ts.times[0],datetime(1989,10,31,3,0))
        self.assertEqual(ts.props[TIMESTAMP],PERIOD_START)
        self.assertEqual(ts.props[AGGREGATION],MEAN)
        self.assertEqual(round(ts.data[0]-25631.9,1),0)
        self.assertAlmostEqual(ts.data[-1],0.0)
        
        
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
        
    def test_retrieve_uniqe_sel(self):
        
        selector="/HIST+CHAN/*/*//*/*/"
        dssfile_path=self.data_file_path
        self.assertRaises(Warning,dss_retrieve_ts,dssfile_path,selector,\
                          unique=True)

    def test_retrieve_irreg_ts(self):
 
        start=datetime(2005,11,1)
        end=datetime(2005,12,1)        
        selector="/SPECIAL STUDY/DLC/STAGE//IR-DAY/CDEC/"
        ts=dss_retrieve_ts(self.data_file_path,selector,(start,end));
        self.assertEqual(len(ts),0)
        
    def test_retrieve_aver_ts(self):
        dssfile_path=self.data_file_path
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2/"
        tss=dss_retrieve_ts(dssfile_path,selector)
        numd=len(tss)
        self.assertEqual(numd,938)
        startdatetime=datetime(1997,1,1)
        self.assertEqual(tss.times[0],startdatetime)
        enddatetime=datetime(1999,7,27)
        self.assertEqual(tss.times[-1],enddatetime)
        self.assertAlmostEqual(tss.data[-1],114.0)
         
        timewindow="(01/01/1997,07/28/1999)"
        tss=dss_retrieve_ts(dssfile_path,selector,timewindow)
        numd=len(tss)
        self.assertEqual(numd,938)
        self.assertEqual(tss.times[0],startdatetime)
    
        
    def test_dss_delete_ts(self):
   
        dssfile_path=self.data_file_path
        selector="/HIST*/SLTR*/*//15MIN/*/"
        dss_delete_ts(dssfile_path,selector)
        self.assertRaises(DssCatalogError,dss_retrieve_ts,dssfile_path,selector)
        
    def test_dss_catalog_update_time_order(self):
   
        dssfile_path=self.data_file_path
        fnames=os.path.split(dssfile_path)
        dsd_path=os.path.join(fnames[0],fnames[1].replace(".dss",".dsd"))

        c = dss_catalog(dssfile_path)
        dss_mtime=os.stat(dssfile_path).st_mtime
        dsd_mtime=os.stat(dsd_path).st_mtime
        dsd_ctime=os.stat(dsd_path).st_ctime
        
        #print dss_mtime,dsd_mtime,dsd_ctime
        
        selector="/HIST*/SLTR*/*//15MIN/*/"
        dss_delete_ts(dssfile_path,selector)
        dss_mtime=os.stat(dssfile_path).st_mtime
        c = dss_catalog(dssfile_path)
        self.assertRaises(DssCatalogError,dss_retrieve_ts,dssfile_path,selector)
        dsd_mtime=os.stat(dsd_path).st_mtime
        dsd_ctime=os.stat(dsd_path).st_ctime
        #print dss_mtime,dsd_mtime,dsd_ctime
#        self.assertTrue(dss_mtime>dsd_mtime,msg="dss modification time is not after dsd modification\
#                        dss:%s,dsd:%s"%(dss_mtime,dsd_mtime))
 
        c = dss_catalog(dssfile_path)
        dss_mtime=os.stat(dssfile_path).st_mtime
        dsd_mtime=os.stat(dsd_path).st_mtime
        dsd_ctime=os.stat(dsd_path).st_ctime
        #print dss_mtime,dsd_mtime,dsd_ctime

    def test_dss_catalog(self):
        dssfile_path=self.data_file_path
        selector="/HIST*/SLTR*/*//15MIN/*/"
        cat=dss_catalog(dssfile_path)
        self.assertEqual(len(cat),28)
        cat=dss_catalog(dssfile_path,selector)
        self.assertEqual(len(cat),3)
    
    def test_dss_catalog_many_times(self):
        dssfile_path=self.data_file_path
        
        for i in range(100):
            cat=dss_catalog(dssfile_path)
            self.assertEqual(len(cat),28)
         
     
    def test_retrieve_save__inst_rts(self):

        ## READ A SHORT INST REGUALR TS
        dssfile_path=self.data_file_path
        fnames=os.path.split(dssfile_path)
        dsd_path=os.path.join(fnames[0],fnames[1].replace(".dss",".dsd"))
        selector="/HIST*/RSAC054/STAGE//15MIN/UCB-ELI/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        c=dss_catalog(dssfile_path)
        savepath="/HIST+FILL/RSAC054/STAGE//15MIN/UCB-ELI_CMAX/"
 
        dss_store_ts(ts,dssfile_path,savepath)
       
        dss_mtime=os.stat(dssfile_path).st_mtime
        dsd_mtime=os.stat(dsd_path).st_mtime
 
        nts=dss_retrieve_ts(dssfile_path,savepath)
        self.assertEqual(len(nts),len(ts))
        self.assertEqual(nts.times[0],ts.times[0])
        self.assertEqual(nts.props,ts.props)
        self.assertEqual(nts.data[0],ts.data[0])
        self.assertEqual(nts.data[-1],ts.data[-1])   

    def test_retrieve_save_aver_rts(self):
        
        dssfile_path=self.data_file_path
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        
        savepath="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2_C/"
        ts.props["unit"]="xddd"
        dss_store_ts(ts,dssfile_path,savepath)
        nts=dss_retrieve_ts(dssfile_path,savepath)
        
        self.assertEqual(len(nts),len(ts))
        self.assertEqual(nts.times[0],ts.times[0])
        self.assertEqual(nts.props,ts.props)
        self.assertEqual(nts.data[0],ts.data[0])
        self.assertEqual(nts.data[-1],ts.data[-1])       
        
    
    def test_save_ts_invalid_path(self):
        
        dssfile_path=self.data_file_path
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2/"
        ts=dss_retrieve_ts(dssfile_path,selector)
        
        ## invalid path without trailing /
        savepath="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2_C"
        
        self.assertRaises(ValueError,dss_store_ts,ts,dssfile_path,savepath)
        
        
if __name__=="__main__":
    
    unittest.main()  
        
        
        

        

        


    



        

        
        

    
                    




        

                 

    
    
