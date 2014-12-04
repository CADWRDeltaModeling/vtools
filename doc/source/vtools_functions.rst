
Timeseries operations and function
====================================

VTools provides a number of time series operations and functions. 

Python Imports
--------------

A lot of the functions are split off in their own files. If 
you are writing a module for reuse, you may want to use the
modules and do a minimal import for name hiding. However, 
for analysis everything in the functions API can be accessed using this import::

from vtools.functions.api import *


Interpolation
-------------

There are several vtools functions for interpolation. Your choice 
of function and interpolation method should hinge on:

 * whether you are interpolating to a new set of times or filling gaps

    * to interpolate to new times (perhaps using another time series as a
      prototype): :func:`~vtools.functions.interpolate.interpolate_ts`
    * to fill gaps: :func:`~vtools.functions.interpolate.interpolate_ts_nan`
    
 * whether your time series is instantaneous or period averaged:
 
    * Most methods assume instantaneous. Use the function :func:`~vtools.functions.interpolate.rhistinterp` for period averaged data or the RHIST method option from the abovementioned functions. The
    tension parameter can also be used to enforce a lower bound (e.g. positivity of salinity).
 
The interpolation method will depend on:
 
 * how smooth the series is:
 
     * LINEAR is robust in noisy data
     * MSPLINE is a monotonicity preserving spline that combines great accuracy with good robustness.
     * SPLINE is the spline technique from Scipy which is a smoothing spline, not an exact interpolant. The spline is slower than the others.
     * RHIST is the best choice for period averaged data
     * PREVIOUS means the previous value will be repeated. Good for discrete valued data such as gate opening and closing.
     * NEXT means the forward value will be copied backward.
 
 * whether you need an "exact" interpolant that goes through all values exactly.
 * whether you need to enforce monotonicity or positivity. If these are important, MSPLINE and RHIST are preferred.
 
Here is an example of how :func:`~vtools.functions.interpolate.inteprolate_ts_nan` fills 
nan values on an existing series. : and :func:`~vtools.functions.interpolate.inteprolate_ts`
which interpolates one time series to a new interval or to times
from a sample series or time sequence. 

.. plot:: ../../vtools/examples/functions/interpolation.py
  :include-source:

Low Pass Filtering (noise, tidal, spring-neap)
-------------------------------------------------

The cases below are all just special cases of low pass filtering, but motivated by
different goals (noise removal, tidal filtering and spring-neap filtering). All of the
filters are phase-neutral, meaning they do not cause an apparent shift in the time series
as a single pass of a Cosine-Lanczos or Butterworth filter might do.

For tidal filtering, we recommend the cosine-Lanczos (really CL squared) filter with a cutoff of 40 hours which is fairly standard in the tidal literature. The Godin filter is
commonly used for its simplicity and minimal support which means less amplification of gaps. However, its performance on signals with a period of 2-3 days is abysmal.

Noise filter
^^^^^^^^^^^^^^^
.. plot:: ../../vtools/examples/functions/filter.py
  :include-source:
  
Tidal filter
^^^^^^^^^^^^
.. plot:: ../../vtools/examples/functions/tidal.py
  :include-source:
  
Spring-neap filter
^^^^^^^^^^^^^^^^^^
.. plot:: ../../vtools/examples/functions/spring_neap_tide.py
  :include-source:


Resampling and decimation
-------------------------
:func:`vtools.functions.resample` takes a finer time series and downsamples it to a coarser time step. :func:`vtools.functions.decimate` is a refimenment of this strategy which first passes the data through a low pass filter then resamples. Our version comes from
a GNU Octave .m function. Decimation is also something you can do yourself. Just low pass
to a period twice that of the time step you want to resample at. So if you are going to
resample at a one hour frequency, eliminate everything with a period short of two hours.

.. plot:: ../../vtools/examples/functions/resampling.py
  :include-source:

Ufuncs on time series
---------------------
OK, not a very informative name but ufuncs (universal functions) are a standard numpy method for applying the same function to every item in one or two time series. Furthermore, 
the operation can be done cumulatively or pointwise. See the .. _numpy ufunc docs: http://docs.scipy.org/doc/numpy/reference/ufuncs.html. These documents give a good
descripation of what the apply, reduce and accumulate methods do.

In vtools, ufuncs are supported in the :func:`vtools.functions.ts_ufunc module`. The 
ufunc is pretty much passed right over to the data member of the time series,
so this is just a convenience. The generic implementations for time series are :func:`~vtools.functions.ts_ufunc.ts_apply` :func:`~vtools.functions.ts_ufunc.ts_accumulate` and :func:`~vtools.functions.ts_ufunc.ts_reduce`. There are also some specific ufunc implementations for time series such as :func:`~vtools.functions.ts_ufunc.ts_maximum` that are potentially useful.


Period ops
----------
VTools provides for creating period statistics such as daily/monthly averages, max or min.
The output of these operations is a new time series at a coarser time step. 
 
.. plot:: ../../vtools/examples/functions/period_op.py
  :include-source:
  
Shifting
--------
Time series can be shifted forward or back in time with :func:`vtools.functions.shift`.

.. plot:: ../../vtools/examples/functions/shifting.py
  :include-source:

Merging
-------
VTools will facilitate a prioritized merging 
using :func:`vtools.functions.merge`::

    from vtools.functions.api import merge
    ts_merged = merge(ts_high_priority,ts_medium,ts_low)



