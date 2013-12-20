"""  uility to compute ts norm (L_1,L_2,L_inf).

"""
import numpy

########################################################################### 
## Public interface.
###########################################################################

__all__=["norm_diff_l1","norm_diff_l2","norm_diff_linf","ts_equal","ts_almost_equal"]


def _norm_L1_array(data):
    """estimate L_1 norm of input numpy array data.
    
    """
    data=numpy.abs(data)
    return data.sum()
    
def _norm_L2_array(data):
    """estimate L_2 norm of input numpy array data.
    """
    data=numpy.square(data)
    val=data.sum()
    val=numpy.sqrt(val)
    return val


def _norm_Linf_array(data):
    """estimate L_inf norm of input numpy array data.
    
    """
    data=numpy.abs(data)
    return numpy.maximum.reduce(data)
    
    
def norm_diff_l1(ts1,ts2,time_window=None):
    """ compute L1 difference of two input time series.

    Parameters
    -----------

    ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
              Must has data of one dimension, and regular.
    
    time_window : :ref:`time_window<time_window>` ,optional 
        The default implies comparing the full length of two time series.
   
    Returns
    -------
    result : float
        a total L1-difference between two input series .
        
    """

    if time_window is None:
        time_window=(ts1.start,ts1.end)
    st=time_window[0]
    et=time_window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_L1_array(diffts.data)
    
    
def norm_diff_l2(ts1,ts2,time_window=None):
    """ compute L2 difference of two input time series.

    Parameters
    -----------
    ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    time_window : :ref:`time_window<time_window>`,optional
        The default implies comparing the full length of two time series.
           

    Returns
    -------
    result : float
        A total L2-difference between two input series .
        
    """
    if time_window is None:
        time_window=(ts1.start,ts1.end)
    st=time_window[0]
    et=time_window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_L2_array(diffts.data)
    
    
    
def norm_diff_linf(ts1,ts2,time_window=None):
    """ compute L_inf difference of two input time series.

    Parameters
    -----------
    ts1,ts2: :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    time_window : :ref:`time_window<time_window>`,optional
        The default implies comparing the full length of two time series.

    Returns
    -------
    result : float
        A total L_infinite difference between two input series .
        
    """
    if time_window is None:
        time_window=(ts1.start,ts1.end)
    st=time_window[0]
    et=time_window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    return _norm_Linf_array(diffts.data)
            
def ts_equal(ts1,ts2,time_window=None,tol=0.0e0):
    """compare two ts by absolute difference.

    Parameters
    -----------
    ts1.ts2 : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    time_window : :ref:`time_window<time_window>`,optional
        The default implies comparing the full length of two time series.
           
    tol    :float,optional
        Tolerance allowed for two equal time sereies.
        
    Returns
    -------
    result : bool
        if equal within allowed tolerance, return True .
        
    """
    if time_window is None:
        time_window=(ts1.start,ts1.end)
        
    st=time_window[0]
    et=time_window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    l1=_norm_Linf_array(diffts.data)
    if l1<=tol:
        return True
    else:        
        return False
        
def ts_almost_equal(ts1,ts2,time_window=None,tol=1.0e-8):
    """compare two ts by absolute difference.

    Parameters
    -----------
    ts1,ts2 : :class:`~vtools.data.timeseries.TimeSeries`
        Must has data of one dimension, and regular.
    
    time_window : :ref:`time_window<time_window>`,optional
        The default implies comparing the full length of two time series.
           
    tol    :float,optional
        Tolerance allowed for two almost equal time sereies.
        
    Returns
    -------
    result : bool
        If equal within allowed tolerance, return True .
        
    """
    if time_window is None:
        time_window=(ts1.start,ts1.end)
        
    st=time_window[0]
    et=time_window[1]
    diffts=ts1.window(st,et)-ts2.window(st,et)
    if ts1.window(st,et).data.all():
        diffts=diffts/ts1.window(st,et)
    else: ## t
        i=0
        for t1 in ts1.window(st,et).data:
            diff=diffts.data[i]
            if t1 :
                diffts.data[i]=diff/t1  
            i=i+1
    
    l1=_norm_Linf_array(diffts.data)
    if l1<=tol:
        return True
    else:        
        return False
    

    
