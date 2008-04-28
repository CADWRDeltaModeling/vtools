
# system import
import pdb
from string import upper

# enthought specific imports
from enthought.traits.api import List,Str,HasTraits
from enthought.traits.ui.view import View 
from enthought.traits.ui.group import Group
from enthought.traits.ui.item import Item
from enthought.traits.ui.editors import TableEditor
from enthought.traits.ui.table_column \
    import ObjectColumn    
from enthought.traits.ui.table_filter \
    import TableFilter, RuleTableFilter, RuleFilterTemplate, \
           MenuFilterTemplate, EvalFilterTemplate
from enthought.traits.ui.menu \
    import NoButtons  
	
# Vtools import
from vtools.datastore.catalog import Catalog

# Local import
from table_editor import VTToolkitEditorFactory


########################################################################### 
# helper function.
###########################################################################

def _get_non_id_and_extent_rolename_list(schema):
    """ Get the name of roles that are not identity
        from schema.
    """
    rolename_list=[]
    
    for val in schema:
        rolename=getattr(val,"role")
        if not(rolename=="identification") and \
           not(rolename=="extent") and \
           not(rolename in rolename_list):
            rolename_list.append(rolename)

    return rolename_list

def _get_extent_group(schema=None):
    """ Generate data extent items group."""

    columns=[ObjectColumn(name='name',label='scale_name',editable=False)]

    table_editor = TableEditor(columns= columns,\
    editable=False,deletable=False,sortable=False,\
    show_lines=False,orientation='horizontal',\
    edit_view='object.traits_view',\
    show_column_labels=True,\
    configurable = False)
    
    item=Item("_dimensions",editor=table_editor)
    #item=Item("_dimensions")
    
    group=Group(item,'|[]<>')
    return group


def _create_catalogentry_editor(catalogadapter):

    """ Create the editor view for a catalogentry to be viewed
        on catalog GUI.

        Input:
           catalogadapter: catalog object going to be shown.

        Output:
           a trait editor view.
    """

    groups=[]
##    schema=catalogadapter.schema()
##    role_list=_get_non_id_and_extent_rolename_list(schema)
##
##
##    for role in role_list:
##
##        ## Retrieve all attributes with this role
##        item_list=[]
##        for val in schema:
##            rolename=getattr(val,"role")
##            elementtype=getattr(val,"element_type")
##            ## if this attribute has same role,add it
##            ## to this group.
##            if rolename==role and not(elementtype=="dimension"):
##                # Get this item editing style
##                if hasattr(val,"editable"):
##                    editable=getattr(val,"editable")
##                else:
##                    if rolename=="extent":
##                        editable=True
##                    else:
##                        editable=False
##                        
##                if not(editable):
##                    style="readonly"
##                else:
##                    style="simple"
##                    
##                item_list.append(Item(getattr(val,"name"),style=style))
##                
##        group=Group(item_list, '|[]>',label=role,show_border=True)        
##        groups.append(group)

    extent_group=_get_extent_group()
    groups.append(extent_group)
    groups.append('-<>')
    entry_view=View(groups,undo=False,revert=False,\
                help=False,resizable = True,dock='horizontal')
                     
    return entry_view

def _generate_table_columns(schema):

    """ Generate identity column names according to schema. """
           
    if schema is not None:
        columns=[]
        for item in schema:
            name=item.get_element('name')
            role=item.get_element('role')
            
            if role=="identification":
                if item.has_element("editable"):
                    editable=item.get_element("editable")
                else:
                    editable=False
                column=ObjectColumn(name=name,label=upper(name),\
                                    editable=editable)
                columns.append(column)
        return columns

def create_catalog_editor_view(catalog):

    """ This func create a customized table view of
        a catalog.
    """
    ## First get the editor view for each entry.
    entryview=_create_catalogentry_editor(catalog)
    ## Built table column for entry attributes with identity role.
    columns=_generate_table_columns(catalog.schema())
    
    table_editor = VTToolkitEditorFactory(columns= columns,\
    editable=True,deletable=True,sortable=True,\
    sort_model=True,show_lines=True,orientation='vertical',\
    show_column_labels=True,edit_view=entryview)

    traits_view = View(
    [Item('_entries',id='entries',editor=table_editor),'|[]<>'],
    dock='vertical',resizable=True,buttons=NoButtons,\
    kind='live',height=0.2)

    ##   traits_view = View(
    ##    [Item('adaptedentries',id='entries',editor = table_editor),\
    ##      '|[]<>' ],\
    ##    id='vtools.datastore.ui.catalog_adapter.catalog_view',\
    ##    dock='vertical',resizable=True,buttons=NoButtons,\
    ##    kind='live',height=0.2)

    return traits_view

    
    

    
    

    


        

    

    

    

    

    

