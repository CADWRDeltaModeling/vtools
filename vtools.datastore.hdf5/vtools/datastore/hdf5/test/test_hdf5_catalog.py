import sys,os,unittest,shutil #,pdb

from vtools.datastore.hdf5.hdf5_service import HDF5Service
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.hdf5.hdf5_catalog import HDF5Catalog
from vtools.datastore.data_reference import DataReference

class TestHDF5Catalog(unittest.TestCase):

    """ test functionality of hdf5service """


    def __init__(self,methodName="runTest"):

        super(TestHDF5Catalog,self).__init__(methodName)
        self.test_file_path='hist.h5'
        self.test_file_path=os.path.abspath(self.test_file_path)
        self.backup_hdf_file=os.path.abspath('./backup/hist.h5')
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.hdf5_service=self.servic_emanager.get_service("vtools.datastore.hdf5.HDF5Service")

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        shutil.copy(self.backup_hdf_file,self.test_file_path)    
        
    def tearDown(self):
        pass

    def test_get_data_reference(self):        
        hdfile_path=self.test_file_path
        
        
        hfc=self.hdf5_service.get_catalog(hdfile_path)
        catalog=hfc

        for entry in catalog:
            dataref=catalog.get_data_reference(entry)
            self.assertEqual(type(dataref),DataReference)

    def test_filter_catalog(self):

        path="/hydro/data/channel flow"
        hdfile_path=self.test_file_path
        hfc=self.hdf5_service.get_catalog(hdfile_path)
        c1=hfc.filter_catalog(path)
        self.assertEqual(type(c1),HDF5Catalog)
        self.assertEqual(len(c1),1)

    def test_data_references(self):
        
        path="/hydro/data/channel flow"
        extent="channel_number=1;channel_location=upstream"
        time_window="time_window=(2002-5-10 12:00,2002-5-29 13:00);"
        extent=time_window+extent
        hdfile_path=self.test_file_path
        hfc=self.hdf5_service.get_catalog(hdfile_path)
            
        ref=hfc.data_references(path,extent).next()
        
        self.assertEqual(type(ref),DataReference)
        
        self.assertEqual(ref.selector,"/hydro/data/channel flow")
        self.assertEqual(ref.extent,extent)
        ts=self.hdf5_service.get_data(ref)        
                
if __name__=="__main__":
    
    unittest.main()   
    

        

            

    
                    




        

                 

    
    
