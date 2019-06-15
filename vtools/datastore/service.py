import sys

from .data_access_service import DataAccessService,DataAccessError
from .catalog_service import CatalogService



class Register(type):
  """A tiny metaclass to help classes register themselves automagically"""
  
  def __init__(cls, name, bases, dict):      
    
    if ('register' in dict): # initial dummy class
      setattr(cls, 'register', staticmethod(dict['register']))
    elif (getattr(cls, 'DO_NOT_REGISTER', 0)):
      # we don't want to register this non-concrete class      
      delattr(cls, 'DO_NOT_REGISTER')
    elif (object not in bases):
      cls.register(name, cls)
    return


class Service(DataAccessService,CatalogService, metaclass=Register):

    all_service={}
    identification="vtools.datastore.ui.service"

    def factory(identification):

        if identification in list(Service.all_service.keys()):
            return Service.all_service[identification]
        else:
            raise ValueError(identification +" is not a type registed")

    factory=staticmethod(factory)

    def register(name,cls):
        identification=getattr(cls,"identification")
        Service.all_service[identification]=cls


def get_data(catalog_entry):

    catalog=catalog_entry.catalog
    data_reference=catalog.get_data_reference(catalog_entry)

    id=data_reference.source_type_id
    data_service=Service.all_service[id]()

    ts=data_service.get_data(data_reference)
    return ts
    
    


     

      
      
      
      

        



        
