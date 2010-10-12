import sys,os,unittest,shutil
import pdb

from vtools.datastore.hdf5.hdf5_service import HDF5Service
from vtools.datastore.data_service_manager import DataServiceManager
from vtools.datastore.hdf5.hdf5_catalog import HDF5Catalog
from vtools.datastore.dimension import RangeDimension
from vtools.data.timeseries import TimeSeries

from datetime import datetime

class TestHDF5Service(unittest.TestCase):

    """ test functionality of hdf5service """


    def __init__(self,methodName="runTest"):

        super(TestHDF5Service,self).__init__(methodName)
        self.test_file_path='hist.h5'
        self.test_file_path=os.path.join(os.path.split(__file__)[0],self.test_file_path)
        self.backup_hdf_file=os.path.join(os.path.split(__file__)[0],'./backup/hist.h5')
        
    def setUp(self):
        self.servic_emanager=DataServiceManager()
        self.hdf5_service=self.servic_emanager.get_service("vtools.datastore.hdf5.HDF5Service")

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        shutil.copy(self.backup_hdf_file,self.test_file_path)
        
    def tearDown(self):
        pass

    def test_get_catalog(self):

        
        hdfile_path=self.test_file_path
        hfc=self.hdf5_service.get_catalog(hdfile_path)

        self.assert_(type(hfc)==HDF5Catalog)

        self.assert_(hasattr(hfc.schema(),'__iter__'))
        self.assertEqual(len(hfc.entries()),8)

        for item_schema in hfc.schema():
            self.assert_( item_schema.has_element('name'))

        for entry in hfc.entries():            
            for item_schema in hfc.schema():
                self.assert_(entry.item(item_schema.name))
            for dimensionscale in entry.dimension_scales():
                if type(dimensionscale)==RangeDimension:
                    range=dimensionscale.get_range()
                    self.assert_(type(range[0]),datetime)
                    self.assert_(type(range[1]),datetime)
            #print len(entry.dimensions())
                
    def test_get_data(self):


        hdfile_path=self.test_file_path
        hfc=self.hdf5_service.get_catalog(hdfile_path)

        catalog=hfc

        for entry in catalog.entries():
            dataref=catalog.get_data_reference(entry)
            data=self.hdf5_service.get_data(dataref)
            self.assert_(type(data),TimeSeries)
            self.assertEqual(len(data),475)

if __name__=="__main__":
    
    unittest.main()          

        

            

    
                    




        

                 

    
    
