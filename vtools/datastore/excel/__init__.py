
try:
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

    
def make_plugin():
    from .excel_service import ExcelService