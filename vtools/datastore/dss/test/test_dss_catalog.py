import sys,os,unittest,shutil #,pdb
from copy import copy

from vtools.datastore.dss.dss_service import DssService,DssAccessError
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.dss.dss_catalog import DssCatalog,block_dic
from vtools.datastore.catalog import CatalogEntry
from vtools.datastore.data_reference import DataReference


from vtools.datastore.dimension import RangeDimension
from datetime import datetime
from dateutil.parser import parse


class TestDssCatalog(unittest.TestCase):
    """ test functionality of dss catalog """
    
    def __init__(self,methodName="runTest"):

        super(TestDssCatalog,self).__init__(methodName)     
        import vtools.datastore.dss
        pkgfile = vtools.datastore.dss.__file__
        self.test_file_path='testfile.dss'
        self.test_file_path=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],self.test_file_path)
        self.backup_dss_file=os.path.join(os.path.split(os.path.abspath(pkgfile))[0],'test/backup_dssfile/testfile.dss')    
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.dss_service=self.servic_emanager.get_service("vtools.datastore.dss.DssService")

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        shutil.copy(self.backup_dss_file,self.test_file_path)
        
    def tearDown(self):        
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)


    def test_get_data_reference(self):
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        for entry in dssc.entries():           
            data_ref=dssc.get_data_reference(entry)
        
    def test_copy_remove(self):
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)

        len1=len(dssc.entries())
        entry1=dssc.entries()[-1]
        entry2=dssc.copy(entry1)
        len2=len(dssc.entries())
        # Length of calalog entry list should be
        # increased by 1
        self.assertEqual(len1+1,len2)
        
        A1=entry1.item('A')
        A2=entry2.item('A')
        self.assertEqual(A1+'_COPY',A2)
        
        data_ref1=dssc.get_data_reference(entry1)
        data_ref2=dssc.get_data_reference(entry2)
        
        # Those two dataferfence should have same time extent.
        self.assertEqual(data_ref1.extent,data_ref2.extent)

        # Make time window smaller to speed up
        extent="time_window=(12/1/1991 03:45,12/24/1991 01:30)"
        data_ref1.extent= extent
        data_ref2.extent= extent        
        data1=self.dss_service.get_data(data_ref1)
        data2=self.dss_service.get_data(data_ref2)
        
        for (d1,d2) in zip(data1.data,data2.data):
            self.assertEqual(d1,d2)
        for (t1,t2) in zip(data1.ticks,data2.ticks):
            self.assertEqual(t1,t2)

        # Test remove the new entry.
        dssc.remove(entry2)
        self.assertTrue(entry2 not in dssc.entries())

        # Try to get data from based on new datareference
        # , service should raise exception.        
        self.assertRaises(DssAccessError,\
                          self.dss_service.get_data,data_ref2)
                
    def test_modify(self):
##
##        import pdb
##        pdb.set_trace()
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)        

        for entry in dssc.entries():
            new_entry=copy(entry)
            A=new_entry.item('A')
            A=A+'_MODIFIED'
            new_entry.set_item('A',A)
            dssc.modify(entry,new_entry)
            
        for newentry in dssc.entries():
            dataref=dssc.get_data_reference(newentry)
            self.assertTrue('_MODIFIED' in dataref.selector)
            
    def test_filter_catalog(self):
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        selector="/HIST*/SLTR*/*//15MIN/*/"
        dl=dssc.filter_catalog(selector)
        self.assertEqual(type(dl),DssCatalog)
        self.assertEqual(len(dl),3)
                
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/"        
        dl=dssc.filter_catalog(selector)
        self.assertEqual(type(dl),DssCatalog)
        self.assertEqual(len(dl),1)
        
        ## this selector has a trailing space intentionally, I made it still correct by stripping the space.
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/ "       
        dl=dssc.filter_catalog(selector)
        self.assertEqual(type(dl),DssCatalog)
        self.assertEqual(len(dl),1)
        
        selector="nothing here "      
        self.assertRaises(ValueError,dssc.filter_catalog,selector)
        
        ## this selector intentionaly misses last backslash, it should report error
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER"    
        self.assertRaises(ValueError,dssc.filter_catalog,selector)
        
    def test_filter_catalog2(self):
        
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        selector="F=DWR*"
        dl=dssc.filter_catalog(selector)
        self.assertEqual(type(dl),DssCatalog)
        self.assertEqual(len(dl),7)
                
    def test_filter_catalog_dot_bug(self):
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        selector="B.SLTMP017,F=USGS-RIM"
        dl=dssc.filter_catalog(selector)
        self.assertEqual(len(dl),1)      
        

    def test_data_references(self):
        
        dssfile_path=self.test_file_path
        dssc=self.dss_service.get_catalog(dssfile_path)
        selector="/HIST*/SLTR*/*//15MIN/*/"
        range="(10/2/1997 1200, 7/4/1998 1315)"
        dl=dssc.data_references(selector,range)
        numd=0
        for d in dl:
            self.assertEqual(type(d),DataReference)
            numd=numd+1
        self.assertEqual(numd,3)

        range=("10/2/1997 12:00", "7/4/1998 13:15")
        dl=dssc.data_references(selector,range)
        numd=0
        for d in dl:
            self.assertEqual(type(d),DataReference)
            numd=numd+1
        self.assertEqual(numd,3)

        range=(datetime(1997,10,2,12), datetime(1998,7,4, 13,15))
        dl=dssc.data_references(selector,range)
        numd=0
        for d in dl:
            self.assertEqual(type(d),DataReference)
            numd=numd+1
        self.assertEqual(numd,3)        
        
        selector="/HIST+CHAN/SLTMP017/STAGE//15MIN/DWR-CD-SURFWATER/"        
        dl=dssc.data_references(selector)
        numd=0
        for d in dl:
            self.assertEqual(type(d),DataReference)
            numd=numd+1
        self.assertEqual(numd,1)
 
if __name__=="__main__":
    
    unittest.main()          

        
        

    
                    




        

                 

    
    
