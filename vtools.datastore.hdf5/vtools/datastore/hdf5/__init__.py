
try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

def make_plugin():
    from hdf5_service import HDF5Service

## submerge those boring warnings from hdf tables
from warnings import filterwarnings
filterwarnings("ignore")