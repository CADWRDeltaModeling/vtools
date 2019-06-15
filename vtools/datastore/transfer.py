""" Transfer and transform data from one source to another
    This module provides functionality for opening one data
    source,grabbing data that matches selecting criteria,
    transforming it or clipping it in time and then exporting
    it to another data source.

    usage: transfer [options]
      -i, --in=input: data store of orginal data records.
      -s, --selector=select: selection criteria of input data.
      -o, --out=output: data store where data will be written.
      -d, --dest=dest: optional,map from selector to the output location in the output data store.
      -t, --trans=transformer:  optional,path to the tranformation func to be applied.
      -e, --extent=extent: optional, extent within a selected time series.
      -u, --usage: help info.
"""
## python import
import sys,types#,pdb
import os.path
from copy import deepcopy

from vtools.datastore.dss.api import *
from vtools.datastore.dss.dss_service import *
from vtools.datastore.transfer import *


## local import
from vtools.datastore.dss.dss_service import *
from vtools.datastore.excel.excel_service import *
from .data_service_manager import DataServiceManager
from .service import Service

from .translate import *
from .group import *
from .optionparse import parse




## vtools import
#from vtools.debugtools.timeprofile import debug_timeprofiler
__all__=["transfer","batch_transfer"]




for plugin in  __import__('pkg_resources').iter_entry_points(group="vtools.datastore",name=None):
    try:
        pe=plugin.parse(str(plugin))
        pe.load(False)
        
    except Exception as e:
        raise ImportError("fail to load required data source service plugin %s due to %s"%(str(plugin),str(e)))


########################################################################### 
## Public interface.
###########################################################################

def batch_transfer(source,dest=None,selector=None,extent=None\
                   ,mapper=None,transform=None,**func_args):
    """
       Batch transfer selected time series from data source1 to source2, 
       with optional transformation operation
       on orginal data series.

       usage: batch_transfer(source1,selector1,source2,selector2,transform,**func_args):       
       input:
          source: path to source  (full path or relative path).
          dest: path to destination of transfer (full path or relative path). 
          selector: selection criteria for source1, given as string.
          extent: data extent selection for source1.
          mapper: selection seting for source2, given as string, it 
                     is translation for the moment(thus no support for transfer
                     to exsiting paths in exisiting data source available yet).

                     
          optional input:

          transform: transforming operation function,can be as full path
                     string of existing function provided by vtools package,
                     ,etc. "vtools.functions.data_interpolate.interpolate_its
                     _rts" or a function object defined by user.
          **func_args: arguments dic for transform function.
        output:
           None.
    """

    ds=DataServiceManager()
    s1=None

    if not dest:
      raise ValueError("input dest should not be None")

    if os.path.isfile(source):
       source=os.path.abspath(source)

    if os.path.isfile(dest):
       dest=os.path.abspath(dest)
      
    s1=_service(source,ds)
    s2=_service(dest,ds)

    if not s1:
      raise ValueError("Invalid source")

    if not s2:
      raise ValueError("Invalid destination")

      
    c1=s1.get_catalog(source)
    try:
      data_ref1=[rf for rf in c1.data_references(selector,extent)]
    except NotImplementedError as e:
      raise ValueError("Batch transfer timeseries from"
                       "this type of source is not supported yet.")
    
    if not data_ref1:
      print(" Warning:selection criteria "\
       "return no data records from source "\
       "no transfer was done.")
      return
      
    data_ref2=translate_references(s1,data_ref1,\
    s2,dest,mapper)

    if not len(data_ref2)==len(data_ref1):
      raise ValueError("Incorrect destination location mapper,which"
                       "can't built correct one to one mapping from"
                       "source to destination")

    ##### time profile ####
    #debug_timeprofiler.mark("begin transfer")
    ######################
    transfer(s1,data_ref1,s2,data_ref2,transform,**func_args)
    ##### time profile ####
    #print 'total time in transfer',debug_timeprofiler.timegap()
    ######################  
    
        
def transfer(s1,reference1,s2,reference2,transform=None,**func_args):
    """
       Transfer time series data pointed by reference1 to location
       refered by reference2, with optional transformation operation
       on orginal data series.

       input:
          reference1: instance/list of data reference class of orginal data.
          reference2: instance/list of data reference class of new data.
          transformfunc: transforming operation function,can be as full path
                         string of existing function provided by vtools package,
                         ,etc. "vtools.functions.data_interpolate.interpolate_its
                         _rts" or a function object defined by user.
          **func_args: arguments dic for transform function.
        output:
           None.
    """
    ds=DataServiceManager()
    if not(type(reference1)==type([1])):
      reference1=[reference1]

    if not(type(reference2)==type([1])):
      reference2=[reference2]

    ## it is assumed each data_reference ensemble only contain
    ## data references point to same type of data source, but
    ## may different with each other.
        

    transtime=0.
    writetime=0.

    for d1,d2 in zip(reference1,reference2):
      try:
        dt=s1.get_data(d1)
      except:
        raise Exception("Failed to retrieve data pointed to by %s"%d1.selector)
      ts_groups =[]
      if "compress_size" in list(func_args.keys()):
          compress_size = func_args["compress_size"]
          ts_groups = ts_group(dt,compress_size)
      else:
          ts_groups=[dt]

      for a_dt in ts_groups:
          try:
              ts=_transform(a_dt,transform,**func_args)
          except:
              raise Exception("Failed to transform input timeseries" )
          try:
              s2.add_data(d2,ts)
          except:
              raise Exception("Failed to add new data into path %s in dest %s"%(d2.selector,d2.source))
    return

########################################################################### 
## Private interface.
###########################################################################

