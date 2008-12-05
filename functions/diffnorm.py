"""  uility to compute ts norm (L_1,L_2,L_inf)
"""
import numpy

########################################################################### 
## Public interface.
###########################################################################

__all__=["norm_diff_L1","norm_diff_L2","norm_diff_Linf","ts_equal"]


def _norm_L1_array(data):
    """
        estimate L_1 norm of input numpy array data
    """
    data=numpy.abs(data)
    return data.sum()
    
def _norm_L2_array(data):
    """
        estimate L_2 norm of input numpy array data
    """
    data=numpy.square(data)
    val=data.sum()
    val=numpy.sqrt(val)
    return val


def _norm_Linf_array(data):
    """
        estimate L_inf norm of input numpy array data
    """
    data=numpy.abs(data)
    return numpy.maximum.reduce(data)
    
    
def norm_diff_L1(ts1,ts2,window=None):
    if window is None:
        window=(ts1.start,ts1.end)
    st=window[0]
    et=window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_L1_array(diffts.data)
    
    
def norm_diff_L2(ts1,ts2,window=None):
    if window is None:
        window=(ts1.start,ts1.end)
    st=window[0]
    et=window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_L2_array(diffts.data)
    
    
    
def norm_diff_Linf(ts1,ts2,window=None):
    if window is None:
        window=(ts1.start,ts1.end)
    st=window[0]
    et=window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_Linf_array(diffts.data)
            
def ts_equal(ts1,ts2,window=None,tol=0.0e0):

    if window is None:
        window=(ts1.start,ts1.end)
        
    st=window[0]
    et=window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    l1=_norm_Linf_array(diffts.data)
    if l1<=tol:
        return True
    else:        
        return False
    
