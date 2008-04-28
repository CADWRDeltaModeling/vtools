
## python import
import os.path
import pdb
import copy

##scipy import
from scipy import zeros,string_

## pytable import.
import tables

# vtools import
from vtools.datastore.service import Service
from vtools.datastore.catalog_schema import CatalogSchemaItem
from vtools.datastore.catalog import CatalogEntry
from vtools.datastore.dimension import ChannelDimension
from vtools.datastore.dimension import RangeDimension
from vtools.data.timeseries import rts,its
from vtools.data.vtime import parse_interval,number_intervals,\
     time_sequence,parse_time,increment,ticks_to_time
from vtools.data.timeseries import TimeSeries
from vtools.datastore.data_reference import *

# local import 
from hdf5_catalog import HDF5Catalog
from hdf5_catalog_service_error import HDF5CatalogServiceError
from hdf5_access_error import HDF5AccessError
from hdf5_constants import *

__all__=["HDF5Service"]

def process_array_val(val):
    """ Coerce array of size 1 readed
    from a hdf5 file as single value
    """    
    ## remove this part for py2.5
    ##if type(val)==CharArray:
    ##    val=val.tolist()[0]
    ##    return val
    ##elif type(val)==NumArray and len(val)==1:
    ##    return val[0]
    if type(val)==type(zeros(2)) and len(val)==1:
        return val[0]
    else:
        return val

## those attr should not be treated as usual meta data
_NOT_USUAL_ATTR=["start_time","interval","CLASS",\
                 "DIMENSION_LIST","DIMENSION_LABELS",\
                 "DIMENSION_PATH"]
                 
                 
## hardwared dimension_sacle map for dataset nodes, used for dsm2 tide file
_DIMENSION_SACLE_MAP={"channel area":[("channel_location",1),("channel_number",2)],
                      "channel avg area":[("channel_number",1)],
                      "channel flow":[("channel_location",1),("channel_number",2)],
                      "channel stage":[("channel_location",1),("channel_number",2)],
                      "qext changed":[("external_flow_names",1)],
                      "reservoir flow":[("connection",1),("reservoir_names",2)],
                      "reservoir height":[("reservoir_names",1)],
                      "transfer flow":[("transfer_names",1)]
                      }
_DIMENSION_SCALE_PATH="/hydro/geometry/"
_DIMENSION_SACLE_NAME=["channel_location","channel_number","external_flow_names","connection",\
"reservoir_names","transfer_names"]

class HDF5Service(Service):
    """ Service class to retrieve catalog and accsse timeseries
        stored in a hdf5 file. 
    """

    ## static method to decide whether a source can be served.

    def serve(source):

        return source.lower().endswith('.h5')

        
    serve=staticmethod(serve)
    
    # ID of service type
    identification=HDF5_DATA_SOURCE

    ########################################################################### 
    # Protected interface.
    ########################################################################### 

    def _get_catalog(self,hdf5_file_path):
        """ return catalog based on the file name given,
            return a list of catalog if more than one views are defined in hdf5 file
        """
        catalog_list=[]
        fileh=tables.openFile(hdf5_file_path,mode='a')
        #retrieve defined schema for views as a list of tuple from file
        schema=self._gen_schema(fileh)
        dimension_scales=self._retrieve_dimension_scales(fileh)
        entries=self._retrieve_meta_entries(fileh,schema,dimension_scales)
        hdf5_catalog=HDF5Catalog(hdf5_file_path,schema,self,entries)
        fileh.close()  
        return hdf5_catalog

    def _get_data(self,dataref):        
        """ Given a datafererence return a time series."""
                        
        (array,fh)=self._get_array_node(dataref)
        (index_extents,time_seq)=self.\
        _parse_extents(dataref.extents(),array)
        parameter=self._compose_array_parameter(index_extents)
        data=array[parameter]

        props={}##populate ts attr dic
        for attrname in array.attrs._v_attrnamesuser:
            if not attrname in _NOT_USUAL_ATTR:
                val=getattr(array.attrs,attrname)
                val=str(process_array_val(val))
                props[attrname]=val

        if hasattr(array.attrs,"interval"):
            interval=getattr(array.attrs,"interval")
            interval=str(process_array_val(interval))
            interval=parse_interval(interval)
            start=time_seq[0]
            start=ticks_to_time(start)
            ts=rts(data,start,interval,props)
        else:
            ts=its(time_seq,data,props)
        
        fh.close()
        return ts


    def _modify_data(self,dataref,ts):
        """ Modify dataset with a time series at location pointed by 
        datareference.
        """
        self._check_data_reference(dataref)
        (array_node,fh)=self._get_array_node(dataref)
        para=self._compose_array_para(dataref.extent)        
        array_node[para]=ts.data
        fh.close()

