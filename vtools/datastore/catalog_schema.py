class CatalogSchemaItem(object):
    """ Class stores the definition for catalog entry item.  """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self,attr_dict=None):
        """ CatalogShemaItem can be initialized by optional element difinition
            dictionary.
        """

        from string import rstrip
        self.user_attrname=[]
        self.description="["
        
        if attr_dict:
            if not(type(attr_dict)==dict):
                raise TypeError("Inappropriate argument type \
                                in initializing CagalogSchemItem")         
            for (attr,value) in list(attr_dict.items()):
                setattr(self,attr,value)
                self.description=self.description+attr+"="+str(value)+","
                self.user_attrname.append(attr)
                
##        if not (hasattr(self,"show")):
##            ## to control if the metaitem should be shown or not
##            setattr(self,"show",True)
            
        self.description=rstrip(self.description,",")   
        self.description=self.description+"]\n"

    def __str__(self):
        """ This function generate a string representation of class instance.
        """
        
        return self.description
        
    ###########################################################################
    # 'CatalogSchemaItem' interface.
    ###########################################################################

    def append_element(self,element_name,value):
        """ This function append a definition element to exist list.

        element_name is the string name of definition, value is the
        context of the definition, this function preclude user to reset
        any existing element values.
        """
        
        from string import replace
        
        if not (element_name in self.user_attrname):
            setattr(self,element_name,value)
            self.user_attrname.append(element_name)
            des=element_name+"="+str(value)+"]"
            self.description=replace(self.description,"]",des)
        else:
            raise ValueError("%s already exist"%element_name)

    def get_element(self,element_name):
        """ This function return a definition element based on name given.

        element_name is the string name of definition.
        """
        
        if element_name in self.user_attrname: 
            return getattr(self,element_name)
        else:
            raise AttributeError("%s don't exist"%element_name)

    def has_element(self,element_name):
        """ Function to check if element_name exist in this schema item"""

        if element_name in self.user_attrname: 
            return True
        else:
            return False
        


