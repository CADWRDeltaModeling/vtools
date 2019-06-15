
# Standard Library imports

# Scipy import
from scipy import array,string_

# datetime import
from datetime import datetime

class Dimension(object):
    """ Parent Class store meaningful index information of a dataset
        dimension.
      
        For instance, within a multi-dimensional array dataset, first
        dimension is indexing of location, second dimension is indexing
        of time, and so on.
    """

    # Public traits ########################################## 
    # A single describing label used for the dimension.
    label="unkown_scale"
    # Dimension may have a name to identify it
    name=""
    # Dimension keep track of the index of dimension, todo: not needed?
    #dimension_index=Int(-9999)
    

class ChannelDimension(Dimension):
    """ Sub Class store meaningful index information of a dataset
        dimension as a list.
         
    """

    # Private traits ##########################################    
    _channel=[]
    #_channel=Array
    _index_map={}

  
    
    ########################################################################### 
    # Object interface.
    ###########################################################################
    def __init__(self,channel_list=[]):        
        self.set_channels(channel_list)

    def __str__(self):
        return self.label+":"+str(self._channel[0])

    ########################################################################### 
    # Public interface.
    ###########################################################################
    def set_channels(self,channel_list):
        """ Set internal data channel list."""
        for e in channel_list:
            if type(e)==type(' ') or\
               type(e)==string_:
                e=e.strip()
                
            self._channel.append(e)
            
        for i in range(0,len(channel_list)):
            self._index_map[channel_list[i]]=i
        
    def get_channel(self,index):
        """ Return data channel at index """

        if (index<0) or (index>(len(self._channel)-1)):
            raise ValueError("invalid channel index")
        return self._channel[index]

    def get_index(self,channel):
        """ return the index of a channel in the
        inner list.
        """                
        if channel in list(self._index_map.keys()):
            return self._index_map[channel]
        else:
            raise KeyError("%s doesn't exist in this dimension"%channel)
            

class RangeDimension(Dimension):
    """ Sub Class store meaningful index information of a dataset
        dimension as a pair of start and end of some kind of value.
         
    """
    
    ########################################################################### 
    # Object interface.
    ###########################################################################

    def __init__(self,range=None,label="time_window",\
                 name="time_window",index=0,interval=None):

        if range:           
            if not(type(range)==tuple):
                raise TypeError("Instance of RangeDimension must be initalized by \
                a tuple if given")

            if range[0]>range[1]:
                raise ValueError("first item of range tuple must not be larger than\
                second")                
            self._start=range[0]
            self._end=range[1]

            self.label=label
            self.name=name
            self.dimension_index=index
            if interval:
                self.interval=interval
    def __str__(self):

        result=self.label+":"

        if self._start:
            start=self._start
            if type(start)==datetime:
                start=start.strftime('%m/%d/%Y %H:%M')
            else:
                start=str(start)
            result=result+start
        
        if self._end:
            end=self._end
            if type(end)==datetime:
                end=end.strftime('%m/%d/%Y %H:%M')
            else:
                end=str(end)
            result=result+"-"+end        
        
        return result
        
            
    ########################################################################### 
    # Public interface.
    ###########################################################################
    def isregular(self):
        return hasattr(self,"interval")

    def set_range(self,range):
        """ Setup inner range of range dimension"""
        
        if not(type(range)==tuple):
            raise TypeError("Range of Instance of RangeDimension must be set by \
            a tuple")

        if range[0]>range[1]:
            raise ValueError("first item of range tuple must not be larger than\
            second")
            
        self._start=range[0]
        self._end=range[1]

    def get_range(self):

        """ Return range setted"""

        return (self._start,self._end)


    


    
    







    
          

     
