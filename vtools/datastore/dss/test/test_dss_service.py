import sys,os,unittest,shutil ,pdb
from copy import deepcopy

from vtools.datastore.dss.dss_service import DssService,DssAccessError
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.dss.dss_catalog import DssCatalog,DssCatalogError
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
        self.test_file_path=os.path.join(os.path.split(__file__)[0],"testfile.dss")
        self.backup_dss_file=os.path.join(os.path.split(__file__)[0],"backup_dssfile/testfile.dss")  
        print "**********************"
        print self.backup_dss_file        
        self.service_manager=DataServiceManager()
        self.dss_service=self.service_manager.get_service("vtools.datastore.dss.DssService")
        
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
        self.assertEqual(len(entries),28)
        
    def test_get_data(self):

        id="vtools.datastore.dss.DssService"
        view=""
        source=self.test_file_path

        # Regular time series.
      
        selector="/TUTORIAL/DOWNSTREAM/EC//15MIN/REALISTIC/"
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

        # regular time series didn't accept overlap option
        overlap =(0,0)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref,overlap)


     
        # Irregular time series.
        selector="/TUTORIAL/GATE/FLAP_OP//IR-YEAR/CONSTANT/"
        extent="time_window=(12/11/1991 01:00,04/02/1992 21:50)"
        data_ref=DataReference(id,source,view,selector,extent)
        data=self.dss_service.get_data(data_ref)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),106)
        
        ## retrieve data of monthly interval
        ## Note this operation will trigger the exception handling line
        ## of funciton _multiple_window of dss_service.py. For dss_service
        ## will try to forward input time window start time by DSS_MAX_RTS_POINTS
        ## months, which is over the maximum year set by Python Datetime.
        
        selector="/SHORT/SYNTHETIC/DATA//1MON/TEST-MONTHLY-INTERVAL/"
        extent="time_window=(12/1/1990,06/02/1991)"
        data_ref=DataReference(id,source,view,selector,extent)
        data=self.dss_service.get_data(data_ref)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),5)
        


    def test_get_its_data_overlap(self):
        
        id="vtools.datastore.dss.DssService"
        view=""
        source=self.test_file_path
        # Irregular time series.
        selector="/TUTORIAL/GATE/FLAP_OP//IR-YEAR/CONSTANT/"
        extent="time_window=(12/10/1991 00:05,01/24/1992 20:58)"
        data_ref=DataReference(id,source,view,selector,extent)
        ##  retrieve data within 
        overlap = (0,0)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),46)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:08'))

        ##  retrieve data within and preceding
        overlap = (1,0)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),47)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:04'))

        ##  retrieve data within  and following
        overlap = (0,1)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),47)
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/24/1992 21:00'))

        ##  retrieve data within 
        overlap = (1,1)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),48)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:04'))
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/24/1992 21:00'))


        ## test when time window exaclty coincide with record time points
        ## the data preceding and following time window will still be returned
        ## depends the overlap option
        extent="time_window=(12/10/1991 00:08,01/24/1992 21:00)"
        data_ref=DataReference(id,source,view,selector,extent)
        ##  retrieve data within 
        overlap = (0,0)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),47)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:08'))
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/24/1992 21:00'))

        ##  retrieve data within and preceding
        overlap = (1,0)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),48)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:04'))
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/24/1992 21:00'))

        ##  retrieve data within  and following
        overlap = (0,1)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),48)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:08'))
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/26/1992 08:00'))
        ##  retrieve data within 
        overlap = (1,1)
        data=self.dss_service.get_data(data_ref,overlap)
        self.assert_(type(data)==TimeSeries)
        self.assertEqual(len(data.data),49)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('12/10/1991 00:04'))
        self.assertEqual(ticks_to_time(data.ticks[-1]),parse('1/26/1992 08:00'))
        
    def test_get_aggregated_data(self):
        
        # Regular time series.
        id="vtools.datastore.dss.DssService"
        view=""
        selector="/RLTM+CHAN/SLBAR002/FLOW-EXPORT//1DAY/DWR-OM-JOC-DSM2/"
        source=self.test_file_path
        extent="time_window=(1/2/1997,1/5/1997)"
        data_ref=DataReference(id,source,view,selector,extent)
        data=self.dss_service.get_data(data_ref)
        self.assert_(type(data)==TimeSeries)
        l=len(data.data)
        self.assertEqual(len(data.data),3)
        self.assertEqual(data.data[0],11.0)
        self.assertEqual(ticks_to_time(data.ticks[0]),parse('1/2/1997'))
        # Here dss reading func only read up to right end of
        # time window (not include).
        self.assertEqual(ticks_to_time(data.ticks[l-1]),parse('1/4/1997'))

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

        ## read this ts back it be sa me length as original one
        data_refs=dssc.data_references(selector)
        data_ref=data_refs.next()
        nts=self.dss_service.get_data(data_ref)
        self.assert_(len(ts)==len(nts))
        
        ##clean up this temp data
        cat=self.dss_service.get_catalog(source)
        cat_filtered=cat.filter_catalog(path)
        cat_filtered.set_editable()
        cat_filtered.remove(cat_filtered.entries()[0])
        
        ##read catalog again, this path shouldn't be there
        cat_new=self.dss_service.get_catalog(source)
        self.assertEqual(len(cat_new),len(cat)-1)
        self.assertRaises(DssCatalogError,cat_new.filter_catalog,path)
        
    
        
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

        ts.props.clear()
        ts.props[AGGREGATION]=MEAN
        ts.props[TIMESTAMP]='PERIOD_START'
        ts.props[UNIT]='CFS'
        ts.props["VDATUM"]="NGVD88"
        ts.props["AUTHOR"]="John Doe"
        ts.props["MODEL"]="hydro 7.5"
    
        ## then save this ts back into dss in a different path
        ## to simulate pratical cases
        id="vtools.datastore.dss.DssService"
        path="/RLTM+CHAN/SLBAR002_COPY/FLOW-EXPORT//1DAY/DWR-OM-JOC/"
        source=self.test_file_path
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,ts)

        ## read this ts back it AGGREGATION should be MEAN
        ## also with all other properties
        dssc=self.dss_service.get_catalog(source)
        data_refs=dssc.data_references(path)
        data_ref=data_refs.next()
        ts=self.dss_service.get_data(data_ref)
        
        self.assert_(type(ts)==TimeSeries)
        self.assert_(ts.props[AGGREGATION]==MEAN)
        self.assert_(ts.props["VDATUM"]=="NGVD88")
        self.assert_(ts.props["AUTHOR"]=="John Doe")
        self.assert_(ts.props["MODEL"]=="hydro 7.5")
        
        
        ##clean up this temp data
        cat=self.dss_service.get_catalog(source)
        cat_filtered=cat.filter_catalog(path)
        cat_filtered.set_editable()
        cat_filtered.remove(cat_filtered.entries()[0])
    

    def test_read_aggregated_rts_timewindow(self):
        ## save some ts into dss file, ts is hourly averaged
        
        ## save rts first.
        data=range(1000)
        start="12/21/2000 2:00"
        interval="1hour"
        prop={}
        prop[TIMESTAMP]=PERIOD_START
        prop[AGGREGATION]=MEAN
        rt1=rts(data,start,interval,prop)

        id="vtools.datastore.dss.DssService"
        path="/TEST/DOWNSTREAM/EC//1HOUR/DWR/"
        source=self.test_file_path
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,rt1)
        

        ## test return part of stored data up to the end
        ## it should get 992 numbers and value is (8,9,...,1000)
        ## it start datetime shoudl be 12/21/2000 10:00
        extent="time_window=(12/21/2000 10:00,01/31/2001 18:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt2.start==parse_time("12/21/2000 10:00"))
        self.assert_(len(rtt2)==992)
        correct_data = range(8,len(rtt2)+8)
        for i in range(len(rtt2)):
            self.assert_(rtt2.data[i]==float(correct_data[i]))

        ## test return middle part of stored data
        ## it should get 12 numbers and value is (8,9,...,19)
        ## it start datetime should be 12/21/2000 10:00, end
        ## at 12/21/2000 21:00 (not include the late side)
        extent="time_window=(12/21/2000 10:00,12/21/2000 22:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt2.start==parse_time("12/21/2000 10:00"))
        self.assert_(rtt2.end==parse_time("12/21/2000 21:00"))
        self.assert_(len(rtt2)==12)
        correct_data = range(8,len(rtt2)+8)
        for i in range(len(rtt2)):
            self.assert_(rtt2.data[i]==float(correct_data[i]))

        ## test return middle part of stored data
        ## it should get 12 numbers and value is (8,9,...,19)
        ## it start datetime should be 12/21/2000 10:00, end
        ## at 12/21/2000 21:00 (not include the late side)
        ## time window is not given at the correct hourly time points.
        extent="time_window=(12/21/2000 09:45,12/21/2000 22:15)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt2.start==parse_time("12/21/2000 10:00"))
        self.assert_(rtt2.end==parse_time("12/21/2000 21:00"))
        self.assert_(len(rtt2)==12)
        correct_data = range(8,len(rtt2)+8)
        for i in range(len(rtt2)):
            self.assert_(rtt2.data[i]==float(correct_data[i]))

        ## test valid timewindow overlap exaclty the last data of
        ## the record
        extent="time_window=(1/31/2001 17:00,1/31/2001 18:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(999))

        ## test invalid time window with same start and end
        ## excatly at beginig time sequence
        extent="time_window=(12/21/2000 02:00,12/21/2000 02:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)

        ## test invalid time window with same start and end in the
        ## middle of time sequence
        extent="time_window=(12/21/2000 05:00,12/21/2000 05:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)

        ## test invalid time window with same start and end at the
        ## end of time sequence
        extent="time_window=(12/21/2000 17:00,12/21/2000 17:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)

        ## test invalid time window with same start and end not aligined with interval
        extent="time_window=(12/21/2000 05:15,12/21/2000 05:15)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)

        ## test invalid time window with different start and end within a hour interval
        extent="time_window=(12/21/2000 05:15,12/21/2000 05:55)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)

        ## test invalid time window with different start and end across two hour intervals
        ## but intervals are incomplete, so it should return no value
        extent="time_window=(12/21/2000 05:15,12/21/2000 06:55)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)


        ## test invalid time window with same start and end
        ## excatly at the middle time sequence
        extent="time_window=(12/21/2000 17:15,12/21/2000 17:15)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)


        ## test valid time window overlap exactly the first data
        ## at the begining
        extent="time_window=(12/21/2000 02:00,12/21/2000 03:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(0))


        ## test valid time window overlap exactly a data in the middle
        extent="time_window=(12/21/2000 05:00,12/21/2000 06:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(3))

        ## test valid time window overlap exactly a data at the end
        extent="time_window=(1/31/2001 17:00,1/31/2001 18:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(999))

        ## test invalid timewindow before the data starting
        ## but still overlap data block window
        extent="time_window=(12/21/2000 00:00,12/21/2000 1:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)
        


        ## test invalid timewindow overlapping data block window,
        extent="time_window=(1/31/2001 18:00,1/31/2001 22:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)
       

        ## test invalid timewindow not overlapping data block window
        extent="time_window=(11/21/2000 00:00,11/22/2000 1:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)
         
    def test_read_instant_rts_timewindow(self):
        ## save some ts into dss file, ts is hourly spaned instanteous
        
        ## save rts first.
        data=range(1000)
        start="12/21/2000 2:00"
        interval="1hour"
        prop={}

        rt1=rts(data,start,interval,prop)

        id="vtools.datastore.dss.DssService"
        path="/TEST/DOWNSTREAM/EC//1HOUR/STAGE/"
        source=self.test_file_path
        data_ref=DataReference(id,source=source,selector=path)
        self.dss_service.add_data(data_ref,rt1)
        

        ## test returning part of stored data up to the end
        ## it should get 992 numbers and value is (8,9,...,1000)
        ## it start datetime shoudl be 12/21/2000 10:00
        extent="time_window=(12/21/2000 10:00,01/31/2001 18:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt2.start==parse_time("12/21/2000 10:00"))
        self.assert_(len(rtt2)==992)
        correct_data = range(8,len(rtt2)+8)
        for i in range(len(rtt2)):
            self.assert_(rtt2.data[i]==float(correct_data[i]))

        ## test returning middle part of stored data
        ## it should get 13 numbers and value is (8,9,...,19,20)
        ## it start datetime should be 12/21/2000 10:00, end
        ## at 12/21/2000 22:00 (include the later side)
        extent="time_window=(12/21/2000 10:00,12/21/2000 22:00)"
        data_ref=DataReference(id,source,None,path,extent)        
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(rtt2.start==parse_time("12/21/2000 10:00"))
        self.assert_(rtt2.end==parse_time("12/21/2000 22:00"))
        self.assert_(len(rtt2)==13)
        correct_data = range(8,len(rtt2)+8)
        for i in range(len(rtt2)):
            self.assert_(rtt2.data[i]==float(correct_data[i]))

        ## test valid timewindow overlap exaclty the last data of
        ## the record
        extent="time_window=(1/31/2001 17:00,1/31/2001 17:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(999))

        ## test valid time window with same start and end
        ## excatly at begining of the time sequence
        extent="time_window=(12/21/2000 02:00,12/21/2000 02:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(0))


        ## test valid time window overlap exactly a data in the middle
        extent="time_window=(12/21/2000 05:00,12/21/2000 05:00)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==1)
        self.assert_(rtt2.data[0]==float(3))

        ## test invalid time window with same end and start not aligned with
        ## interval
        extent="time_window=(12/21/2000 05:15,12/21/2000 05:15)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)
        

        
        ## test invalid time window in the middle with the same earlier and later side
        ## not aligns with time sequence
        extent="time_window=(12/21/2000 05:15,12/21/2000 05:15)"
        data_ref=DataReference(id,source,None,path,extent)
        rtt2=self.dss_service.get_data(data_ref)
        self.assert_(len(rtt2)==0)
       

        ## test invalid timewindow before the data starting
        ## but still overlap data block window
        extent="time_window=(12/21/2000 00:00,12/21/2000 1:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)
        


        ## test invalid timewindow overlapping data block window,
        extent="time_window=(1/31/2001 18:00,1/31/2001 22:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)
        

        ## test invalid timewindow not overlapping data block window
        extent="time_window=(11/21/2000 00:00,11/22/2000 1:00)"
        data_ref=DataReference(id,source,None,path,extent)
        self.assertRaises(ValueError,self.dss_service.get_data,data_ref)


                
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
        
        
    def test_get_two_catalog_same_time(self):
        """ test get two catlogs of same file"""
        c1=self.dss_service.get_catalog(self.test_file_path)
        c2=self.dss_service.get_catalog(self.test_file_path)
        self.assertEqual(len(c1),len(c2))
     
        
    def test_get_save_ts_manytimes(self):
        """ get some ts from test file and save it back, repeat many times"""
        
        selector="/RLTM+CHAN/*/*//*/*/"
        loops =100
        print "this is a time consuming test case ,be patient..."
        for i in range(loops):
            c=self.dss_service.get_catalog(self.test_file_path)
            data_ref=[df for df in c.data_references(selector)]
            tslist=[]
            for a_data_ref in data_ref:
                ts=self.dss_service.get_data(a_data_ref)
                tslist.append(ts)

            for a_data_ref,ts in zip(data_ref,tslist):
                self.dss_service.add_data(a_data_ref,ts)
        print "finish repeating get and save ts %i rounds"%loops
           
           
      
        
if __name__=="__main__": 
    unittest.main()  
        
        

        

        


    



        

        
        

    
                    




        

                 

    
    
