""" Functions to translate between different data references."""

#import pdb

## vtools import.

__all__=["translate_references"]

########################################################################### 
## Public interface.
###########################################################################

def translate_references(s1,references,s2,destination,translation=None):
    """ Translate a number of datareferences (which usually point
        to the location of a different data source, for the moment
        same type of data source assumed) to the references points
        to the locations within the current data source (one to one).

        input:
           s1: service for input references.
           references: list of data references.
           s2: service for input destination.
           destination: full path to detination data source,string.
           scenario of translation:                        
        output:
            a list of new references.
        To do:
           Implement translation between different data source.           
    """
    nr=[]
    pre_sel=None
    for ref in references:
        ref_elements=s1.dissect(ref)
        new_dic={}
        new_dic["dest"]=destination
        new_dic["ref_dic"]=ref_elements
        new_dic["pre_sel"]=pre_sel ## it is here only for the usage of excel
                                   ## for the time being, for excel assembling
                                   ## needs to know location of its immediate
                                   ## previous ts if a number of ts is saving
                                   ## into spreadsheet.
        new_ref=s2.assemble(translation,**new_dic)
        nr.append(new_ref)
        pre_sel=new_ref.selector

    return nr

