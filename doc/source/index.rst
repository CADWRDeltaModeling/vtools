.. vtools documentation master file, created by
   sphinx-quickstart on Fri Nov 15 21:20:59 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================
Introduction
=================
Welcome to the vtools documentation page. Vtools is a package to perform time-aligned operations on time series, as well as some specialty analyses encountered in hydrology and hydrodynamic work and modeling. The goal of vtools is to fill in around tools like `pandas <http://pandas.sourceforge.net/>`_  and `netcdf4-python <http://code.google.com/p/netcdf4-python/>`_ and to provide a bridge between netcdf and the legacy format HEC-DSS from the Hydrologic Engineering Center of the Army Corps of Engineers.

====================
Documentation 
====================
Learning vtools is something you can mostly learn by example, so most of the topics below are coding examples with a few explanations. There is some traditional api documentation as well.


Contents
--------

.. toctree::
   :maxdepth: 2

   Installing vtools <install_vtools>
   Time and time series concepts <timeseries>
   Functions <vtools_functions>
   Getting data in and out of vtools <datastore>
   Plotting recipes <plotting>


Test of inline class doc
------------------------
See :class:`~vtools.data.timeseries.TimeSeries`

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