def _service(source,ds):
   """ return a service based on the source given.
   """
   s1=None
   for cls in list(Service.all_service.values()):
      if cls.serve(source):
         s1=cls()
         break
   return s1

def _transform(d1,transform=None,**func_args):
    """ internal function do the work of get and transform one ts.
        
    """
    ##d1=s1.get_data(r1)
    ## function given by full path within vtools
    ## or other packages.
    if type(transform)==type("fun"):
        func=_get_func(transform)
        nd=func(d1,**func_args)
    ## or function given as a function object.
    elif callable(transform):
        nd=transform(d1,**func_args)
    elif (transform is None):
        #nd=deepcopy(d1)
        return d1
    else:
        raise ValueError("Input transform function is invalid.")

    return nd

##def _transfer(r2,s2,nd):
##    """ Internal function finishes the real tasks of transfer."""
##
##    if len(r2)==len(nd):
##       for rt2,ndt in zip(r2,nd):
##          s2.add_data(rt2,ndt)
##    elif len(r2)==1:
##       if hasattr(s2,'batch_add'):
##          s2.batch_add(r2[0],nd)
##       else:
##          raise ValueError("Unsupported ts transfer setting")
##    else:
##       raise ValueError("Unsupported ts transfer setting")
    
                    
## function code from ASPN.
    
def _get_mod(modulePath):
    try:
        aMod = sys.modules[modulePath]
        if not isinstance(aMod, types.ModuleType):
            raise KeyError
    except KeyError:
        # The last [''] is very important!
        aMod = __import__(modulePath, globals(), locals(), [''])
        sys.modules[modulePath] = aMod
    return aMod

def _get_func(fullFuncName):
    
    """Retrieve a function object from a full dotted-package name."""
    
    # Parse out the path, module, and function
    lastDot = fullFuncName.rfind(".")
    funcName = fullFuncName[lastDot + 1:]
    modPath = fullFuncName[:lastDot]
    
    aMod = _get_mod(modPath)
    aFunc = getattr(aMod, funcName)
    
    # Assert that the function is a *callable* attribute.
    assert callable(aFunc), "%s is not callable." % fullFuncName
    
    # Return a reference to the function itself,
    # not the results of the function.
    return aFunc

################# command line application #####################
def main():   
   

   opt,otherarg=parse(__doc__)

   if (not opt) or getattr(opt,"usage"):
      print(""" 
                  Transfer and transform data from one source to another
                  This module provides functionality for opening one data
                  source,grabbing data that matches selecting criteria,
                  transforming it or clipping it in time and then exporting
                  it to another data source.

                  usage: transfer -i input -s select -o out [-d dest] [-e extent] [-t transformer]
                  -i, --in=input: data store of orginal data records.
                  -s, --selector=select: selection criteria of input data.
                  -o, --out=output: data store where data will be written.
                  -d, --dest=dest: optional,map from selector to the output location in the output data store.
                  -e, --extent=extent: optional, extent within a selected time series, such as a time window
                                       (6/26/1929 12:00,12/9/1940 12:00).
                  -t, --trans=transformer:  optional, path to the tranformation func to be applied.
                                           can be a full path string of existing function
                                           provided by vtools package,
                                           ,etc. vtools.functions.data_interpolate.interpolate_its
                                           or a function defined by user,etc. 
                                           mypackage.mymodule.myfunctions or mymodule.myfunctions
                  
                  Instance of typical usages:

                    copying all timeseries whose C part is "flow" in
                    file a.dss to a new file b.dss within time window of (4/26/2001 09:30 to 08/30/2004 11:40)
                    with application of Godin filtering:
                  
                    transfer -i a.dss -s C=FLOW -o b.dss -e (4/26/2001T09:30,08/30/2004T11:40) -t vtools.functions.api.godin
                    
                    copying all timeseries whose C part is "flow" in
                    file a.dss to a new file b.dss within time window of (4/26/2001 09:30 to 08/30/2004 11:40)
                    with application of ond day averaging:
                    
                    transfer -i a.dss -s C=FLOW -o b.dss --extent (4/26/2001T09:30,08/30/2004T11:40) 
                    -t vtools.functions.api.period_ave interval=1day
                  
               """)
      return 
     
   if not hasattr(opt,"in"):
      raise ValueError("no source option is given.")

   if not hasattr(opt,"out"):
      raise ValueError("no destination option is given.")

   if not hasattr(opt,"selector"):
      raise ValueError("no source selection option is given.")

   if not hasattr(opt,"dest"):
      raise ValueError("no destination selection option is given.")

   source=getattr(opt,"in")
   dest=getattr(opt,"out")
   sel1=getattr(opt,"selector")
   sel2=getattr(opt,"dest")

   if hasattr(opt,"trans"):
      trans=getattr(opt,"trans")
   else:
      trans=None
   
   #(transname,varlst)=parse_func_args(trans)   
   transname=trans
   varlst=parse_func_args(otherarg)
   
   if hasattr(opt,"extent"):
      ext=getattr(opt,"extent")
   else:
      ext=None      
   print(source)
   print(dest)
   print(sel1)
   print(ext)
   batch_transfer(source,dest=dest,selector=sel1,extent=ext\
                   ,mapper=sel2,transform=transname,**varlst)
                   
def parse_func_args(arg):
    
   #import re
   #al=re.compile("(.+?)\((.+?)\)")
    
   vardic={}

   if arg:
      for ele in arg:
         if "=" in ele:
            elelst=ele.split("=")
            vardic[elelst[0]]=elelst[1]
                
                                
   return vardic


if __name__=='__main__':
    main()


