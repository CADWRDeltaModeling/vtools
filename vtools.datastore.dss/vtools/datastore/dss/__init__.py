try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

def make_plugin():
    from dss_service import DssService

## submerge those boring warnings from hdf tables
from warnings import filterwarnings
filterwarnings("ignore")