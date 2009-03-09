import sys,os,unittest,shutil ,pdb
from copy import deepcopy

from vtools.datastore.dss.dss_service import DssService
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.dss.dss_catalog import DssCatalog
from vtools.datastore.dss.dss_constants import *
from vtools.datastore.catalog import CatalogEntry
from vtools.data.constants import *
from vtools.datastore.data_reference import DataReference
from vtools.data.timeseries import TimeSeries,rts,its,minutes
from vtools.data.vtime import ticks_to_time,parse_time
from dateutil.parser import parse
 
   
class TestDssService(unittest.TestCase):

    """ test functionality of dss service """
    def __init__(self,methodName="runTest"):

        super(TestDssService,self).__init__(methodName)
        #self.test_file_path='\\datastore\\dss\\test\\testfile.dss'
        #fs=__import__("vtools").__file__
        #(fsp,fsn)=os.path.split(fs)
        #self.test_file_path=fsp+self.test_file_path
        #self.backup_dss_file=fsp+'\\datastore\\dss\\test\\backup_dssfile\\testfile.dss'
        
        self.test_file_path=os.path.abspath("testfile.dss")
        self.backup_dss_file=os.path.abspath("./backup_dssfile/testfile.dss")
        
        self.servic_emanager=DataServiceManager()
        self.dss_service=self.servic_emanager.\
        get_service("vtools.datastore.dss.DssService")
        
    def setUp(self):


        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
            
        shutil.copy(self.backup_dss_file,self.test_file_path)

        if os.path.exists('newdss.dss'):
            os.remove('newdss.dss')
        
    def tearDown(self):
        
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_get_catalog(self):

        dssfile_path=self.test_file_path

        dssc=self.dss_service.get_catalog(dssfile_path)
        self.assert_(type(dssc)==DssCatalog)
        
        entries=dssc.entries()
        
        for entry in entries:
            self.assert_(type(entry)==CatalogEntry)
            
        self.assertEqual(len(entries),25)
        
    def test_get_data(self):
        # Regular time series.
        id="vtools.datastore.dss.DssService"
        view=""
        selector="/TUTORIAL/DOWNSTREAM/EC//15MIN/REALISTIC/"
        source=self.test_file_path
        extent="time_window=(12/1/1991 03:45,12/24/1991 01:30)"
        data_ref=DataReference(id,source,view,selector,extent)
        data=self.dss_service.get_data(data_ref)
        self.assert_(type(data)==TimeSeries)
        l=len(data.data)
        self.assertEqual(len(data.data),2200)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/1/1991 03:45'))
        # Here dss reading func only read up to right end of
        # time window (not include).
        self.assertEqual(ticks_to_time(data.ticks[l-1]),parse('12/24/1991 01:30'))

        # Irregular time series.
        selector="/TUTORIAL/GATE/FLAP_OP//IR-YEAR/CONSTANT/"
        extent="time_window=(12/11/1991 01:00,04/02/1992 21:50)"
        data_ref=DataReference(id,source,view,selector,extent)
        data=self.dss_service.get_data(data_ref)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),106)

    def test_get_data_all(self):
        ## here to test pull out all the data from a
        ## path given(through data references).

        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        entries=dssc.entries()

        ## for each entry ,bulit a datareference without
        ## time window given
        for entry in entries:
            data_ref=dssc.get_data_reference(entry)
            #print data_ref.selector
            #print entry.dimension_scales()[0].get_range()
            #pdb.set_trace()
            ts=self.dss_service.get_data(data_ref)
            self.assert_(type(ts)==TimeSeries)


    def test_get_save_ts(self):
        ## test ts property unchanged after read and save ts into dss
            
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC/"
        source=self.test_file_path
        dssc=self.dss_service.get_catalog(source)
        ##cagatalog function return a itertor over possible data reference
        ##we only get one data ref
        data_refs=dssc.data_references(selector)
        data_ref=data_refs.next()
        ts=self.dss_service.get_data(data_ref)


        ## then save this ts back into dss in a different path with some
        ## extra props to simulate props in pratical cases
        id="vtools.datastore.dss.DssService"
        path="/RLTM+CHAN/SLBAR002_COPY/FLOW-EXPORT//1DAY/DWR-OM-JOC/"
        source=self.test_file_path
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,ts)

        ## read this ts back it be same length as original one
        data_refs=dssc.data_references(selector)
        data_ref=data_refs.next()
        nts=self.dss_service.get_data(data_ref)
        self.assert_(len(ts)==len(nts))
    
        
    def test_save_ts_props(self):
        ## test ts property unchanged after read and save ts into dss
            
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC/"
        source=self.test_file_path
        dssc=self.dss_service.get_catalog(source)
        ##cagatalog function return a itertor over possible data reference
        ##we only get one data ref
        data_refs=dssc.data_references(selector)
        data_ref=data_refs.next()
        ts=self.dss_service.get_data(data_ref)
        self.assert_(type(ts)==TimeSeries)
        self.assert_(ts.props[AGGREGATION]==MEAN)
        self.assert_(ts.props["DATUMN"]=="NGVD88")
        self.assert_(ts.props["AUTHOR"]=="John Doe")
        self.assert_(ts.props["MODEL"]=="hydro 7.5")
        
        ## then save this ts back into dss in a different path
        ## to simulate pratical cases
        id="vtools.datastore.dss.DssService"
        path="/RLTM+CHAN/SLBAR002_COPY/FLOW-EXPORT//1DAY/DWR-OM-JOC/"
        source=self.test_file_path
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,ts)

        ## read this ts back it AGGREATION should be MEAN
        ## also with all other properties
        dssc=self.dss_service.get_catalog(source)
        data_refs=dssc.data_references(path)
        data_ref=data_refs.next()
        ts=self.dss_service.get_data(data_ref)
        self.assert_(type(ts)==TimeSeries)
        self.assert_(ts.props[AGGREGATION]==MEAN)
        self.assert_(ts.props["DATUMN"]=="NGVD88")
        self.assert_(ts.props["AUTHOR"]=="John Doe")
        self.assert_(ts.props["MODEL"]=="hydro 7.5")
                
    def test_save_data(self):
        ## save some ts into dss file, ts may contain
        ## header.

        ## save rts first.
        data=range(1000)
        start="12/21/2000 2:00"
        interval="1hour"
        prop={}
        prop[TIMESTAMP]=PERIOD_START
        prop[AGGREGATION]=MEAN

        prop["datum"]="NGVD88"
        prop["manager"]="John Doe"
        prop["model"]="hydro 7.5"

        rt1=rts(data,start,interval,prop)

        id="vtools.datastore.dss.DssService"
        path="/TEST/DOWNSTREAM/EC//1HOUR/STAGE/"
        source=self.test_file_path

        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,rt1)
        dssc=self.dss_service.get_catalog(source)        
        path="/TEST/DOWNSTREAM/EC//1HOUR/STAGE/"
        
        data_ref=dssc.data_references(path).next()       
        rtt=self.dss_service.get_data(data_ref)      
        self.assert_(len(rtt)==len(data))
        self.assert_(rtt.props[TIMESTAMP]==PERIOD_START)
        self.assert_(rtt.props[AGGREGATION]==MEAN)      

        extent="time_window=(12/21/2000 02:00,01/31/2001 18:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt.start==rtt2.start)
        self.assert_(rtt.end==rtt2.end)
        
        ## then its.

        path="/HERE/IS/ITS//IR-YEAR/TEST/"
        data=range(20)
        data_ref=DataReference(id,source=source,selector=path)
        prop[AGGREGATION]=INDIVIDUAL
        
        times=["01/15/1997","02/17/1997","03/5/1997",\
               "04/25/1997","05/1/1997","06/15/1997",\
               "07/25/1997","08/14/1997","09/17/1997",\
               "10/15/1997","11/21/1997","12/3/1997",\
               "01/9/1998","02/15/1998","03/19/1998",\
               "04/15/1998","05/19/1998","06/30/1998",\
               "07/15/1998","08/24/1998"]
        
        times=map(parse_time,times)
        itt=its(times,data,prop)
        self.dss_service.add_data(data_ref,itt)
        extent="time_window=(1/10/1997 02:00,09/30/1998 18:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt3=self.dss_service.get_data(data_ref)
        self.assert_(parse_time("01/15/1997")==rtt3.start)
        self.assert_(parse_time("08/24/1998")==rtt3.end)
        
    def test_retrievesave_longits(self):
        ## save some ts into dss file, ts may contain
        ## header.

        ## save rts first.
        data=range(36009)
        start="12/21/2000 2:00"
        interval="1hour"
        prop={}
        prop[TIMESTAMP]=INST
        prop[AGGREGATION]=INDIVIDUAL

        prop["datum"]="NGVD88"
        prop["manager"]="John Doe"
        prop["model"]="hydro 7.5"

        rt1=rts(data,start,interval,prop)
        it1=its(data,rt1.ticks,prop)

        id="vtools.datastore.dss.DssService"
        path="/TEST/DOWNSTREAM/EC//1HOUR/SRT/"
        source=self.test_file_path
        
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,rt1)  
        
        ##path="/TEST/DOWNSTREAM/EC//IR-MONTH/STAGE/"
        ##data_ref=DataReference(id,source=source,selector=path)
        ##self.dss_service.add_data(data_ref,it1)   
      

    def test_save2newf(self):
        """ try to save ts to a non exist file."""
        ## save rts first.
        data=range(1000)
        start="12/21/2000 2:00"
        interval="1hour"
        prop={}
        prop[TIMESTAMP]=PERIOD_START
        prop[AGGREGATION]=MEAN

        prop["datum"]="NGVD88"
        prop["manager"]="John Doe"
        prop["model"]="hydro 7.5"

        rt1=rts(data,start,interval,prop)

        id="vtools.datastore.dss.DssService"
        path="/TEST/DOWNSTREAM/EC//1HOUR/STAGE/"
        source='newdss.dss'
        
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,rt1)

        self.assert_(os.path.exists(source))
           
      
        
if __name__=="__main__":
    
    unittest.main()  
        
        

        

        


    



        

        
        

    
                    




        

                 

    
    
