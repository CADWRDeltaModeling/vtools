



# Standard libary imports.
import pdb

# Enthought library imports.
from enthought.pyface import SplitPanel
from enthought.pyface.grid import Grid, TraitGridModel, SimpleGridModel, \
     GridRow, GridColumn, TraitGridColumn
from enthought.traits import Float, Str,List,Any,Trait,Instance,Color,\
     Bool,HasTraits,Int,Enum


# vtools import.

class CatalogGridPanel(SplitPanel):

    """ Container visiualizing catalog entrise of datasource in grids"""
    ########################################################################### 
    # private traits.
    ###########################################################################

    ## Bookkeeping a number of non identity models .
    _subdata_models=List(TraitGridModel)
    ## Bookkeeping one identity model.
    _identity_model=Trait(TraitGridModel)

    
    ########################################################################### 
    # 'object' interface.
    ###########################################################################

    def __init__(self,models,parent,**traits):

        """ CatalogGrid Panel must be initailized by a number of grid models,
            among them, one must be identity model.
        """

        for m in models:
            if m.name=="identity":
                self._identity_model==m
                models.remove(m)
                
        self._subdata_models=models

        ## Base class constructor.       
        super(CatalogGridPanel,self).__init__(parent,traits)

    ########################################################################### 
    # Protected interface.
    ###########################################################################

    def _create_lhs(self, parent):
       
       identity_grid=Grid(parent,model=self._identity_model) 
       return identity_grid.control
    
    def _create_rhs(self, parent):

       junk_grid=Grid(parent,model=self._identity_model)
       return junk_grid.control
    

    ########################################################################### 
    # Private interface.
    ###########################################################################

    