##    def _add_data(self,dataref,data):
##        """ Add a time series to place pointed by datareference."""
##        
##        self._check_data_reference(dataref)
##        (array_node,fh)=self._get_array_node(dataref)
##        para=self._compose_array_para(dataref.extent) 
##        array_node.append(data)
##        fh.close()
        
    def _check_data_reference(self,dataref):
        """ Check validility of a data reference"""
        
        if not(dataref.source_type_id==HDF5_DATA_SOURCE):
            raise HDF5AccessError("wrong type of data reference used when \
            trying to access HDF5 data")

        if not(dataref.selector):
            raise HDF5AccessError("empty path in data reference used when \
            trying to access HDF5 data")

        if not(dataref.extent):
            raise HDF5AccessError("empty extent in data reference used when \
            trying to access HDF5 data")

    ########################################################################### 
    # Private interface.
    ########################################################################### 
        
    def _gen_schema(self,fileh):
        """ Function to create definition of catalog schema,
            fileh is HDF5 tables.file instance.
        """
        schema=[]

        schema_item=CatalogSchemaItem({"name":"path",\
        "role":"identification","element_type":"path"})
        schema.append(schema_item)
        schema_item=CatalogSchemaItem({"name":"data_extent",\
        "role":"extent","element_type":"dimension_scale"})
        schema.append(schema_item)          
        schema_item=CatalogSchemaItem({"name":"data_attr",\
        "role":"attribute","element_type":"attribute"})                
        schema.append(schema_item)
            
        return schema

    def _retrieve_dimension_scales(self,fileh):
        """ retrieve all the dimension scales stored in
            fileh and return it as dic.

            To do, may change in future when dimension
            -scale is supported by python hdf tables.
        """

        scales={} ## key is path to reference node
                  ## values is tuple of scale and
                  ## dimension index.
          
        nl= fileh.walkNodes("/",classname="Array")   
              
        for node in nl:  
            # if hasattr(node.attrs,"CLASS"):
                # c=node.attrs.CLASS
                # c=process_array_val(c)
                # c=c.strip()
                #if c==HDF_DIMENSION_SCALE_CLASS:
            if node.name in  _DIMENSION_SACLE_NAME:
                    # path=node.attrs.REFERENCE_PATH
                    # path=process_array_val(path).strip()
                    # str_nodes=node.attrs.REFERENCE_NODE
                    # str_nodes=process_array_val(str_nodes).strip()
                    # str_nodes=str_nodes.split(",")
                    # str_nodes=[path+nd for nd in str_nodes]
                    # dimensions=node.attrs.REFERENCE_DIMENSION
                scale=node.read()
                scales[node.name]=scale
                    # for (di,nd) in zip(dimensions,str_nodes):
                        # if nd in scales.keys():
                            # scales[nd].append((node.name,di,scale))
                        # else:
                            # scales[nd]=[(node.name,di,scale)]
        return scales
                
    
    def _retrieve_meta_entries(self,hdf5f,schema,dimension_scale):
        """ Retrieve meta data entries from hdf5 file based
            on the schema.
        
            hdf5f is pytable hdf5 file handler, schema is a
            list of instances of CatalogSchemaItem
        """
        
        entries=[]
        index=0
        
        for node in hdf5f.walkNodes("/",classname="Array"):
            if hasattr(node.attrs,"CLASS"):
                cc=node.attrs.CLASS
                cc=process_array_val(cc)
                cc=cc.strip()

                if cc==HDF_TS_CLASS:
                    catalog_entry=self._retrieve_node_metadata\
                                   (node,schema,dimension_scale)
                    
                    catalog_entry.index=index
                    entries.append(catalog_entry)
                    index=index+1
        return entries
    
    def _retrieve_node_metadata(self,node,schema,scaledic):
        """"
           retrieve meta data entry just for a data node,
           return it as a CatalogEntry instance
        """
        
        catalogentry=CatalogEntry(schema)
        
        for item_schema in schema: 
                element_type=item_schema.get_element("element_type")
                if element_type=="dimension_scale":
                    scales=self._retrive_node_scales_tide(node,scaledic)
                    if scales:
                        for scale in scales:
                            catalogentry.add_dimension_scale(scale)
                else:
                    meta_entry_item=self._retrieve_entry_item\
                                     (node,item_schema)
                    if type(meta_entry_item)==list:
                        for name,item in meta_entry_item:
                            catalogentry.add_item(name,item)
                            catalogentry.add_trait(name,item) 
                    else:
                        element_name=item_schema.get_element("name")
                        catalogentry.add_item(element_name,\
                                              meta_entry_item)
                        catalogentry.add_trait(element_name,\
                                              meta_entry_item) 

        return catalogentry

             
    def _retrieve_entry_item(self,node,entry_item_schema):

        """ return value of a item within a metadata entry according to its actual schema"""

        try:
            element_type=getattr(entry_item_schema,"element_type")
        except AttributeError,e:
            raise HDF5CatalogServiceError("no element type setting for meta \
            item %s"%(entry_item_schema.name))
        
        if "path" in element_type:
           metaentry_item=self._retrieve_item_by_path(node)
        elif "attribute" in element_type:
           metaentry_item=self._retrieve_item_by_attribute(node)
        else:
            raise HDF5CatalogServiceError("not recognizable element type \
            setting for meta item %s"%attrname)
        return metaentry_item


    def _retrieve_item_by_path(self,node):
        """ This function returns path of data
        node as meta data item
        """
        return node._v_pathname
    
    def _retrieve_item_by_attribute(self,node):
        """ This function return value of a node's
            attribute as list of tuple(attr_name,attr_val).
        """
        lst=[]
        for name in node.attrs._v_attrnamesuser:
            if not (name in _NOT_USUAL_ATTR):
              val=getattr(node.attrs,name)
              val=process_array_val(val)
              lst.append((name,val))
        return lst
        
        
    def _retrive_node_scales_tide(self,node,scale_dic):

        """ This function returns list of dimensions-scale of a node
            (instance of class dimensions) by hardwared dimension-scale
             map.
        """
        name=node.name
         
        if not name in _DIMENSION_SACLE_MAP.keys():
            raise Warning("%s don't have dimension scale defined"%name)
                
        scalelst=_DIMENSION_SACLE_MAP[name]
        scalelst2=copy.deepcopy(scalelst)
        dimension_scales=[]
        gottime=False
        
        avadi=range(len(node.shape))## bookkeeping dimension
                                       ## indexes.
        #pdb.set_trace()
        for (scalename,scaledi) in scalelst:          
            if scalename in scale_dic.keys(): ## common data channels
                scale=scale_dic[scalename]
                dimensionscale=ChannelDimension(scale)
                dimensionscale.name=scalename
                dimensionscale.label=scalename
                dimensionscale.index=scaledi
                dimension_scales.append(dimensionscale)
                scalelst2.remove((scalename,scaledi))
            
        if not gottime: ## if time not given explicity try
                        ## to calculate it form nodes attribute
                        ## setting.
            if len(scalelst2)>0: ## Besides time scale, there are
                             ## some dimension scales not given.
                             ## try to interpret them directly
               
               for (scalename,scaledi) in scalelst2:
                    scale=range(node.shape[scaledi])
                    dimensionscale=ChannelDimension(scale)
                    dimensionscale.name=scalename
                    dimensionscale.label=scalename
                    dimensionscale.index=scaledi
                    dimension_scales.append(dimensionscale)
               
            dimensionscale=self._retrieve_time_scale(node,0)
            dimension_scales.append(dimensionscale)
        #print "scale done with "+node.name 
        return dimension_scales


    def _retrive_node_scales(self,node,scale_dic):

        """ This function returns list of dimensions-scale of a node
            (instance of class dimensions).

            To do: scale_dic is a dic of availble defined
            dimensions scales in hdf file. its keys are
            path to nodes used scales for the moment.
        """

        path=node._v_pathname
        if not path in scale_dic.keys():
            raise Warning("%s don't have dimension\
            scale defined"%path)
                
        scalelst=scale_dic[path]
        dimension_scales=[]
        gottime=False
        
        avadi=range(len(node.shape))## bookkeeping dimension
                                       ## indexes.
        #pdb.set_trace()
        for (scalename,scaledi,scale) in scalelst:
            if scalename==HDF_TIME_SCALE: ## if time extent is
                                          ## given implicitly
                                          ## i.e. irregular ts
                gottime=True
                dimensionscale=RangeDimension((scale[0],scale[-1]),\
                                         label="time_window",\
                                         name=scalename,\
                                         index=scaledi)
                
            else: ## common data channels
                dimensionscale=ChannelDimension(scale)
                dimensionscale.name=scalename
                dimensionscale.label=scalename
                dimensionscale.index=scaledi
            dimension_scales.append(dimensionscale)
            avadi.remove(scaledi)
            
        if not gottime: ## if time not given explicity try
                        ## to calculate it form nodes attribute
                        ## setting.
            if len(avadi)>1: ## Besides time scale, there are
                             ## some dimension scales not given.
                             ## try to interpret them directly
               (t,avadi)=self._interpret_nontime_scale(node,avadi)
               for tt in t:
                   dimension_scales.append(tt) 
               
            dimensionscale=self._retrieve_time_scale(node,avadi[0])
            dimension_scales.append(dimensionscale)
        #print "scale done with "+node.name 
        return dimension_scales
    
    def _interpret_nontime_scale(self,node,avadi):
        """ a tempory way intepret those non time scales. """

        dmap=self._retrieve_scale_map(node)
        t=[]
        for index in avadi:
            if index in dmap.keys():
                if not dmap[index]==HDF_TIME_SCALE:
                    scalename=dmap[index]
                    scaledi=index
                    scale=range(node.shape[index])
                    dimensionscale=ChannelDimension(scale)
                    dimensionscale.name=scalename
                    dimensionscale.index=scaledi
                    t.append(dimensionscale)
                    avadi.remove(index)
        if len(avadi)>1:
            raise HDF5CatalogServiceError(\
                "Some non-time dimension scale of node %s\
                is not given"%node.name)        
        return (t,avadi)
    
    def _retrieve_scale_map(self,node):
        """ try to retrieve a map of dimension labels(scale name)
        and dimension index,temp implementation, may change .

        """

        labels=process_array_val(node.attrs.DIMENSION_LABELS)
        labels=labels.split(",")
        labels=[label.strip() for label in labels ]
        
        indexes=None
        gotindexes=False
        
        if hasattr(node.attrs,'SCALE_INDEXES'):
            indexes=node.attrs.SCALE_INDEXES
            gotindexes=True
            
        if not gotindexes:
            indexes=range(len(labels))
            
        di={}
        for (label,index) in zip(labels,indexes):
            di[index]=label
        return di
                
    def _retrieve_time_scale(self,node,index):
        """ gen time dimension scale based on node
            attribute i.e rts.
        """
        
        num_points=node.shape[index]
        try:
            start_time=process_array_val(node.attrs.start_time)
            interval=process_array_val(node.attrs.interval)
            start_time=parse_time(str(start_time))
            interval=parse_interval(str(interval))

            end_time=increment(start_time,interval,num_points-1)
            dimension=RangeDimension((start_time,end_time),\
                                     label="time_window",
                                     index=index,
                                     interval=interval)
                                     
        except:
            raise HDF5CatalogServiceError(\
                    "Error in retrieve time scale for node %s "%node)
        return dimension
        
        
                
    def _get_group_path(self,path):
        """ Return the parent path of a path
        """
        from os.path import split
         
        if path=="/":
            return path
        else:
            return split(path)[0]

            
    def _get_array_node(self,dataref):
        """ Return the dataset array node referred by
        dataref in hdf5 file"""
        
        hdf5_file_path=dataref.source
        fileh=tables.openFile(hdf5_file_path,mode='a')
        path=dataref.selector       
        try:
            hdfarray=fileh.getNode(path,classname="Array")
            #fileh.close()
            return (hdfarray,fileh)
        except Exception,e:
            fileh.close()
            raise e

    def _compose_array_parameter(self,index_extent):
        """ Create input tuple to read pytable array node
        according to data extent given
        """
        
        l=len(index_extent)       
        if l<1:
            raise HDF5DataSourceErr("invalid datarefference\
            extent used when trying to access HDF5 data")
        
        para=[0]*l
        i=0
        for val in index_extent:            
            if type(val)==tuple:
                val=slice(*val)
            para[i]=val
            i=i+1
        return tuple(para)

    def _parse_extents(self,extents,node):
        
        """ Temporary function to interpret data
            extent to dimension indexes.

            extent is list of extent tuple, node
            is array node,temporary solution.
        """
        extent_indexs=[None]*len(node.shape)
        time_seq=None        
        hastime=False

        name=node.name
        if not name in _DIMENSION_SACLE_MAP.keys():
            raise Warning("%s don't have dimension scale defined"%name)       
        scalelst=_DIMENSION_SACLE_MAP[name]
        nlst=[nl[0] for nl in scalelst]
        nlst.append(HDF_TIME_SCALE)
        
        for extent in extents:
            extent_name=extent[0]           
            if extent_name=="time_window":
                hastime=True
                extent_name=HDF_TIME_SCALE
                ((index,time_seq),di)= \
                self._parse_extent(extent,node)
            else:
                (index,di)=self._parse_extent(extent,node)
                
                
            extent_indexs[di]=index
            nlst.remove(extent_name)
            
        if not hastime:
            ((index,time_seq),di)=self._parse_extent(("time_window","all"),node)
            extent_indexs[di]=index
            nlst.remove(HDF_TIME_SCALE)

        if len(nlst)>0:
            raise HDF5AccessError("Data channel %s not setting"%nlst)
            
        return (extent_indexs,time_seq)

    def _map_extentname_to_index(self,extent_name,node):

        ## for the time being using dimension_labels
        ## str attr of node to map extent_name to
        ## mapping to dimension index.
        if extent_name=="time_window":
            return 0

        name=node.name
        if not name in _DIMENSION_SACLE_MAP.keys():
            raise Warning("%s don't have dimension scale defined"%name)   
            
        scalelst=_DIMENSION_SACLE_MAP[name]
                
        for (scalename,index) in scalelst:
            if scalename==extent_name:
                return index
        #pdb.set_trace()
        raise HDF5AccessError("Cann't map extent %s to dimension index"%extent_name)         

    def _parse_extent(self,extent,node):
        
        """ This part intepret extent into
            range of node array indexes.
        """
        #pdb.set_trace()
        
        extent_name=extent[0]
        extent_value=extent[1]

        hdf5fh=node._v_file
        
        dim_index=self._map_extentname_to_index(extent_name,node)
        
        if not HDF_TIME_SCALE in extent_name:##usual channel
            path2scale_node=_DIMENSION_SCALE_PATH+extent_name
            try:
                scale_node=hdf5fh.getNode(path2scale_node,classname="Array")
            except tables.NoSuchNodeError,e:
                ## if this dimension have no scale, then
                ## assuming dimension index used directly
                ## as scale.
                try: ## try to cast extent value into int as index of dimension
                    index=int(extent_value)-1
                    return (index,dim_index)
                except:
                    raise ValueError("Input extent %s cann't \
                    be interpreted"%extent)
            
            scale_lst=scale_node.read()
            temp=[]

            for scale in scale_lst:
                if type(scale)==string_:
                    scale=scale.strip()
                temp.append(scale)
                
            return (temp.index(extent_value),dim_index)
        else: ## for time only
            return (self._parse_time_extent(extent_value,node,\
                                           dim_index),dim_index)
                
    
    def _parse_time_extent(self,time_extent_val,node,di):
       """ Based on the given time_extent string return
           index extent of data array.

           Temporary solution only.
       """
       if hasattr(node.attrs,"interval"):## this is rts
           (indexes,tseq)=self._parse_rts_time_ex(time_extent_val,node,di)
       else: ## treat it as its,try to find ordered time
            ## points saved in file
           (indexes,tseq)=self._parse_its_time_ex(time_extent_val,node,di)
       return (indexes,tseq)

    def _parse_rts_time_ex(self,time_extent_val,node,di):
        """ parse index of time dimension, also return rt time seq"""
            
        if hasattr(node.attrs,'start_time'):
            start_time=process_array_val(\
                getattr(node.attrs,'start_time'))
            if type(start_time)==type(' ') or \
               type(start_time)==string_:
                start_time=str(start_time)
                start_time=parse_time(start_time)
        else:
            raise HDF5AccessError("No start time given for node %s"\
                                  %node.name)
        
        interval=process_array_val(getattr(node.attrs,'interval'))
        
        if type(interval)==type(' ') or \
           type(interval)==string_:
            interval=str(interval)
            interval=parse_interval(interval)
            
        if time_extent_val=="all":
            time_seq=time_sequence\
            (start_time,interval,node.shape[di])
            return ((0,node.shape[di]),time_seq)
            
        (stime,etime)=time_extent_val
        stime=parse_time(stime)
        etime=parse_time(etime)
        i=0
        if stime<start_time:
            stime=start_time
        
        num1=number_intervals(start_time,stime,interval)
        i=num1
        ## find out number of intervals from data start
        ## time to time window endint time.
        num2=number_intervals(start_time,etime,interval)
        
        
        ## find out total num of intervals       
        num_of_interval=node.shape[di]-1
        
        if num2>num_of_interval:
            num2=num_of_interval
        
        time_seq=time_sequence(stime,interval,num2-i+1)
        
        return ((i,num2+1),time_seq)
        
    def _parse_its_time_ex(self,time_extent_val,node):
        
        if time_extent_val=="all":
            return range(0,scalename.shape[di],1)

    def _dissect(self,dataref):
        return None

    def _assemble(self,translation,**kargs):
        
        if not translation:
            raise ValueError("input translation must be given in"
                             "assembling hdf reference.")
        else:
            selector=translation

        return  [DataReferenceFactory(DSS_DATA_SOURCE,source=destination,\
                                     view=None,selector=selector)]       
             

        
 
        

        

           
           
            
            
                
                    

                

                

        


        


   
            

            

        
        
        


        



    
        



    
        
    

