
from enthought.envisage.repository.template_repository_root_factory import TemplateRepositoryRootFactory

class BuiltInRootFactory(TemplateRepositoryRootFactory):
    name = 'Vtools Data Repository'
    
    path = '.'
    
    class_name = 'vtools.datastore.plugin.root_factories.BuiltInRootFactory'
    
    def roots(self):  
       
        ret = super(BuiltInRootFactory, self).roots()
        
        return ret